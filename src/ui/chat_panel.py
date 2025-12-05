"""Chat panel component for ClaimsIQ Nexus.

Provides the left-side chat interface (40% width) with message
history and input handling.
"""

import streamlit as st
from typing import Callable, Optional

from src.models import ReasoningTrace, TraceStep


def initialize_chat_state() -> None:
    """Initialize chat-related session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "reasoning_traces" not in st.session_state:
        st.session_state.reasoning_traces = []


def render_chat_history() -> None:
    """Render the chat message history."""
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show reasoning trace for assistant messages if available
            if message["role"] == "assistant" and i < len(st.session_state.reasoning_traces):
                trace = st.session_state.reasoning_traces[i]
                if trace and trace.get("steps"):
                    render_reasoning_trace(trace)


def render_reasoning_trace(trace: dict) -> None:
    """Render a reasoning trace in an expandable section.

    Args:
        trace: Dictionary containing reasoning trace data
    """
    steps = trace.get("steps", [])
    tools_called = trace.get("tools_called", [])
    total_duration = trace.get("total_duration_ms", 0)
    used_cache = trace.get("used_cache", False)

    if not steps:
        return

    # Create expander label
    cache_indicator = " 🎯 (cached)" if used_cache else ""
    duration_str = f"{total_duration / 1000:.1f}s" if total_duration else "N/A"
    expander_label = f"🔍 Reasoning ({len(steps)} steps, {duration_str}){cache_indicator}"

    with st.expander(expander_label, expanded=False):
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Steps", len(steps))
        with col2:
            st.metric("Tools Used", len(tools_called))
        with col3:
            st.metric("Duration", duration_str)

        st.divider()

        # Detailed steps
        for step in steps:
            action_type = step.get("action_type", "unknown")
            content = step.get("content", "")
            tool_name = step.get("tool_name")
            duration = step.get("duration_ms", 0)

            # Icon based on action type
            icons = {
                "think": "💭",
                "tool_call": "🔧",
                "observe": "👁️",
                "respond": "💬",
            }
            icon = icons.get(action_type, "•")

            # Display step
            step_header = f"{icon} **{action_type.title()}**"
            if tool_name:
                step_header += f" - `{tool_name}`"
            if duration:
                step_header += f" ({duration}ms)"

            st.markdown(step_header)

            # Show content in a subtle container
            if content:
                st.markdown(
                    f'<div style="padding: 0.5rem; margin: 0.5rem 0 1rem 1.5rem; '
                    f'background: rgba(255,255,255,0.05); border-radius: 8px; '
                    f'font-size: 0.875rem;">{content}</div>',
                    unsafe_allow_html=True,
                )

            # Show tool input/output if present
            if step.get("tool_input"):
                with st.expander("Input", expanded=False):
                    st.json(step["tool_input"])
            if step.get("tool_output"):
                with st.expander("Output", expanded=False):
                    st.json(step["tool_output"])


def render_chat_input(on_submit: Callable[[str], None]) -> Optional[str]:
    """Render the chat input and handle submission.

    Args:
        on_submit: Callback function to handle message submission

    Returns:
        User input if submitted, None otherwise
    """
    prompt = st.chat_input("Ask about claims, fraud patterns, or denial trends...")

    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Call the submission handler (this will add assistant message to session state)
        on_submit(prompt)
        
        # Force a rerun to display the new messages properly in the chat history
        # This ensures the assistant response appears immediately in the correct location
        st.rerun()

    return prompt


def add_assistant_message(content: str, trace: Optional[dict] = None) -> None:
    """Add an assistant message to the chat history.

    Args:
        content: The assistant's response text
        trace: Optional reasoning trace for transparency
    """
    st.session_state.messages.append({"role": "assistant", "content": content})

    # Store the trace (or None placeholder)
    st.session_state.reasoning_traces.append(trace)


def clear_chat_history() -> None:
    """Clear all chat history and traces."""
    st.session_state.messages = []
    st.session_state.reasoning_traces = []
