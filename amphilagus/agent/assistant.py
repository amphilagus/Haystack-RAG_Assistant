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
from .tools import run_embedding_search, format_with_references as tools_format_with_references, get_collection_titles as tools_get_collection_titles

from ..logger import get_logger

# Get logger
logger = get_logger("agent")

class Collection_Base_Assistant:
    """
    Base assistant class that provides common functionality for all assistant types.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        collection_name: str = None,
        max_steps: int = 10,
        top_k: int = 5
    ):
        """
        Initialize the Base Assistant.
        
        Args:
            model: The OpenAI model to use
            collection_name: The default collection to query
            max_steps: Maximum number of agent steps
            top_k: Default number of results to return
        """
        # Save the basic parameters
        self.model = model
        self.collection_name = collection_name
        self.max_steps = max_steps
        self.top_k = top_k
        
        # Tools will be set up by the subclass
        self.tools = []
        
        # Initialize specific tools for the subclass
        self._setup_tools()
        
        # Initialize the agent
        self._initialize_agent()
    
    def _setup_tools(self):
        """
        Set up the tools for the assistant.
        This method should be overridden by subclasses.
        """
        @tool
        def get_collection_titles(collection_name: Optional[str] = None) -> Dict[str, Any]:
            """
            Retrieve a list of all unique document titles from a collection.
            
            This tool fetches all unique document titles from the specified collection or from the 
            default collection if no collection name is provided. It's useful for getting an overview
            of available documents before searching for specific content.
            
            Args:
                collection_name: Optional name of the collection to retrieve titles from. 
                                If not provided, the default collection will be used.
            
            Returns:
                Dictionary containing the collection name, list of unique titles, and title count
            
            Example:
                ```python
                # Get titles from the default collection
                titles = get_collection_titles()
                
                # Get titles from a specific collection
                titles = get_collection_titles("research_papers")
                ```
            """
            # Use the specified collection or fall back to the default
            coll_name = collection_name or self.collection_name
            
            if not coll_name:
                return {
                    "error": "No collection specified. Either provide a collection_name parameter or set a default collection when initializing.",
                    "collection_name": None,
                    "titles": [],
                    "title_count": 0
                }
                
            # Call the original get_collection_titles function
            return tools_get_collection_titles(collection_name=coll_name)
            
        # Add the tool to the list (subclasses will add more specific tools)
        self.tools = [get_collection_titles]
    
    def _initialize_agent(self):
        """
        Initialize the agent with the tools.
        """
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
    
    def _get_system_prompt(self, query: str) -> str:
        """
        Get the system prompt for the agent.
        This method should be overridden by subclasses.
        
        Args:
            query: The user's query or statement
            
        Returns:
            The system prompt as a string
        """
        return "You are a helpful assistant."
    
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
        
        # Get the system prompt
        system_prompt = self._get_system_prompt(query)
        
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
            error_message = f"Error processing your request: {str(e)}"
            if debug:
                return {
                    "response": error_message,
                    "debug_info": {"error": str(e)}
                }
            else:
                return error_message


class Collection_QA_Assistant(Collection_Base_Assistant):
    """
    Assistant class for embedding-based collection querying.
    Provides a wrapper around Haystack Agent with embedding search tool.
    """
    
    def _setup_tools(self):
        """
        Set up the search_collection tool.
        """
        # Call the parent class method to get the base tools
        super()._setup_tools()
    
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
    
        # Append the new tool to the existing base tools
        self.tools.append(search_collection)

    def _get_system_prompt(self, query: str) -> str:
        """
        Get the QA system prompt.
        
        Args:
            query: The user's question
            
        Returns:
            The system prompt for QA
        """
        return f"""You are a specialized scientific literature assistant that helps researchers find relevant information in document collections.

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
        

class Collection_Ref_Assistant(Collection_Base_Assistant):
    """
    Assistant class that takes a statement, divides it into sections, finds the most relevant 
    references for each section, and then combines them into a properly referenced document.
    """
    
    def _setup_tools(self):
        """
        Set up the specific tools for reference assistant.
        """
        # Call the parent class method to get the base tools
        super()._setup_tools()
    
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
            results = run_embedding_search(
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
            
        # Append the new tools to the existing base tools
        self.tools.extend([search_collection_with_refs, format_with_references])

    def _get_system_prompt(self, statement: str) -> str:
        """
        Get the reference system prompt.
        
        Args:
            statement: The user's statement
            
        Returns:
            The system prompt for references
        """
        return f"""You are a specialized scientific reference assistant that helps add appropriate references to scientific statements WITHOUT changing their content or length.

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

    def run(self, statement: str, collection_name: str = None, top_k: int = 5, debug: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Process a statement by dividing it into sections, finding references, and formatting.
        Overrides the base run method to use statement terminology instead of query.
        
        Args:
            statement: The statement text to process
            collection_name: Optional collection name (overrides default)
            top_k: Number of results to return
            debug: Whether to return debug information along with the response
            
        Returns:
            Either a response string (debug=False) or a dictionary with response and debug info (debug=True)
        """
        # Use the base class run method but with statement as query
        return super().run(statement, collection_name, top_k, debug)


class Collection_Sum_Assistant(Collection_Base_Assistant):
    """
    Assistant class specialized in summarizing comprehensive information from specified articles.
    It extracts key aspects like research background, methods, objectives, content, conclusions,
    highlights, reception time, and research field.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        collection_name: str = None,
        max_steps: int = 30,  # Increased max steps for more thorough analysis
        top_k: int = 5  # Increased top_k for more context
    ):
        """
        Initialize the Summary Assistant with specialized parameters.
        
        Args:
            model: The OpenAI model to use
            collection_name: The default collection to query
            max_steps: Maximum number of agent steps
            top_k: Default number of results to return
        """
        super().__init__(model, collection_name, max_steps, top_k)
    
    def _setup_tools(self):
        """
        Set up the search_collection tool for article summarization.
        """
        # Call the parent class method to get the base tools
        super()._setup_tools()
        
        @tool
        def search_collection(queries: List[str], title: str) -> Dict[str, Any]:
            """
            Search documents in the predefined collection using embedding-based semantic search.
            
            Args:
                queries: List of question strings to search for in the collection
                title: The title of the article to search within. The search will be limited to 
                      documents with this title. This parameter is required for targeted article 
                      summarization.
            Returns:
                Dictionary containing the search results for each query
            
            Example:
                ```python
                # Simple usage with a list of questions
                results = search_collection(["What is the research background of this article?", 
                                           "What methods were used in this research?"])
                ```
            
            Raises:
                ValueError: If no collection_name was specified during initialization
            """
            
            # Convert simple string queries to the expected format
            formatted_queries = []
            for query in queries[:6]:
                formatted_queries.append({
                    "query": query,
                    "mode": "run_with_selected_title",
                    "top_k": self.top_k,
                    "title": title,
                })
            logger.debug(f"total number of queries: {len(queries)}")
            logger.debug(f"total number of formatted queries: {len(formatted_queries)}")
            # Call the original run_embedding_search with fixed collection_name and top_k
            return run_embedding_search(
                collection_name=self.collection_name,
                queries=formatted_queries,
            )
        
        # Append the new tool to the existing base tools
        self.tools.append(search_collection)

    def _get_system_prompt(self, article_title: str) -> str:
        """
        Get the system prompt for comprehensive article summarization.
        
        Args:
            article_title: The title of the article to summarize
            
        Returns:
            The system prompt for article summarization
        """
        return f"""You are a specialized scientific article summarization assistant that provides comprehensive information about academic papers.

Your task is to create a detailed summary of the article titled "{article_title}" by extracting information from the document collection.

First, confirm that the article exists in the collection by using the get_collection_titles tool. 

Then, perform a systematic, multi-round search to gather all necessary information. For each information category, make multiple targeted queries as needed to ensure comprehensive coverage.

IMPORTANT: To manage token usage effectively, follow these guidelines when searching:
1. Make focused, single-direction queries for each information type
2. Break down your searches into multiple smaller, specific queries rather than fewer broad ones
3. Progressively build your understanding through sequential, targeted searches
4. Always perform at least two rounds of searches for each information category to ensure accuracy and completeness
5. If initial search results are incomplete or unclear, formulate follow-up queries that address specific gaps
6. Use the information from earlier searches to inform and refine subsequent queries

Extract and summarize information in the following categories:

### Research Background (背景)
- Historical context of the research
- Current state of the field
- Problems or gaps being addressed
- Importance of the research area

### Research Objectives (目标)
- Primary aims and goals of the research
- Specific research questions
- Hypotheses being tested
- What the authors intended to achieve

### Research Methods (方法)
- Experimental design and approach
- Techniques and methodologies used
- Equipment, materials, or datasets utilized
- Analytical frameworks or models
- Statistical methods or analyses employed

### Research Content (内容)
- Main experiments or studies conducted
- Key data collection procedures
- Implementation details
- Step-by-step process of the research

### Main Conclusions (结论)
- Primary findings and results
- Answer to research questions
- Support or rejection of hypotheses
- Interpretation of results
- Implications of the findings

### Research Highlights (亮点)
- Novel contributions to the field
- Innovative approaches
- Significant breakthroughs
- Limitations acknowledged
- Advantages over existing methods or studies

### Reception Time (接收时间)
- When the paper was submitted
- When it was accepted
- When it was published
- Any revision history

### Research Field (领域)
- Primary discipline
- Interdisciplinary connections
- Specific subfields involved
- Potential application domains

CRITICAL REQUIREMENT: You MUST complete ALL the above categories before concluding your summary. 
Do not return a partial response! If you haven't gathered information for all categories yet, 
continue searching and collecting information until you have addressed every category.

For any category where information truly cannot be found despite exhaustive searching 
(at least 3 different targeted queries), explicitly state "Information not available for this category 
after multiple search attempts" under that heading.

Format your response in clean, well-structured Markdown with main sections for each category. Use bullet points for key items and proper headings.

Your summary must be:
1. Comprehensive - covering ALL listed categories with multiple relevant details
2. Accurate - based only on information found in the document collection
3. Well-organized - with clear section headings and logical structure
4. Concise yet thorough - providing key information without unnecessary repetition
5. Formatted in Markdown - using proper headings, bullet points, and emphasis

Begin with a brief overview of the article, then organize the information under the appropriate headings.
"""

    def run(self, article_title: str, collection_name: str = None, top_k: int = None, debug: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Summarize comprehensive information from a specified article.
        
        Args:
            article_title: The title of the article to summarize
            collection_name: Optional collection name (overrides default)
            top_k: Number of results to return
            debug: Whether to return debug information along with the response
            
        Returns:
            Either a formatted summary (debug=False) or a dictionary with response and debug info (debug=True)
        """
        # Use the base class run method with article_title as query
        return super().run(article_title, collection_name, top_k, debug)


class Collection_Chat_Assistant(Collection_Base_Assistant):
    """
    A meta-assistant that provides a simple chat interface to access various established workflow tools
    and other assistants. This assistant doesn't perform specialized tasks itself but rather
    coordinates the use of other tools based on user requests.
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
            collection_name: The default collection to query
            max_steps: Maximum number of agent steps
            top_k: Default number of results to return
        """
        super().__init__(model, collection_name, max_steps, top_k)
    
    def _setup_tools(self):
        """
        Set up the tools for the chat assistant, providing access to the full suite
        of collection-based tools and workflows.
        """
        # Call the parent class method to get the base tools
        super()._setup_tools()
        
        @tool
        def generate_article_summary(article_title: str) -> str:
            """
            Generate a comprehensive summary of a specific article.
            
            This tool uses the Collection_Sum_Assistant to create a detailed summary of 
            the specified article from the current collection, covering research background,
            methods, objectives, content, conclusions, highlights, reception time, and field.
            
            Args:
                article_title: The exact title of the article to summarize
                
            Returns:
                A comprehensive markdown-formatted summary of the article
            """
            try:
                # Create a summarization assistant for the current collection
                summarizer = Collection_Sum_Assistant(
                    model=self.model,
                    collection_name=self.collection_name,
                    top_k=self.top_k
                )
                
                # Generate the summary
                summary = summarizer.run(article_title=article_title)
                return summary
                
            except Exception as e:
                logger.error(f"Error generating article summary: {str(e)}", exc_info=True)
                return f"Error generating summary for '{article_title}': {str(e)}"
        
        @tool
        def summarize_all_collection_articles(model: Optional[str] = None) -> Dict[str, Any]:
            """
            Generate comprehensive summaries for all articles in the current collection.
            
            This tool processes every article in the collection, creates detailed summaries,
            and saves them as markdown files in a dedicated directory.
            
            Args:
                model: Optional model to use for summarization. If not specified, the
                       current assistant's model will be used.
                
            Returns:
                A dictionary with information about the summarization process,
                including success/failure counts and the directory where summaries are saved
            """
            from .agent_tools import batch_summarize_articles
            # Use specified model or fall back to the assistant's model
            model_to_use = model or self.model
            
            # Call the batch summarization tool
            return batch_summarize_articles(
                collection_name=self.collection_name,
                model=model_to_use,
                top_k=self.top_k
            )
        
        @tool
        def add_references_to_text(text: str) -> Dict[str, Any]:
            """
            Add scientific references to a statement or text using the current collection.
            
            This tool analyzes the provided text, finds relevant scientific articles in the
            collection, and adds citation markers to the text along with a reference list.
            
            Args:
                text: The statement or text to add references to
                
            Returns:
                A dictionary containing the original text with citations added and a list of references
            """
            try:
                # Create a reference assistant for the current collection
                ref_assistant = Collection_Ref_Assistant(
                    model=self.model,
                    collection_name=self.collection_name,
                    top_k=self.top_k
                )
                
                # Add references to the text
                result = ref_assistant.run(statement=text)
                
                # Check if the result is already a dictionary with main_text and references_list
                if isinstance(result, dict) and "main_text" in result and "references_list" in result:
                    return result
                
                # If the result is a string, it might be an error message or the raw result
                return {
                    "main_text": result,
                    "references_list": []
                }
                
            except Exception as e:
                logger.error(f"Error adding references to text: {str(e)}", exc_info=True)
                return {
                    "error": f"Error adding references: {str(e)}",
                    "main_text": text,
                    "references_list": []
                }
        
        @tool
        def ask_collection_question(question: str) -> str:
            """
            Ask a question about the content in the current collection.
            
            This tool uses the Collection_QA_Assistant to find relevant information
            in the collection and provide a comprehensive answer.
            
            Args:
                question: The question to ask about the collection's content
                
            Returns:
                A detailed answer based on the collection's content
            """
            try:
                # Create a QA assistant for the current collection
                qa_assistant = Collection_QA_Assistant(
                    model=self.model,
                    collection_name=self.collection_name,
                    top_k=self.top_k
                )
                
                # Get the answer to the question
                answer = qa_assistant.run(query=question)
                return answer
                
            except Exception as e:
                logger.error(f"Error answering collection question: {str(e)}", exc_info=True)
                return f"Error answering question: {str(e)}"
        
        # Append the new tools to the existing base tools
        self.tools.extend([
            generate_article_summary,
            summarize_all_collection_articles,
            add_references_to_text,
            ask_collection_question
        ])
    
    def _get_system_prompt(self, query: str) -> str:
        """
        Get the system prompt for the chat assistant.
        
        Args:
            query: The user's message
            
        Returns:
            The system prompt for the chat assistant
        """
        return f"""You are a helpful collection assistant that provides access to various specialized tools for working with scientific document collections.

Your current collection is: {self.collection_name}

You can help the user by calling the appropriate tool based on their request:

1. If they want information about what articles are in the collection:
   - Use get_collection_titles to retrieve a list of all article titles

2. If they want a detailed summary of a specific article:
   - Use generate_article_summary to create a comprehensive summary of that article

3. If they want to summarize all articles in the collection:
   - Use summarize_all_collection_articles to process the entire collection

4. If they want to add scientific references to a statement or text:
   - Use add_references_to_text to find relevant citations in the collection

5. If they have a question about the content in the collection:
   - Use ask_collection_question to find and synthesize relevant information

When the user asks for something:
- Identify which tool would be most appropriate
- Call that tool with the necessary parameters
- Present the results in a user-friendly way

Be conversational and helpful, but focus on using the right tool for each task rather than trying to do the work yourself. Your strength is in coordinating specialized tools to accomplish complex tasks.

If the user asks for something that doesn't clearly match one of your tools, ask clarifying questions to determine which tool would be most appropriate.
"""

