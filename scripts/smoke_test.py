#!/usr/bin/env python3
"""Smoke test script for ClaimsIQ Nexus.

Verifies that all 3 Golden Path scenarios execute without error
and return expected results.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_golden_path_files_exist():
    """Verify all golden path JSON files exist."""
    print("🔍 Testing Golden Path files exist...")
    
    golden_path_dir = project_root / "data" / "golden_path"
    required_files = [
        "silo_breaker.json",
        "fraud_hunter.json",
        "trend_analyst.json",
    ]
    
    missing = []
    for file in required_files:
        if not (golden_path_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"  ❌ Missing files: {missing}")
        return False
    
    print("  ✅ All golden path files exist")
    return True


def test_golden_path_loading():
    """Verify golden path files can be loaded and parsed."""
    print("🔍 Testing Golden Path loading...")
    
    try:
        from src.agent.fallback import load_golden_path
        
        scenarios = ["silo_breaker", "fraud_hunter", "trend_analyst"]
        for scenario in scenarios:
            data = load_golden_path(scenario)
            if not data:
                print(f"  ❌ Failed to load {scenario}")
                return False
            if "response" not in data:
                print(f"  ❌ Missing 'response' in {scenario}")
                return False
            print(f"  ✅ {scenario} loaded successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Error loading golden paths: {e}")
        return False


def test_golden_path_matching():
    """Verify golden path query matching works correctly."""
    print("🔍 Testing Golden Path matching...")
    
    try:
        from src.agent.fallback import match_golden_path_query
        
        test_cases = [
            ("Why was Claim #1023 denied?", "silo_breaker"),
            ("Why was claim 1023 denied", "silo_breaker"),
            ("Analyze Dr. X for fraud", "fraud_hunter"),
            ("Investigate Dr X", "fraud_hunter"),
            ("Show denial trends by specialty", "trend_analyst"),
            ("What are the denial rates?", "trend_analyst"),
            ("Hello, how are you?", None),
        ]
        
        for query, expected in test_cases:
            result = match_golden_path_query(query)
            if result != expected:
                print(f"  ❌ Query '{query}' returned '{result}', expected '{expected}'")
                return False
            status = "✅" if expected else "⚪"
            print(f"  {status} '{query[:30]}...' → {result or 'None'}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error in golden path matching: {e}")
        return False


def test_model_imports():
    """Verify all models can be imported."""
    print("🔍 Testing model imports...")
    
    try:
        from src.models import (
            Claim, ClaimStatus, DenialReason, ProviderSpecialty,
            Provider, Patient,
            ClinicalNote, NoteType,
            CanvasMode, CanvasState,
            ReasoningTrace, TraceStep,
        )
        print("  ✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Error importing models: {e}")
        return False


def test_service_imports():
    """Verify all services can be imported."""
    print("🔍 Testing service imports...")
    
    try:
        from src.services import (
            load_claims, filter_claims, get_claim_by_id,
            init_chromadb, search_notes,
            load_fraud_graph, get_provider_network,
        )
        print("  ✅ All services imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Error importing services: {e}")
        return False


def test_tool_imports():
    """Verify all tools can be imported."""
    print("🔍 Testing tool imports...")
    
    try:
        from src.tools import (
            query_claims_db,
            search_clinical_notes,
            analyze_network_graph,
            analyze_trends,
        )
        print("  ✅ All tools imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Error importing tools: {e}")
        return False


def test_ui_imports():
    """Verify UI components can be imported."""
    print("🔍 Testing UI imports...")
    
    try:
        from src.ui.styles import get_dark_mode_css, get_canvas_css
        from src.ui.chat_panel import (
            initialize_chat_state,
            render_chat_history,
            render_chat_input,
        )
        from src.ui.canvas_renderer import (
            initialize_canvas_state,
            render_canvas,
            update_canvas_state,
        )
        from src.ui.components import (
            render_claim,
            render_doc,
            render_chart,
            render_graph,
        )
        print("  ✅ All UI components imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Error importing UI components: {e}")
        return False


def test_config():
    """Verify configuration is valid."""
    print("🔍 Testing configuration...")
    
    try:
        from src.config import (
            OPENAI_API_KEY,
            OPENAI_MODEL,
            OPENAI_EMBEDDING_MODEL,
        )
        
        if not OPENAI_API_KEY:
            print("  ⚠️  OPENAI_API_KEY not set (required for live testing)")
        else:
            print("  ✅ OPENAI_API_KEY is set")
        
        print(f"  ✅ OPENAI_MODEL: {OPENAI_MODEL}")
        print(f"  ✅ OPENAI_EMBEDDING_MODEL: {OPENAI_EMBEDDING_MODEL}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error checking config: {e}")
        return False


def test_data_generation_script():
    """Verify data generation script exists and is valid Python."""
    print("🔍 Testing data generation script...")
    
    script_path = project_root / "scripts" / "generate_data.py"
    if not script_path.exists():
        print("  ❌ generate_data.py not found")
        return False
    
    try:
        import ast
        with open(script_path) as f:
            ast.parse(f.read())
        print("  ✅ generate_data.py is valid Python")
        return True
    except SyntaxError as e:
        print(f"  ❌ Syntax error in generate_data.py: {e}")
        return False


def run_all_tests():
    """Run all smoke tests and report results."""
    print("\n" + "=" * 60)
    print(" ClaimsIQ Nexus - Smoke Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_model_imports,
        test_service_imports,
        test_tool_imports,
        test_ui_imports,
        test_config,
        test_golden_path_files_exist,
        test_golden_path_loading,
        test_golden_path_matching,
        test_data_generation_script,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"  ❌ Unexpected error in {test.__name__}: {e}")
            results.append((test.__name__, False))
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Total: {passed} passed, {failed} failed")
    print()
    
    if failed > 0:
        print("❌ Some tests failed! Please fix before demo.")
        return 1
    else:
        print("✅ All smoke tests passed! Ready for demo.")
        return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
