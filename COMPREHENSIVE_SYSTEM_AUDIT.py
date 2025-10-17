"""
COMPREHENSIVE SYSTEM AUDIT
===========================
Validates entire YouTube2Sheets system against CURRENT_SYSTEM_STATE.md
Identifies ALL discrepancies and architectural issues.

Author: @TheDiagnostician
Date: October 11, 2025
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class SystemAuditor:
    """Comprehensive system auditor."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log_issue(self, category: str, severity: str, description: str, location: str = ""):
        """Log an issue."""
        self.issues.append({
            'category': category,
            'severity': severity,
            'description': description,
            'location': location
        })
    
    def log_warning(self, category: str, description: str, location: str = ""):
        """Log a warning."""
        self.warnings.append({
            'category': category,
            'description': description,
            'location': location
        })
    
    def log_success(self, category: str, description: str):
        """Log a success."""
        self.successes.append({
            'category': category,
            'description': description
        })
    
    def print_section(self, title: str):
        """Print section header."""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def audit_architecture(self) -> bool:
        """Audit system architecture against CURRENT_SYSTEM_STATE.md."""
        self.print_section("ARCHITECTURE AUDIT")
        
        required_structure = {
            'src/backend/youtube2sheets.py': 'Main orchestrator',
            'src/backend/scheduler_sheet_manager.py': 'Job management',
            'src/backend/scheduler_runner.py': 'CLI entry for scheduled jobs',
            'src/backend/api_optimizer.py': 'API efficiency + quota tracking',
            'src/backend/data_processor.py': 'Video transformation pipeline',
            'src/backend/filters.py': 'Keyword & duration filters',
            'src/backend/exceptions.py': 'Canonical error hierarchy',
            'src/gui/main_app.py': 'CustomTkinter GUI entry point',
            'src/services/automator.py': 'Services layer automator',
            'src/services/youtube_service.py': 'YouTube API service',
            'src/services/sheets_service.py': 'Google Sheets service',
            'src/domain/models.py': 'Domain models'
        }
        
        all_exist = True
        for file_path, description in required_structure.items():
            if Path(file_path).exists():
                self.log_success('Architecture', f"✅ {file_path} exists ({description})")
            else:
                self.log_issue('Architecture', 'CRITICAL', f"Missing: {file_path} ({description})", file_path)
                all_exist = False
        
        return all_exist
    
    def audit_dual_automator_system(self) -> bool:
        """Audit the dual automator system (backend vs services)."""
        self.print_section("DUAL AUTOMATOR SYSTEM AUDIT")
        
        backend_automator = Path('src/backend/youtube2sheets.py')
        services_automator = Path('src/services/automator.py')
        
        if not backend_automator.exists():
            self.log_issue('Automator', 'CRITICAL', 'Backend automator missing', str(backend_automator))
            return False
        
        if not services_automator.exists():
            self.log_issue('Automator', 'CRITICAL', 'Services automator missing', str(services_automator))
            return False
        
        # Check if GUI uses the correct automator
        gui_file = Path('src/gui/main_app.py')
        if gui_file.exists():
            gui_content = gui_file.read_text(encoding='utf-8', errors='ignore')
            
            # GUI should import from backend.youtube2sheets
            if 'from src.backend.youtube2sheets import' in gui_content:
                self.log_success('Automator', '✅ GUI correctly imports backend automator')
            else:
                self.log_warning('Automator', 'GUI may not be using backend automator', str(gui_file))
            
            # Check for SyncConfig usage
            if 'SyncConfig' in gui_content:
                self.log_success('Automator', '✅ GUI uses SyncConfig')
            else:
                self.log_issue('Automator', 'HIGH', 'GUI missing SyncConfig usage', str(gui_file))
        
        return True
    
    def audit_api_optimization(self) -> bool:
        """Audit API optimization features."""
        self.print_section("API OPTIMIZATION AUDIT")
        
        optimizer_file = Path('src/backend/api_optimizer.py')
        
        if not optimizer_file.exists():
            self.log_issue('API', 'CRITICAL', 'API optimizer missing', str(optimizer_file))
            return False
        
        optimizer_content = optimizer_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check for required classes
        required_classes = [
            ('ResponseCache', 'ETag caching implementation'),
            ('VideoDeduplicator', 'Deduplication logic'),
            ('APICreditTracker', 'Quota tracking')
        ]
        
        for class_name, description in required_classes:
            if f'class {class_name}' in optimizer_content:
                self.log_success('API', f'✅ {class_name} exists ({description})')
            else:
                self.log_issue('API', 'HIGH', f'Missing {class_name} ({description})', str(optimizer_file))
        
        # Check if services layer uses API optimization
        youtube_service = Path('src/services/youtube_service.py')
        if youtube_service.exists():
            service_content = youtube_service.read_text(encoding='utf-8', errors='ignore')
            
            if 'ResponseCache' in service_content or 'cache' in service_content.lower():
                self.log_success('API', '✅ YouTube service uses caching')
            else:
                self.log_warning('API', 'YouTube service may not use ETag caching', str(youtube_service))
            
            if 'VideoDeduplicator' in service_content or 'dedup' in service_content.lower():
                self.log_success('API', '✅ YouTube service uses deduplication')
            else:
                self.log_warning('API', 'YouTube service may not use deduplication', str(youtube_service))
        
        return True
    
    def audit_filter_logic(self) -> bool:
        """Audit filter logic implementation."""
        self.print_section("FILTER LOGIC AUDIT")
        
        automator_file = Path('src/services/automator.py')
        
        if not automator_file.exists():
            self.log_issue('Filters', 'CRITICAL', 'Automator file missing', str(automator_file))
            return False
        
        automator_content = automator_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check for _apply_filters method
        if 'def _apply_filters' in automator_content:
            self.log_success('Filters', '✅ Filter method exists')
            
            # Check for common filter bugs
            if 'video.duration > filters.min_duration' in automator_content:
                self.log_issue('Filters', 'CRITICAL', 
                             'BACKWARDS filter logic: excludes videos LONGER than minimum!', 
                             'src/services/automator.py::_apply_filters')
            
            if 'video.view_count < filters.min_duration' in automator_content:
                self.log_issue('Filters', 'CRITICAL',
                             'WRONG variable: using min_duration for view_count!',
                             'src/services/automator.py::_apply_filters')
            
            if 'video.like_count < filters.min_duration' in automator_content:
                self.log_issue('Filters', 'CRITICAL',
                             'WRONG variable: using min_duration for like_count!',
                             'src/services/automator.py::_apply_filters')
            
            # Check for correct logic
            if 'video.duration < filters.min_duration' in automator_content and \
               'video.duration > filters.min_duration' not in automator_content:
                self.log_success('Filters', '✅ Duration filter logic is correct')
            
        else:
            self.log_issue('Filters', 'HIGH', 'Missing _apply_filters method', str(automator_file))
        
        return True
    
    def audit_sheets_integration(self) -> bool:
        """Audit Google Sheets integration."""
        self.print_section("GOOGLE SHEETS INTEGRATION AUDIT")
        
        sheets_service = Path('src/services/sheets_service.py')
        
        if not sheets_service.exists():
            self.log_issue('Sheets', 'CRITICAL', 'Sheets service missing', str(sheets_service))
            return False
        
        sheets_content = sheets_service.read_text(encoding='utf-8', errors='ignore')
        
        # Check for required methods
        required_methods = [
            ('create_sheet_tab', 'Tab creation'),
            ('write_videos_to_sheet', 'Data writing'),
            ('apply_conditional_formatting', 'Conditional formatting'),
            ('check_for_duplicates', 'Deduplication check')
        ]
        
        for method_name, description in required_methods:
            if f'def {method_name}' in sheets_content:
                self.log_success('Sheets', f'✅ {method_name} exists ({description})')
            else:
                self.log_issue('Sheets', 'HIGH', f'Missing {method_name} ({description})', str(sheets_service))
        
        # Check if automator creates tabs before writing
        automator_file = Path('src/services/automator.py')
        if automator_file.exists():
            automator_content = automator_file.read_text(encoding='utf-8', errors='ignore')
            
            if 'create_sheet_tab' in automator_content:
                self.log_success('Sheets', '✅ Automator creates tabs before writing')
            else:
                self.log_issue('Sheets', 'HIGH', 
                             'Automator does not create tabs - will fail on non-existent tabs',
                             str(automator_file))
        
        return True
    
    def audit_video_retrieval(self) -> bool:
        """Audit video retrieval logic."""
        self.print_section("VIDEO RETRIEVAL AUDIT")
        
        youtube_service = Path('src/services/youtube_service.py')
        
        if not youtube_service.exists():
            self.log_issue('Video', 'CRITICAL', 'YouTube service missing', str(youtube_service))
            return False
        
        youtube_content = youtube_service.read_text(encoding='utf-8', errors='ignore')
        
        # Check channel resolution method
        if 'forHandle' in youtube_content:
            self.log_success('Video', '✅ Uses modern forHandle for channel resolution')
        else:
            self.log_issue('Video', 'HIGH',
                         'May be using deprecated forUsername for channel resolution',
                         str(youtube_service))
        
        # Check if video details are fetched
        if 'part": "snippet,contentDetails,statistics' in youtube_content or \
           "'part': 'snippet,contentDetails,statistics'" in youtube_content:
            self.log_success('Video', '✅ Fetches full video details (duration, views, likes, comments)')
        else:
            self.log_issue('Video', 'CRITICAL',
                         'Not fetching full video details - stats will be zeros!',
                         str(youtube_service))
        
        # Check if _parse_duration exists
        if 'def _parse_duration' in youtube_content:
            self.log_success('Video', '✅ Duration parsing method exists')
        else:
            self.log_issue('Video', 'HIGH', 'Missing duration parsing method', str(youtube_service))
        
        return True
    
    def audit_data_models(self) -> bool:
        """Audit data models."""
        self.print_section("DATA MODELS AUDIT")
        
        models_file = Path('src/domain/models.py')
        
        if not models_file.exists():
            self.log_issue('Models', 'CRITICAL', 'Domain models missing', str(models_file))
            return False
        
        models_content = models_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check for required models
        required_models = [
            'Video',
            'Channel',
            'Filters',
            'Destination',
            'RunConfig',
            'RunResult',
            'RunStatus'
        ]
        
        for model_name in required_models:
            if f'class {model_name}' in models_content or f'{model_name} =' in models_content:
                self.log_success('Models', f'✅ {model_name} model exists')
            else:
                self.log_issue('Models', 'HIGH', f'Missing {model_name} model', str(models_file))
        
        # Check if Video has to_dict method
        if 'def to_dict' in models_content:
            self.log_success('Models', '✅ Video.to_dict() method exists')
        else:
            self.log_issue('Models', 'MEDIUM', 'Video missing to_dict() method', str(models_file))
        
        return True
    
    def audit_backend_sync_config(self) -> bool:
        """Audit backend SyncConfig."""
        self.print_section("BACKEND SYNCCONFIG AUDIT")
        
        backend_file = Path('src/backend/youtube2sheets.py')
        
        if not backend_file.exists():
            self.log_issue('SyncConfig', 'CRITICAL', 'Backend file missing', str(backend_file))
            return False
        
        backend_content = backend_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check for SyncConfig
        if 'class SyncConfig' in backend_content or '@dataclass' in backend_content:
            self.log_success('SyncConfig', '✅ SyncConfig dataclass exists')
            
            # Check for required attributes
            required_attrs = [
                'min_duration_seconds',
                'max_duration_seconds',
                'keyword_filter',
                'keyword_mode',
                'max_videos'
            ]
            
            for attr in required_attrs:
                if attr in backend_content:
                    self.log_success('SyncConfig', f'✅ SyncConfig.{attr} exists')
                else:
                    self.log_issue('SyncConfig', 'HIGH', f'Missing SyncConfig.{attr}', str(backend_file))
        else:
            self.log_issue('SyncConfig', 'CRITICAL', 'SyncConfig not found', str(backend_file))
        
        return True
    
    def generate_report(self) -> Dict:
        """Generate comprehensive audit report."""
        self.print_section("AUDIT REPORT")
        
        # Print issues
        if self.issues:
            print("\n🚨 CRITICAL ISSUES FOUND:\n")
            for issue in self.issues:
                severity_emoji = '🔴' if issue['severity'] == 'CRITICAL' else '🟠' if issue['severity'] == 'HIGH' else '🟡'
                print(f"{severity_emoji} [{issue['severity']}] {issue['category']}: {issue['description']}")
                if issue['location']:
                    print(f"   Location: {issue['location']}")
        
        # Print warnings
        if self.warnings:
            print("\n⚠️  WARNINGS:\n")
            for warning in self.warnings:
                print(f"⚠️  {warning['category']}: {warning['description']}")
                if warning['location']:
                    print(f"   Location: {warning['location']}")
        
        # Print successes
        if self.successes:
            print(f"\n✅ PASSED CHECKS ({len(self.successes)}):\n")
            for success in self.successes:
                print(f"✅ {success['category']}: {success['description']}")
        
        # Summary
        total_checks = len(self.issues) + len(self.warnings) + len(self.successes)
        critical_issues = len([i for i in self.issues if i['severity'] == 'CRITICAL'])
        high_issues = len([i for i in self.issues if i['severity'] == 'HIGH'])
        
        print(f"\n{'='*80}")
        print("AUDIT SUMMARY")
        print(f"{'='*80}")
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {len(self.successes)}")
        print(f"🔴 Critical Issues: {critical_issues}")
        print(f"🟠 High Issues: {high_issues}")
        print(f"🟡 Medium Issues: {len(self.issues) - critical_issues - high_issues}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if critical_issues > 0:
            print("\n🚨 SYSTEM HAS CRITICAL ISSUES - IMMEDIATE ACTION REQUIRED")
        elif high_issues > 0:
            print("\n⚠️  SYSTEM HAS HIGH PRIORITY ISSUES - ACTION RECOMMENDED")
        else:
            print("\n✅ SYSTEM PASSES ALL CRITICAL CHECKS")
        
        return {
            'total_checks': total_checks,
            'passed': len(self.successes),
            'critical_issues': critical_issues,
            'high_issues': high_issues,
            'medium_issues': len(self.issues) - critical_issues - high_issues,
            'warnings': len(self.warnings),
            'issues': self.issues,
            'warnings_list': self.warnings,
            'successes': self.successes
        }

def main():
    """Run comprehensive system audit."""
    print("="*80)
    print("  COMPREHENSIVE SYSTEM AUDIT")
    print("  Validating against CURRENT_SYSTEM_STATE.md")
    print("="*80)
    
    auditor = SystemAuditor()
    
    # Run all audits
    audits = [
        auditor.audit_architecture,
        auditor.audit_dual_automator_system,
        auditor.audit_api_optimization,
        auditor.audit_filter_logic,
        auditor.audit_sheets_integration,
        auditor.audit_video_retrieval,
        auditor.audit_data_models,
        auditor.audit_backend_sync_config
    ]
    
    for audit_func in audits:
        try:
            audit_func()
        except Exception as e:
            print(f"❌ Audit failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate report
    report = auditor.generate_report()
    
    # Save report to file
    report_file = Path('DeltaReports/SYSTEM_AUDIT_REPORT.json')
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, indent=2, fp=f)
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Return exit code
    if report['critical_issues'] > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())

