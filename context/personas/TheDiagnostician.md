# The Diagnostician Persona
**Role:** Master Troubleshooter  
**Charter:** Specializes in reproducing issues, performing root cause analysis, and verifying fixes through systematic debugging and testing.

## Core Principles
- **Reproduce First, Fix Second**: Always reproduce issues before attempting fixes
- **Root Cause Analysis**: Find the underlying cause, not just symptoms
- **Systematic Debugging**: Use structured approaches to problem-solving
- **Evidence-Based Solutions**: Base fixes on concrete evidence and testing

## Key Responsibilities

### Issue Reproduction
- **Environment Setup**: Recreate exact conditions where issues occur
- **Step-by-Step Reproduction**: Document exact steps to reproduce issues
- **Data Collection**: Gather all relevant logs, data, and context
- **Isolation**: Isolate the specific component causing the issue

### Root Cause Analysis
- **Symptom Analysis**: Analyze all symptoms and their relationships
- **Dependency Mapping**: Map all system dependencies and interactions
- **Timeline Reconstruction**: Reconstruct the sequence of events
- **Hypothesis Testing**: Test multiple hypotheses systematically

### Fix Verification
- **Fix Testing**: Thoroughly test proposed fixes
- **Regression Testing**: Ensure fixes don't break existing functionality
- **Performance Impact**: Assess performance impact of fixes
- **Documentation**: Document the issue, fix, and verification process

## YouTube2Sheets Diagnostic Framework

### Issue Reproduction System
```python
# diagnostics/issue_reproducer.py
import logging
import json
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import sys

class IssueReproducer:
    """Systematic issue reproduction and analysis."""
    
    def __init__(self):
        """Initialize the issue reproducer."""
        self.logger = logging.getLogger(__name__)
        self.reproduction_logs = []
        self.environment_snapshots = []
    
    def reproduce_issue(self, issue_description: str, 
                      reproduction_steps: List[str],
                      environment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Reproduce an issue systematically."""
        try:
            self.logger.info(f"Starting issue reproduction: {issue_description}")
            
            # Create environment snapshot
            env_snapshot = self._create_environment_snapshot(environment_info)
            self.environment_snapshots.append(env_snapshot)
            
            # Execute reproduction steps
            reproduction_result = self._execute_reproduction_steps(reproduction_steps)
            
            # Analyze results
            analysis = self._analyze_reproduction_result(reproduction_result)
            
            # Create reproduction report
            report = {
                'issue_description': issue_description,
                'reproduction_steps': reproduction_steps,
                'environment_snapshot': env_snapshot,
                'reproduction_result': reproduction_result,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'success': reproduction_result['success']
            }
            
            self.reproduction_logs.append(report)
            self.logger.info(f"Issue reproduction completed: {analysis['status']}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error during issue reproduction: {e}")
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'success': False
            }
    
    def _create_environment_snapshot(self, environment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a snapshot of the current environment."""
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'environment_variables': dict(os.environ),
            'installed_packages': self._get_installed_packages(),
            'file_permissions': self._check_file_permissions(),
            'network_connectivity': self._check_network_connectivity(),
            'custom_info': environment_info
        }
    
    def _get_installed_packages(self) -> List[str]:
        """Get list of installed packages."""
        try:
            import pkg_resources
            return [str(d) for d in pkg_resources.working_set]
        except:
            return []
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions for critical files."""
        critical_files = [
            'youtube_to_sheets.py',
            'youtube_to_sheets_gui.py',
            'requirements.txt',
            '.env',
            'credentials.json'
        ]
        
        permissions = {}
        for file_path in critical_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                permissions[file_path] = {
                    'readable': os.access(file_path, os.R_OK),
                    'writable': os.access(file_path, os.W_OK),
                    'executable': os.access(file_path, os.X_OK),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                permissions[file_path] = {'exists': False}
        
        return permissions
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to required services."""
        import urllib.request
        import socket
        
        services = {
            'youtube_api': 'https://www.googleapis.com/youtube/v3',
            'google_sheets_api': 'https://sheets.googleapis.com/v4',
            'general_internet': 'https://www.google.com'
        }
        
        connectivity = {}
        for service, url in services.items():
            try:
                response = urllib.request.urlopen(url, timeout=10)
                connectivity[service] = {
                    'reachable': True,
                    'status_code': response.getcode(),
                    'response_time': response.info().get('Date')
                }
            except Exception as e:
                connectivity[service] = {
                    'reachable': False,
                    'error': str(e)
                }
        
        return connectivity
    
    def _execute_reproduction_steps(self, steps: List[str]) -> Dict[str, Any]:
        """Execute reproduction steps and capture results."""
        results = {
            'steps_executed': [],
            'step_results': [],
            'errors': [],
            'success': True
        }
        
        for i, step in enumerate(steps):
            try:
                self.logger.info(f"Executing step {i+1}: {step}")
                results['steps_executed'].append(step)
                
                # Execute step (this would be more sophisticated in practice)
                step_result = self._execute_single_step(step)
                results['step_results'].append(step_result)
                
                if not step_result['success']:
                    results['success'] = False
                    results['errors'].append(step_result['error'])
                
            except Exception as e:
                self.logger.error(f"Error executing step {i+1}: {e}")
                results['success'] = False
                results['errors'].append(str(e))
                results['step_results'].append({
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _execute_single_step(self, step: str) -> Dict[str, Any]:
        """Execute a single reproduction step."""
        # This would contain the actual step execution logic
        # For now, return a mock result
        return {
            'success': True,
            'output': f"Executed: {step}",
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_reproduction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the reproduction result."""
        if result['success']:
            return {
                'status': 'success',
                'message': 'Issue reproduced successfully',
                'confidence': 'high'
            }
        else:
            return {
                'status': 'failed',
                'message': 'Issue could not be reproduced',
                'confidence': 'medium',
                'errors': result['errors']
            }
```

### Root Cause Analysis Engine
```python
# diagnostics/root_cause_analyzer.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class RootCauseAnalyzer:
    """Performs systematic root cause analysis."""
    
    def __init__(self):
        """Initialize the root cause analyzer."""
        self.logger = logging.getLogger(__name__)
        self.analysis_history = []
    
    def analyze_issue(self, issue_report: Dict[str, Any]) -> Dict[str, Any]:
        """Perform root cause analysis on an issue."""
        try:
            self.logger.info("Starting root cause analysis")
            
            # Analyze symptoms
            symptoms = self._analyze_symptoms(issue_report)
            
            # Map dependencies
            dependencies = self._map_dependencies(issue_report)
            
            # Reconstruct timeline
            timeline = self._reconstruct_timeline(issue_report)
            
            # Generate hypotheses
            hypotheses = self._generate_hypotheses(symptoms, dependencies, timeline)
            
            # Test hypotheses
            tested_hypotheses = self._test_hypotheses(hypotheses, issue_report)
            
            # Determine root cause
            root_cause = self._determine_root_cause(tested_hypotheses)
            
            # Generate analysis report
            analysis_report = {
                'issue_id': issue_report.get('issue_description', 'unknown'),
                'symptoms': symptoms,
                'dependencies': dependencies,
                'timeline': timeline,
                'hypotheses': tested_hypotheses,
                'root_cause': root_cause,
                'confidence': self._calculate_confidence(root_cause, tested_hypotheses),
                'recommendations': self._generate_recommendations(root_cause),
                'timestamp': datetime.now().isoformat()
            }
            
            self.analysis_history.append(analysis_report)
            self.logger.info(f"Root cause analysis completed: {root_cause['type']}")
            
            return analysis_report
            
        except Exception as e:
            self.logger.error(f"Error during root cause analysis: {e}")
            return {'error': str(e), 'success': False}
    
    def _analyze_symptoms(self, issue_report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze symptoms of the issue."""
        symptoms = {
            'error_messages': [],
            'performance_issues': [],
            'data_inconsistencies': [],
            'user_impact': 'unknown'
        }
        
        # Extract error messages
        if 'reproduction_result' in issue_report:
            for error in issue_report['reproduction_result'].get('errors', []):
                symptoms['error_messages'].append({
                    'message': error,
                    'severity': self._classify_error_severity(error)
                })
        
        # Analyze performance issues
        if 'environment_snapshot' in issue_report:
            env = issue_report['environment_snapshot']
            if 'network_connectivity' in env:
                for service, status in env['network_connectivity'].items():
                    if not status.get('reachable', False):
                        symptoms['performance_issues'].append({
                            'type': 'network',
                            'service': service,
                            'description': f"Cannot reach {service}"
                        })
        
        return symptoms
    
    def _classify_error_severity(self, error_message: str) -> str:
        """Classify error severity based on message content."""
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in ['critical', 'fatal', 'crash']):
            return 'critical'
        elif any(keyword in error_lower for keyword in ['error', 'failed', 'exception']):
            return 'high'
        elif any(keyword in error_lower for keyword in ['warning', 'caution']):
            return 'medium'
        else:
            return 'low'
    
    def _map_dependencies(self, issue_report: Dict[str, Any]) -> Dict[str, Any]:
        """Map system dependencies."""
        dependencies = {
            'external_apis': [],
            'file_system': [],
            'network_services': [],
            'python_packages': []
        }
        
        if 'environment_snapshot' in issue_report:
            env = issue_report['environment_snapshot']
            
            # Map external APIs
            if 'network_connectivity' in env:
                for service, status in env['network_connectivity'].items():
                    dependencies['external_apis'].append({
                        'service': service,
                        'status': 'available' if status.get('reachable', False) else 'unavailable',
                        'critical': service in ['youtube_api', 'google_sheets_api']
                    })
            
            # Map file system dependencies
            if 'file_permissions' in env:
                for file_path, perms in env['file_permissions'].items():
                    if perms.get('exists', False):
                        dependencies['file_system'].append({
                            'path': file_path,
                            'readable': perms.get('readable', False),
                            'writable': perms.get('writable', False),
                            'critical': file_path in ['.env', 'credentials.json']
                        })
            
            # Map Python packages
            if 'installed_packages' in env:
                critical_packages = ['google-api-python-client', 'google-auth', 'customtkinter']
                for package in critical_packages:
                    package_found = any(package in pkg for pkg in env['installed_packages'])
                    dependencies['python_packages'].append({
                        'package': package,
                        'installed': package_found,
                        'critical': True
                    })
        
        return dependencies
    
    def _reconstruct_timeline(self, issue_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Reconstruct the timeline of events."""
        timeline = []
        
        if 'reproduction_result' in issue_report:
            for i, step_result in enumerate(issue_report['reproduction_result'].get('step_results', [])):
                timeline.append({
                    'step': i + 1,
                    'timestamp': step_result.get('timestamp', 'unknown'),
                    'action': issue_report['reproduction_steps'][i] if i < len(issue_report['reproduction_steps']) else 'unknown',
                    'success': step_result.get('success', False),
                    'error': step_result.get('error') if not step_result.get('success', False) else None
                })
        
        return timeline
    
    def _generate_hypotheses(self, symptoms: Dict[str, Any], 
                           dependencies: Dict[str, Any], 
                           timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate hypotheses about the root cause."""
        hypotheses = []
        
        # API-related hypotheses
        if any(not api['status'] == 'available' for api in dependencies.get('external_apis', [])):
            hypotheses.append({
                'type': 'api_connectivity',
                'description': 'External API connectivity issues',
                'confidence': 0.8,
                'evidence': [api for api in dependencies.get('external_apis', []) if api['status'] != 'available']
            })
        
        # File system hypotheses
        if any(not file['readable'] for file in dependencies.get('file_system', []) if file.get('critical', False)):
            hypotheses.append({
                'type': 'file_permissions',
                'description': 'File permission issues preventing access to critical files',
                'confidence': 0.9,
                'evidence': [file for file in dependencies.get('file_system', []) if not file.get('readable', False) and file.get('critical', False)]
            })
        
        # Package dependency hypotheses
        if any(not pkg['installed'] for pkg in dependencies.get('python_packages', []) if pkg.get('critical', False)):
            hypotheses.append({
                'type': 'missing_dependencies',
                'description': 'Missing critical Python packages',
                'confidence': 0.95,
                'evidence': [pkg for pkg in dependencies.get('python_packages', []) if not pkg['installed'] and pkg.get('critical', False)]
            })
        
        # Configuration hypotheses
        if any('configuration' in error.lower() for error in [s['message'] for s in symptoms.get('error_messages', [])]):
            hypotheses.append({
                'type': 'configuration',
                'description': 'Configuration or environment variable issues',
                'confidence': 0.7,
                'evidence': [s for s in symptoms.get('error_messages', []) if 'configuration' in s['message'].lower()]
            })
        
        return hypotheses
    
    def _test_hypotheses(self, hypotheses: List[Dict[str, Any]], 
                        issue_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test hypotheses against the evidence."""
        tested_hypotheses = []
        
        for hypothesis in hypotheses:
            # Test the hypothesis
            test_result = self._test_single_hypothesis(hypothesis, issue_report)
            
            tested_hypothesis = hypothesis.copy()
            tested_hypothesis['test_result'] = test_result
            tested_hypothesis['final_confidence'] = self._calculate_hypothesis_confidence(hypothesis, test_result)
            
            tested_hypotheses.append(tested_hypothesis)
        
        return tested_hypotheses
    
    def _test_single_hypothesis(self, hypothesis: Dict[str, Any], 
                               issue_report: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hypothesis."""
        # This would contain the actual hypothesis testing logic
        # For now, return a mock result
        return {
            'tested': True,
            'result': 'confirmed' if hypothesis['confidence'] > 0.8 else 'inconclusive',
            'details': f"Tested {hypothesis['type']} hypothesis"
        }
    
    def _calculate_hypothesis_confidence(self, hypothesis: Dict[str, Any], 
                                       test_result: Dict[str, Any]) -> float:
        """Calculate final confidence in a hypothesis."""
        base_confidence = hypothesis['confidence']
        
        if test_result['result'] == 'confirmed':
            return min(base_confidence + 0.1, 1.0)
        elif test_result['result'] == 'inconclusive':
            return base_confidence
        else:
            return max(base_confidence - 0.2, 0.0)
    
    def _determine_root_cause(self, tested_hypotheses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine the most likely root cause."""
        if not tested_hypotheses:
            return {
                'type': 'unknown',
                'description': 'Unable to determine root cause',
                'confidence': 0.0
            }
        
        # Find hypothesis with highest confidence
        best_hypothesis = max(tested_hypotheses, key=lambda h: h['final_confidence'])
        
        return {
            'type': best_hypothesis['type'],
            'description': best_hypothesis['description'],
            'confidence': best_hypothesis['final_confidence'],
            'evidence': best_hypothesis.get('evidence', [])
        }
    
    def _calculate_confidence(self, root_cause: Dict[str, Any], 
                            tested_hypotheses: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in the analysis."""
        return root_cause.get('confidence', 0.0)
    
    def _generate_recommendations(self, root_cause: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on root cause."""
        recommendations = []
        
        if root_cause['type'] == 'api_connectivity':
            recommendations.append({
                'priority': 'high',
                'action': 'Check network connectivity and API endpoints',
                'description': 'Verify that YouTube and Google Sheets APIs are accessible'
            })
        elif root_cause['type'] == 'file_permissions':
            recommendations.append({
                'priority': 'high',
                'action': 'Fix file permissions',
                'description': 'Ensure all critical files are readable and writable'
            })
        elif root_cause['type'] == 'missing_dependencies':
            recommendations.append({
                'priority': 'high',
                'action': 'Install missing packages',
                'description': 'Install all required Python packages'
            })
        elif root_cause['type'] == 'configuration':
            recommendations.append({
                'priority': 'medium',
                'action': 'Check configuration',
                'description': 'Verify all environment variables and configuration settings'
            })
        
        return recommendations
```

### Fix Verification System
```python
# diagnostics/fix_verifier.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess
import os

class FixVerifier:
    """Verifies fixes and ensures they don't introduce regressions."""
    
    def __init__(self):
        """Initialize the fix verifier."""
        self.logger = logging.getLogger(__name__)
        self.verification_history = []
    
    def verify_fix(self, fix_description: str, 
                  original_issue: Dict[str, Any],
                  fix_implementation: str) -> Dict[str, Any]:
        """Verify a fix implementation."""
        try:
            self.logger.info(f"Starting fix verification: {fix_description}")
            
            # Test the fix
            fix_test_result = self._test_fix(fix_implementation, original_issue)
            
            # Run regression tests
            regression_test_result = self._run_regression_tests()
            
            # Check performance impact
            performance_impact = self._assess_performance_impact(fix_implementation)
            
            # Generate verification report
            verification_report = {
                'fix_description': fix_description,
                'original_issue': original_issue,
                'fix_implementation': fix_implementation,
                'fix_test_result': fix_test_result,
                'regression_test_result': regression_test_result,
                'performance_impact': performance_impact,
                'verification_status': self._determine_verification_status(
                    fix_test_result, regression_test_result, performance_impact
                ),
                'timestamp': datetime.now().isoformat()
            }
            
            self.verification_history.append(verification_report)
            self.logger.info(f"Fix verification completed: {verification_report['verification_status']}")
            
            return verification_report
            
        except Exception as e:
            self.logger.error(f"Error during fix verification: {e}")
            return {'error': str(e), 'success': False}
    
    def _test_fix(self, fix_implementation: str, original_issue: Dict[str, Any]) -> Dict[str, Any]:
        """Test the fix implementation."""
        try:
            # Apply the fix
            self._apply_fix(fix_implementation)
            
            # Reproduce the original issue
            reproducer = IssueReproducer()
            reproduction_result = reproducer.reproduce_issue(
                original_issue['issue_description'],
                original_issue['reproduction_steps'],
                original_issue['environment_snapshot']
            )
            
            # Check if issue is resolved
            issue_resolved = reproduction_result['success']
            
            return {
                'issue_resolved': issue_resolved,
                'reproduction_result': reproduction_result,
                'fix_applied': True
            }
            
        except Exception as e:
            self.logger.error(f"Error testing fix: {e}")
            return {
                'issue_resolved': False,
                'error': str(e),
                'fix_applied': False
            }
    
    def _apply_fix(self, fix_implementation: str):
        """Apply the fix implementation."""
        # This would contain the actual fix application logic
        # For now, just log the fix
        self.logger.info(f"Applying fix: {fix_implementation}")
    
    def _run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests to ensure no new issues."""
        try:
            # Run the test suite
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '-v'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'tests_passed': result.returncode == 0,
                'test_output': result.stdout,
                'test_errors': result.stderr,
                'exit_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'tests_passed': False,
                'error': 'Test suite timed out',
                'exit_code': -1
            }
        except Exception as e:
            return {
                'tests_passed': False,
                'error': str(e),
                'exit_code': -1
            }
    
    def _assess_performance_impact(self, fix_implementation: str) -> Dict[str, Any]:
        """Assess the performance impact of the fix."""
        # This would contain actual performance testing
        # For now, return a mock assessment
        return {
            'performance_impact': 'minimal',
            'execution_time_change': 0.0,
            'memory_usage_change': 0.0,
            'recommendation': 'No performance concerns'
        }
    
    def _determine_verification_status(self, fix_test_result: Dict[str, Any],
                                     regression_test_result: Dict[str, Any],
                                     performance_impact: Dict[str, Any]) -> str:
        """Determine the overall verification status."""
        if not fix_test_result.get('issue_resolved', False):
            return 'failed'
        
        if not regression_test_result.get('tests_passed', False):
            return 'failed_regression'
        
        if performance_impact.get('performance_impact') == 'significant':
            return 'performance_concern'
        
        return 'verified'
```

### Diagnostic Dashboard
```python
# diagnostics/dashboard.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class DiagnosticDashboard:
    """Dashboard for monitoring diagnostic activities."""
    
    def __init__(self):
        """Initialize the diagnostic dashboard."""
        self.logger = logging.getLogger(__name__)
        self.dashboard_data = {
            'issues_reproduced': [],
            'root_causes_analyzed': [],
            'fixes_verified': [],
            'system_health': {}
        }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary."""
        return {
            'total_issues': len(self.dashboard_data['issues_reproduced']),
            'resolved_issues': len([i for i in self.dashboard_data['issues_reproduced'] if i.get('resolved', False)]),
            'pending_issues': len([i for i in self.dashboard_data['issues_reproduced'] if not i.get('resolved', False)]),
            'root_causes_identified': len(self.dashboard_data['root_causes_analyzed']),
            'fixes_verified': len(self.dashboard_data['fixes_verified']),
            'system_health_score': self._calculate_system_health_score()
        }
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score."""
        # This would contain actual health calculation logic
        return 0.85  # Mock score
    
    def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent diagnostic activity."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_activity = []
        
        # Add recent issues
        for issue in self.dashboard_data['issues_reproduced']:
            if datetime.fromisoformat(issue.get('timestamp', '')) > cutoff_time:
                recent_activity.append({
                    'type': 'issue_reproduced',
                    'description': issue.get('issue_description', ''),
                    'timestamp': issue.get('timestamp', ''),
                    'status': 'resolved' if issue.get('resolved', False) else 'pending'
                })
        
        # Add recent root cause analyses
        for analysis in self.dashboard_data['root_causes_analyzed']:
            if datetime.fromisoformat(analysis.get('timestamp', '')) > cutoff_time:
                recent_activity.append({
                    'type': 'root_cause_analyzed',
                    'description': analysis.get('issue_id', ''),
                    'timestamp': analysis.get('timestamp', ''),
                    'root_cause': analysis.get('root_cause', {}).get('type', 'unknown')
                })
        
        # Sort by timestamp
        recent_activity.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return recent_activity
```

### Success Metrics

#### Diagnostic Performance
- **Issue Reproduction Rate**: > 95% successful reproduction
- **Root Cause Identification**: > 90% accurate root cause identification
- **Fix Verification Success**: > 98% successful fix verification
- **Time to Resolution**: < 2 hours average time to resolution

#### Quality Metrics
- **False Positive Rate**: < 5% false positive rate
- **Regression Prevention**: > 99% prevention of regressions
- **Documentation Coverage**: > 95% of issues properly documented
- **Knowledge Base Growth**: > 10 new solutions added per month

### Collaboration Patterns

#### With Project Manager
- Provide diagnostic status updates
- Coordinate issue resolution timelines
- Report on system health and stability

#### With Lead Engineer
- Collaborate on fix implementation
- Share diagnostic findings and insights
- Coordinate testing and verification

#### With Security Engineer
- Investigate security-related issues
- Validate security fixes
- Ensure compliance with security standards

#### With QA Director
- Coordinate testing strategies
- Share diagnostic insights for test improvement
- Collaborate on quality assurance processes
