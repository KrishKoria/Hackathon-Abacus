"""Claim card component for displaying claim details.

Renders a comprehensive claim detail view with status indicators,
amounts, and diagnostic information.
"""

import streamlit as st
from typing import Any, Optional


def _get_field(data: Any, *field_names, default=None):
    """Get a field value trying multiple possible field names.
    
    Args:
        data: Data dictionary or object
        field_names: Field names to try in order
        default: Default value if none found
        
    Returns:
        Field value or default
    """
    for name in field_names:
        if isinstance(data, dict):
            value = data.get(name)
        else:
            value = getattr(data, name, None)
        
        if value is not None:
            # Handle NaN values from pandas
            if isinstance(value, float) and str(value) == 'nan':
                continue
            return value
    return default


def render_claim(data: Any, on_action: Optional[callable] = None) -> None:
    """Render a claim detail card.

    Args:
        data: Claim data dictionary from CSV with fields:
            - claim_id: Claim identifier
            - patient_id: Patient identifier  
            - patient_name: Patient name
            - patient_age: Patient age
            - patient_gender: Patient gender
            - provider_id: Provider identifier
            - provider_name: Provider name
            - provider_specialty: Provider specialty
            - claim_amount: Amount billed
            - approved_amount: Amount allowed/approved
            - claim_status: Claim status (Approved, Denied, Pending)
            - denial_reason: Reason for denial (if applicable)
            - claim_date: Date of service
            - processing_date: Date processed
            - diagnosis_code: ICD-10 code
            - diagnosis_description: Description of diagnosis
            - procedure_code: CPT code
            - procedure_description: Description of procedure
            - is_emergency: Emergency flag
            - is_inpatient: Inpatient flag
        on_action: Optional callback for button actions
    """
    if not data:
        st.warning("No claim data available")
        return

    # Extract fields with fallbacks for different naming conventions
    claim_id = _get_field(data, "claim_id", default="Unknown")
    patient_id = _get_field(data, "patient_id", default="Unknown")
    patient_name = _get_field(data, "patient_name", default="Unknown")
    patient_age = _get_field(data, "patient_age", default=None)
    patient_gender = _get_field(data, "patient_gender", default=None)
    provider_id = _get_field(data, "provider_id", default="Unknown")
    provider_name = _get_field(data, "provider_name", default="Unknown")
    provider_specialty = _get_field(data, "provider_specialty", default="Unknown")
    
    # Financial fields - try both naming conventions
    billed_amount = _get_field(data, "claim_amount", "billed_amount", default=0)
    allowed_amount = _get_field(data, "approved_amount", "allowed_amount", default=0)
    paid_amount = _get_field(data, "paid_amount", default=allowed_amount)  # Use approved as paid if not specified
    
    # Status fields
    status = _get_field(data, "claim_status", "status", default="Unknown")
    denial_reason = _get_field(data, "denial_reason", default=None)
    
    # Date fields
    service_date = _get_field(data, "claim_date", "service_date", default="Unknown")
    processing_date = _get_field(data, "processing_date", "submission_date", default="Unknown")
    
    # Diagnosis and procedure - handle single values or lists
    diagnosis_code = _get_field(data, "diagnosis_code", default=None)
    diagnosis_desc = _get_field(data, "diagnosis_description", default=None)
    procedure_code = _get_field(data, "procedure_code", default=None)
    procedure_desc = _get_field(data, "procedure_description", default=None)
    
    # Convert single codes to display format
    diagnosis_codes = _get_field(data, "diagnosis_codes", default=[])
    if not diagnosis_codes and diagnosis_code:
        diagnosis_codes = [f"{diagnosis_code} - {diagnosis_desc}" if diagnosis_desc else diagnosis_code]
    
    procedure_codes = _get_field(data, "procedure_codes", default=[])
    if not procedure_codes and procedure_code:
        procedure_codes = [f"{procedure_code} - {procedure_desc}" if procedure_desc else procedure_code]
    
    # Additional info
    is_emergency = _get_field(data, "is_emergency", default=False)
    is_inpatient = _get_field(data, "is_inpatient", default=False)
    
    # Ensure numeric values
    try:
        billed_amount = float(billed_amount) if billed_amount else 0
    except (ValueError, TypeError):
        billed_amount = 0
    try:
        allowed_amount = float(allowed_amount) if allowed_amount else 0
    except (ValueError, TypeError):
        allowed_amount = 0
    try:
        paid_amount = float(paid_amount) if paid_amount else 0
    except (ValueError, TypeError):
        paid_amount = 0

    # Status color mapping - handle different case formats
    status_upper = status.upper() if isinstance(status, str) else "UNKNOWN"
    status_colors = {
        "PAID": ("#22c55e", "#166534"),
        "APPROVED": ("#22c55e", "#166534"),
        "DENIED": ("#ef4444", "#991b1b"),
        "PENDING": ("#eab308", "#854d0e"),
        "PARTIALLY_PAID": ("#3b82f6", "#1e40af"),
    }
    status_bg, status_border = status_colors.get(status_upper, ("#64748b", "#475569"))

    # Build denial reason HTML separately
    denial_html = ""
    if denial_reason:
        denial_html = f'<div style="color: {status_bg}; font-size: 0.875rem; margin-top: 0.25rem;">Reason: {denial_reason}</div>'

    # Status banner
    st.markdown(
        f"""
        <div style="
            background: {status_bg}20;
            border: 2px solid {status_bg};
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <div style="color: {status_bg}; font-size: 1.5rem; font-weight: 700;">
                {status}
            </div>
            {denial_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Claim ID header
    st.markdown(
        f"""
        <div style="
            color: #f8fafc;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        ">
            {claim_id}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Financial summary
    st.markdown("#### 💰 Financial Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Billed Amount", f"${billed_amount:,.2f}")
    with col2:
        st.metric("Allowed Amount", f"${allowed_amount:,.2f}")
    with col3:
        st.metric("Paid Amount", f"${paid_amount:,.2f}")

    st.divider()

    # Patient and Provider info
    col_patient, col_provider = st.columns(2)

    with col_patient:
        st.markdown("#### 👤 Patient Information")
        # Build patient details
        patient_details = f"""
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #64748b;">Name:</span>
                <span style="color: #f8fafc; font-weight: 500;"> {patient_name}</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #64748b;">ID:</span>
                <span style="color: #f8fafc; font-weight: 500;"> {patient_id}</span>
            </div>
        """
        if patient_age:
            patient_details += f"""
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #64748b;">Age:</span>
                <span style="color: #f8fafc; font-weight: 500;"> {patient_age}</span>
            </div>
            """
        if patient_gender:
            patient_details += f"""
            <div>
                <span style="color: #64748b;">Gender:</span>
                <span style="color: #f8fafc; font-weight: 500;"> {patient_gender}</span>
            </div>
            """
        st.markdown(
            f"""
            <div style="
                background: #1e293b;
                border-radius: 8px;
                padding: 1rem;
            ">
                {patient_details}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_provider:
        st.markdown("#### 🏥 Provider Information")
        st.markdown(
            f"""
            <div style="
                background: #1e293b;
                border-radius: 8px;
                padding: 1rem;
            ">
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #64748b;">Name:</span>
                    <span style="color: #f8fafc; font-weight: 500;"> {provider_name}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #64748b;">ID:</span>
                    <span style="color: #f8fafc; font-weight: 500;"> {provider_id}</span>
                </div>
                <div>
                    <span style="color: #64748b;">Specialty:</span>
                    <span style="color: #f8fafc; font-weight: 500;"> {provider_specialty}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Dates and Service Type
    st.markdown("#### 📅 Important Dates")
    col_service, col_submit = st.columns(2)
    with col_service:
        st.markdown(f"**Service Date:** {service_date}")
    with col_submit:
        st.markdown(f"**Processing Date:** {processing_date}")
    
    # Service type indicators
    service_type_parts = []
    if is_inpatient:
        service_type_parts.append("🏥 Inpatient")
    else:
        service_type_parts.append("🏃 Outpatient")
    if is_emergency:
        service_type_parts.append("🚨 Emergency")
    
    if service_type_parts:
        st.markdown(f"**Service Type:** {' | '.join(service_type_parts)}")

    st.divider()

    # Codes
    st.markdown("#### 🏷️ Diagnosis & Procedure Codes")
    col_diag, col_proc = st.columns(2)

    with col_diag:
        st.markdown("**Diagnosis Codes (ICD-10)**")
        if diagnosis_codes:
            for code in diagnosis_codes:
                st.markdown(f"- `{code}`")
        else:
            st.markdown("*No diagnosis codes*")

    with col_proc:
        st.markdown("**Procedure Codes (CPT)**")
        if procedure_codes:
            for code in procedure_codes:
                st.markdown(f"- `{code}`")
        else:
            st.markdown("*No procedure codes*")

    # Action buttons with functionality
    st.markdown("---")
    st.markdown("#### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Find Related Notes", key=f"find_notes_{claim_id}", use_container_width=True):
            # Store the action in session state for the chat panel to pick up
            st.session_state.pending_action = {
                "type": "find_notes",
                "query": f"Search for clinical notes related to patient {patient_id} and claim {claim_id}",
                "patient_id": patient_id,
                "claim_id": claim_id,
            }
            st.rerun()
    
    with col2:
        if st.button("📊 Provider History", key=f"provider_hist_{claim_id}", use_container_width=True):
            st.session_state.pending_action = {
                "type": "provider_history",
                "query": f"Show me the claims history for provider {provider_name} ({provider_id})",
                "provider_id": provider_id,
                "provider_name": provider_name,
            }
            st.rerun()
    
    with col3:
        # Only show appeal button for denied claims
        if status_upper == "DENIED":
            if st.button("📋 Appeal Template", key=f"appeal_{claim_id}", use_container_width=True):
                st.session_state.pending_action = {
                    "type": "appeal_template",
                    "query": f"Generate an appeal template for denied claim {claim_id} with denial reason: {denial_reason}",
                    "claim_id": claim_id,
                    "denial_reason": denial_reason,
                }
                st.rerun()
        else:
            st.button("📋 Appeal Template", key=f"appeal_{claim_id}", use_container_width=True, disabled=True, help="Only available for denied claims")