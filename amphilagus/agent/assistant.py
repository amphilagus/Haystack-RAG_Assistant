"""
Assistant module for collection-based question answering using embeddings.
"""
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack.tools import tool
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional, Union
from functools import partial

from .. import config

# Import the tools with an alias to avoid name conflicts
from .tools import run_embedding_search, format_with_references as tools_format_with_references


class Collection_QA_Assistant:
    """
    Assistant class for embedding-based collection querying.
    Provides a wrapper around Haystack Agent with embedding search tool.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        collection_name: str = None,
        max_steps: int = 10,
        top_k: int = 5
    ):
        """
        Initialize the Collection Assistant.
        
        Args:
            model: The OpenAI model to use
            collection_name: The default collection to query
            max_steps: Maximum number of agent steps
            top_k: Default number of results to return
        """
        # Save the default collection name and top_k
        self.collection_name = collection_name
        self.top_k = top_k
    
        @tool
        def search_collection(queries: List[str]) -> Dict[str, Any]:
            """
            Search documents in the predefined collection using embedding-based semantic search.
            
            Args:
                queries: List of question strings to search for in the collection
            
            Returns:
                Dictionary containing the search results for each query
            
            Example:
                ```python
                # Simple usage with a list of questions
                results = search_collection(["What is quantum computing?", "How do neural networks work?"])
                ```
            
            Raises:
                ValueError: If no collection_name was specified during initialization
            """
            
            # Convert simple string queries to the expected format
            formatted_queries = []
            for query in queries:
                formatted_queries.append({
                    "query": query,
                    "mode": "run",
                    "top_k": self.top_k,
                })
            
            # Call the original run_embedding_search with fixed collection_name and top_k
            return run_embedding_search(
                collection_name=self.collection_name,
                queries=formatted_queries,
                top_k=self.top_k,
                mode="run"
            )
    
        # Initialize the agent
        self.agent = Agent(
            chat_generator=OpenAIChatGenerator(
                model=model,
                tools=[search_collection],
                api_key=Secret.from_token(config.api_key)
            ),
            tools=[search_collection],
            max_agent_steps=max_steps,
            exit_conditions=["text"]
        )

    def run(self, query: str, collection_name: str = None, top_k: int = 5, debug: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Run the agent with a user query.
        
        Args:
            query: User query string
            collection_name: Optional collection name (overrides default)
            top_k: Number of results to return
            debug: Whether to return debug information along with the response
            
        Returns:
            Either a response string (debug=False) or a dictionary with response and debug info (debug=True)
        """
        # Determine which collection to use
        collection = collection_name or self.collection_name
        if not collection:
            raise ValueError("No collection specified. Either provide a collection_name parameter or set a default collection when initializing.")
        
        # Create a system prompt that instructs the agent how to use the embedding tool
        system_prompt = f"""You are a specialized scientific literature assistant that helps researchers find relevant information in document collections.

Follow this specific two-step process to get the best results:

Step 1: Generate high-quality search queries
- Based on the user's question, create 2-4 focused queries that will be effective for embedding-based retrieval
- Break down complex questions into specific, targeted queries
- Use precise technical terminology when appropriate
- Consider different phrasings and aspects of the question

Step 2: Search and synthesize information
- Use the search_collection tool with your generated queries to find relevant documents
- Carefully analyze the retrieved information, focusing on scientific content
- Synthesize a comprehensive answer based ONLY on the retrieved documents
- Your response should follow this formatting structure:
  * Start with a main heading using the user's question (e.g., "## What is a Memristor?")
  * Organize content with subheadings (e.g., "### Definition and Origin")
  * Use bullet points for listing information under each section
  * Use **bold** for emphasizing key terms and concepts
  * Include properly formatted tables using Markdown syntax when presenting comparative data

REQUIRED FORMAT EXAMPLE:
```
## What is a Memristor?

### Definition and Origin
- The **memristor** (memory resistor) is a fundamental circuit element theorized by Leon Chua in 1971.
- It was physically realized by HP Labs in 2008.

### Physical Properties
- Memristors exhibit a "pinched hysteresis loop" in their I-V characteristics.
- Resistance depends on the history of current that has passed through it.
```

IMPORTANT: 
- Never make up information. If the documents don't contain the answer, admit knowledge gaps rather than inventing details.
- Focus on organizing information clearly with appropriate headings, subheadings, and bullet points.
- Your main heading (##) must be the user's question.
- Use subheadings (###) to organize different aspects of the answer.
- Do NOT include citations or references - just present the information clearly and concisely.
"""
        
        # Create the initial messages with system and user prompts
        messages = [
            ChatMessage.from_system(system_prompt),
            ChatMessage.from_user(query)
        ]
        
        try:
            # Run the agent
            result = self.agent.run(messages=messages)
            
            if debug:
                response = result["messages"]
            else:
                # In normal mode, only return the last message text
                response = result["messages"][-1].text

            return response
                
        except Exception as e:
            # Handle errors
            error_message = f"Error processing your query: {str(e)}"
            if debug:
                return {
                    "response": error_message,
                    "debug_info": {"error": str(e)}
                }
            else:
                return error_message


class Collection_Ref_Assistant:
    """
    Assistant class that takes a statement, divides it into sections, finds the most relevant 
    references for each section, and then combines them into a properly referenced document.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        collection_name: str = None,
        max_steps: int = 10,
        top_k: int = 5
    ):
        """
        Initialize the Reference Assistant.
        
        Args:
            model: The OpenAI model to use
            collection_name: The default collection to query
            max_steps: Maximum number of agent steps
            top_k: Default number of results to return
        """
        # Save the default collection name and top_k
        self.collection_name = collection_name
        self.top_k = top_k
    
        @tool
        def search_collection_with_refs(queries: List[str]) -> Dict[str, Any]:
            """
            Search documents in the collection and return both content and most related article references.
            
            Args:
                queries: List of statement strings to search for in the collection
            
            Returns:
                Dictionary containing the search results for each query with most related articles
            
            Example:
                ```python
                # Simple usage with a list of statements
                results = search_collection_with_refs(["Memristors can be used in neuromorphic computing.", 
                                                     "2D materials show promise for memory applications."])
                ```
            
            Raises:
                ValueError: If no collection_name was specified during initialization
            """
            
            # Convert simple string queries to the expected format
            formatted_queries = []
            for query in queries:
                formatted_queries.append({
                    "query": query,
                    "mode": "run",
                    "top_k": self.top_k,
                    "only_most_related_articles": True
                })
            
            # Call the run_embedding_search with fixed collection_name and top_k
            results =  run_embedding_search(
                collection_name=self.collection_name,
                queries=formatted_queries,
                top_k=self.top_k,
                mode="run"
            )["results"]

            return results

        @tool
        def format_with_references(sections: List[Dict[str, Any]]) -> Dict[str, Any]:
            """
            Format sections of text with their corresponding references.
            
            This tool takes sections of text that have been processed by the search_collection_with_refs
            tool and formats them into a coherent document with proper scientific references.
            
            Args:
                sections: List of section objects, each containing text and reference information
            
            Returns:
                Dictionary containing the main_text (with citations) and references_list separately
            
            Example structure for sections:
            [
                {
                    "text": "Memristors have revolutionized neuromorphic computing.",
                    "references": [
                        {"title": "The Future of Memristors", "score": 0.92},
                        {"title": "Neuromorphic Computing with Memristors", "score": 0.85}
                    ]
                },
                {
                    "text": "2D materials show promise for memory applications.",
                    "references": [
                        {"title": "2D Materials in Memory Devices", "score": 0.91}
                    ]
                }
            ]
            """
            # 调用tools.py中的format_with_references函数
            result = tools_format_with_references(
                sections=sections,
                top_k=self.top_k
            )
            
            # 如果有错误，返回错误信息
            if "error" in result and result["error"]:
                return {
                    "main_text": f"Error formatting references: {result['error']}",
                    "references_list": []
                }
                
            # 返回格式化后的结果（包含main_text和references_list）
            return result
            
        # Initialize the agent
        self.agent = Agent(
            chat_generator=OpenAIChatGenerator(
                model=model,
                tools=[search_collection_with_refs, format_with_references],
                api_key=Secret.from_token(config.api_key)
            ),
            tools=[search_collection_with_refs, format_with_references],
            max_agent_steps=max_steps,
            exit_conditions=["text"]
        )

    def run(self, statement: str, collection_name: str = None, top_k: int = 5, debug: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Process a statement by dividing it into sections, finding references, and formatting.
        
        Args:
            statement: The statement text to process
            collection_name: Optional collection name (overrides default)
            top_k: Number of results to return
            debug: Whether to return debug information along with the response
            
        Returns:
            Either a response string (debug=False) or a dictionary with response and debug info (debug=True)
        """
        # Determine which collection to use
        collection = collection_name or self.collection_name
        if not collection:
            raise ValueError("No collection specified. Either provide a collection_name parameter or set a default collection when initializing.")

      # 修改系统提示
        system_prompt = f"""You are a specialized scientific reference assistant that helps add appropriate references to scientific statements WITHOUT changing their content or length.

Follow this specific process to add references to the provided statement:

Step 1: Analyze the provided statement
- Identify key claims, facts, and concepts in the statement that can be referenced
- DO NOT rewrite, summarize, or shorten the original statement
- Preserve ALL of the original content and meaning exactly as provided
- Understand and maintain any Markdown formatting in the original statement

Step 2: Find relevant references for different parts of the statement
- Use the search_collection_with_refs tool to find relevant scientific articles for different parts
- Send specific phrases or sentences as separate queries to get the most relevant articles
- You can divide the statement into logical sections for searching purposes only

Step 3: Format the statement with references
- Use the format_with_references tool to add citations to the original statement
- The original text should remain COMPLETELY intact - only add citation markers
- IMPORTANT: The format_with_references tool returns a dictionary with two keys:
  * main_text: The original text with added citation markers
  * references_list: A list of reference titles
- Preserve and maintain any Markdown formatting from the original text
- Use Markdown-compatible citation format [n] within the main_text

Step 4: Present the results
- Your final response must be the EXACT dictionary returned from format_with_references
- Do NOT modify, summarize or reformat this dictionary - return it exactly as received 
- Ensure the dictionary structure with main_text and references_list is preserved
- The main_text will preserve all Markdown formatting plus citation markers
- The references will be formatted as a list for easy display

IMPORTANT RULES:
1. NEVER shorten or paraphrase the user's statement
2. NEVER remove any content from the original statement
3. ONLY add reference citations to support the existing text
4. DO NOT attempt to improve or edit the text itself
5. The final main_text should contain all original content plus citations
6. PRESERVE all Markdown formatting in the original text
7. Add citations in a way that is compatible with Markdown ([n] format)
8. You MUST return the exact dictionary structure from the format_with_references tool

Your job is ONLY to add scientific references while preserving 100% of the original content and its Markdown formatting.
"""       
        # Create the initial messages with system and user prompts
        messages = [
            ChatMessage.from_system(system_prompt),
            ChatMessage.from_user(statement)
        ]
        
        try:
            # Run the agent
            result = self.agent.run(messages=messages)
            
            if debug:
                response = result["messages"]
            else:
                # In normal mode, only return the last message text
                response = result["messages"][-1].text

            return response
                
        except Exception as e:
            # Handle errors
            error_message = f"Error processing your statement: {str(e)}"
            if debug:
                return {
                    "response": error_message,
                    "debug_info": {"error": str(e)}
                }
            else:
                return error_message


class Chat_Assistant:
    """
    General purpose chat assistant that can be extended with various tools.
    Provides a flexible framework for processing user queries using LLM agents.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        collection_name: str = None,
        max_steps: int = 10,
        top_k: int = 5
    ):
        """
        Initialize the Chat Assistant.
        
        Args:
            model: The OpenAI model to use
            collection_name: The default collection to query (if needed)
            max_steps: Maximum number of agent steps
            top_k: Default number of results to return (if needed)
        """
        # Save basic parameters
        self.model = model
        self.collection_name = collection_name
        self.max_steps = max_steps
        self.top_k = top_k
        
        # Will be defined in _setup_tools method
        self.tools = []
        
        # Set up tools and initialize the agent
        self._setup_tools()
        self._initialize_agent()
    
    def _setup_tools(self):
        """
        Set up the tools for the assistant.
        This method should be overridden by subclasses to add specific tools.
        """
        # Example tool placeholder - to be replaced or extended
        @tool
        def example_tool(query: str) -> str:
            """
            Example tool placeholder.
            
            Args:
                query: The input query
                
            Returns:
                A response string
            """
            return f"This is a placeholder response for: {query}"
        
        # Add tools to the list
        self.tools = [example_tool]
    
    def _initialize_agent(self):
        """Initialize the agent with the defined tools."""
        self.agent = Agent(
            chat_generator=OpenAIChatGenerator(
                model=self.model,
                tools=self.tools,
                api_key=Secret.from_token(config.api_key)
            ),
            tools=self.tools,
            max_agent_steps=self.max_steps,
            exit_conditions=["text"]
        )
    
    def run(self, query: str, debug: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Process a user query using the agent.
        
        Args:
            query: The user query text
            debug: Whether to return debug information along with the response
            
        Returns:
            Either a response string (debug=False) or a dictionary with response and debug info (debug=True)
        """
        # Default system prompt - can be overridden in subclasses
        system_prompt = """You are a helpful AI assistant that can answer questions and perform tasks.
Use the provided tools when appropriate to help the user with their request.
Respond in a clear, concise, and helpful manner.
If you don't know the answer or can't perform a task, be honest about it.
"""
        
        # Create the initial messages with system and user prompts
        messages = [
            ChatMessage.from_system(system_prompt),
            ChatMessage.from_user(query)
        ]
        
        try:
            # Run the agent
            result = self.agent.run(messages=messages)
            
            if debug:
                # In debug mode, return full message objects
                response = result["messages"]
            else:
                # In normal mode, only return the last message text
                response = result["messages"][-1].text

            return response
                
        except Exception as e:
            # Handle errors
            error_message = f"Error processing your query: {str(e)}"
            if debug:
                return {
                    "response": error_message,
                    "debug_info": {"error": str(e)}
                }
            else:
                return error_message
