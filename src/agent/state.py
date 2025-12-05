"""Agent state definition for ClaimsIQ Nexus.

Contains the AgentState TypedDict for LangGraph state management.
"""

from typing import Annotated, Any, Optional, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema for the LangGraph agent.

    Attributes:
        messages: Conversation history with add_messages reducer
        canvas_mode: Current Canvas display mode (MODE_EMPTY, MODE_CLAIM, etc.)
        canvas_data: Mode-specific data payload for Canvas rendering
        canvas_title: Optional title for the Canvas display
        last_tool: Name of the last tool that was called
        reasoning_trace: List of reasoning steps for transparency
    """

    # Messages with add_messages reducer for proper message handling
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Canvas state for UI rendering
    canvas_mode: str
    canvas_data: Optional[Any]
    canvas_title: Optional[str]

    # Tool tracking
    last_tool: Optional[str]

    # Reasoning transparency
    reasoning_trace: list[dict]
