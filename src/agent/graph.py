"""LangGraph ReAct Agent for ClaimsIQ Nexus.

Creates a ReAct-style agent using LangGraph's prebuilt components
with custom tools for healthcare claims investigation.
Supports multiple LLM providers (OpenAI and DeepSeek).
"""

import time
from datetime import datetime
from typing import Any, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from src.agent.llm_provider import get_llm, get_provider_info
from src.agent.state import AgentState
from src.agent.fallback import match_golden_path_query, load_golden_path
from src.models import CanvasMode
from src.tools import (
    query_claims_db,
    search_clinical_notes,
    analyze_network_graph,
    analyze_trends,
)

# Global agent cache
_agent = None

# System prompt for the agent
SYSTEM_PROMPT = """You are ClaimsIQ Nexus, an AI-powered investigator for healthcare payer intelligence.

Your role is to help users:
1. Investigate denied claims by finding supporting clinical evidence
2. Detect fraud patterns through provider-patient relationship analysis
3. Analyze denial trends across specialties and time periods

You have access to four tools:
- query_claims_db: Query structured claims data (patient info, provider info, amounts, status, dates)
- search_clinical_notes: Semantic search over unstructured clinical documentation
- analyze_network_graph: Analyze provider-patient relationships for fraud detection
- analyze_trends: Generate statistical analysis and visualizations

CRITICAL INVESTIGATION GUIDELINES:

For claim investigations:
1. ALWAYS start by querying the claim details using query_claims_db
2. If a claim is denied, search for clinical notes that might contradict the denial
3. Look for evidence in clinical notes that supports or refutes the denial reason
4. Highlight any contradictions between structured data and clinical documentation

For fraud investigations:
1. Use analyze_network_graph to visualize relationships
2. Look for circular referral patterns between providers
3. Check for unusual billing patterns in related claims
4. Report severity of findings (LOW, MEDIUM, HIGH)

For trend analysis:
1. Use analyze_trends with appropriate metric and grouping
2. Compare to benchmarks when available
3. Highlight anomalies and actionable insights

RESPONSE STYLE:
- Be concise but thorough
- Lead with the key finding or insight
- Use bullet points for multiple findings
- Cite specific evidence (claim IDs, note IDs, amounts)
- If you find a contradiction, emphasize it clearly with **bold text**

Remember: You are helping payer analysts make better decisions. Your insights should be actionable and evidence-based.
"""


def get_agent():
    """Get or create the LangGraph ReAct agent.
    
    Uses the configured LLM provider (OpenAI or DeepSeek) based on
    the LLM_PROVIDER environment variable.

    Returns:
        Compiled LangGraph agent
    """
    global _agent

    if _agent is not None:
        return _agent

    # Get LLM from provider factory (handles OpenAI or DeepSeek)
    llm = get_llm(temperature=0.1, timeout=60)
    
    # Log provider info for debugging
    provider_info = get_provider_info()
    print(f"[Agent] Using {provider_info['provider'].upper()} provider with model: {provider_info['model']}")

    # Define tools
    tools = [
        query_claims_db,
        search_clinical_notes,
        analyze_network_graph,
        analyze_trends,
    ]

    # Create ReAct agent with system prompt
    _agent = create_react_agent(
        model=llm,
        tools=tools,
    )

    return _agent


def reset_agent():
    """Reset the cached agent instance.
    
    Call this when switching LLM providers or updating configuration.
    The next call to get_agent() will create a new agent with the
    current provider configuration.
    """
    global _agent
    _agent = None
    
    # Also reset the LLM cache
    from src.agent.llm_provider import reset_llm_cache
    reset_llm_cache()


def invoke_agent(user_message: str) -> dict:
    """Invoke the agent with a user message.

    Args:
        user_message: The user's input query

    Returns:
        Dictionary containing:
            - response: Text response from the agent
            - canvas_mode: CanvasMode enum for UI
            - canvas_data: Data for canvas rendering
            - canvas_title: Title for the canvas
            - last_tool: Name of last tool called
            - trace: Reasoning trace for transparency
    """
    start_time = time.time()

    # Check for golden path match first
    golden_match = match_golden_path_query(user_message)
    if golden_match:
        golden_data = load_golden_path(golden_match)
        if golden_data:
            return _format_golden_response(golden_data, golden_match, user_message, start_time)

    # Regular agent invocation
    try:
        agent = get_agent()

        # Create messages with system prompt
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        # Invoke agent
        result = agent.invoke({"messages": messages})

        # Process result
        return _process_agent_result(result, start_time)

    except Exception as e:
        return {
            "response": f"I encountered an error while processing your request: {str(e)}",
            "canvas_mode": CanvasMode.EMPTY,
            "canvas_data": None,
            "canvas_title": None,
            "last_tool": None,
            "trace": None,
            "error": str(e),
        }


def _process_agent_result(result: dict, start_time: float) -> dict:
    """Process the raw agent result into a formatted response.

    Args:
        result: Raw result from agent.invoke()
        start_time: Timestamp when invocation started

    Returns:
        Formatted response dictionary
    """
    messages = result.get("messages", [])

    # Extract the final AI response
    response_text = ""
    last_tool = None
    canvas_mode = CanvasMode.EMPTY
    canvas_data = None
    canvas_title = None
    tool_results = []

    for msg in messages:
        if isinstance(msg, AIMessage):
            if msg.content:
                response_text = msg.content

            # Check for tool calls
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    last_tool = tc.get("name")

        # Look for tool results in messages
        if hasattr(msg, "name") and hasattr(msg, "content"):
            # This is a tool message
            tool_results.append({
                "tool": msg.name,
                "result": msg.content,
            })

    # Determine canvas state from tool results
    # Priority: GRAPH > CHART > CLAIM > DOC > EMPTY
    # This ensures fraud graphs take priority over incidental clinical note searches
    canvas_priority = {
        CanvasMode.GRAPH: 4,
        CanvasMode.CHART: 3,
        CanvasMode.CLAIM: 2,
        CanvasMode.DOC: 1,
        CanvasMode.EMPTY: 0,
    }
    current_priority = 0
    
    for tr in tool_results:
        try:
            import json
            tool_data = json.loads(tr["result"]) if isinstance(tr["result"], str) else tr["result"]

            ui_hint = tool_data.get("ui_hint", "")
            
            # Skip empty results
            if ui_hint == "MODE_EMPTY":
                continue

            if ui_hint == "MODE_CLAIM":
                new_priority = canvas_priority.get(CanvasMode.CLAIM, 0)
                if new_priority > current_priority:
                    claims = tool_data.get("claims", [])
                    if claims:
                        canvas_mode = CanvasMode.CLAIM
                        canvas_data = claims[0]
                        claim_id = canvas_data.get("claim_id", "Unknown")
                        canvas_title = f"Claim Details: {claim_id}"
                        current_priority = new_priority

            elif ui_hint == "MODE_DOC":
                new_priority = canvas_priority.get(CanvasMode.DOC, 0)
                if new_priority > current_priority:
                    results = tool_data.get("results", [])
                    if results:
                        canvas_mode = CanvasMode.DOC
                        canvas_data = results[0]
                        note_id = canvas_data.get("note_id", "Unknown")
                        canvas_title = f"Clinical Note: {note_id}"
                        current_priority = new_priority

            elif ui_hint == "MODE_GRAPH":
                new_priority = canvas_priority.get(CanvasMode.GRAPH, 0)
                if new_priority > current_priority:
                    # Only use graph if it has actual data
                    nodes = tool_data.get("nodes", [])
                    if nodes:
                        canvas_mode = CanvasMode.GRAPH
                        canvas_data = tool_data
                        entity = tool_data.get("analyzed_entity", "Network")
                        canvas_title = f"Network Analysis: {entity}"
                        current_priority = new_priority

            elif ui_hint == "MODE_CHART":
                new_priority = canvas_priority.get(CanvasMode.CHART, 0)
                if new_priority > current_priority:
                    canvas_mode = CanvasMode.CHART
                    canvas_data = tool_data
                    metric = tool_data.get("metric", "analysis")
                    group_by = tool_data.get("group_by", "")
                    canvas_title = f"{metric.replace('_', ' ').title()} by {group_by.replace('_', ' ').title()}"
                    current_priority = new_priority

        except (json.JSONDecodeError, TypeError, AttributeError):
            continue

    # Build reasoning trace
    duration_ms = int((time.time() - start_time) * 1000)
    trace = _build_reasoning_trace(messages, duration_ms, last_tool)

    return {
        "response": response_text or "I couldn't generate a response.",
        "canvas_mode": canvas_mode,
        "canvas_data": canvas_data,
        "canvas_title": canvas_title,
        "last_tool": last_tool,
        "trace": trace,
    }


def _format_golden_response(
    golden_data: dict,
    scenario: str,
    query: str,
    start_time: float,
) -> dict:
    """Format a golden path response for guaranteed demo success.

    Args:
        golden_data: Pre-computed golden path data
        scenario: Scenario name
        query: Original user query
        start_time: Timestamp when invocation started

    Returns:
        Formatted response dictionary
    """
    duration_ms = int((time.time() - start_time) * 1000)

    # Determine canvas mode based on scenario
    if scenario == "silo_breaker":
        canvas_mode = CanvasMode.DOC
        canvas_data = golden_data.get("clinical_note", {})
        # Use content from JSON, or fall back to embedded content
        if not canvas_data.get("content") and not canvas_data.get("full_content"):
            canvas_data["full_content"] = _get_golden_note_content()
        note_id = canvas_data.get("note_id", "CN-001")
        canvas_title = f"Clinical Note: {note_id}"
        last_tool = "search_clinical_notes"

    elif scenario == "fraud_hunter":
        canvas_mode = CanvasMode.GRAPH
        canvas_data = {
            "nodes": golden_data.get("nodes", []),
            "edges": golden_data.get("edges", []),
            "findings": golden_data.get("findings", []),
            "center_entity": "PRV-007",
        }
        canvas_title = "Network Analysis: Dr. X (PRV-007)"
        last_tool = "analyze_network_graph"

    elif scenario == "trend_analyst":
        canvas_mode = CanvasMode.CHART
        canvas_data = {
            "data": golden_data.get("data", []),
            "insights": golden_data.get("insights", []),
            "chart_config": {
                "chart_type": "bar",
                "x": [d["specialty"] for d in golden_data.get("data", [])],
                "y": [d["denial_rate"] for d in golden_data.get("data", [])],
                "benchmarks": [d.get("benchmark") for d in golden_data.get("data", [])],
                "x_title": "Specialty",
                "y_title": "Denial Rate",
                "y_format": ".0%",
                "title": "Denial Rate by Specialty",
                "color": "#6366f1",
                "benchmark_color": "#ef4444",
            },
            "metric": "denial_rate",
            "group_by": "specialty",
        }
        canvas_title = "Denial Rate by Specialty"
        last_tool = "analyze_trends"

    else:
        canvas_mode = CanvasMode.EMPTY
        canvas_data = None
        canvas_title = None
        last_tool = None

    # Build trace
    trace = {
        "query": query,
        "steps": [
            {
                "step_number": 1,
                "timestamp": datetime.now().isoformat(),
                "action_type": "think",
                "content": f"Matched golden path scenario: {scenario}",
                "duration_ms": 10,
            },
            {
                "step_number": 2,
                "timestamp": datetime.now().isoformat(),
                "action_type": "respond",
                "content": "Returning cached response",
                "duration_ms": duration_ms - 10,
            },
        ],
        "total_duration_ms": duration_ms,
        "tools_called": [last_tool] if last_tool else [],
        "final_canvas_mode": canvas_mode.value,
        "used_cache": True,
    }

    return {
        "response": golden_data.get("response", ""),
        "canvas_mode": canvas_mode,
        "canvas_data": canvas_data,
        "canvas_title": canvas_title,
        "last_tool": last_tool,
        "trace": trace,
    }


def _get_golden_note_content() -> str:
    """Get the full content of the golden nugget clinical note."""
    return """# Emergency Department Note

**Patient:** John Smith (P-0456)
**Date:** June 15, 2024, 14:30
**Chief Complaint:** Severe chest pain

## Presenting Symptoms
Patient presented to the Emergency Department via ambulance with severe crushing chest pain radiating to the left arm and jaw. Pain started approximately 2 hours prior to arrival. Patient reports associated diaphoresis, shortness of breath, and nausea.

## Vital Signs on Arrival
- BP: 165/95 mmHg
- HR: 110 bpm, irregular
- RR: 24/min
- SpO2: 92% on room air
- Temp: 98.6°F

## Initial Assessment
**This is a life-threatening cardiac emergency.** ECG shows ST-elevation in leads V1-V4, consistent with anterior STEMI. Troponin I elevated at 2.5 ng/mL (normal <0.04).

## Clinical Impression
**Acute ST-Elevation Myocardial Infarction (STEMI)** - This is a medical emergency requiring immediate intervention.

## Plan
1. **IMMEDIATE cardiac catheterization** - Door-to-balloon time critical
2. Aspirin 325mg given
3. Heparin bolus administered
4. Cardiology consulted - Dr. X responding

**This patient requires emergent cardiac catheterization. Any delay in treatment could result in permanent cardiac damage or death. This intervention is medically necessary and time-critical.**

---
*Documented by: ED Attending*"""


def _build_reasoning_trace(messages: list, duration_ms: int, last_tool: Optional[str]) -> dict:
    """Build a reasoning trace from agent messages.

    Args:
        messages: List of messages from agent
        duration_ms: Total duration in milliseconds
        last_tool: Name of last tool called

    Returns:
        Reasoning trace dictionary
    """
    steps = []
    tools_called = []
    step_number = 0

    for msg in messages:
        step_number += 1

        if isinstance(msg, HumanMessage):
            steps.append({
                "step_number": step_number,
                "timestamp": datetime.now().isoformat(),
                "action_type": "observe",
                "content": "Received user query",
                "duration_ms": 0,
            })

        elif isinstance(msg, AIMessage):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_name = tc.get("name", "unknown")
                    tools_called.append(tool_name)
                    steps.append({
                        "step_number": step_number,
                        "timestamp": datetime.now().isoformat(),
                        "action_type": "tool_call",
                        "content": f"Calling {tool_name}",
                        "tool_name": tool_name,
                        "tool_input": tc.get("args", {}),
                        "duration_ms": 100,  # Estimate
                    })
                    step_number += 1

            if msg.content:
                steps.append({
                    "step_number": step_number,
                    "timestamp": datetime.now().isoformat(),
                    "action_type": "respond",
                    "content": "Generated response",
                    "duration_ms": 50,
                })

    return {
        "query": "",  # Will be filled by caller
        "steps": steps,
        "total_duration_ms": duration_ms,
        "tools_called": list(set(tools_called)),
        "final_canvas_mode": None,  # Will be set by caller
        "used_cache": False,
    }
