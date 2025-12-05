"""ClaimsIQ Nexus - Streamlit Application Entry Point.

Agentic Payer Intelligence Platform featuring a split-screen
"Investigator's Canvas" for healthcare claims analysis.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="ClaimsIQ Nexus",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from src.ui.styles import get_dark_mode_css, get_canvas_css
from src.ui.chat_panel import (
    initialize_chat_state,
    render_chat_history,
    render_chat_input,
    add_assistant_message,
)
from src.ui.canvas_renderer import (
    initialize_canvas_state,
    render_canvas,
    update_canvas_state,
)
from src.models import CanvasMode
from src.agent.llm_provider import get_provider_info


def initialize_session_state() -> None:
    """Initialize all session state variables."""
    initialize_chat_state()
    initialize_canvas_state()

    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    if "processing" not in st.session_state:
        st.session_state.processing = False


def process_user_message(message: str) -> None:
    """Process a user message through the agent.

    Args:
        message: The user's input message
    """
    st.session_state.processing = True

    try:
        # Import agent graph here to avoid circular imports
        from src.agent.graph import invoke_agent, get_agent

        # Initialize agent if needed
        if not st.session_state.agent_initialized:
            with st.spinner("Initializing agent..."):
                get_agent()
                st.session_state.agent_initialized = True

        # Process the message
        with st.spinner("Investigating..."):
            result = invoke_agent(message)

        # Extract response and trace
        response_text = result.get("response", "I couldn't process that request.")
        trace = result.get("trace")
        canvas_mode = result.get("canvas_mode", CanvasMode.EMPTY)
        canvas_data = result.get("canvas_data")
        canvas_title = result.get("canvas_title")
        last_tool = result.get("last_tool")

        # Update canvas state
        update_canvas_state(
            mode=canvas_mode,
            data=canvas_data,
            title=canvas_title,
            last_tool=last_tool,
        )

        # Add assistant response to chat
        add_assistant_message(response_text, trace)

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        add_assistant_message(error_msg, None)

    finally:
        st.session_state.processing = False


def main():
    """Main application entry point."""
    # Apply custom CSS
    st.markdown(get_dark_mode_css(), unsafe_allow_html=True)
    st.markdown(get_canvas_css(), unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()
    
    # Check for pending actions from buttons (e.g., "Find Related Notes")
    if "pending_action" in st.session_state and st.session_state.pending_action:
        action = st.session_state.pending_action
        st.session_state.pending_action = None  # Clear it
        
        # Add the action as a user message and process it
        query = action.get("query", "")
        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            process_user_message(query)

    # Get provider info for display
    provider_info = get_provider_info()
    provider_badge = "🟢 OpenAI" if provider_info["provider"] == "openai" else "🔵 DeepSeek"
    model_name = provider_info["model"]

    # App header with provider indicator
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="margin: 0; font-size: 2rem;">
                ClaimsIQ Nexus
            </h1>
            <p style="color: #64748b; margin: 0.5rem 0;">
                Cognitive Workspace for Payer Intelligence
            </p>
            <p style="color: #94a3b8; font-size: 0.75rem; margin: 0.25rem 0;">
                {provider_badge} • {model_name}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Main layout: 40% Chat | 60% Canvas
    col_chat, col_canvas = st.columns([0.4, 0.6])

    # Chat Panel (Left - 40%)
    with col_chat:
        st.markdown("### Investigator Chat")

        # Chat container with scrollable history
        chat_container = st.container(height=500)
        with chat_container:
            render_chat_history()

        # Chat input (outside container so it floats at bottom)
        if not st.session_state.processing:
            render_chat_input(process_user_message)
        else:
            st.chat_input("Processing...", disabled=True)

    # Canvas Panel (Right - 60%)
    with col_canvas:
        st.markdown("### Evidence Canvas")

        # Canvas container
        canvas_container = st.container(height=550)
        with canvas_container:
            render_canvas()


if __name__ == "__main__":
    main()
