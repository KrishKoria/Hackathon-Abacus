"""Document viewer component for clinical notes.

Renders clinical documentation with appropriate styling,
highlighting key medical information.
"""

import streamlit as st
from typing import Any


def render_doc(data: Any) -> None:
    """Render a clinical note document.

    Args:
        data: Clinical note data dictionary containing:
            - note_id: Note identifier
            - patient_id or patient_name: Patient identifier/name
            - claim_id: Associated claim ID
            - note_type: Type of clinical note
            - provider_id or provider_name: Provider who authored the note
            - date: Date of the note
            - summary: Brief summary
            - content or full_content: Note content
            - is_golden_nugget: Whether this is key evidence
            - similarity_score: RAG similarity score
    """
    if not data:
        st.warning("No document data available")
        return

    # Handle both dict and object access patterns
    if isinstance(data, dict):
        note_id = data.get("note_id", "Unknown")
        # Support both patient_id and patient_name
        patient_id = data.get("patient_id") or data.get("patient_name", "Unknown")
        claim_id = data.get("claim_id", "Unknown")
        note_type = data.get("note_type", "Unknown")
        # Support both provider_id and provider_name
        provider_id = data.get("provider_id") or data.get("provider_name", "Unknown")
        date = data.get("date", "Unknown")
        summary = data.get("summary", "")
        content = data.get("full_content") or data.get("content", "")
        is_golden = data.get("is_golden_nugget", False)
        similarity = data.get("similarity_score", 0.0)
    else:
        note_id = getattr(data, "note_id", "Unknown")
        patient_id = getattr(data, "patient_id", None) or getattr(data, "patient_name", "Unknown")
        claim_id = getattr(data, "claim_id", "Unknown")
        note_type = getattr(data, "note_type", "Unknown")
        provider_id = getattr(data, "provider_id", None) or getattr(data, "provider_name", "Unknown")
        date = getattr(data, "date", "Unknown")
        summary = getattr(data, "summary", "")
        content = getattr(data, "full_content", None) or getattr(data, "content", "")
        is_golden = getattr(data, "is_golden_nugget", False)
        similarity = getattr(data, "similarity_score", 0.0)

    # Golden nugget indicator
    if is_golden:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border: 2px solid #f59e0b;
                border-radius: 8px;
                padding: 0.75rem 1rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span style="font-size: 1.25rem;">⭐</span>
                <span style="color: #92400e; font-weight: 600;">
                    Key Evidence Found - High Relevance Match
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Document metadata card
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div>
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                        Note ID
                    </div>
                    <div style="color: #f8fafc; font-weight: 600;">{note_id}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                        Patient
                    </div>
                    <div style="color: #f8fafc; font-weight: 600;">{patient_id}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                        Claim
                    </div>
                    <div style="color: #f8fafc; font-weight: 600;">{claim_id}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                        Note Type
                    </div>
                    <div style="color: #f8fafc; font-weight: 600;">{note_type}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                        Provider
                    </div>
                    <div style="color: #f8fafc; font-weight: 600;">{provider_id}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                        Date
                    </div>
                    <div style="color: #f8fafc; font-weight: 600;">{date}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Similarity score indicator
    if similarity > 0:
        score_color = "#22c55e" if similarity > 0.8 else "#eab308" if similarity > 0.5 else "#ef4444"
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 1rem;
            ">
                <span style="color: #64748b; font-size: 0.875rem;">Relevance:</span>
                <div style="
                    flex: 1;
                    height: 8px;
                    background: #1e293b;
                    border-radius: 4px;
                    overflow: hidden;
                ">
                    <div style="
                        width: {similarity * 100}%;
                        height: 100%;
                        background: {score_color};
                        border-radius: 4px;
                    "></div>
                </div>
                <span style="color: {score_color}; font-weight: 600;">
                    {similarity:.0%}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Summary section (if available)
    if summary:
        st.markdown("#### Summary")
        st.info(summary)

    # Document content
    st.markdown("#### Clinical Note Content")

    # Render content with markdown support
    if content:
        # Convert markdown to HTML and render with styling in a single call
        # This is necessary because Streamlit doesn't maintain HTML state across calls
        import markdown
        
        # Convert markdown content to HTML
        html_content = markdown.markdown(
            content,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Render the full HTML with styling in a single call
        st.markdown(
            f"""<div style="background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; color: #e2e8f0;">{html_content}</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.warning("No content available for this clinical note.")

    # Action buttons
    st.markdown("---")
    
    # Prepare content for export
    export_content = f"""Clinical Note: {note_id}
Patient: {patient_id}
Claim: {claim_id}
Type: {note_type}
Provider: {provider_id}
Date: {date}

{summary if summary else ''}

{content if content else 'No content available'}
"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as text file
        st.download_button(
            label="📋 Copy/Download Note",
            data=export_content,
            file_name=f"clinical_note_{note_id}.txt",
            mime="text/plain",
            key=f"download_doc_{note_id}",
            use_container_width=True,
            help="Download the clinical note as a text file"
        )
    
    with col2:
        # Download as markdown file
        md_content = f"""# Clinical Note: {note_id}

## Metadata
- **Patient:** {patient_id}
- **Claim:** {claim_id}
- **Type:** {note_type}
- **Provider:** {provider_id}
- **Date:** {date}

## Summary
{summary if summary else 'N/A'}

## Content
{content if content else 'No content available'}
"""
        st.download_button(
            label="📄 Export as Markdown",
            data=md_content,
            file_name=f"clinical_note_{note_id}.md",
            mime="text/markdown",
            key=f"export_md_{note_id}",
            use_container_width=True,
            help="Export the clinical note in Markdown format"
        )
