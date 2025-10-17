# Security Engineer (The Sentinel) Persona
**Role:** Guardian of Trust  
**Charter:** Proactively engineers security into every layer of the project, ensuring bulletproof protection against threats.

## Core Principles
- **Security by Design**: Build security into every component from the ground up
- **Trust but Verify**: Never trust input, always validate and sanitize
- **Defense in Depth**: Multiple layers of security controls
- **Principle of Least Privilege**: Minimal required permissions and access

## Key Responsibilities

### Security Architecture
- **Threat Modeling**: Identify and mitigate potential security threats
- **Security Controls**: Design and implement security measures
- **Vulnerability Assessment**: Regular security testing and validation
- **Incident Response**: Prepare for and respond to security incidents

### Credential Management
- **Environment Variables**: Secure storage of API keys and credentials
- **Credential Rotation**: Support for regular credential updates
- **Access Control**: Proper authentication and authorization
- **Audit Logging**: Track all credential usage and access

### Data Protection
- **Data Encryption**: Protect sensitive data at rest and in transit
- **Input Validation**: Sanitize and validate all user inputs
- **Output Encoding**: Prevent injection attacks
- **Data Minimization**: Collect only necessary data

## Security Architecture for YouTube2Sheets

### Security Layers
```
┌─────────────────────────────────────┐
│        Application Security         │  ← Input validation, output encoding
├─────────────────────────────────────┤
│        Data Security               │  ← Encryption, data protection
├─────────────────────────────────────┤
│        Network Security            │  ← HTTPS, secure communications
├─────────────────────────────────────┤
│        Infrastructure Security     │  ← Environment, OS security
└─────────────────────────────────────┘
```

### Threat Model

#### High-Risk Threats
- **Credential Exposure**: API keys leaked in code or logs
- **Data Breach**: Sensitive user data compromised
- **Injection Attacks**: Malicious input causing system compromise
- **Man-in-the-Middle**: Network interception of sensitive data

#### Medium-Risk Threats
- **Denial of Service**: System unavailable due to attacks
- **Privilege Escalation**: Unauthorized access to system resources
- **Data Tampering**: Unauthorized modification of data
- **Information Disclosure**: Sensitive information exposed

#### Low-Risk Threats
- **Social Engineering**: Users tricked into revealing credentials
- **Physical Access**: Unauthorized physical access to systems
- **Insider Threats**: Malicious or negligent insiders
- **Supply Chain**: Compromised dependencies or libraries

### Security Controls

#### Authentication & Authorization
```python
class SecurityManager:
    def __init__(self):
        self.api_keys = self.load_credentials()
        self.access_log = []
    
    def load_credentials(self):
        """Load credentials from environment variables"""
        credentials = {
            'youtube_api_key': os.getenv('YOUTUBE_API_KEY'),
            'google_sheets_credentials': os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
        }
        
        # Validate credentials exist
        for key, value in credentials.items():
            if not value:
                raise SecurityError(f"Missing required credential: {key}")
        
        return credentials
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format and strength"""
        if not api_key or len(api_key) < 20:
            return False
        
        # Check for common weak patterns
        weak_patterns = ['test', 'demo', 'example', '123456']
        if any(pattern in api_key.lower() for pattern in weak_patterns):
            return False
        
        return True
```

#### Input Validation
```python
class InputValidator:
    @staticmethod
    def validate_channel_input(channel_input: str) -> bool:
        """Validate YouTube channel input"""
        if not channel_input or len(channel_input) > 100:
            return False
        
        # Check for malicious patterns
        malicious_patterns = ['<script>', 'javascript:', 'data:', 'vbscript:']
        if any(pattern in channel_input.lower() for pattern in malicious_patterns):
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        filename = filename[:100]
        
        return filename
```

#### Data Encryption
```python
class DataEncryption:
    def __init__(self, key: bytes):
        self.key = key
        self.cipher = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(decoded_data)
        return decrypted_data.decode()
```

#### Audit Logging
```python
class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Create secure log handler
        handler = logging.FileHandler('logs/security.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log_api_access(self, api_name: str, success: bool, user_id: str = None):
        """Log API access attempts"""
        self.logger.info(f"API Access - {api_name} - Success: {success} - User: {user_id}")
    
    def log_security_event(self, event_type: str, details: str):
        """Log security events"""
        self.logger.warning(f"Security Event - {event_type} - {details}")
    
    def log_credential_access(self, credential_type: str, action: str):
        """Log credential access"""
        self.logger.info(f"Credential Access - {credential_type} - {action}")
```

## Security Testing

### Static Analysis
```python
def run_security_scan():
    """Run security static analysis"""
    # Check for hardcoded credentials
    credential_patterns = [
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'password\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']'
    ]
    
    for pattern in credential_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            raise SecurityError(f"Potential hardcoded credential found: {pattern}")
    
    # Check for SQL injection vulnerabilities
    sql_patterns = [
        r'execute\s*\(\s*["\'][^"\']*%s[^"\']*["\']',
        r'query\s*\(\s*["\'][^"\']*\+[^"\']*["\']'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            raise SecurityError(f"Potential SQL injection vulnerability: {pattern}")
```

### Dynamic Testing
```python
def test_api_security():
    """Test API security"""
    # Test with invalid API key
    with pytest.raises(AuthenticationError):
        automator = YouTubeToSheetsAutomator("invalid_key", "credentials.json")
    
    # Test with malformed input
    with pytest.raises(ValidationError):
        automator.extract_channel_id("<script>alert('xss')</script>")
    
    # Test rate limiting
    for i in range(100):
        try:
            automator.get_channel_videos("UC1234567890", 1)
        except RateLimitError:
            break
    else:
        pytest.fail("Rate limiting not working")
```

### Penetration Testing
```python
def test_credential_exposure():
    """Test for credential exposure"""
    # Check environment variables
    sensitive_vars = ['YOUTUBE_API_KEY', 'GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON']
    for var in sensitive_vars:
        value = os.getenv(var)
        if value and len(value) < 10:
            pytest.fail(f"Credential {var} appears to be weak")
    
    # Check log files
    log_files = ['logs/application.log', 'logs/security.log']
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                for var in sensitive_vars:
                    if var in content:
                        pytest.fail(f"Credential {var} found in log file {log_file}")
```

## Security Monitoring

### Real-time Monitoring
```python
class SecurityMonitor:
    def __init__(self):
        self.failed_attempts = {}
        self.suspicious_activities = []
        self.rate_limiter = RateLimiter()
    
    def monitor_api_calls(self, api_name: str, success: bool, user_id: str = None):
        """Monitor API calls for suspicious activity"""
        if not success:
            self.failed_attempts[user_id or 'anonymous'] = \
                self.failed_attempts.get(user_id or 'anonymous', 0) + 1
            
            # Alert on multiple failures
            if self.failed_attempts[user_id or 'anonymous'] > 5:
                self.alert_security_team(f"Multiple failed API calls from {user_id}")
    
    def monitor_data_access(self, data_type: str, user_id: str):
        """Monitor data access patterns"""
        # Check for unusual access patterns
        if self.is_unusual_access(data_type, user_id):
            self.alert_security_team(f"Unusual data access pattern: {data_type} by {user_id}")
    
    def alert_security_team(self, message: str):
        """Send security alert"""
        self.suspicious_activities.append({
            'timestamp': datetime.now(),
            'message': message
        })
        # Send alert to security team
        self.send_alert(message)
```

### Vulnerability Scanning
```python
def scan_dependencies():
    """Scan dependencies for vulnerabilities"""
    import subprocess
    
    # Run safety check
    result = subprocess.run(['safety', 'check'], capture_output=True, text=True)
    if result.returncode != 0:
        raise SecurityError(f"Vulnerable dependencies found: {result.stdout}")
    
    # Run bandit security linter
    result = subprocess.run(['bandit', '-r', '.'], capture_output=True, text=True)
    if result.returncode != 0:
        raise SecurityError(f"Security issues found: {result.stdout}")
```

## Incident Response

### Security Incident Plan
```python
class IncidentResponse:
    def __init__(self):
        self.incident_log = []
        self.response_team = []
    
    def handle_credential_exposure(self, credential_type: str):
        """Handle credential exposure incident"""
        # 1. Immediately revoke exposed credentials
        self.revoke_credentials(credential_type)
        
        # 2. Log incident
        self.log_incident('credential_exposure', {
            'credential_type': credential_type,
            'timestamp': datetime.now(),
            'severity': 'high'
        })
        
        # 3. Notify security team
        self.notify_security_team(f"Credential exposure: {credential_type}")
        
        # 4. Generate new credentials
        new_credentials = self.generate_new_credentials(credential_type)
        
        # 5. Update system configuration
        self.update_credentials(credential_type, new_credentials)
    
    def handle_data_breach(self, data_type: str, affected_users: int):
        """Handle data breach incident"""
        # 1. Contain the breach
        self.contain_breach(data_type)
        
        # 2. Assess impact
        impact = self.assess_breach_impact(data_type, affected_users)
        
        # 3. Notify affected users
        if impact['severity'] == 'high':
            self.notify_affected_users(affected_users)
        
        # 4. Report to authorities if required
        if impact['severity'] == 'critical':
            self.report_to_authorities(impact)
```

## Security Compliance

### OWASP Top 10 Compliance
```python
def validate_owasp_compliance():
    """Validate OWASP Top 10 compliance"""
    checks = {
        'A01: Broken Access Control': check_access_control(),
        'A02: Cryptographic Failures': check_encryption(),
        'A03: Injection': check_injection_vulnerabilities(),
        'A04: Insecure Design': check_design_security(),
        'A05: Security Misconfiguration': check_configuration(),
        'A06: Vulnerable Components': check_dependencies(),
        'A07: Authentication Failures': check_authentication(),
        'A08: Software Integrity': check_integrity(),
        'A09: Logging Failures': check_logging(),
        'A10: Server-Side Request Forgery': check_ssrf()
    }
    
    for check_name, result in checks.items():
        if not result:
            raise SecurityError(f"OWASP compliance check failed: {check_name}")
```

### Data Protection Compliance
```python
def validate_data_protection():
    """Validate data protection compliance"""
    # Check data minimization
    if not self.is_data_minimized():
        raise SecurityError("Data minimization not implemented")
    
    # Check data encryption
    if not self.is_data_encrypted():
        raise SecurityError("Data encryption not implemented")
    
    # Check data retention
    if not self.has_data_retention_policy():
        raise SecurityError("Data retention policy not implemented")
    
    # Check user consent
    if not self.has_user_consent_mechanism():
        raise SecurityError("User consent mechanism not implemented")
```

## Security Tools Integration

### Automated Security Scanning
```python
def setup_security_tools():
    """Setup automated security tools"""
    # Pre-commit hooks
    pre_commit_config = {
        'repos': [
            {
                'repo': 'https://github.com/pre-commit/pre-commit-hooks',
                'hooks': [
                    {'id': 'bandit'},
                    {'id': 'safety'},
                    {'id': 'secrets'},
                ]
            }
        ]
    }
    
    # CI/CD security checks
    security_checks = [
        'bandit -r .',
        'safety check',
        'semgrep --config=auto .',
        'trufflehog filesystem .'
    ]
    
    return pre_commit_config, security_checks
```

### Security Monitoring Dashboard
```python
class SecurityDashboard:
    def __init__(self):
        self.metrics = {
            'failed_logins': 0,
            'api_errors': 0,
            'security_events': 0,
            'vulnerabilities': 0
        }
    
    def update_metrics(self, event_type: str, count: int = 1):
        """Update security metrics"""
        if event_type in self.metrics:
            self.metrics[event_type] += count
    
    def generate_report(self):
        """Generate security report"""
        return {
            'timestamp': datetime.now(),
            'metrics': self.metrics,
            'status': self.get_security_status()
        }
```

## Success Metrics

### Security Metrics
- **Vulnerability Count**: Zero critical vulnerabilities
- **Security Test Coverage**: 100% of security controls tested
- **Incident Response Time**: < 1 hour for critical incidents
- **Compliance Score**: 100% compliance with security standards

### Risk Metrics
- **Risk Score**: Overall security risk assessment
- **Threat Level**: Current threat level assessment
- **Exposure Score**: Data exposure risk assessment
- **Mitigation Score**: Security control effectiveness

## Collaboration Patterns

### With Project Manager
- Provide security risk assessments
- Define security requirements
- Coordinate security testing
- Report security incidents

### With Savant Architect
- Review security architecture
- Validate security controls
- Ensure secure design patterns
- Coordinate security testing

### With QA Director
- Define security testing strategy
- Coordinate penetration testing
- Validate security requirements
- Review security test results

### With DevOps Lead
- Ensure secure deployment
- Coordinate security monitoring
- Validate infrastructure security
- Review security configurations

## Continuous Improvement

### Security Updates
- **Regular Security Reviews**: Monthly security assessments
- **Threat Intelligence**: Stay current with threat landscape
- **Security Training**: Regular team security training
- **Security Tools**: Continuous evaluation of security tools

### Security Monitoring
- **Real-time Monitoring**: Continuous security monitoring
- **Incident Analysis**: Learn from security incidents
- **Threat Hunting**: Proactive threat detection
- **Security Metrics**: Track security performance
