"""
Agent module for interacting with MCPTool.
"""
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional, Union


class MCPToolAgent:
    """
    Agent class for interacting with MCPTool.
    Provides a wrapper around Haystack Agent with MCPTool integration.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        server_url: str = "http://localhost:8000",
        tool_names: List[str] = None,
        api_key: Optional[str] = None,
        max_steps: int = 100
    ):
        """
        Initialize the MCPTool Agent.
        
        Args:
            model: The OpenAI model to use
            server_url: The MCP server URL
            tool_names: List of tool names to use
            api_key: OpenAI API key (if None, will try to get from environment)
            max_steps: Maximum number of agent steps
        """
        # Load environment variables if API key not provided
        if not api_key:
            load_dotenv(override=True)
            api_key = os.getenv("OPENAI_API_KEY")
            
        if not api_key:
            raise ValueError("OpenAI API key not found. Please provide it or set OPENAI_API_KEY environment variable.")
            
        # Default tool names if not provided
        if tool_names is None:
            tool_names = ["list_collections", "query_by_title", "batch_query", "verify_collection", "extract_research_paper_content"]
            
        # Initialize MCP tools
        self.tools = []
        for tool_name in tool_names:
            self.tools.append(
                MCPTool(
                    name=tool_name,
                    server_info=SSEServerInfo(base_url=server_url)
                )
            )
            
        # Initialize the agent
        self.agent = Agent(
            chat_generator=OpenAIChatGenerator(
                model=model,
                tools=self.tools,
                api_key=Secret.from_token(api_key)
            ),
            tools=self.tools,
            max_agent_steps=max_steps,
            exit_conditions=["text"]
        )
        
    def run(self, query: str, debug: bool = False) -> Union[str, List[Dict[str, Any]]]:
        """
        Run the agent with a user query.
        
        Args:
            query: User query string
            debug: Whether to return all messages in debug mode
            
        Returns:
            Either a response string (normal mode) or all messages (debug mode)
        """
        messages = [ChatMessage.from_user(query)]
        result = self.agent.run(messages=messages)
        
        if debug:
            # 在debug模式下，返回所有消息
            return result["messages"]
        else:
            # 正常模式，只返回最后一条消息的文本
            response_messages = result["messages"][-1].text
            return response_messages
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools]
