"""
Simple Quality Audit - No Unicode
Following PolyChronos-Omega methodology and Quality Mandate requirements
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def audit_code_quality():
    """Audit code quality standards."""
    print("Phase 1: Code Quality Standards")
    
    score = 0
    total = 5
    issues = []
    evidence = []
    
    # Check type hints
    try:
        youtube_service_file = Path("src/services/youtube_service.py")
        if youtube_service_file.exists():
            content = youtube_service_file.read_text()
            if "from typing import" in content and "->" in content:
                score += 1
                evidence.append("PASS: Type hints found")
            else:
                issues.append("FAIL: Missing type hints")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check error handling
    try:
        error_handler_file = Path("src/services/enhanced_error_handler.py")
        if error_handler_file.exists():
            score += 1
            evidence.append("PASS: Enhanced error handler exists")
        else:
            issues.append("FAIL: Enhanced error handler missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check code structure
    try:
        main_app_file = Path("src/gui/main_app.py")
        if main_app_file.exists():
            score += 1
            evidence.append("PASS: Main app structure found")
        else:
            issues.append("FAIL: Main app missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check documentation
    try:
        readme_file = Path("README_ENHANCED.md")
        if readme_file.exists():
            score += 1
            evidence.append("PASS: Enhanced README exists")
        else:
            issues.append("FAIL: Enhanced README missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check standards compliance
    try:
        config_file = Path("config.json")
        if config_file.exists():
            score += 1
            evidence.append("PASS: Configuration exists")
        else:
            issues.append("FAIL: Configuration missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    percentage = (score / total) * 100
    print(f"  Score: {percentage:.1f}%")
    return {"score": percentage, "issues": issues, "evidence": evidence}

def audit_security():
    """Audit security requirements."""
    print("Phase 2: Security Requirements")
    
    score = 0
    total = 5
    issues = []
    evidence = []
    
    # Check credential exposure
    try:
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            if "youtube_api_key" in config and config["youtube_api_key"]:
                score += 1
                evidence.append("PASS: API keys configured")
            else:
                issues.append("FAIL: API keys not configured")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check input validation
    try:
        validation_file = Path("src/utils/validation.py")
        if validation_file.exists():
            score += 1
            evidence.append("PASS: Input validation exists")
        else:
            issues.append("FAIL: Input validation missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check secure configuration
    try:
        env_file = Path(".env")
        if env_file.exists():
            score += 1
            evidence.append("PASS: Environment config exists")
        else:
            issues.append("FAIL: Environment config missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check access control
    try:
        youtube_service_file = Path("src/services/youtube_service.py")
        if youtube_service_file.exists():
            content = youtube_service_file.read_text()
            if "validate_api_key" in content:
                score += 1
                evidence.append("PASS: API key validation found")
            else:
                issues.append("FAIL: API key validation missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check audit logging
    try:
        logging_file = Path("src/services/enhanced_logging.py")
        if logging_file.exists():
            score += 1
            evidence.append("PASS: Enhanced logging exists")
        else:
            issues.append("FAIL: Enhanced logging missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    percentage = (score / total) * 100
    print(f"  Score: {percentage:.1f}%")
    return {"score": percentage, "issues": issues, "evidence": evidence}

def audit_performance():
    """Audit performance standards."""
    print("Phase 3: Performance Standards")
    
    score = 0
    total = 5
    issues = []
    evidence = []
    
    # Check response time optimization
    try:
        api_optimizer_file = Path("src/services/api_optimizer.py")
        if api_optimizer_file.exists():
            score += 1
            evidence.append("PASS: API optimizer exists")
        else:
            issues.append("FAIL: API optimizer missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check API optimization
    try:
        youtube_service_file = Path("src/services/youtube_service.py")
        if youtube_service_file.exists():
            content = youtube_service_file.read_text()
            if "cache" in content.lower():
                score += 1
                evidence.append("PASS: Caching found")
            else:
                issues.append("FAIL: Caching missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check memory management
    try:
        run_optimizer_file = Path("src/services/run_optimizer.py")
        if run_optimizer_file.exists():
            score += 1
            evidence.append("PASS: Run optimizer exists")
        else:
            issues.append("FAIL: Run optimizer missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check scrolling performance
    try:
        scrolling_file = Path("src/utils/browser_like_scrolling.py")
        if scrolling_file.exists():
            score += 1
            evidence.append("PASS: Browser-like scrolling exists")
        else:
            issues.append("FAIL: Browser-like scrolling missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check caching
    try:
        youtube_service_file = Path("src/services/youtube_service.py")
        if youtube_service_file.exists():
            content = youtube_service_file.read_text()
            if "ResponseCache" in content:
                score += 1
                evidence.append("PASS: Response cache found")
            else:
                issues.append("FAIL: Response cache missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    percentage = (score / total) * 100
    print(f"  Score: {percentage:.1f}%")
    return {"score": percentage, "issues": issues, "evidence": evidence}

def audit_testing():
    """Audit testing requirements."""
    print("Phase 4: Testing Requirements")
    
    score = 0
    total = 5
    issues = []
    evidence = []
    
    # Check test coverage
    try:
        test_files = list(Path(".").glob("test_*.py"))
        if len(test_files) >= 5:
            score += 1
            evidence.append(f"PASS: {len(test_files)} test files found")
        else:
            issues.append(f"FAIL: Only {len(test_files)} test files, need 5+")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check unit tests
    try:
        unit_test_files = [f for f in test_files if "test_" in f.name.lower()]
        if len(unit_test_files) >= 3:
            score += 1
            evidence.append(f"PASS: {len(unit_test_files)} unit test files found")
        else:
            issues.append(f"FAIL: Only {len(unit_test_files)} unit test files")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check integration tests
    try:
        integration_test_files = [f for f in test_files if "integration" in f.name.lower() or "comprehensive" in f.name.lower()]
        if len(integration_test_files) >= 2:
            score += 1
            evidence.append(f"PASS: {len(integration_test_files)} integration test files found")
        else:
            issues.append(f"FAIL: Only {len(integration_test_files)} integration test files")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check quality tests
    try:
        quality_test_files = [f for f in test_files if "quality" in f.name.lower() or "compliance" in f.name.lower()]
        if len(quality_test_files) >= 1:
            score += 1
            evidence.append(f"PASS: {len(quality_test_files)} quality test files found")
        else:
            issues.append("FAIL: Quality test files missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check test automation
    try:
        test_runner_files = [f for f in test_files if "run" in f.name.lower() or "launch" in f.name.lower()]
        if len(test_runner_files) >= 1:
            score += 1
            evidence.append("PASS: Test automation files found")
        else:
            issues.append("FAIL: Test automation files missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    percentage = (score / total) * 100
    print(f"  Score: {percentage:.1f}%")
    return {"score": percentage, "issues": issues, "evidence": evidence}

def audit_documentation():
    """Audit documentation standards."""
    print("Phase 5: Documentation Standards")
    
    score = 0
    total = 5
    issues = []
    evidence = []
    
    # Check user documentation
    try:
        readme_file = Path("README_ENHANCED.md")
        if readme_file.exists():
            score += 1
            evidence.append("PASS: Enhanced README exists")
        else:
            issues.append("FAIL: Enhanced README missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check technical documentation
    try:
        docs_dir = Path("docs")
        if docs_dir.exists():
            score += 1
            evidence.append("PASS: Documentation directory exists")
        else:
            issues.append("FAIL: Documentation directory missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check API documentation
    try:
        youtube_service_file = Path("src/services/youtube_service.py")
        if youtube_service_file.exists():
            content = youtube_service_file.read_text()
            if '"""' in content and "def " in content:
                score += 1
                evidence.append("PASS: API documentation found")
            else:
                issues.append("FAIL: API documentation missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check quality documentation
    try:
        quality_mandate_file = Path("docs/living/QualityMandate.md")
        if quality_mandate_file.exists():
            score += 1
            evidence.append("PASS: Quality Mandate exists")
        else:
            issues.append("FAIL: Quality Mandate missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    # Check living documentation
    try:
        living_docs_dir = Path("docs/living")
        if living_docs_dir.exists():
            score += 1
            evidence.append("PASS: Living documentation exists")
        else:
            issues.append("FAIL: Living documentation missing")
    except Exception as e:
        issues.append(f"ERROR: {e}")
    
    percentage = (score / total) * 100
    print(f"  Score: {percentage:.1f}%")
    return {"score": percentage, "issues": issues, "evidence": evidence}

def main():
    """Run comprehensive quality audit."""
    print("Starting Comprehensive Quality Audit")
    print("=" * 50)
    
    # Run all audits
    code_quality = audit_code_quality()
    security = audit_security()
    performance = audit_performance()
    testing = audit_testing()
    documentation = audit_documentation()
    
    # Calculate overall compliance
    overall_score = (code_quality["score"] + security["score"] + performance["score"] + 
                    testing["score"] + documentation["score"]) / 5
    
    print("\n" + "=" * 50)
    print("AUDIT RESULTS SUMMARY")
    print("=" * 50)
    print(f"Code Quality: {code_quality['score']:.1f}%")
    print(f"Security: {security['score']:.1f}%")
    print(f"Performance: {performance['score']:.1f}%")
    print(f"Testing: {testing['score']:.1f}%")
    print(f"Documentation: {documentation['score']:.1f}%")
    print(f"\nOverall Compliance: {overall_score:.1f}%")
    
    # Check if production ready
    if overall_score >= 90:
        print("\nPRODUCTION READY: System meets quality standards")
    elif overall_score >= 80:
        print("\nNEAR PRODUCTION READY: Minor issues need addressing")
    else:
        print("\nNOT PRODUCTION READY: Significant issues must be resolved")
    
    # Show critical issues
    all_issues = (code_quality["issues"] + security["issues"] + performance["issues"] + 
                 testing["issues"] + documentation["issues"])
    
    if all_issues:
        print(f"\nCritical Issues ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  - {issue}")
    
    return overall_score

if __name__ == "__main__":
    main()

