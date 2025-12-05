<p align="center">
  <img src="https://img.shields.io/badge/ClaimsIQ-Nexus-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTEyIDIyYzUuNTIzIDAgMTAtNC40NzcgMTAtMTBTMTcuNTIzIDIgMTIgMiAyIDYuNDc3IDIgMTJzNC40NzcgMTAgMTAgMTB6Ii8+PHBhdGggZD0ibTkgMTIgMiAyIDQtNCIvPjwvc3ZnPg==&logoColor=white" alt="ClaimsIQ Nexus"/>
</p>

<h1 align="center">🔍 ClaimsIQ Nexus</h1>

<h3 align="center"><em>Breaking the Silo Between Claims and Care</em></h3>

<p align="center">
  <strong>An Agentic Payer Intelligence Platform for Healthcare Claims Investigation</strong>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick%20Start-blue?style=flat-square" alt="Quick Start"/></a>
  <a href="#-features"><img src="https://img.shields.io/badge/Features-green?style=flat-square" alt="Features"/></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Architecture-purple?style=flat-square" alt="Architecture"/></a>
  <a href="#-demo-scenarios"><img src="https://img.shields.io/badge/Demo-orange?style=flat-square" alt="Demo"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/LangGraph-1.0+-green?style=flat-square" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/Streamlit-1.52+-red?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/ChromaDB-1.3+-yellow?style=flat-square" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square" alt="License"/>
</p>

---

## 📋 Table of Contents

- [Executive Summary](#-executive-summary)
- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
  - [High-Level System Architecture](#high-level-system-architecture)
  - [LangGraph Agent Flow](#langgraph-agent-flow)
  - [RAG Pipeline](#rag-pipeline)
  - [ETL Pipeline](#etl-pipeline)
  - [Canvas State Machine](#canvas-state-machine)
- [Tech Stack](#-tech-stack)
- [Data Model](#-data-model)
  - [Claims Schema](#claims-schema-structured-silo)
  - [Clinical Notes Schema](#clinical-notes-schema-unstructured-silo)
  - [Fraud Ring Configuration](#fraud-ring-configuration)
- [MCP Tool API Reference](#-mcp-tool-api-reference)
- [Demo Scenarios](#-demo-scenarios)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Fallback Architecture](#-fallback-architecture)
- [Testing](#-testing)
- [Hackathon Context](#-hackathon-context)
- [Author](#-author)
- [License](#-license)

---

## 🎯 Executive Summary

**ClaimsIQ Nexus** is not just a chatbot—it's a **Cognitive Workspace** for healthcare payer operations. Built for the **Abacus Insights Hackathon**, it demonstrates enterprise-grade AI engineering by combining:

- 🔗 **Data Silo Unification**: Correlates structured claims data with unstructured clinical notes
- 🕸️ **Graph-Based Fraud Detection**: Visualizes provider-patient collusion networks
- 🤖 **Agentic Workflows**: LangGraph ReAct agent with self-healing capabilities
- 🎨 **Investigator's Canvas**: Split-screen UI where AI drives dynamic visualizations

> _"We didn't build a chatbot. We built a Cognitive Workspace for Abacus."_

---

## 🚨 Problem Statement

### The Challenge

Healthcare payers lose **billions annually** due to disconnected data systems. Claims are denied or approved without visibility into clinical documentation, while fraud patterns hide across siloed databases that never communicate.

### The Pain Points

| Problem                  | Impact                                                                   |
| ------------------------ | ------------------------------------------------------------------------ |
| **Data Silos**           | Claims (structured) and Clinical Notes (unstructured) exist in isolation |
| **Wrongful Denials**     | 50% of initial denials are eventually overturned on appeal               |
| **Hidden Fraud**         | $300B+ in annual healthcare fraud in the US alone                        |
| **Manual Investigation** | Analysts spend 80% of time gathering data, not investigating             |

### Why This Matters

- **Denied claims that should be paid** damage patient outcomes and create costly appeals
- **Fraud rings operate** across provider networks invisible to single-silo analysis
- **Payer analysts need** a cognitive workspace, not another dashboard

---

## 💡 Solution Overview

ClaimsIQ Nexus **breaks the silo between Claims and Care** by providing:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 ClaimsIQ Nexus Value Prop                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   STRUCTURED DATA          +           UNSTRUCTURED DATA            │
│   (Claims CSV)                         (Clinical Notes)             │
│                                                                      │
│   "Claim Denied:                       "Patient presented with      │
│    Not Medically                        life-threatening STEMI      │
│    Necessary"                           requiring immediate         │
│                                         intervention"               │
│                                                                      │
│                        ═══════════════                               │
│                              ▼                                       │
│                    🔍 AI AGENT FINDS                                │
│                      CONTRADICTION                                  │
│                              ▼                                       │
│                  ⚠️ FLAGS FOR REVIEW                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The "Platform" Difference

| Feature             | Standard Hackathon Bot | ClaimsIQ Nexus                  |
| ------------------- | ---------------------- | ------------------------------- |
| **Interface**       | Simple Chat Window     | **Split-Screen Command Center** |
| **Data Source**     | CSV only (Structured)  | **Structured + Unstructured**   |
| **Architecture**    | Basic Function Calls   | **MCP-Ready Tool Server**       |
| **Fraud Detection** | Simple Rules           | **Graph-Based Ring Detection**  |
| **Reliability**     | Fails on bad queries   | **Self-Correcting Agent**       |

---

## ✨ Key Features

### 1. 🔀 Hybrid Data Fusion

Correlates **structured claims data** (CSV) with **unstructured clinical notes** (Markdown) to find truths that neither dataset shows alone.

### 2. 🕸️ Graph-Based Fraud Detection

Uses **NetworkX** to detect circular referral patterns, unusual billing, and provider collusion networks with interactive **Plotly visualizations**.

### 3. 🤖 LangGraph ReAct Agent

Intelligent agent that **reasons, plans, and investigates** using four specialized MCP-style tools with self-correction capabilities.

### 4. 🎨 Investigator's Canvas

**Split-screen UI** (40% Chat / 60% Canvas) where the AI agent dynamically renders evidence:

- Claim details cards
- Clinical note viewer with highlighting
- Interactive network graphs
- Plotly analytics charts

### 5. 📊 Trend Analytics

Computes denial rates, claim volumes, and amounts **grouped by specialty, provider, time, or denial reason** with benchmark comparisons.

### 6. 🛡️ Production-Grade Reliability

**5-tier fallback architecture** ensures the demo never fails:

- Golden Path cache for demo scenarios
- Graceful degradation chains
- UI resilience wrappers

---

## 🏗️ Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       🖥️ PRESENTATION LAYER (Streamlit)                     │
│  ┌──────────────────────────┐  │  ┌──────────────────────────────────────┐  │
│  │    💬 Investigator       │  │  │       🎨 The Evidence Canvas         │  │
│  │        Chat Panel        │  │  │      (Dynamic Renderer)              │  │
│  │                          │  │  │                                      │  │
│  │ • Message history        │  │  │  [ 🕸️ Network Graph ]                │  │
│  │ • Reasoning trace        │  │  │  [ 📄 Clinical Note Viewer ]         │  │
│  │ • Chat input             │  │  │  [ 📊 Plotly Analytics ]             │  │
│  │                          │  │  │  [ 🏥 Claim Detail Card ]            │  │
│  └──────────────────────────┘  │  └──────────────────────────────────────┘  │
│            40%                 │                   60%                      │
├────────────────────────────────┴────────────────────────────────────────────┤
│                       🤖 AGENT LAYER (LangGraph)                            │
│                                                                              │
│    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│    │ System  │───▶│  Route  │───▶│  Plan   │───▶│ Execute │───▶│ Respond │  │
│    │ Prompt  │    │ Intent  │    │Strategy │    │  Tools  │    │  User   │  │
│    └─────────┘    └─────────┘    └─────────┘    └────┬────┘    └─────────┘  │
│                                                      │                       │
│                                        ┌─────────────┴─────────────┐        │
│                                        │    Self-Correction Loop   │        │
│                                        │  (Retry on Error/Empty)   │        │
│                                        └───────────────────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                       🔌 MCP TOOL SERVER LAYER                              │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐    │
│  │ 🔍 query_     │ │ 🩺 search_    │ │ 🕸️ analyze_   │ │ 📊 analyze_   │    │
│  │  claims_db    │ │ clinical_     │ │  network_     │ │    trends     │    │
│  │              │ │   notes       │ │    graph      │ │               │    │
│  │ (Structured) │ │(Unstructured) │ │  (NetworkX)   │ │   (Pandas)    │    │
│  └───────┬──────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘    │
│          │                │                 │                 │             │
├──────────┴────────────────┴─────────────────┴─────────────────┴─────────────┤
│                       💾 DATA LAYER                                         │
│                                                                              │
│  ┌────────────────┐   ┌────────────────────┐   ┌────────────────────────┐   │
│  │   Claims DB    │   │   Clinical Notes   │   │    Fraud Graph Data    │   │
│  │   (Pandas)     │   │     (ChromaDB)     │   │      (NetworkX)        │   │
│  │                │   │                    │   │                        │   │
│  │ • 2,500 claims │   │ • 100 notes        │   │ • 3 fraud rings        │   │
│  │ • 20 fields    │   │ • OpenAI embed     │   │ • Pre-computed graphs  │   │
│  │ • CSV storage  │   │ • Vector search    │   │ • JSON storage         │   │
│  └────────────────┘   └────────────────────┘   └────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### LangGraph Agent Flow

```
                              ┌─────────────────┐
                              │   User Query    │
                              └────────┬────────┘
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │  Golden Path Matcher    │
                         │  (Demo Scenario Check)  │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
           ┌───────────────┐                  ┌───────────────┐
           │ Cached Demo   │                  │ Live Agent    │
           │   Response    │                  │  Invocation   │
           └───────────────┘                  └───────┬───────┘
                                                      │
                                                      ▼
                                        ┌─────────────────────────┐
                                        │     System Prompt       │
                                        │  + Investigation Rules  │
                                        └────────────┬────────────┘
                                                     │
                                                     ▼
                         ┌───────────────────────────────────────────┐
                         │              ReAct Loop                   │
                         │  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
                         │  │ Thought │─▶│  Action │─▶│Observe  │   │
                         │  └─────────┘  └────┬────┘  └────┬────┘   │
                         │                    │            │        │
                         │                    ▼            │        │
                         │        ┌─────────────────┐     │        │
                         │        │   Tool Call     │     │        │
                         │        │ • query_claims  │◀────┘        │
                         │        │ • search_notes  │              │
                         │        │ • analyze_graph │              │
                         │        │ • analyze_trend │              │
                         │        └────────┬────────┘              │
                         │                 │                        │
                         │                 ▼                        │
                         │        ┌─────────────────┐              │
                         │        │  Tool Result +  │              │
                         │        │    UI_HINT      │──────────────┘
                         │        └─────────────────┘
                         └───────────────────────────────────────────┘
                                                     │
                                                     ▼
                                        ┌─────────────────────────┐
                                        │   Canvas State Update   │
                                        │  (MODE_CLAIM/DOC/GRAPH/ │
                                        │        CHART/EMPTY)     │
                                        └────────────┬────────────┘
                                                     │
                                                     ▼
                                        ┌─────────────────────────┐
                                        │   Response + Trace +    │
                                        │    Canvas Rendering     │
                                        └─────────────────────────┘
```

### RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        📚 RAG PIPELINE (Clinical Notes)                     │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────┐
                    │        INDEXING PHASE (Offline)         │
                    └─────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   Clinical   │     │   Parse      │     │   Extract    │
    │    Notes     │────▶│  Frontmatter │────▶│   Metadata   │
    │ (100 .md)    │     │   (YAML)     │     │              │
    └──────────────┘     └──────────────┘     └──────┬───────┘
                                                      │
                                                      ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   OpenAI     │     │    Store     │     │   Remove     │
    │  Embeddings  │◀────│   Vectors    │◀────│ Frontmatter  │
    │ (3-small)    │     │  (ChromaDB)  │     │   Content    │
    └──────────────┘     └──────────────┘     └──────────────┘


                    ┌─────────────────────────────────────────┐
                    │        RETRIEVAL PHASE (Runtime)        │
                    └─────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │    User      │     │   Embed      │     │   Vector     │
    │    Query     │────▶│   Query      │────▶│   Search     │
    │              │     │  (OpenAI)    │     │  (ChromaDB)  │
    └──────────────┘     └──────────────┘     └──────┬───────┘
                                                      │
                                                      ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   Return     │     │   Filter by  │     │   Rank by    │
    │   Results    │◀────│  Threshold   │◀────│  Similarity  │
    │  + UI_HINT   │     │   (0.75)     │     │   Score      │
    └──────────────┘     └──────────────┘     └──────────────┘


                    ┌─────────────────────────────────────────┐
                    │          METADATA STRUCTURE             │
                    └─────────────────────────────────────────┘

                    ┌────────────────────────────────┐
                    │  note_id: CN-001               │
                    │  patient_id: P-0456            │
                    │  claim_id: CLM-01023           │  ◀── Links to Claims!
                    │  note_date: 2024-06-15         │
                    │  note_type: EmergencyNote      │
                    │  is_golden_nugget: true        │  ◀── Demo Evidence
                    └────────────────────────────────┘
```

### ETL Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🔄 ETL PIPELINE (Data Generation)                        │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────────┐
                         │    EXTRACT PHASE        │
                         │   (Configuration)       │
                         └───────────┬─────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Specialty      │       │   ICD-10 &      │       │   Fraud Ring    │
│  Definitions    │       │   CPT Codes     │       │   Configs       │
│                 │       │                 │       │                 │
│ • Cardiology    │       │ • I21.0 STEMI   │       │ • Ring 1: Dr.X/Y│
│ • Oncology      │       │ • E11.9 T2DM    │       │ • Ring 2: Alpha │
│ • Orthopedics   │       │ • 93458 Cath    │       │ • Ring 3: Phantom│
│ • Neurology     │       │ • 99285 ED Visit│       │                 │
│ • Emergency     │       │                 │       │                 │
│ • Primary Care  │       │                 │       │                 │
│ • Dermatology   │       │                 │       │                 │
│ • Gastro        │       │                 │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘


                         ┌─────────────────────────┐
                         │   TRANSFORM PHASE       │
                         │   (Generation)          │
                         └───────────┬─────────────┘
                                     │
    ┌────────────────────────────────┼────────────────────────────────┐
    │                                │                                │
    ▼                                ▼                                ▼
┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│   PROVIDERS     │       │      PATIENTS       │       │     CLAIMS      │
│   (75 records)  │       │    (400 records)    │       │  (2,500 records)│
│                 │       │                     │       │                 │
│ • provider_id   │       │ • patient_id        │       │ • claim_id      │
│ • name          │       │ • name              │       │ • patient_id    │
│ • specialty     │─────┐ │ • age               │       │ • provider_id   │
│ • fraud_ring    │     │ │ • chronic_cohort    │──┐    │ • diagnosis     │
│ • behavior      │     │ │ • fraud_ring        │  │    │ • procedure     │
│   profile       │     │ │                     │  │    │ • amount        │
└─────────────────┘     │ └─────────────────────┘  │    │ • status        │
                        │                          │    │ • denial_reason │
                        │                          │    └────────┬────────┘
                        └──────────────────────────┴─────────────┘


                         ┌─────────────────────────┐
                         │     LOAD PHASE          │
                         │   (Persistence)         │
                         └───────────┬─────────────┘
                                     │
    ┌────────────────────────────────┼────────────────────────────────┐
    │                                │                                │
    ▼                                ▼                                ▼
┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│   claims.csv    │       │  clinical_notes/    │       │  golden_path/   │
│                 │       │                     │       │                 │
│ 2,500 records   │       │ CN-001.md (Golden)  │       │ silo_breaker    │
│ 20 fields       │       │ CN-002.md           │       │   .json         │
│                 │       │ ...                 │       │ fraud_hunter    │
│ Injected:       │       │ CN-100.md           │       │   .json         │
│ • 50 duplicates │       │                     │       │ trend_analyst   │
│ • 30 outliers   │       │ Linked to claims    │       │   .json         │
│ • 20 mismatches │       │ via frontmatter     │       │                 │
│ • Fraud rings   │       │                     │       │ Pre-computed    │
└─────────────────┘       └─────────────────────┘       └─────────────────┘
```

### Canvas State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🎨 CANVAS STATE MACHINE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │ MODE_EMPTY  │◀──────────────────────┐
                              │             │                       │
                              │ "Ready to   │                       │
                              │ Investigate"│                       │
                              └──────┬──────┘                       │
                                     │                              │
                    ┌────────────────┼────────────────┐             │
                    │                │                │             │
            Tool: query_     Tool: search_    Tool: analyze_       │
             claims_db      clinical_notes    network_graph        │
                    │                │                │             │
                    ▼                ▼                ▼             │
           ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
           │ MODE_CLAIM  │  │  MODE_DOC   │  │ MODE_GRAPH  │       │
           │             │  │             │  │             │       │
           │ Single claim│  │ Clinical    │  │ Network     │       │
           │ detail card │  │ note viewer │  │ visualization│       │
           │             │  │             │  │             │       │
           │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │       │
           │ │ Patient │ │  │ │ Golden  │ │  │ │ Nodes   │ │       │
           │ │ Info    │ │  │ │ Nugget  │ │  │ │ (Red=   │ │       │
           │ │ Provider│ │  │ │ Badge   │ │  │ │ Flagged)│ │       │
           │ │ Amount  │ │  │ │         │ │  │ │ Edges   │ │       │
           │ │ Status  │ │  │ │ Content │ │  │ │ Findings│ │       │
           │ │ Denial  │ │  │ │ Metadata│ │  │ │         │ │       │
           │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │       │
           └─────────────┘  └─────────────┘  └─────────────┘       │
                    │                │                │             │
                    │                │                │             │
                    └────────────────┴────────────────┘             │
                                     │                              │
                         Tool: analyze_trends                       │
                                     │                              │
                                     ▼                              │
                            ┌─────────────┐                        │
                            │ MODE_CHART  │                        │
                            │             │                        │
                            │ Plotly bar  │                        │
                            │ chart with  │                        │
                            │ benchmarks  │                        │
                            │             │        No Results      │
                            │ • Denial %  │────────────────────────┘
                            │ • Amounts   │
                            │ • Volume    │
                            │ • Insights  │
                            └─────────────┘


                    ┌─────────────────────────────────────────┐
                    │         PRIORITY RESOLUTION             │
                    │                                         │
                    │   When multiple tools return results:   │
                    │                                         │
                    │   GRAPH (4) > CHART (3) > CLAIM (2)    │
                    │            > DOC (1) > EMPTY (0)        │
                    │                                         │
                    │   Higher priority mode wins             │
                    └─────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component           | Technology    | Version                | Purpose                         |
| ------------------- | ------------- | ---------------------- | ------------------------------- |
| **Language**        | Python        | 3.12+                  | Core runtime                    |
| **Agent Framework** | LangGraph     | ≥1.0.4                 | ReAct pattern, state management |
| **LLM Provider**    | OpenAI        | GPT-4o-mini            | Cost-effective, fast responses  |
| **Embeddings**      | OpenAI        | text-embedding-3-small | Vector embeddings for RAG       |
| **Vector Store**    | ChromaDB      | ≥1.3.5                 | Semantic search, local storage  |
| **UI Framework**    | Streamlit     | ≥1.52.0                | Split-screen interface          |
| **Data Processing** | Pandas        | ≥2.3.3                 | Claims queries, aggregations    |
| **Visualization**   | Plotly        | ≥6.5.0                 | Charts + network graphs         |
| **Graph Analysis**  | NetworkX      | ≥3.6                   | Fraud ring detection            |
| **Data Generation** | Faker         | ≥38.2.0                | Synthetic healthcare data       |
| **Type Safety**     | Pydantic      | ≥2.12.5                | Data models, validation         |
| **Config**          | python-dotenv | ≥1.2.1                 | Environment management          |
| **Retry Logic**     | Tenacity      | ≥9.1.2                 | Resilient API calls             |

---

## 📊 Data Model

### Claims Schema (Structured Silo)

The claims database contains **2,500 synthetic records** with **20 fields**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAIMS TABLE (claims.csv)                    │
├─────────────────────────────────────────────────────────────────┤
│  Field                  │ Type      │ Description              │
├─────────────────────────┼───────────┼──────────────────────────┤
│  claim_id               │ STRING    │ "CLM-00001" to "CLM-02500" │
│  patient_id             │ STRING    │ "P-0001" to "P-0400"     │
│  patient_name           │ STRING    │ Faker-generated name     │
│  patient_age            │ INTEGER   │ 18-90 years              │
│  patient_gender         │ STRING    │ Male/Female/Other        │
│  provider_id            │ STRING    │ "PRV-001" to "PRV-075"   │
│  provider_name          │ STRING    │ "Dr. [LastName]"         │
│  provider_specialty     │ STRING    │ 8 specialties            │
│  diagnosis_code         │ STRING    │ ICD-10 code              │
│  diagnosis_description  │ STRING    │ Condition name           │
│  procedure_code         │ STRING    │ CPT code                 │
│  procedure_description  │ STRING    │ Procedure name           │
│  claim_amount           │ DECIMAL   │ $50 - $50,000            │
│  approved_amount        │ DECIMAL   │ 70-100% of claim_amount  │
│  claim_status           │ STRING    │ Approved/Denied/Pending  │
│  denial_reason          │ STRING    │ 8 reason codes           │
│  claim_date             │ DATE      │ 2024-01-01 to 2025-12-01 │
│  processing_date        │ DATE      │ 1-14 days after claim    │
│  is_emergency           │ BOOLEAN   │ Emergency procedure flag │
│  is_inpatient           │ BOOLEAN   │ Inpatient stay flag      │
└─────────────────────────────────────────────────────────────────┘
```

#### Data Distribution

| Attribute          | Distribution                                                                                                                                                                 |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Status**         | Approved 60% / Denied 25% / Pending 15%                                                                                                                                      |
| **Specialties**    | Cardiology, Oncology, Orthopedics, Neurology, Emergency Medicine, Primary Care, Dermatology, Gastroenterology                                                                |
| **Denial Reasons** | Pre-auth not obtained, Out of network, Not medically necessary, Duplicate claim, Incomplete information, Experimental procedure, Benefit limit exceeded, Service not covered |
| **Amounts**        | Log-normal distribution ($50 - $50,000)                                                                                                                                      |

#### Injected Anomalies

| Anomaly Type          | Count | Description                             |
| --------------------- | ----- | --------------------------------------- |
| Duplicate Claims      | 50    | Same patient + date + provider + amount |
| Amount Outliers       | 30    | >5x standard deviation for procedure    |
| Specialty Mismatches  | 20    | Wrong specialty for procedure           |
| High Denial Providers | 5     | >80% denial rate                        |
| Fraud Ring Members    | 14    | 3 distinct fraud patterns               |

### Clinical Notes Schema (Unstructured Silo)

**100 Markdown files** with YAML frontmatter:

```yaml
---
note_id: CN-001
patient_id: P-0456
claim_id: CLM-01023        # Links to claims!
note_date: 2024-06-15T14:30:00
note_type: EmergencyNote   # EmergencyNote, ProcedureNote, FollowUp, etc.
is_golden_nugget: true     # Demo contradiction flag
---

# Emergency Department Note

**Patient:** John Smith (P-0456)
**Chief Complaint:** Severe chest pain

## Clinical Content...
```

#### Note Types

| Type             | Description                |
| ---------------- | -------------------------- |
| EmergencyNote    | ED visit documentation     |
| ProcedureNote    | Surgical/treatment records |
| ProgressNote     | Ongoing care updates       |
| DischargeSummary | Hospitalization summary    |
| ConsultNote      | Specialist consultation    |

### Fraud Ring Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRAUD RING CONFIGURATIONS                    │
└─────────────────────────────────────────────────────────────────┘

RING 1: "Cardiology Kickback Ring" (Circular Referral)
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│         ┌──────────┐                    ┌──────────┐            │
│         │  Dr. X   │◀──── Referrals ───▶│  Dr. Y   │            │
│         │ PRV-007  │                    │ PRV-012  │            │
│         │Cardiology│                    │Cardiology│            │
│         └────┬─────┘                    └────┬─────┘            │
│              │                               │                   │
│              │ Treats                        │ Treats            │
│              ▼                               ▼                   │
│    ┌─────────────────────────────────────────────────┐          │
│    │  P-0101  P-0102  P-0103  P-0104  P-0105  P-0106 │          │
│    │         (Shared Patient Pool - 6 patients)       │          │
│    └─────────────────────────────────────────────────┘          │
│                                                                  │
│    Pattern: Bidirectional referrals with high-cost procedures   │
└─────────────────────────────────────────────────────────────────┘

RING 2: "Upcoding Scheme" (Billing Fraud)
┌─────────────────────────────────────────────────────────────────┐
│    Dr. Alpha (PRV-023) ─┬─ Dr. Beta (PRV-024)                   │
│    Dr. Gamma (PRV-025) ─┘   (All Orthopedics)                   │
│                                                                  │
│    Patients: P-0150, P-0151, P-0152, P-0153, P-0154             │
│    Pattern: Complex procedures billed for routine visits         │
└─────────────────────────────────────────────────────────────────┘

RING 3: "Phantom Billing Network" (Services Not Rendered)
┌─────────────────────────────────────────────────────────────────┐
│    Dr. Shadow (PRV-035) ─── Dr. Ghost (PRV-036)                 │
│    (Primary Care)                                                │
│                                                                  │
│    Patients: P-0180, P-0181, P-0182, P-0183                     │
│    Pattern: Billing for services never rendered                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 MCP Tool API Reference

### 1. `query_claims_db`

Query the structured claims database with SQL-like filters.

```python
query_claims_db(
    filters: dict = None,      # Filter criteria
    sort_by: str = "claim_date",  # Sort field
    limit: int = 10            # Max results (1-100)
) -> dict
```

**Filter Options:**
| Filter | Type | Example |
|--------|------|---------|
| `claim_id` | string | "CLM-01023" |
| `patient_id` | string | "P-0456" |
| `provider_id` | string | "PRV-007" |
| `status` | string | "Denied" |
| `specialty` | string | "Cardiology" |
| `denial_reason` | string | "Not medically necessary" |
| `date_from` | string | "2024-01-01" |
| `date_to` | string | "2024-12-31" |

**Returns:**

```json
{
  "claims": [...],
  "total_count": 15,
  "ui_hint": "MODE_CLAIM",
  "query_type": "single_claim"
}
```

---

### 2. `search_clinical_notes`

Semantic search over unstructured clinical documentation.

```python
search_clinical_notes(
    query: str,                # Natural language query (3-500 chars)
    patient_id: str = None,    # Optional patient filter
    limit: int = 5             # Max results (1-20)
) -> dict
```

**Returns:**

```json
{
  "results": [
    {
      "note_id": "CN-001",
      "patient_id": "P-0456",
      "claim_id": "CLM-01023",
      "note_type": "EmergencyNote",
      "content_snippet": "...",
      "full_content": "...",
      "similarity_score": 0.92,
      "is_golden_nugget": true
    }
  ],
  "ui_hint": "MODE_DOC"
}
```

---

### 3. `analyze_network_graph`

Analyze provider-patient relationships for fraud detection.

```python
analyze_network_graph(
    entity_id: str,    # Provider/patient ID or alias ("Dr. X")
    depth: int = 2     # Relationship depth (1-3)
) -> dict
```

**Returns:**

```json
{
  "nodes": [
    {
      "id": "PRV-007",
      "type": "provider",
      "label": "Dr. X",
      "risk_score": 0.92,
      "is_fraud_ring_member": true
    }
  ],
  "edges": [
    {
      "source": "PRV-007",
      "target": "P-0101",
      "relationship_type": "treated_by",
      "weight": 5
    }
  ],
  "findings": [
    {
      "finding_type": "circular_referral",
      "description": "Bidirectional referral pattern detected",
      "severity": "HIGH"
    }
  ],
  "ui_hint": "MODE_GRAPH"
}
```

---

### 4. `analyze_trends`

Generate statistical analysis and visualizations.

```python
analyze_trends(
    metric: str,       # "denial_rate", "acceptance_rate", "claim_amount", "volume"
    group_by: str,     # "specialty", "provider", "month", "denial_reason"
    filters: dict = None
) -> dict
```

**Returns:**

```json
{
  "data": [
    {"category": "Cardiology", "value": 0.34, "benchmark": 0.25, "count": 450}
  ],
  "chart_config": {...},
  "insights": ["Cardiology has the highest denial rate at 34%"],
  "ui_hint": "MODE_CHART"
}
```

---

## 🎬 Demo Scenarios

### Scenario A: "The Silo Breaker"

**Trigger Queries:**

- "Why was Claim #1023 denied?"
- "Show me claim 1023"
- "What happened with CLM-01023?"

**What Happens:**

1. Agent queries claim details → Finds denial reason: "Not medically necessary"
2. Agent searches clinical notes → Finds CN-001 with matching patient
3. Agent discovers contradiction → Clinical note shows "life-threatening STEMI"
4. Canvas displays clinical note with golden nugget highlighting

**Expected Response:**

> I found a significant discrepancy in Claim #1023. The claim was denied for 'Not medically necessary', but the clinical documentation clearly shows this was an **acute ST-elevation myocardial infarction (STEMI)** - a life-threatening heart attack requiring immediate intervention. This denial may warrant immediate review.

---

### Scenario B: "The Fraud Hunter"

**Trigger Queries:**

- "Analyze Dr. X for fraud"
- "Investigate Dr X"
- "Show me PRV-007 network"

**What Happens:**

1. Agent invokes network graph analysis
2. Pre-baked fraud ring data loaded (Dr. X + Dr. Y + 6 patients)
3. Circular referral pattern detected
4. Canvas displays red "spiderweb" network graph

**Expected Response:**

> **Investigation: Dr. X (PRV-007)**
>
> **Findings:**
>
> 1. Circular referral pattern detected with Dr. Y (PRV-012)
> 2. Shared patient pool of 6 individuals
> 3. Volume 340% above peer average
>
> **Risk Score: HIGH**

---

### Scenario C: "The Trend Analyst"

**Trigger Queries:**

- "Show denial trends by specialty"
- "What are the denial rates?"

**What Happens:**

1. Agent invokes trend analysis tool
2. Calculates denial rates grouped by specialty
3. Compares against 25% benchmark
4. Canvas displays Plotly bar chart with benchmark line

**Expected Response:**

> **Denial Rate Analysis by Specialty**
>
> Top denial rates:
>
> 1. **Cardiology: 34%** (9% above benchmark)
> 2. Orthopedics: 31%
> 3. Oncology: 28%
>
> Primary Care and Emergency Medicine perform below benchmark.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key (or DeepSeek API key)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claimsiq-nexus.git
cd claimsiq-nexus

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Or with pyproject.toml:
pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env with your API key
# OPENAI_API_KEY=sk-your-key-here
```

### Generate Data (Optional - pre-generated data included)

```bash
python scripts/generate_data.py
```

### Run Smoke Test

```bash
python scripts/smoke_test.py
```

### Launch Application

```bash
streamlit run src/app.py
```

Open http://localhost:8501 in your browser.

---

## 📁 Project Structure

```
claimsiq-nexus/
├── README.md                       # This file
├── pyproject.toml                  # Project metadata & dependencies
├── requirements.txt                # Pip requirements
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
│
├── data/
│   ├── generated/
│   │   ├── claims.csv              # 2,500 synthetic claims
│   │   └── clinical_notes/         # 100 markdown files
│   │       ├── CN-001.md           # Golden nugget (links to CLM-01023)
│   │       ├── CN-002.md
│   │       └── ...
│   │
│   └── golden_path/                # Pre-computed demo responses
│       ├── silo_breaker.json       # Claim contradiction demo
│       ├── fraud_hunter.json       # Network graph + fraud ring
│       └── trend_analyst.json      # Denial trends chart
│
├── scripts/
│   ├── generate_data.py            # ETL pipeline for synthetic data
│   ├── index_clinical_notes.py     # ChromaDB indexing utility
│   └── smoke_test.py               # Pre-demo verification
│
├── src/
│   ├── __init__.py
│   ├── app.py                      # Streamlit entry point
│   ├── config.py                   # Environment configuration
│   │
│   ├── agent/                      # LangGraph agent
│   │   ├── __init__.py
│   │   ├── graph.py                # ReAct agent definition
│   │   ├── state.py                # Agent state management
│   │   ├── llm_provider.py         # OpenAI/DeepSeek factory
│   │   └── fallback.py             # Golden path + fallbacks
│   │
│   ├── models/                     # Pydantic data models
│   │   ├── __init__.py
│   │   ├── claim.py                # Claim, Provider, Patient
│   │   ├── clinical_note.py        # ClinicalNote, NoteType
│   │   ├── canvas_state.py         # CanvasMode, CanvasState
│   │   └── reasoning_trace.py      # TraceStep, ReasoningTrace
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── claims_service.py       # Pandas-based claims queries
│   │   ├── rag_service.py          # ChromaDB vector search
│   │   └── graph_service.py        # NetworkX fraud analysis
│   │
│   ├── tools/                      # MCP-style tool definitions
│   │   ├── __init__.py
│   │   ├── query_claims_db.py
│   │   ├── search_clinical_notes.py
│   │   ├── analyze_network_graph.py
│   │   └── analyze_trends.py
│   │
│   └── ui/                         # Streamlit components
│       ├── __init__.py
│       ├── chat_panel.py           # Left panel (40%)
│       ├── canvas_renderer.py      # Right panel (60%)
│       ├── styles.py               # Dark mode CSS
│       └── components/
│           ├── claim_card.py       # Claim detail view
│           ├── doc_viewer.py       # Clinical note viewer
│           ├── chart_view.py       # Plotly analytics
│           └── graph_view.py       # Network visualization
│
├── tests/                          # Test suite
│
└── plan/                           # Implementation documentation
    └── claimsiq-implementation-plan-v1.md
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM Provider Selection (openai or deepseek)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# DeepSeek Configuration (alternative provider)
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_MODEL=deepseek-chat

# Application Settings
APP_DEBUG=false
APP_LOG_LEVEL=INFO

# Performance Thresholds (milliseconds)
TIMEOUT_API=60000
TIMEOUT_VECTOR_SEARCH=5000
TIMEOUT_GRAPH_RENDER=5000

# Data Configuration
CLAIMS_COUNT=2500
CLINICAL_NOTES_COUNT=100
FRAUD_RING_ENABLED=true
GOLDEN_NUGGETS_COUNT=10
```

### Multi-LLM Provider Support

ClaimsIQ Nexus supports **OpenAI** and **DeepSeek** as LLM providers:

```bash
# Use OpenAI (default)
export LLM_PROVIDER=openai

# Use DeepSeek (cost-effective alternative)
export LLM_PROVIDER=deepseek
```

---

## 🛡️ Fallback Architecture

### Philosophy

> **"Fallbacks should look like INTENTIONAL DESIGN CHOICES, not failures."**

### 5-Tier Defense System

```
┌─────────────────────────────────────────────────────────────────┐
│                    FALLBACK ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: PREVENTION                                              │
│ ──────────────────                                              │
│ • Pre-flight smoke test (scripts/smoke_test.py)                │
│ • Verify API keys, data files, ChromaDB                        │
│ • Run 30 minutes before any demo                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: GOLDEN PATH CACHE                                       │
│ ─────────────────────────                                       │
│ • 3 pre-computed demo scenarios                                │
│ • Pattern matching on user queries                             │
│ • Instant responses with correct canvas state                  │
│                                                                  │
│   Triggers:                                                      │
│   • "claim 1023" → silo_breaker.json                           │
│   • "dr. x" → fraud_hunter.json                                │
│   • "denial trends by specialty" → trend_analyst.json          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: DEGRADATION CHAINS                                      │
│ ──────────────────────────                                      │
│                                                                  │
│ GRAPH:    Plotly Network → Table → Markdown List               │
│ CHART:    Plotly Chart → Table → Stats Text                    │
│ DOC:      Styled Markdown → Blockquote → Raw Text              │
│ CLAIM:    Claim Card → JSON Pretty → Raw Dict                  │
│ AGENT:    Full LangGraph → Simple Chain → Cached Response      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 4: UI RESILIENCE                                           │
│ ─────────────────────                                           │
│ • Every renderer wrapped in try/except                         │
│ • Safe fallback to simpler visualization                       │
│ • Never show raw Python errors to users                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 5: HONEST FAILURE PROTOCOL                                 │
│ ───────────────────────────────                                 │
│                                                                  │
│ DON'T: Pretend it's working, make excuses                      │
│                                                                  │
│ DO: "This is hitting an edge case. But watch: the system       │
│     gracefully falls back to [table view]. That's              │
│     production thinking."                                       │
│                                                                  │
│ WHY: Shows you anticipated failures (senior thinking)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Smoke Test

Run before any demo to verify system health:

```bash
python scripts/smoke_test.py
```

**Checks:**

- Golden path files exist
- Golden paths load correctly
- Query matching works
- All models import
- All services import
- All tools import
- UI components import
- Claims data loads
- ChromaDB initializes

### Pre-Demo Checklist

```
[ ] OpenAI API key is valid and has credits
[ ] .env file configured correctly
[ ] ChromaDB loads successfully
[ ] Golden Path 1 (Claim 1023) works
[ ] Golden Path 2 (Dr. X) works
[ ] Golden Path 3 (Trends) works
[ ] Graph rendering works
[ ] All Canvas modes render
[ ] No console errors
```

---

## 🏆 Hackathon Context

### About Abacus Insights

**Abacus Insights** is a mission-driven healthcare technology company focused on transforming the payer industry. They provide:

- **Data Transformation Platform**: Makes siloed healthcare data usable, accurate, complete, and timely
- **Key Solutions**: Risk Adjustment, CMS Interoperability, Clinical Data, Cost of Care Management
- **Core Technology**: Cloud-enabled data integration, AI and Agentic workflows, MCP/API services

### Hackathon Theme

This project implements **Theme #5: "ETL + RAG for Fraud Detection"** from the Abacus Insights Hackathon, elevated into a comprehensive Agentic Investigation Platform.

### Judging Criteria

| Criteria               | How ClaimsIQ Nexus Addresses It                                                          |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| **COMPLETENESS**       | Fully functional end-to-end system with data generation, RAG, agent, UI                  |
| **INNOVATION**         | Split-screen "Investigator's Canvas", data silo unification, graph-based fraud detection |
| **Technical Depth**    | LangGraph ReAct agent, ChromaDB RAG, NetworkX analysis, Plotly visualizations            |
| **Production Quality** | 5-tier fallback architecture, MCP-ready tools, modular code structure                    |

### Skills Demonstrated

- **RAG Systems**: ChromaDB vector search with OpenAI embeddings
- **Agentic Workflows**: LangGraph ReAct pattern with tool calling
- **MCP Concepts**: Tool server architecture with UI hints
- **SQL-like Queries**: Pandas-based structured data access
- **Healthcare Domain**: ICD-10, CPT codes, denial reasons, fraud patterns
- **Data Engineering**: ETL pipeline for synthetic data generation
- **Visualization**: Plotly charts and network graphs
- **Production Thinking**: Fallbacks, error handling, graceful degradation

---

## 👤 Author

**Krish Koria**

Built for the Abacus Insights Hackathon

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>ClaimsIQ Nexus</strong><br/>
  <em>Breaking the Silo Between Claims and Care</em>
</p>
