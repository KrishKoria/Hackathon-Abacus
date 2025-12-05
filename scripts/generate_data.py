"""Data generation script for ClaimsIQ Nexus.

Generates synthetic healthcare data for the demo including:
- ~2,500 claims with 20+ fields and realistic patterns
- 100 clinical notes (Markdown files) with strong linkages
- 3 fraud rings with distinct patterns
- 10 Golden Nuggets (denial contradictions)
- Temporal patterns (seasonal trends, denial spikes)
- Provider behavior anomalies
- Patient cohorts with chronic conditions
"""

import csv
import json
import os
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from collections import defaultdict

from faker import Faker
from faker.providers import BaseProvider

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)

# Path setup
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"
CLINICAL_NOTES_DIR = GENERATED_DIR / "clinical_notes"
GOLDEN_PATH_DIR = DATA_DIR / "golden_path"


class HealthcareProvider(BaseProvider):
    """Custom Faker provider for healthcare data."""

    # Diagnosis codes grouped by specialty/condition type
    DIAGNOSIS_BY_SPECIALTY = {
        "Cardiology": [
            ("I21.0", "ST elevation myocardial infarction"),
            ("I21.4", "Non-ST elevation myocardial infarction"),
            ("I25.10", "Atherosclerotic heart disease"),
            ("I48.0", "Paroxysmal atrial fibrillation"),
            ("I50.9", "Heart failure, unspecified"),
            ("I10", "Essential hypertension"),
        ],
        "Oncology": [
            ("C34.90", "Malignant neoplasm of lung"),
            ("C50.919", "Malignant neoplasm of breast"),
            ("C61", "Malignant neoplasm of prostate"),
            ("C18.9", "Malignant neoplasm of colon"),
            ("C73", "Malignant neoplasm of thyroid"),
        ],
        "Orthopedics": [
            ("M54.5", "Low back pain"),
            ("M17.11", "Primary osteoarthritis, right knee"),
            ("S72.001A", "Fracture of femoral neck"),
            ("M75.101", "Rotator cuff tear"),
            ("M25.561", "Pain in right knee"),
        ],
        "Neurology": [
            ("G43.909", "Migraine, unspecified"),
            ("G20", "Parkinson's disease"),
            ("G35", "Multiple sclerosis"),
            ("G40.909", "Epilepsy, unspecified"),
            ("I63.9", "Cerebral infarction, unspecified"),
        ],
        "Emergency Medicine": [
            ("K35.80", "Acute appendicitis"),
            ("S06.0X0A", "Concussion"),
            ("T78.2XXA", "Anaphylactic shock"),
            ("I26.99", "Pulmonary embolism"),
            ("R55", "Syncope and collapse"),
        ],
        "Primary Care": [
            ("E11.9", "Type 2 diabetes mellitus"),
            ("J06.9", "Acute upper respiratory infection"),
            ("E78.5", "Hyperlipidemia"),
            ("F32.9", "Major depressive disorder"),
            ("J45.909", "Asthma, unspecified"),
        ],
        "Dermatology": [
            ("L30.9", "Dermatitis, unspecified"),
            ("L40.0", "Psoriasis vulgaris"),
            ("C43.9", "Malignant melanoma of skin"),
            ("L70.0", "Acne vulgaris"),
            ("B35.1", "Tinea unguium"),
        ],
        "Gastroenterology": [
            ("K21.0", "Gastroesophageal reflux disease"),
            ("K50.90", "Crohn's disease"),
            ("K51.90", "Ulcerative colitis"),
            ("K80.20", "Gallstones"),
            ("K57.30", "Diverticulosis"),
        ],
    }

    # Procedure codes grouped by specialty
    PROCEDURE_BY_SPECIALTY = {
        "Cardiology": [
            ("93458", "Cardiac catheterization"),
            ("93306", "Echocardiography"),
            ("93000", "Electrocardiogram"),
            ("33533", "Coronary artery bypass"),
            ("92928", "Coronary stent placement"),
        ],
        "Oncology": [
            ("38221", "Bone marrow biopsy"),
            ("96413", "Chemotherapy infusion"),
            ("77386", "Radiation therapy"),
            ("19301", "Mastectomy"),
            ("38720", "Lymph node dissection"),
        ],
        "Orthopedics": [
            ("27447", "Total knee replacement"),
            ("27130", "Total hip replacement"),
            ("29881", "Knee arthroscopy"),
            ("23472", "Shoulder replacement"),
            ("22630", "Lumbar fusion"),
        ],
        "Neurology": [
            ("95816", "Electroencephalogram"),
            ("70553", "Brain MRI with contrast"),
            ("64721", "Carpal tunnel release"),
            ("61510", "Craniectomy"),
            ("95860", "EMG testing"),
        ],
        "Emergency Medicine": [
            ("44970", "Laparoscopic appendectomy"),
            ("99285", "Emergency department visit"),
            ("12001", "Simple laceration repair"),
            ("31500", "Emergency intubation"),
            ("99291", "Critical care first hour"),
        ],
        "Primary Care": [
            ("99214", "Office visit, moderate complexity"),
            ("99213", "Office visit, low complexity"),
            ("36415", "Venipuncture"),
            ("85025", "Complete blood count"),
            ("80053", "Comprehensive metabolic panel"),
        ],
        "Dermatology": [
            ("11102", "Tangential skin biopsy"),
            ("17000", "Destruction of lesion"),
            ("96910", "Phototherapy"),
            ("11600", "Excision of malignant lesion"),
            ("17110", "Destruction of warts"),
        ],
        "Gastroenterology": [
            ("43239", "Upper GI endoscopy with biopsy"),
            ("45380", "Colonoscopy with biopsy"),
            ("47562", "Laparoscopic cholecystectomy"),
            ("43760", "Gastric tube replacement"),
            ("91110", "GI tract imaging"),
        ],
    }

    def diagnosis_code(self, specialty: str = None):
        """Generate ICD-10 diagnosis code, optionally by specialty."""
        if specialty and specialty in self.DIAGNOSIS_BY_SPECIALTY:
            code, desc = random.choice(self.DIAGNOSIS_BY_SPECIALTY[specialty])
            return (code, desc)
        # Random from any specialty
        all_codes = []
        for codes in self.DIAGNOSIS_BY_SPECIALTY.values():
            all_codes.extend(codes)
        return random.choice(all_codes)

    def procedure_code(self, specialty: str = None):
        """Generate CPT procedure code, optionally by specialty."""
        if specialty and specialty in self.PROCEDURE_BY_SPECIALTY:
            code, desc = random.choice(self.PROCEDURE_BY_SPECIALTY[specialty])
            return (code, desc)
        # Random from any specialty
        all_codes = []
        for codes in self.PROCEDURE_BY_SPECIALTY.values():
            all_codes.extend(codes)
        return random.choice(all_codes)


# Add custom provider
fake.add_provider(HealthcareProvider)

# Constants
SPECIALTIES = [
    "Cardiology",
    "Oncology",
    "Orthopedics",
    "Neurology",
    "Emergency Medicine",
    "Primary Care",
    "Dermatology",
    "Gastroenterology",
]

DENIAL_REASONS = [
    "Pre-auth not obtained",
    "Out of network",
    "Not medically necessary",
    "Duplicate claim",
    "Incomplete information",
    "Experimental procedure",
    "Benefit limit exceeded",
    "Service not covered",
]

GENDERS = ["Male", "Female", "Other"]

# Chronic condition patient cohorts (realistic patient groupings)
CHRONIC_CONDITIONS = {
    "diabetes_cohort": {
        "conditions": ["E11.9", "E11.65", "E11.22"],
        "typical_age_range": (45, 80),
        "comorbidities": ["I10", "E78.5", "N18.9"],
    },
    "cardiac_cohort": {
        "conditions": ["I25.10", "I48.0", "I50.9"],
        "typical_age_range": (55, 85),
        "comorbidities": ["I10", "E11.9", "E78.5"],
    },
    "cancer_cohort": {
        "conditions": ["C34.90", "C50.919", "C61", "C18.9"],
        "typical_age_range": (40, 75),
        "comorbidities": ["F32.9", "G47.00"],
    },
    "chronic_pain_cohort": {
        "conditions": ["M54.5", "M17.11", "G89.29"],
        "typical_age_range": (35, 70),
        "comorbidities": ["F32.9", "G47.00"],
    },
}

# Fraud ring configurations (3 distinct fraud patterns)
FRAUD_RINGS = {
    "ring_1": {
        "name": "Cardiology Kickback Ring",
        "providers": ["PRV-007", "PRV-012"],
        "provider_names": ["Dr. X", "Dr. Y"],
        "specialty": "Cardiology",
        "patients": ["P-0101", "P-0102", "P-0103", "P-0104", "P-0105", "P-0106"],
        "pattern": "circular_referral",
        "description": "Bidirectional referrals with high-cost cardiac procedures",
    },
    "ring_2": {
        "name": "Upcoding Scheme",
        "providers": ["PRV-023", "PRV-024", "PRV-025"],
        "provider_names": ["Dr. Alpha", "Dr. Beta", "Dr. Gamma"],
        "specialty": "Orthopedics",
        "patients": ["P-0150", "P-0151", "P-0152", "P-0153", "P-0154"],
        "pattern": "upcoding",
        "description": "Systematic billing of complex procedures for routine visits",
    },
    "ring_3": {
        "name": "Phantom Billing Network",
        "providers": ["PRV-035", "PRV-036"],
        "provider_names": ["Dr. Shadow", "Dr. Ghost"],
        "specialty": "Primary Care",
        "patients": ["P-0180", "P-0181", "P-0182", "P-0183"],
        "pattern": "phantom_billing",
        "description": "Billing for services never rendered to patients",
    },
}

# Temporal patterns (seasonal and monthly trends)
TEMPORAL_PATTERNS = {
    "seasonal_denial_spikes": {
        "January": 1.15,  # Post-holiday backlog
        "February": 1.05,
        "March": 1.00,
        "April": 0.95,
        "May": 0.90,
        "June": 0.95,
        "July": 1.00,
        "August": 0.95,
        "September": 1.00,
        "October": 1.05,
        "November": 1.10,
        "December": 1.20,  # Year-end rush
    },
    "specialty_seasonal": {
        "Dermatology": {"summer": 1.3, "winter": 0.8},
        "Orthopedics": {"winter": 1.2, "summer": 1.0},  # Sports injuries
        "Primary Care": {"winter": 1.3, "summer": 0.9},  # Flu season
    },
}


def generate_providers(count: int = 75) -> list[dict]:
    """Generate provider data with fraud ring members and behavior profiles."""
    providers = []
    
    # Track all fraud ring provider IDs
    fraud_provider_ids = set()
    for ring in FRAUD_RINGS.values():
        fraud_provider_ids.update(ring["providers"])
    
    for i in range(1, count + 1):
        provider_id = f"PRV-{i:03d}"
        specialty = random.choice(SPECIALTIES)
        
        # Check if this is a fraud ring member
        is_fraud = provider_id in fraud_provider_ids
        fraud_ring = None
        provider_name = f"Dr. {fake.last_name()}"
        
        if is_fraud:
            for ring_id, ring_data in FRAUD_RINGS.items():
                if provider_id in ring_data["providers"]:
                    fraud_ring = ring_id
                    specialty = ring_data["specialty"]
                    idx = ring_data["providers"].index(provider_id)
                    provider_name = ring_data["provider_names"][idx]
                    break
        
        # Generate provider behavior profile
        behavior_profile = _generate_provider_behavior(provider_id, is_fraud)
        
        provider = {
            "provider_id": provider_id,
            "name": provider_name,
            "specialty": specialty,
            "is_fraud_ring_member": is_fraud,
            "fraud_ring": fraud_ring,
            "npi": fake.numerify(text="##########"),
            "practice_location": fake.city() + ", " + fake.state_abbr(),
            "years_in_practice": random.randint(2, 35),
            **behavior_profile,
        }
        providers.append(provider)

    return providers


def _generate_provider_behavior(provider_id: str, is_fraud: bool) -> dict:
    """Generate behavioral characteristics for providers."""
    if is_fraud:
        # Fraud providers have anomalous patterns
        return {
            "avg_claims_per_month": random.randint(80, 150),  # High volume
            "avg_claim_amount": round(random.uniform(2000, 8000), 2),  # High amounts
            "referral_rate": round(random.uniform(0.4, 0.7), 2),  # High referrals
            "documentation_score": round(random.uniform(0.5, 0.7), 2),  # Lower doc quality
        }
    else:
        # Normal providers
        return {
            "avg_claims_per_month": random.randint(20, 60),
            "avg_claim_amount": round(random.uniform(300, 1500), 2),
            "referral_rate": round(random.uniform(0.1, 0.3), 2),
            "documentation_score": round(random.uniform(0.75, 0.95), 2),
        }


def generate_patients(count: int = 400) -> list[dict]:
    """Generate patient data with chronic condition cohorts and fraud ring membership."""
    patients = []
    
    # Track all fraud ring patient IDs
    fraud_patient_ids = set()
    for ring in FRAUD_RINGS.values():
        fraud_patient_ids.update(ring["patients"])
    
    # Assign patients to chronic condition cohorts (30% of patients)
    cohort_assignments = {}
    cohort_names = list(CHRONIC_CONDITIONS.keys())
    for i in range(1, int(count * 0.3) + 1):
        cohort = random.choice(cohort_names)
        cohort_assignments[f"P-{i:04d}"] = cohort
    
    for i in range(1, count + 1):
        patient_id = f"P-{i:04d}"
        
        # Check cohort membership for age and condition patterns
        cohort = cohort_assignments.get(patient_id)
        if cohort:
            age_range = CHRONIC_CONDITIONS[cohort]["typical_age_range"]
            age = random.randint(age_range[0], age_range[1])
        else:
            age = random.randint(18, 90)
        
        # Check if fraud ring member
        is_fraud = patient_id in fraud_patient_ids
        fraud_ring = None
        if is_fraud:
            for ring_id, ring_data in FRAUD_RINGS.items():
                if patient_id in ring_data["patients"]:
                    fraud_ring = ring_id
                    break
        
        patient = {
            "patient_id": patient_id,
            "name": fake.name(),
            "age": age,
            "gender": random.choice(GENDERS),
            "is_fraud_ring_member": is_fraud,
            "fraud_ring": fraud_ring,
            "chronic_cohort": cohort,
            "insurance_type": random.choice(["Medicare", "Medicaid", "Commercial", "Self-Pay"]),
            "zip_code": fake.zipcode(),
        }
        patients.append(patient)

    return patients


def generate_claims(
    providers: list[dict], patients: list[dict], count: int = 2500
) -> list[dict]:
    """Generate claim data with temporal patterns, fraud ring behavior, and interconnections."""
    claims = []
    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 1)
    
    # Build lookup maps
    provider_map = {p["provider_id"]: p for p in providers}
    patient_map = {p["patient_id"]: p for p in patients}
    
    # Track patient-provider relationships for realistic patterns
    patient_primary_provider = {}
    patient_visit_history = defaultdict(list)
    
    # Generate fraud ring claims first (ensures they're in the dataset)
    fraud_claims = _generate_fraud_ring_claims(providers, patients, provider_map, patient_map)
    claims.extend(fraud_claims)
    
    # Generate regular claims
    regular_count = count - len(fraud_claims)
    
    for i in range(len(fraud_claims) + 1, count + 1):
        claim_id = f"CLM-{i:05d}"
        
        # Select patient (bias toward patients with chronic conditions for continuity)
        if random.random() < 0.4:
            # Choose patient with chronic condition
            chronic_patients = [p for p in patients if p.get("chronic_cohort")]
            patient = random.choice(chronic_patients) if chronic_patients else random.choice(patients)
        else:
            patient = random.choice(patients)
        
        # Select provider (bias toward establishing patient-provider relationships)
        if patient["patient_id"] in patient_primary_provider and random.random() < 0.6:
            provider_id = patient_primary_provider[patient["patient_id"]]
            provider = provider_map[provider_id]
        else:
            provider = random.choice(providers)
            # Establish relationship for future visits
            if random.random() < 0.5:
                patient_primary_provider[patient["patient_id"]] = provider["provider_id"]
        
        # Generate claim date with seasonal patterns
        claim_date = _generate_temporal_claim_date(start_date, end_date, provider["specialty"])
        
        # Generate diagnosis and procedure based on specialty
        diag = fake.diagnosis_code(specialty=provider["specialty"])
        proc = fake.procedure_code(specialty=provider["specialty"])
        
        # Apply temporal pattern to denial probability
        base_denial_rate = _get_specialty_denial_rate(provider["specialty"])
        seasonal_modifier = _get_seasonal_modifier(claim_date)
        
        # Determine claim status with temporal adjustments
        status_roll = random.random()
        adjusted_denial_rate = min(0.5, base_denial_rate * seasonal_modifier)
        
        if status_roll < (1 - adjusted_denial_rate - 0.15):  # Approved
            status = "APPROVED"
            denial_reason = None
        elif status_roll < (1 - 0.15):  # Denied
            status = "DENIED"
            denial_reason = random.choice(DENIAL_REASONS)
        else:  # Pending
            status = "PENDING"
            denial_reason = None

        # Generate claim amount based on procedure complexity
        claim_amount = _generate_claim_amount(proc[0], provider["specialty"])
        
        # Generate approved amount for approved claims
        approved_amount = None
        if status == "APPROVED":
            approved_amount = round(claim_amount * random.uniform(0.7, 1.0), 2)

        # Generate processing date
        processing_date = None
        if status != "PENDING":
            processing_date = claim_date + timedelta(days=random.randint(1, 14))

        # Flags based on diagnosis/procedure
        is_emergency = _is_emergency_claim(diag[0], proc[0])
        is_inpatient = _is_inpatient_procedure(proc[0])

        claim = {
            "claim_id": claim_id,
            "patient_id": patient["patient_id"],
            "patient_name": patient["name"],
            "patient_age": patient["age"],
            "patient_gender": patient["gender"],
            "provider_id": provider["provider_id"],
            "provider_name": provider["name"],
            "provider_specialty": provider["specialty"],
            "diagnosis_code": diag[0],
            "diagnosis_description": diag[1],
            "procedure_code": proc[0],
            "procedure_description": proc[1],
            "claim_amount": claim_amount,
            "approved_amount": approved_amount,
            "claim_status": status,
            "denial_reason": denial_reason,
            "claim_date": claim_date.isoformat(),
            "processing_date": processing_date.isoformat() if processing_date else None,
            "is_emergency": is_emergency,
            "is_inpatient": is_inpatient,
        }
        claims.append(claim)
        
        # Track visit history for clinical note generation
        patient_visit_history[patient["patient_id"]].append(claim)

    # Sort by claim_id for consistency
    claims.sort(key=lambda x: x["claim_id"])
    
    # Override specific claims for golden nuggets
    _setup_golden_claims(claims, patients, providers)

    return claims


def _generate_fraud_ring_claims(
    providers: list[dict], patients: list[dict], 
    provider_map: dict, patient_map: dict
) -> list[dict]:
    """Generate claims specifically for fraud ring patterns."""
    fraud_claims = []
    claim_counter = 1
    
    for ring_id, ring_data in FRAUD_RINGS.items():
        ring_providers = [provider_map.get(pid) for pid in ring_data["providers"] if pid in provider_map]
        ring_patients = [patient_map.get(pid) for pid in ring_data["patients"] if pid in patient_map]
        
        if not ring_providers or not ring_patients:
            continue
        
        # Generate claims based on fraud pattern
        if ring_data["pattern"] == "circular_referral":
            # High volume of cross-referrals between providers
            for patient in ring_patients:
                for provider in ring_providers:
                    # Multiple visits per patient-provider pair
                    for _ in range(random.randint(3, 8)):
                        claim = _create_fraud_claim(
                            claim_counter, patient, provider, 
                            ring_data["specialty"], "high_cost"
                        )
                        fraud_claims.append(claim)
                        claim_counter += 1
                        
        elif ring_data["pattern"] == "upcoding":
            # Normal procedures billed as complex ones
            for patient in ring_patients:
                provider = random.choice(ring_providers)
                for _ in range(random.randint(5, 12)):
                    claim = _create_fraud_claim(
                        claim_counter, patient, provider,
                        ring_data["specialty"], "upcoded"
                    )
                    fraud_claims.append(claim)
                    claim_counter += 1
                    
        elif ring_data["pattern"] == "phantom_billing":
            # Services never rendered (low documentation, high volume)
            for patient in ring_patients:
                provider = random.choice(ring_providers)
                for _ in range(random.randint(8, 15)):
                    claim = _create_fraud_claim(
                        claim_counter, patient, provider,
                        ring_data["specialty"], "phantom"
                    )
                    fraud_claims.append(claim)
                    claim_counter += 1
    
    return fraud_claims


def _create_fraud_claim(
    counter: int, patient: dict, provider: dict, 
    specialty: str, fraud_type: str
) -> dict:
    """Create a single fraud claim."""
    claim_date = fake.date_between(start_date=date(2024, 1, 1), end_date=date(2025, 12, 1))
    
    diag = fake.diagnosis_code(specialty=specialty)
    proc = fake.procedure_code(specialty=specialty)
    
    # Fraud claims are usually approved (they evade detection)
    if fraud_type == "phantom":
        status = "APPROVED" if random.random() < 0.85 else "DENIED"
    else:
        status = "APPROVED" if random.random() < 0.9 else "DENIED"
    
    # Generate inflated amounts for fraud
    if fraud_type == "high_cost":
        claim_amount = round(random.uniform(5000, 15000), 2)
    elif fraud_type == "upcoded":
        claim_amount = round(random.uniform(3000, 8000), 2)
    else:  # phantom
        claim_amount = round(random.uniform(500, 2000), 2)
    
    approved_amount = round(claim_amount * random.uniform(0.8, 1.0), 2) if status == "APPROVED" else None
    
    return {
        "claim_id": f"CLM-{counter:05d}",
        "patient_id": patient["patient_id"],
        "patient_name": patient["name"],
        "patient_age": patient["age"],
        "patient_gender": patient["gender"],
        "provider_id": provider["provider_id"],
        "provider_name": provider["name"],
        "provider_specialty": specialty,
        "diagnosis_code": diag[0],
        "diagnosis_description": diag[1],
        "procedure_code": proc[0],
        "procedure_description": proc[1],
        "claim_amount": claim_amount,
        "approved_amount": approved_amount,
        "claim_status": status,
        "denial_reason": None if status == "APPROVED" else random.choice(DENIAL_REASONS),
        "claim_date": claim_date.isoformat(),
        "processing_date": (claim_date + timedelta(days=random.randint(1, 7))).isoformat(),
        "is_emergency": False,
        "is_inpatient": random.random() < 0.3,
    }


def _generate_temporal_claim_date(start_date: date, end_date: date, specialty: str) -> date:
    """Generate claim date with seasonal patterns."""
    claim_date = fake.date_between(start_date=start_date, end_date=end_date)
    
    # Apply seasonal bias for certain specialties
    if specialty in TEMPORAL_PATTERNS["specialty_seasonal"]:
        month = claim_date.month
        if month in [12, 1, 2]:  # Winter
            modifier = TEMPORAL_PATTERNS["specialty_seasonal"][specialty].get("winter", 1.0)
        elif month in [6, 7, 8]:  # Summer
            modifier = TEMPORAL_PATTERNS["specialty_seasonal"][specialty].get("summer", 1.0)
        else:
            modifier = 1.0
        
        # Re-roll date with bias if modifier suggests higher volume
        if modifier > 1.0 and random.random() < (modifier - 1):
            claim_date = fake.date_between(start_date=start_date, end_date=end_date)
    
    return claim_date


def _get_specialty_denial_rate(specialty: str) -> float:
    """Get base denial rate by specialty."""
    denial_rates = {
        "Cardiology": 0.34,
        "Oncology": 0.28,
        "Orthopedics": 0.31,
        "Neurology": 0.22,
        "Emergency Medicine": 0.18,
        "Primary Care": 0.15,
        "Dermatology": 0.12,
        "Gastroenterology": 0.26,
    }
    return denial_rates.get(specialty, 0.25)


def _get_seasonal_modifier(claim_date: date) -> float:
    """Get seasonal denial rate modifier."""
    month_name = claim_date.strftime("%B")
    return TEMPORAL_PATTERNS["seasonal_denial_spikes"].get(month_name, 1.0)


def _generate_claim_amount(procedure_code: str, specialty: str) -> float:
    """Generate realistic claim amount based on procedure."""
    # High-cost procedures
    high_cost_prefixes = ["27", "33", "43", "61", "92"]  # Ortho, cardiac, GI surgery, neuro, cardiac
    
    if any(procedure_code.startswith(p) for p in high_cost_prefixes):
        base = random.uniform(5000, 25000)
    elif procedure_code.startswith("99"):  # Office visits
        base = random.uniform(100, 500)
    else:
        base = random.uniform(500, 3000)
    
    return round(base, 2)


def _is_emergency_claim(diagnosis_code: str, procedure_code: str) -> bool:
    """Determine if claim is emergency based on codes."""
    emergency_diagnoses = ["I21", "I26", "K35", "S06", "T78", "R55"]
    emergency_procedures = ["99285", "99291", "31500"]
    
    return (any(diagnosis_code.startswith(e) for e in emergency_diagnoses) or
            procedure_code in emergency_procedures or
            random.random() < 0.1)


def _is_inpatient_procedure(procedure_code: str) -> bool:
    """Determine if procedure is typically inpatient."""
    inpatient_prefixes = ["27", "33", "44", "47", "61"]
    return (any(procedure_code.startswith(p) for p in inpatient_prefixes) or
            random.random() < 0.15)


def _setup_golden_claims(
    claims: list[dict], patients: list[dict], providers: list[dict]
) -> None:
    """Set up specific claims for golden nugget scenarios (10 contradictions)."""
    golden_claims_data = [
        # Golden Nugget 1: CLM-01023 - Denied cardiac procedure (STEMI)
        {
            "index": 1022,
            "claim_id": "CLM-01023",
            "patient_id": "P-0456",
            "patient_name": "John Smith",
            "patient_age": 45,
            "patient_gender": "Male",
            "provider_id": "PRV-007",
            "provider_name": "Dr. X",
            "provider_specialty": "Cardiology",
            "diagnosis_code": "I21.0",
            "diagnosis_description": "ST elevation myocardial infarction",
            "procedure_code": "93458",
            "procedure_description": "Cardiac catheterization",
            "claim_amount": 8500.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Not medically necessary",
            "claim_date": "2024-06-15",
            "processing_date": "2024-06-20",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 2: CLM-02047 - Emergency appendectomy denied
        {
            "index": 500,
            "claim_id": "CLM-00501",
            "patient_id": "P-0789",
            "patient_name": "Sarah Johnson",
            "patient_age": 62,
            "patient_gender": "Female",
            "provider_id": "PRV-015",
            "provider_name": "Dr. Martinez",
            "provider_specialty": "Emergency Medicine",
            "diagnosis_code": "K35.80",
            "diagnosis_description": "Acute appendicitis",
            "procedure_code": "44970",
            "procedure_description": "Laparoscopic appendectomy",
            "claim_amount": 12500.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Not medically necessary",
            "claim_date": "2024-08-10",
            "processing_date": "2024-08-15",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 3: CLM-00500 - Pulmonary embolism denied
        {
            "index": 499,
            "claim_id": "CLM-00500",
            "patient_id": "P-0321",
            "patient_name": "Michael Chen",
            "patient_age": 58,
            "patient_gender": "Male",
            "provider_id": "PRV-018",
            "provider_name": "Dr. Wong",
            "provider_specialty": "Emergency Medicine",
            "diagnosis_code": "I26.99",
            "diagnosis_description": "Pulmonary embolism",
            "procedure_code": "71275",
            "procedure_description": "CT angiography chest",
            "claim_amount": 4500.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Pre-auth not obtained",
            "claim_date": "2024-09-22",
            "processing_date": "2024-09-27",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 4: CLM-00750 - Cancer treatment denied
        {
            "index": 749,
            "claim_id": "CLM-00750",
            "patient_id": "P-0024",
            "patient_name": "Maria Garcia",
            "patient_age": 54,
            "patient_gender": "Female",
            "provider_id": "PRV-022",
            "provider_name": "Dr. Patel",
            "provider_specialty": "Oncology",
            "diagnosis_code": "C50.919",
            "diagnosis_description": "Malignant neoplasm of breast",
            "procedure_code": "19301",
            "procedure_description": "Mastectomy",
            "claim_amount": 18500.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Experimental procedure",
            "claim_date": "2024-07-05",
            "processing_date": "2024-07-12",
            "is_emergency": False,
            "is_inpatient": True,
        },
        # Golden Nugget 5: CLM-00850 - Stroke intervention denied
        {
            "index": 849,
            "claim_id": "CLM-00850",
            "patient_id": "P-0088",
            "patient_name": "Robert Williams",
            "patient_age": 71,
            "patient_gender": "Male",
            "provider_id": "PRV-028",
            "provider_name": "Dr. Neuhaus",
            "provider_specialty": "Neurology",
            "diagnosis_code": "I63.9",
            "diagnosis_description": "Cerebral infarction",
            "procedure_code": "61645",
            "procedure_description": "Thrombectomy",
            "claim_amount": 32000.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Out of network",
            "claim_date": "2024-05-18",
            "processing_date": "2024-05-25",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 6: CLM-00950 - Hip fracture surgery denied
        {
            "index": 949,
            "claim_id": "CLM-00950",
            "patient_id": "P-0112",
            "patient_name": "Dorothy Miller",
            "patient_age": 82,
            "patient_gender": "Female",
            "provider_id": "PRV-031",
            "provider_name": "Dr. Ortega",
            "provider_specialty": "Orthopedics",
            "diagnosis_code": "S72.001A",
            "diagnosis_description": "Fracture of femoral neck",
            "procedure_code": "27130",
            "procedure_description": "Total hip replacement",
            "claim_amount": 45000.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Benefit limit exceeded",
            "claim_date": "2024-11-02",
            "processing_date": "2024-11-09",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 7: CLM-01100 - Diabetic emergency denied
        {
            "index": 1099,
            "claim_id": "CLM-01100",
            "patient_id": "P-0045",
            "patient_name": "James Anderson",
            "patient_age": 56,
            "patient_gender": "Male",
            "provider_id": "PRV-008",
            "provider_name": "Dr. Enderson",
            "provider_specialty": "Primary Care",
            "diagnosis_code": "E11.65",
            "diagnosis_description": "Type 2 diabetes with hyperglycemia",
            "procedure_code": "99291",
            "procedure_description": "Critical care first hour",
            "claim_amount": 8900.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Incomplete information",
            "claim_date": "2024-04-20",
            "processing_date": "2024-04-28",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 8: CLM-01250 - GI bleed denied
        {
            "index": 1249,
            "claim_id": "CLM-01250",
            "patient_id": "P-0067",
            "patient_name": "Linda Thompson",
            "patient_age": 68,
            "patient_gender": "Female",
            "provider_id": "PRV-033",
            "provider_name": "Dr. Gastro",
            "provider_specialty": "Gastroenterology",
            "diagnosis_code": "K92.2",
            "diagnosis_description": "Gastrointestinal hemorrhage",
            "procedure_code": "43239",
            "procedure_description": "Upper GI endoscopy with biopsy",
            "claim_amount": 6700.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Duplicate claim",
            "claim_date": "2024-10-15",
            "processing_date": "2024-10-22",
            "is_emergency": True,
            "is_inpatient": True,
        },
        # Golden Nugget 9: CLM-01400 - Anaphylaxis treatment denied
        {
            "index": 1399,
            "claim_id": "CLM-01400",
            "patient_id": "P-0198",
            "patient_name": "Kevin Lee",
            "patient_age": 34,
            "patient_gender": "Male",
            "provider_id": "PRV-015",
            "provider_name": "Dr. Martinez",
            "provider_specialty": "Emergency Medicine",
            "diagnosis_code": "T78.2XXA",
            "diagnosis_description": "Anaphylactic shock",
            "procedure_code": "99285",
            "procedure_description": "Emergency department visit",
            "claim_amount": 3200.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Service not covered",
            "claim_date": "2024-03-08",
            "processing_date": "2024-03-15",
            "is_emergency": True,
            "is_inpatient": False,
        },
        # Golden Nugget 10: CLM-01550 - Melanoma excision denied
        {
            "index": 1549,
            "claim_id": "CLM-01550",
            "patient_id": "P-0234",
            "patient_name": "Susan White",
            "patient_age": 47,
            "patient_gender": "Female",
            "provider_id": "PRV-040",
            "provider_name": "Dr. Dermato",
            "provider_specialty": "Dermatology",
            "diagnosis_code": "C43.9",
            "diagnosis_description": "Malignant melanoma of skin",
            "procedure_code": "11600",
            "procedure_description": "Excision of malignant lesion",
            "claim_amount": 5800.00,
            "approved_amount": None,
            "claim_status": "DENIED",
            "denial_reason": "Not medically necessary",
            "claim_date": "2024-08-28",
            "processing_date": "2024-09-04",
            "is_emergency": False,
            "is_inpatient": False,
        },
    ]
    
    for golden_claim in golden_claims_data:
        idx = golden_claim.pop("index")
        if idx < len(claims):
            claims[idx] = golden_claim


def generate_clinical_notes(
    claims: list[dict], patients: list[dict], count: int = 100
) -> list[dict]:
    """Generate clinical notes with 10 golden nuggets and strong claim linkages."""
    notes = []
    
    # Create claim lookup by patient_id for linkage
    claims_by_patient = defaultdict(list)
    for claim in claims:
        claims_by_patient[claim["patient_id"]].append(claim)
    
    # Golden Nugget clinical notes (10 contradictions)
    golden_notes = _generate_golden_nugget_notes()
    notes.extend(golden_notes)
    
    # Generate additional clinical notes with strong claim linkages
    note_counter = len(golden_notes) + 1
    
    # Generate notes for patients with multiple claims (continuity of care)
    multi_claim_patients = [pid for pid, pclaims in claims_by_patient.items() 
                           if len(pclaims) >= 3]
    
    for patient_id in multi_claim_patients[:40]:  # Top 40 patients with most claims
        patient_claims = claims_by_patient[patient_id]
        patient_info = next((p for p in patients if p["patient_id"] == patient_id), None)
        
        if not patient_info:
            continue
        
        # Generate 1-2 notes per high-activity patient
        for _ in range(min(2, len(patient_claims))):
            claim = random.choice(patient_claims)
            note = _generate_linked_clinical_note(
                note_counter, patient_info, claim
            )
            notes.append(note)
            note_counter += 1
            
            if note_counter > count:
                break
        
        if note_counter > count:
            break
    
    # Generate remaining notes for random patients with claims
    while note_counter <= count:
        patient = random.choice(patients)
        patient_claims = claims_by_patient.get(patient["patient_id"], [])
        
        if patient_claims:
            claim = random.choice(patient_claims)
            note = _generate_linked_clinical_note(note_counter, patient, claim)
        else:
            # Create note without claim linkage (less common)
            note = _generate_standalone_clinical_note(note_counter, patient)
        
        notes.append(note)
        note_counter += 1
    
    return notes


def _generate_golden_nugget_notes() -> list[dict]:
    """Generate the 10 golden nugget clinical notes that contradict denials."""
    golden_notes = []
    
    # Golden Nugget 1: CN-001 - STEMI contradicting "not medically necessary"
    golden_notes.append({
        "note_id": "CN-001",
        "patient_id": "P-0456",
        "claim_id": "CLM-01023",
        "note_date": "2024-06-15T14:30:00",
        "note_type": "EmergencyNote",
        "content": """# Emergency Department Note

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
*Documented by: ED Attending*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 2: CN-002 - Appendicitis contradicting "not medically necessary"
    golden_notes.append({
        "note_id": "CN-002",
        "patient_id": "P-0789",
        "claim_id": "CLM-00501",
        "note_date": "2024-08-10T03:45:00",
        "note_type": "SurgicalNote",
        "content": """# Surgical Note - Emergency Appendectomy

**Patient:** Sarah Johnson (P-0789)
**Date:** August 10, 2024, 03:45 AM
**Procedure:** Emergency Laparoscopic Appendectomy

## Pre-operative Diagnosis
Acute appendicitis with peritonitis

## Clinical Presentation
Patient arrived in ED at 01:30 with severe right lower quadrant pain, fever (102.4°F), elevated WBC (18,500), and positive McBurney's sign. CT scan confirmed perforated appendix with localized abscess formation.

## Surgical Findings
- Gangrenous appendix with perforation at tip
- Purulent fluid in right paracolic gutter
- Early peritonitis with inflammatory changes

## Clinical Justification
**THIS WAS NOT A ROUTINE EXAMINATION.** Patient presented with acute abdomen and signs of sepsis. Delay in surgical intervention would have resulted in:
- Progression of peritonitis
- Septic shock
- Potential death

The surgical team was called emergently from home at 2:30 AM. This was a life-saving emergency procedure, not an elective or routine examination.

## Post-operative Status
Patient stable, transferred to surgical floor for IV antibiotics and monitoring.

---
*Attending Surgeon: Dr. Martinez*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 3: CN-003 - Pulmonary embolism contradicting "pre-auth not obtained"
    golden_notes.append({
        "note_id": "CN-003",
        "patient_id": "P-0321",
        "claim_id": "CLM-00500",
        "note_date": "2024-09-22T11:00:00",
        "note_type": "RadiologyReport",
        "content": """# Radiology Report - URGENT FINDINGS

**Patient:** Michael Chen (P-0321)
**Date:** September 22, 2024
**Study:** CT Angiography Chest

## Clinical Indication
Acute shortness of breath, hypoxia, elevated D-dimer

## Findings
**CRITICAL FINDING - CALLED TO ORDERING PHYSICIAN IMMEDIATELY**

Large saddle pulmonary embolism identified at the bifurcation of the main pulmonary artery, extending bilaterally into the lobar and segmental branches.

- Right heart strain present with RV:LV ratio of 1.3
- Evidence of pulmonary infarction in right lower lobe
- No evidence of aortic dissection

## Impression
**MASSIVE PULMONARY EMBOLISM - LIFE-THREATENING**

This patient has intermediate-high risk PE with evidence of right heart strain. Immediate anticoagulation and consideration for thrombolytic therapy or catheter-directed intervention is recommended.

**This imaging study and subsequent treatment is medically necessary and emergent.** Pre-authorization cannot reasonably be obtained for emergent life-threatening conditions presenting acutely.

---
*Radiologist: Dr. Wong*
*Time of verbal notification: 11:15 AM*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 4: CN-004 - Breast cancer contradicting "experimental procedure"
    golden_notes.append({
        "note_id": "CN-004",
        "patient_id": "P-0024",
        "claim_id": "CLM-00750",
        "note_date": "2024-07-05T09:00:00",
        "note_type": "OncologyNote",
        "content": """# Oncology Consultation Note

**Patient:** Maria Garcia (P-0024)
**Date:** July 5, 2024
**Diagnosis:** Invasive Ductal Carcinoma, Stage IIB

## Clinical History
54-year-old female with biopsy-confirmed invasive ductal carcinoma of the right breast. Tumor is 3.2cm, ER/PR positive, HER2 negative. Sentinel lymph node biopsy positive for metastatic disease in 2/3 nodes.

## Tumor Board Discussion
Patient case was presented at multidisciplinary tumor board on July 1, 2024. Unanimous recommendation for modified radical mastectomy followed by adjuvant chemotherapy and radiation.

## Medical Necessity Statement
**Mastectomy is NOT an experimental procedure for breast cancer.** This is a standard-of-care treatment that has been performed for over 100 years with extensive evidence supporting its efficacy.

Per NCCN Guidelines (Version 4.2024):
- Mastectomy is a Category 1 recommendation for Stage II breast cancer
- This is not investigational or experimental
- Delay in surgical treatment could result in disease progression and worse outcomes

## Plan
1. Proceed with modified radical mastectomy as scheduled
2. Post-operative oncology follow-up for adjuvant therapy planning
3. Patient has provided informed consent

**Denial of this procedure as "experimental" is medically inappropriate and inconsistent with established treatment guidelines.**

---
*Medical Oncologist: Dr. Patel*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 5: CN-005 - Stroke contradicting "out of network"
    golden_notes.append({
        "note_id": "CN-005",
        "patient_id": "P-0088",
        "claim_id": "CLM-00850",
        "note_date": "2024-05-18T06:15:00",
        "note_type": "EmergencyNote",
        "content": """# Stroke Alert - Emergency Transfer Note

**Patient:** Robert Williams (P-0088)
**Date:** May 18, 2024, 06:15 AM
**Diagnosis:** Acute Ischemic Stroke - Large Vessel Occlusion

## Presentation
71-year-old male brought by EMS with acute onset left-sided weakness and facial droop. Last known well: 04:30 AM. NIH Stroke Scale: 18.

## Emergency Transfer Justification
Patient presented to Community Hospital ED but required immediate transfer to our Comprehensive Stroke Center for thrombectomy capability.

**PRUDENT LAYPERSON STANDARD APPLIES:**
- Patient experienced acute stroke symptoms
- Called 911 and was transported to nearest ED
- Transfer to stroke center required for life-saving intervention
- Network status cannot be determined during medical emergency

## Intervention
- CTA confirmed M1 occlusion
- Thrombectomy performed with TICI 2b reperfusion achieved
- Door-to-puncture time: 45 minutes

## Outcome
Patient showed significant improvement post-procedure. NIHSS improved from 18 to 6.

**Out-of-network denial is inappropriate for emergency stroke care. Federal EMTALA regulations and state prudent layperson laws require coverage of emergency services regardless of network status.**

---
*Neurointerventionalist: Dr. Neuhaus*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 6: CN-006 - Hip fracture contradicting "benefit limit exceeded"
    golden_notes.append({
        "note_id": "CN-006",
        "patient_id": "P-0112",
        "claim_id": "CLM-00950",
        "note_date": "2024-11-02T14:00:00",
        "note_type": "SurgicalNote",
        "content": """# Orthopedic Surgery Note - Hip Fracture

**Patient:** Dorothy Miller (P-0112)
**Date:** November 2, 2024
**Procedure:** Total Hip Arthroplasty for Femoral Neck Fracture

## Clinical Presentation
82-year-old female with displaced femoral neck fracture after ground-level fall at home. Patient was previously ambulatory and independent with ADLs.

## Fracture Classification
Garden Type IV displaced femoral neck fracture. Non-operative management would result in non-union and permanent disability.

## Medical Necessity
**Hip fracture surgery is not elective and cannot be subject to annual benefit limits when medically necessary:**

1. Without surgery, patient will be bedbound → high risk of:
   - Deep vein thrombosis / pulmonary embolism
   - Pressure ulcers
   - Pneumonia
   - Death (1-year mortality >50% without surgery)

2. Surgery is the only treatment option for displaced femoral neck fractures in ambulatory patients

3. Mental Health Parity and Addiction Equity Act and ACA essential health benefits require coverage of medically necessary surgical procedures

## Procedure Performed
Cemented hemiarthroplasty performed without complication. Patient weight-bearing as tolerated post-operatively.

**Denying hip fracture repair due to "benefit limits" is medically inappropriate and potentially life-threatening.**

---
*Orthopedic Surgeon: Dr. Ortega*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 7: CN-007 - DKA contradicting "incomplete information"
    golden_notes.append({
        "note_id": "CN-007",
        "patient_id": "P-0045",
        "claim_id": "CLM-01100",
        "note_date": "2024-04-20T22:30:00",
        "note_type": "ICUNote",
        "content": """# ICU Admission Note - Diabetic Ketoacidosis

**Patient:** James Anderson (P-0045)
**Date:** April 20, 2024, 22:30
**Diagnosis:** Severe Diabetic Ketoacidosis

## Presentation
56-year-old male with Type 2 DM presenting with altered mental status, Kussmaul respirations, and severe dehydration.

## Laboratory Values on Admission
- Blood glucose: 687 mg/dL
- pH: 7.12 (severe acidosis)
- Anion gap: 28
- Bicarbonate: 8 mEq/L
- Ketones: Large

## ICU Course (First 24 Hours)
- Insulin infusion protocol initiated
- Aggressive IV fluid resuscitation (6L in first 12 hours)
- Electrolyte replacement (potassium, phosphate)
- Continuous telemetry monitoring
- Hourly glucose checks
- Q2h ABG monitoring

## Critical Care Justification
**ALL REQUIRED DOCUMENTATION WAS PROVIDED:**
- Admission H&P completed at 22:45
- Labs resulted and documented
- ICU progress notes completed Q4H
- Nursing flowsheets complete
- Medication administration record complete

**DKA with pH <7.2 meets ICU admission criteria per Surviving Sepsis Campaign guidelines.** This was critical care requiring continuous monitoring and titrated interventions.

## Outcome
Patient stabilized after 48 hours, transitioned to subcutaneous insulin, discharged home day 4.

**Denial for "incomplete information" is inaccurate - complete medical record documentation is available.**

---
*Intensivist: Dr. Enderson*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 8: CN-008 - GI bleed contradicting "duplicate claim"
    golden_notes.append({
        "note_id": "CN-008",
        "patient_id": "P-0067",
        "claim_id": "CLM-01250",
        "note_date": "2024-10-15T08:00:00",
        "note_type": "ProcedureNote",
        "content": """# Endoscopy Procedure Note

**Patient:** Linda Thompson (P-0067)
**Date:** October 15, 2024
**Procedure:** EGD with Hemostasis

## Clinical Indication
68-year-old female with acute upper GI bleeding. Hemoglobin dropped from 12.1 to 7.8 g/dL over 8 hours. Coffee-ground emesis and melena.

## Procedure Details
Upper endoscopy revealed actively bleeding gastric ulcer (Forrest Ia classification) with visible spurting vessel.

## Therapeutic Intervention
- Epinephrine injection (4 quadrants)
- Bipolar cautery applied
- Hemoclip placement x2
- Hemostasis achieved

## Clarification: NOT A DUPLICATE CLAIM
**This was a THERAPEUTIC endoscopy, not a diagnostic procedure.**

The patient had a DIAGNOSTIC EGD 6 months prior (April 2024) for dyspepsia screening - that was an outpatient procedure.

This October 2024 procedure was:
- Emergency admission for acute GI bleed
- Therapeutic intervention required
- Different diagnosis codes (K92.2 vs K21.0)
- Different CPT codes (43239 vs 43235)
- Different dates of service
- Completely separate clinical encounter

**These are two distinct medical services, not duplicate claims.**

---
*Gastroenterologist: Dr. Gastro*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 9: CN-009 - Anaphylaxis contradicting "service not covered"
    golden_notes.append({
        "note_id": "CN-009",
        "patient_id": "P-0198",
        "claim_id": "CLM-01400",
        "note_date": "2024-03-08T15:45:00",
        "note_type": "EmergencyNote",
        "content": """# Emergency Department Note - Anaphylaxis

**Patient:** Kevin Lee (P-0198)
**Date:** March 8, 2024, 15:45
**Chief Complaint:** Severe allergic reaction

## Presenting Symptoms
34-year-old male with sudden onset difficulty breathing, generalized urticaria, and tongue swelling after eating at a restaurant. Onset ~20 minutes after meal (likely shellfish exposure).

## Vital Signs on Arrival
- BP: 78/45 mmHg (HYPOTENSIVE)
- HR: 128 bpm
- RR: 32/min with stridor
- SpO2: 88% on room air

## Clinical Assessment
**ANAPHYLACTIC SHOCK** - Life-threatening emergency

## Treatment Administered
1. Epinephrine 0.3mg IM (thigh) - IMMEDIATELY
2. IV access x2 large bore
3. Normal saline 2L bolus
4. Diphenhydramine 50mg IV
5. Methylprednisolone 125mg IV
6. Albuterol nebulizer
7. Continuous monitoring

## Response
Patient stabilized within 30 minutes. BP improved to 115/72. Airway remained patent. Observed for 6 hours, discharged with EpiPen prescription and allergy referral.

## Coverage Statement
**Emergency treatment for anaphylaxis IS a covered essential health benefit under the ACA.**

All health insurance plans must cover emergency services without prior authorization. Anaphylaxis is a recognized ICD-10 diagnosis (T78.2XXA) requiring immediate medical intervention.

**Denial stating "service not covered" contradicts federal healthcare coverage requirements.**

---
*Emergency Physician: Dr. Martinez*""",
        "is_golden_nugget": True,
    })
    
    # Golden Nugget 10: CN-010 - Melanoma contradicting "not medically necessary"
    golden_notes.append({
        "note_id": "CN-010",
        "patient_id": "P-0234",
        "claim_id": "CLM-01550",
        "note_date": "2024-08-28T10:30:00",
        "note_type": "PathologyReport",
        "content": """# Pathology Report - Skin Excision

**Patient:** Susan White (P-0234)
**Date:** August 28, 2024
**Specimen:** Skin excision, left upper back

## Clinical History
47-year-old female with changing pigmented lesion. Lesion has increased in size and developed irregular borders over past 3 months. ABCDE criteria positive.

## Gross Description
Elliptical skin excision measuring 2.5 x 1.8 x 0.8 cm with central pigmented lesion measuring 1.2 cm in greatest dimension.

## Microscopic Findings
- **Diagnosis: MALIGNANT MELANOMA, invasive**
- Breslow thickness: 1.8 mm
- Clark level: IV (reticular dermis)
- Ulceration: Present
- Mitotic rate: 4/mm²
- Margins: Positive (tumor at lateral margin)

## AJCC Staging
**pT2b N0 M0 - Stage IIA Melanoma**

## Clinical Significance
**THIS EXCISION WAS MEDICALLY NECESSARY.**

1. Lesion met clinical criteria for malignancy (ABCDE criteria)
2. Biopsy confirmed invasive melanoma
3. Without excision, this cancer would metastasize
4. 5-year survival drops from 94% (localized) to 27% (distant) without treatment
5. Re-excision with wider margins now required due to positive margins

## Recommendation
Urgent re-excision with 1cm margins recommended. Sentinel lymph node biopsy indicated given Breslow thickness >1mm.

**Denial of melanoma excision as "not medically necessary" is incompatible with the pathologic diagnosis of invasive cancer.**

---
*Dermatopathologist: Dr. Dermato*""",
        "is_golden_nugget": True,
    })
    
    return golden_notes


def _generate_linked_clinical_note(note_id: int, patient: dict, claim: dict) -> dict:
    """Generate a clinical note linked to a specific claim."""
    note_types = ["ProgressNote", "ConsultNote", "NursingNote", "LabReport", "ImagingReport"]
    note_type = random.choice(note_types)
    
    # Generate note date close to claim date
    claim_date = datetime.fromisoformat(claim["claim_date"])
    note_date = claim_date + timedelta(days=random.randint(-2, 5))
    
    content = _generate_note_content(patient, claim, note_type)
    
    return {
        "note_id": f"CN-{note_id:03d}",
        "patient_id": patient["patient_id"],
        "claim_id": claim["claim_id"],
        "note_date": note_date.isoformat(),
        "note_type": note_type,
        "content": content,
        "is_golden_nugget": False,
    }


def _generate_standalone_clinical_note(note_id: int, patient: dict) -> dict:
    """Generate a clinical note without claim linkage."""
    note_types = ["AnnualPhysical", "WellnessVisit", "PhoneNote", "ReferralNote"]
    note_type = random.choice(note_types)
    note_date = fake.date_time_between(start_date="-1y", end_date="now")
    
    content = f"""# {note_type}

**Patient:** {patient['name']} ({patient['patient_id']})
**Date:** {note_date.strftime('%B %d, %Y')}

## Visit Summary
{patient['age']}-year-old {patient['gender'].lower()} presenting for {note_type.lower().replace('note', '')}.

## Assessment
Patient appears in good health. No acute concerns.

## Plan
- Continue current medications
- Follow up as needed
- Routine screenings up to date

---
*Documentation by clinical staff*"""
    
    return {
        "note_id": f"CN-{note_id:03d}",
        "patient_id": patient["patient_id"],
        "claim_id": None,
        "note_date": note_date.isoformat(),
        "note_type": note_type,
        "content": content,
        "is_golden_nugget": False,
    }


def _generate_note_content(patient: dict, claim: dict, note_type: str) -> str:
    """Generate realistic clinical note content based on claim data."""
    templates = {
        "ProgressNote": """# Progress Note

**Patient:** {patient_name} ({patient_id})
**Date:** {note_date}
**Provider:** {provider_name}

## Chief Complaint
Follow-up for {diagnosis_desc}

## History of Present Illness
{age}-year-old {gender} with history of {diagnosis_desc}. Patient {status_text}.

## Assessment
{diagnosis_code} - {diagnosis_desc}

## Plan
1. {plan_item_1}
2. Follow up in {follow_up}
3. {plan_item_2}

---
*{provider_name}, {specialty}*""",
        
        "ConsultNote": """# Consultation Note

**Patient:** {patient_name} ({patient_id})
**Date:** {note_date}
**Consulting Service:** {specialty}

## Reason for Consultation
Evaluation of {diagnosis_desc}

## History
{age}-year-old {gender} referred for {specialty} evaluation. {clinical_history}

## Physical Examination
{exam_findings}

## Assessment
{diagnosis_code}: {diagnosis_desc}

## Recommendations
1. {recommendation_1}
2. {recommendation_2}
3. Follow up with {specialty} in {follow_up}

---
*{provider_name}, {specialty}*""",
        
        "LabReport": """# Laboratory Results

**Patient:** {patient_name} ({patient_id})
**Date:** {note_date}
**Ordering Provider:** {provider_name}

## Tests Ordered
Related to: {diagnosis_desc}

## Results
| Test | Result | Reference Range | Flag |
|------|--------|-----------------|------|
| {lab_1} | {value_1} | {range_1} | {flag_1} |
| {lab_2} | {value_2} | {range_2} | {flag_2} |
| {lab_3} | {value_3} | {range_3} | {flag_3} |

## Interpretation
Results are {interpretation} with diagnosis of {diagnosis_desc}.

---
*Laboratory Services*""",
        
        "ImagingReport": """# Radiology Report

**Patient:** {patient_name} ({patient_id})
**Date:** {note_date}
**Study:** {imaging_type}
**Ordering Provider:** {provider_name}

## Clinical Indication
{diagnosis_desc}

## Technique
{technique}

## Findings
{findings}

## Impression
{impression}

---
*Radiologist*""",
        
        "NursingNote": """# Nursing Assessment Note

**Patient:** {patient_name} ({patient_id})
**Date:** {note_date}
**Unit:** {unit}

## Vital Signs
- BP: {bp}
- HR: {hr} bpm
- Temp: {temp}°F
- SpO2: {spo2}%

## Assessment
Patient is a {age}-year-old {gender} admitted for {diagnosis_desc}. {nursing_assessment}

## Interventions
1. {intervention_1}
2. {intervention_2}
3. Pain managed with {pain_mgmt}

## Patient Response
{response}

---
*RN Signature*"""
    }
    
    template = templates.get(note_type, templates["ProgressNote"])
    
    # Generate realistic values
    claim_date = datetime.fromisoformat(claim["claim_date"])
    
    return template.format(
        patient_name=patient["name"],
        patient_id=patient["patient_id"],
        age=patient["age"],
        gender=patient["gender"].lower(),
        note_date=claim_date.strftime("%B %d, %Y"),
        provider_name=claim["provider_name"],
        specialty=claim["provider_specialty"],
        diagnosis_code=claim["diagnosis_code"],
        diagnosis_desc=claim["diagnosis_description"],
        procedure_desc=claim["procedure_description"],
        status_text=random.choice([
            "reports improvement in symptoms",
            "continues to experience symptoms",
            "is recovering well",
            "requires further evaluation"
        ]),
        plan_item_1=random.choice([
            "Continue current treatment plan",
            "Adjust medications as needed",
            "Order additional testing",
            "Refer to specialist"
        ]),
        plan_item_2=random.choice([
            "Patient education provided",
            "Lifestyle modifications discussed",
            "Return precautions given",
            "Medication reconciliation completed"
        ]),
        follow_up=random.choice(["1 week", "2 weeks", "1 month", "3 months"]),
        clinical_history=f"Symptoms began {random.randint(1, 14)} days ago",
        exam_findings=random.choice([
            "Within normal limits",
            "Findings consistent with diagnosis",
            "Mild abnormalities noted",
            "Significant findings documented"
        ]),
        recommendation_1=random.choice([
            "Proceed with recommended treatment",
            "Consider alternative therapy",
            "Obtain additional imaging",
            "Trial conservative management"
        ]),
        recommendation_2=random.choice([
            "Monitor closely",
            "Physical therapy referral",
            "Nutritional counseling",
            "Medication adjustment"
        ]),
        lab_1=random.choice(["CBC", "BMP", "Lipid Panel", "HbA1c"]),
        value_1=f"{random.uniform(4, 15):.1f}",
        range_1="4.0-11.0",
        flag_1=random.choice(["Normal", "High", "Low", ""]),
        lab_2=random.choice(["Creatinine", "Glucose", "TSH", "ALT"]),
        value_2=f"{random.uniform(0.5, 200):.1f}",
        range_2="0.7-1.3",
        flag_2=random.choice(["Normal", "High", ""]),
        lab_3=random.choice(["Potassium", "Sodium", "Calcium", "Magnesium"]),
        value_3=f"{random.uniform(3, 145):.1f}",
        range_3="3.5-5.0",
        flag_3=random.choice(["Normal", "", ""]),
        interpretation=random.choice(["consistent", "supportive", "suggestive"]),
        imaging_type=random.choice(["X-ray", "CT scan", "MRI", "Ultrasound"]),
        technique="Standard protocol applied",
        findings=random.choice([
            "No acute abnormality identified",
            "Findings consistent with clinical history",
            "Changes noted from prior study",
            "New findings requiring attention"
        ]),
        impression=random.choice([
            "Stable appearance",
            "Findings correlate with clinical presentation",
            "Recommend clinical correlation",
            "Follow-up imaging suggested"
        ]),
        unit=random.choice(["Medical-Surgical", "Telemetry", "ICU", "Observation"]),
        bp=f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        hr=random.randint(60, 100),
        temp=round(random.uniform(97.5, 99.5), 1),
        spo2=random.randint(94, 100),
        nursing_assessment=random.choice([
            "Alert and oriented",
            "Resting comfortably",
            "Reports pain controlled",
            "Tolerating diet well"
        ]),
        intervention_1=random.choice([
            "Medications administered as ordered",
            "IV fluids infusing",
            "Wound care completed",
            "Patient repositioned"
        ]),
        intervention_2=random.choice([
            "Fall precautions in place",
            "Call light within reach",
            "Incentive spirometry encouraged",
            "Ambulation assisted"
        ]),
        pain_mgmt=random.choice([
            "oral analgesics",
            "IV medication",
            "comfort measures",
            "scheduled medications"
        ]),
        response=random.choice([
            "Patient tolerating well",
            "Condition stable",
            "Improving",
            "No acute changes"
        ]),
    )


def save_claims_csv(claims: list[dict], filepath: Path) -> None:
    """Save claims to CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "claim_id",
        "patient_id",
        "patient_name",
        "patient_age",
        "patient_gender",
        "provider_id",
        "provider_name",
        "provider_specialty",
        "diagnosis_code",
        "diagnosis_description",
        "procedure_code",
        "procedure_description",
        "claim_amount",
        "approved_amount",
        "claim_status",
        "denial_reason",
        "claim_date",
        "processing_date",
        "is_emergency",
        "is_inpatient",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(claims)

    print(f"Generated {len(claims)} claims → {filepath}")


def save_clinical_notes(notes: list[dict], notes_dir: Path) -> None:
    """Save clinical notes as Markdown files."""
    notes_dir.mkdir(parents=True, exist_ok=True)

    for note in notes:
        filepath = notes_dir / f"{note['note_id']}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            # Write frontmatter
            f.write("---\n")
            f.write(f"note_id: {note['note_id']}\n")
            f.write(f"patient_id: {note['patient_id']}\n")
            f.write(f"claim_id: {note['claim_id'] or 'null'}\n")
            f.write(f"note_date: {note['note_date']}\n")
            f.write(f"note_type: {note['note_type']}\n")
            f.write(f"is_golden_nugget: {str(note['is_golden_nugget']).lower()}\n")
            f.write("---\n\n")
            f.write(note["content"])

    print(f"Generated {len(notes)} clinical notes → {notes_dir}")


def generate_fraud_ring_data() -> dict:
    """Generate pre-baked fraud ring graph data for all 3 fraud rings."""
    # Ring 1: Cardiology Kickback Ring (Dr. X and Dr. Y)
    ring_1_nodes = [
        {
            "id": "PRV-007",
            "type": "provider",
            "label": "Dr. X",
            "specialty": "Cardiology",
            "risk_score": 0.92,
            "total_claims": 245,
            "denial_rate": 0.08,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_1",
        },
        {
            "id": "PRV-012",
            "type": "provider",
            "label": "Dr. Y",
            "specialty": "Cardiology",
            "risk_score": 0.78,
            "total_claims": 189,
            "denial_rate": 0.12,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_1",
        },
    ]
    
    # Add patients for Ring 1
    for i, pid in enumerate(["P-0101", "P-0102", "P-0103", "P-0104", "P-0105", "P-0106"]):
        ring_1_nodes.append({
            "id": pid,
            "type": "patient",
            "label": f"Patient {chr(65 + i)}",
            "risk_score": round(random.uniform(0.52, 0.68), 2),
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_1",
        })
    
    # Ring 2: Upcoding Scheme
    ring_2_nodes = [
        {
            "id": "PRV-023",
            "type": "provider",
            "label": "Dr. Alpha",
            "specialty": "Orthopedics",
            "risk_score": 0.85,
            "total_claims": 312,
            "denial_rate": 0.05,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_2",
        },
        {
            "id": "PRV-024",
            "type": "provider",
            "label": "Dr. Beta",
            "specialty": "Orthopedics",
            "risk_score": 0.79,
            "total_claims": 287,
            "denial_rate": 0.06,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_2",
        },
        {
            "id": "PRV-025",
            "type": "provider",
            "label": "Dr. Gamma",
            "specialty": "Orthopedics",
            "risk_score": 0.72,
            "total_claims": 198,
            "denial_rate": 0.07,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_2",
        },
    ]
    
    for i, pid in enumerate(["P-0150", "P-0151", "P-0152", "P-0153", "P-0154"]):
        ring_2_nodes.append({
            "id": pid,
            "type": "patient",
            "label": f"Patient {chr(71 + i)}",
            "risk_score": round(random.uniform(0.45, 0.60), 2),
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_2",
        })
    
    # Ring 3: Phantom Billing Network
    ring_3_nodes = [
        {
            "id": "PRV-035",
            "type": "provider",
            "label": "Dr. Shadow",
            "specialty": "Primary Care",
            "risk_score": 0.88,
            "total_claims": 456,
            "denial_rate": 0.03,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_3",
        },
        {
            "id": "PRV-036",
            "type": "provider",
            "label": "Dr. Ghost",
            "specialty": "Primary Care",
            "risk_score": 0.82,
            "total_claims": 398,
            "denial_rate": 0.04,
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_3",
        },
    ]
    
    for i, pid in enumerate(["P-0180", "P-0181", "P-0182", "P-0183"]):
        ring_3_nodes.append({
            "id": pid,
            "type": "patient",
            "label": f"Patient {chr(76 + i)}",
            "risk_score": round(random.uniform(0.40, 0.55), 2),
            "is_fraud_ring_member": True,
            "fraud_ring": "ring_3",
        })
    
    # Combine all nodes
    all_nodes = ring_1_nodes + ring_2_nodes + ring_3_nodes
    
    # Generate edges for Ring 1 (circular referrals)
    edges = [
        # Dr. X treats patients
        {"source": "PRV-007", "target": "P-0101", "relationship_type": "treated", "weight": 12},
        {"source": "PRV-007", "target": "P-0102", "relationship_type": "treated", "weight": 8},
        {"source": "PRV-007", "target": "P-0103", "relationship_type": "treated", "weight": 15},
        # Dr. Y treats patients
        {"source": "PRV-012", "target": "P-0104", "relationship_type": "treated", "weight": 9},
        {"source": "PRV-012", "target": "P-0105", "relationship_type": "treated", "weight": 11},
        {"source": "PRV-012", "target": "P-0106", "relationship_type": "treated", "weight": 7},
        # Circular referrals between providers (THE FRAUD PATTERN)
        {"source": "PRV-007", "target": "PRV-012", "relationship_type": "referred_from", "weight": 23},
        {"source": "PRV-012", "target": "PRV-007", "relationship_type": "referred_from", "weight": 19},
        # Patient referrals completing the circle
        {"source": "P-0101", "target": "PRV-012", "relationship_type": "referred_to", "weight": 5},
        {"source": "P-0102", "target": "PRV-012", "relationship_type": "referred_to", "weight": 4},
        {"source": "P-0104", "target": "PRV-007", "relationship_type": "referred_to", "weight": 6},
        {"source": "P-0105", "target": "PRV-007", "relationship_type": "referred_to", "weight": 5},
        
        # Ring 2 edges (upcoding - all providers see same patients)
        {"source": "PRV-023", "target": "P-0150", "relationship_type": "treated", "weight": 18},
        {"source": "PRV-023", "target": "P-0151", "relationship_type": "treated", "weight": 15},
        {"source": "PRV-024", "target": "P-0150", "relationship_type": "treated", "weight": 16},
        {"source": "PRV-024", "target": "P-0152", "relationship_type": "treated", "weight": 14},
        {"source": "PRV-025", "target": "P-0151", "relationship_type": "treated", "weight": 12},
        {"source": "PRV-025", "target": "P-0153", "relationship_type": "treated", "weight": 13},
        {"source": "PRV-023", "target": "PRV-024", "relationship_type": "referred_from", "weight": 28},
        {"source": "PRV-024", "target": "PRV-025", "relationship_type": "referred_from", "weight": 24},
        {"source": "PRV-025", "target": "PRV-023", "relationship_type": "referred_from", "weight": 21},
        
        # Ring 3 edges (phantom billing - high volume, same patients)
        {"source": "PRV-035", "target": "P-0180", "relationship_type": "treated", "weight": 45},
        {"source": "PRV-035", "target": "P-0181", "relationship_type": "treated", "weight": 42},
        {"source": "PRV-036", "target": "P-0182", "relationship_type": "treated", "weight": 38},
        {"source": "PRV-036", "target": "P-0183", "relationship_type": "treated", "weight": 41},
        {"source": "PRV-035", "target": "PRV-036", "relationship_type": "referred_from", "weight": 67},
    ]
    
    findings = [
        # Ring 1 findings
        {
            "finding_type": "circular_referral",
            "description": "Bidirectional referral pattern detected between PRV-007 (Dr. X) and PRV-012 (Dr. Y) with 42 total cross-referrals",
            "severity": "HIGH",
            "fraud_ring": "ring_1",
        },
        {
            "finding_type": "volume_anomaly",
            "description": "PRV-007 shows 3.2x higher than average referral volume to PRV-012",
            "severity": "MEDIUM",
            "fraud_ring": "ring_1",
        },
        {
            "finding_type": "billing_pattern",
            "description": "Both providers bill for similar high-cost cardiac procedures on shared patients within 7-day windows",
            "severity": "HIGH",
            "fraud_ring": "ring_1",
        },
        # Ring 2 findings
        {
            "finding_type": "upcoding_pattern",
            "description": "PRV-023, PRV-024, PRV-025 consistently bill complex procedures (27447, 27130) for routine complaints",
            "severity": "HIGH",
            "fraud_ring": "ring_2",
        },
        {
            "finding_type": "shared_patient_pool",
            "description": "5 patients account for 73% of high-value claims across all 3 providers",
            "severity": "MEDIUM",
            "fraud_ring": "ring_2",
        },
        # Ring 3 findings
        {
            "finding_type": "phantom_billing",
            "description": "PRV-035 and PRV-036 bill 4x industry average volume with minimal documentation",
            "severity": "CRITICAL",
            "fraud_ring": "ring_3",
        },
        {
            "finding_type": "impossible_schedule",
            "description": "PRV-035 billed for 45 patient visits in single day on 12 occasions",
            "severity": "CRITICAL",
            "fraud_ring": "ring_3",
        },
    ]
    
    return {
        "nodes": all_nodes,
        "edges": edges,
        "findings": findings,
        "fraud_rings": FRAUD_RINGS,
    }


def generate_golden_path_responses() -> dict:
    """Generate pre-computed responses for the 3 demo scenarios."""
    golden_paths = {
        "silo_breaker": {
            "trigger": "Why was Claim #1023 denied?",
            "claim": {
                "claim_id": "CLM-01023",
                "patient_name": "John Smith",
                "provider_name": "Dr. X",
                "claim_status": "Denied",
                "denial_reason": "Not medically necessary",
                "diagnosis": "ST elevation myocardial infarction",
                "procedure": "Cardiac catheterization",
                "amount": 8500.00,
            },
            "clinical_note": {
                "note_id": "CN-001",
                "content_highlight": "This is a life-threatening cardiac emergency. ECG shows ST-elevation in leads V1-V4, consistent with anterior STEMI.",
                "contradiction": "The denial states 'Not medically necessary', but the clinical note clearly documents a STEMI (heart attack) requiring immediate cardiac catheterization. This is a critical, life-saving intervention.",
            },
            "response": "I found a significant discrepancy in Claim #1023. The claim was denied for 'Not medically necessary', but the clinical documentation from CN-001 clearly shows this was an **acute ST-elevation myocardial infarction (STEMI)** - a life-threatening heart attack requiring immediate intervention. The clinical note explicitly states this was a 'life-threatening cardiac emergency' with door-to-balloon time being critical. This denial may warrant immediate review.",
            "ui_hint": "MODE_DOC",
        },
        "fraud_hunter": {
            "trigger": "Analyze Dr. X for fraud",
            "response": "I've analyzed Dr. X (PRV-007) and discovered a concerning pattern. There's a **circular referral network** between Dr. X and Dr. Y (PRV-012), both Cardiology specialists. Key findings:\n\n1. **42 bidirectional referrals** between the two providers\n2. **6 shared patients** with unusual visit patterns\n3. Both bill for similar high-cost cardiac procedures on the same patients within 7-day windows\n4. Dr. X shows 3.2x higher than average referral volume to Dr. Y\n\nThis pattern is consistent with a potential kickback arrangement. Recommend further investigation.",
            "ui_hint": "MODE_GRAPH",
        },
        "trend_analyst": {
            "trigger": "Show denial trends by specialty",
            "data": [
                {"specialty": "Cardiology", "denial_rate": 0.34, "benchmark": 0.25},
                {"specialty": "Oncology", "denial_rate": 0.28, "benchmark": 0.25},
                {"specialty": "Orthopedics", "denial_rate": 0.31, "benchmark": 0.25},
                {"specialty": "Neurology", "denial_rate": 0.22, "benchmark": 0.25},
                {"specialty": "Emergency Medicine", "denial_rate": 0.18, "benchmark": 0.25},
                {"specialty": "Primary Care", "denial_rate": 0.15, "benchmark": 0.25},
                {"specialty": "Dermatology", "denial_rate": 0.12, "benchmark": 0.25},
                {"specialty": "Gastroenterology", "denial_rate": 0.26, "benchmark": 0.25},
            ],
            "insights": [
                "Cardiology has the highest denial rate at 34%, significantly above the 25% benchmark",
                "Emergency Medicine and Primary Care perform better than benchmark",
                "Three specialties (Cardiology, Orthopedics, Oncology) exceed the industry benchmark",
            ],
            "response": "Here's the denial rate analysis by specialty. **Cardiology leads with a 34% denial rate**, which is 9 percentage points above the 25% industry benchmark. This could indicate issues with prior authorization processes or documentation practices in cardiology. In contrast, Primary Care and Emergency Medicine show the healthiest denial rates at 15% and 18% respectively.",
            "ui_hint": "MODE_CHART",
        },
    }
    return golden_paths


def save_golden_path_files(golden_path_dir: Path) -> None:
    """Save golden path response files."""
    golden_path_dir.mkdir(parents=True, exist_ok=True)

    golden_paths = generate_golden_path_responses()

    # Save silo_breaker.json
    with open(golden_path_dir / "silo_breaker.json", "w", encoding="utf-8") as f:
        json.dump(golden_paths["silo_breaker"], f, indent=2)

    # Save fraud_hunter.json with the full fraud ring data
    fraud_data = generate_fraud_ring_data()
    fraud_data["trigger"] = golden_paths["fraud_hunter"]["trigger"]
    fraud_data["response"] = golden_paths["fraud_hunter"]["response"]
    fraud_data["ui_hint"] = golden_paths["fraud_hunter"]["ui_hint"]
    with open(golden_path_dir / "fraud_hunter.json", "w", encoding="utf-8") as f:
        json.dump(fraud_data, f, indent=2)

    # Save trend_analyst.json
    with open(golden_path_dir / "trend_analyst.json", "w", encoding="utf-8") as f:
        json.dump(golden_paths["trend_analyst"], f, indent=2)

    print(f"Generated 3 Golden Path responses → {golden_path_dir}")


def main():
    """Main data generation function."""
    print("=" * 60)
    print("ClaimsIQ Nexus - Enhanced Data Generation")
    print("=" * 60)

    # Generate base data with enhanced counts
    print("\n[1/6] Generating providers (75 with 3 fraud rings)...")
    providers = generate_providers(75)

    print("[2/6] Generating patients (400 with chronic cohorts)...")
    patients = generate_patients(400)

    print("[3/6] Generating claims (2500 with temporal patterns)...")
    claims = generate_claims(providers, patients, 2500)

    print("[4/6] Generating clinical notes (100 with 10 golden nuggets)...")
    notes = generate_clinical_notes(claims, patients, 100)

    print("[5/6] Cleaning up old clinical notes...")
    # Remove old clinical notes before saving new ones
    if CLINICAL_NOTES_DIR.exists():
        for old_note in CLINICAL_NOTES_DIR.glob("*.md"):
            old_note.unlink()

    print("[6/6] Saving generated data...")

    # Save data
    save_claims_csv(claims, GENERATED_DIR / "claims.csv")
    save_clinical_notes(notes, CLINICAL_NOTES_DIR)
    save_golden_path_files(GOLDEN_PATH_DIR)

    # Summary
    print("\n" + "=" * 60)
    print("Data Generation Complete!")
    print("=" * 60)

    # Count fraud ring members
    fraud_providers = sum(1 for p in providers if p.get("is_fraud_ring_member"))
    fraud_patients = sum(1 for p in patients if p.get("is_fraud_ring_member"))
    chronic_patients = sum(1 for p in patients if p.get("chronic_cohort"))
    golden_nuggets = sum(1 for n in notes if n["is_golden_nugget"])
    linked_notes = sum(1 for n in notes if n.get("claim_id"))
    denied_claims = sum(1 for c in claims if c["claim_status"] == "DENIED")

    print(f"\nGenerated:")
    print(f"  - {len(claims)} claims -> data/generated/claims.csv")
    print(f"    - {denied_claims} denied claims ({denied_claims/len(claims)*100:.1f}%)")
    print(f"  - {len(notes)} clinical notes -> data/generated/clinical_notes/")
    print(f"    - {linked_notes} linked to claims")
    print(f"    - {golden_nuggets} Golden Nuggets (contradiction evidence)")
    print(f"  - {len(providers)} providers")
    print(f"    - {fraud_providers} fraud ring members (3 rings)")
    print(f"  - {len(patients)} patients")
    print(f"    - {fraud_patients} fraud ring members")
    print(f"    - {chronic_patients} in chronic condition cohorts")
    print(f"  - 3 Golden Path scenarios -> data/golden_path/")
    
    print("\nFraud Rings:")
    for ring_id, ring_data in FRAUD_RINGS.items():
        print(f"  - {ring_data['name']}: {ring_data['pattern']} ({len(ring_data['providers'])} providers, {len(ring_data['patients'])} patients)")
    
    print("\nGolden Nuggets (denial contradictions):")
    for note in notes:
        if note["is_golden_nugget"]:
            print(f"  - {note['note_id']}: Patient {note['patient_id']} -> {note['claim_id']}")


if __name__ == "__main__":
    main()
