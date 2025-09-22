# YouTube2Sheets Security Guidelines

## 🛡️ Critical Security Information

**This document outlines security best practices for the YouTube2Sheets project to prevent credential exposure and maintain system integrity.**

---

## 🚨 IMMEDIATE SECURITY CHECKLIST

### ✅ Before Every Commit
- [ ] No `.env` files in the repository
- [ ] No `service-account-*.json` files tracked
- [ ] No `oauth-token*.json` files tracked
- [ ] No API keys in code or configuration files
- [ ] All sensitive data in environment variables only

### ✅ If You Accidentally Commit Sensitive Data
1. **IMMEDIATELY** remove from git history
2. **ROTATE** all compromised credentials
3. **NOTIFY** the team of the security incident
4. **UPDATE** this security documentation

---

## 🔐 Credential Management

### Required Credentials
The YouTube2Sheets project requires the following credentials:

| Credential Type | Storage Method | Example File | Status |
|----------------|----------------|--------------|--------|
| **YouTube API OAuth** | Environment Variables | `.env` | ✅ Protected |
| **Google Sheets Service Account** | Environment Variables | `.env` | ✅ Protected |
| **API Keys** | Environment Variables | `.env` | ✅ Protected |
| **Refresh Tokens** | Environment Variables | `.env` | ✅ Protected |

### Environment Variables Setup
Create a `.env` file in the project root (this file is gitignored):

```bash
# YouTube API Configuration
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here

# Google Sheets Configuration
GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=path_to_service_account.json
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_SHEET_TAB_NAME=your_tab_name_here

# Application Configuration
MIN_VIDEO_DURATION_SECONDS=60
KEYWORD_FILTER=tutorial, how to, python programming, data science
KEYWORD_FILTER_MODE=include
LOG_LEVEL=INFO
```

---

## 🚫 Files NEVER to Commit

### Critical Security Files
- `.env` - Environment variables
- `service-account-*.json` - Google Service Account keys
- `oauth-token*.json` - OAuth tokens
- `client_secret*.json` - OAuth client secrets
- `*.key`, `*.pem`, `*.p12`, `*.pfx` - Private keys
- `credentials.json` - Any credential files
- `secrets.json` - Secret configuration

### Cache and Temporary Files
- `etag-cache.json` - API cache data
- `*.cache` - Any cache files
- `*.log` - Log files (may contain sensitive data)
- `tmp/`, `temp/` - Temporary directories

---

## 🔍 Security Verification Commands

### Check for Sensitive Files
```bash
# Check for common sensitive file patterns
find . -name "*.env*" -o -name "*service-account*.json" -o -name "*oauth*.json" -o -name "*.key" -o -name "*.pem"

# Check git status for sensitive files
git status --porcelain | grep -E "\.(env|key|json|pem|p12|pfx)$"

# Check git history for sensitive files
git log --name-only --pretty=format: | grep -E "\.(env|key|json|pem|p12|pfx)$"
```

### Verify .gitignore is Working
```bash
# Create a test sensitive file
echo "test-key=12345" > test.env

# Check if it's ignored
git status --porcelain | grep test.env

# Clean up
rm test.env
```

---

## 🛠️ Development Security Practices

### 1. Credential Setup
- Always use environment variables for sensitive data
- Never hardcode API keys or secrets in source code
- Use `.env.example` as a template for required variables
- Rotate credentials regularly

### 2. Code Review Security Checklist
- [ ] No hardcoded credentials in code
- [ ] All sensitive data in environment variables
- [ ] No debug logs containing sensitive information
- [ ] Proper error handling without exposing internals
- [ ] Input validation for all user-provided data

### 3. API Security
- Use HTTPS for all API communications
- Implement proper rate limiting
- Validate all API responses
- Handle authentication errors gracefully
- Log security events appropriately

---

## 🚨 Incident Response

### If Credentials Are Exposed
1. **Immediate Actions:**
   - Remove sensitive data from git history
   - Rotate all compromised credentials
   - Notify team members immediately
   - Review recent commits for other sensitive data

2. **Cleanup Commands:**
   ```bash
   # Remove file from git history
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch path/to/sensitive/file' --prune-empty --tag-name-filter cat -- --all
   
   # Force push to remote (DANGEROUS - coordinate with team)
   git push origin --force --all
   ```

3. **Post-Incident:**
   - Update security documentation
   - Review and strengthen .gitignore
   - Conduct team security training
   - Implement additional security measures

---

## 📋 Security Audit Checklist

### Weekly Security Review
- [ ] Review recent commits for sensitive data
- [ ] Verify .gitignore is comprehensive
- [ ] Check for new credential files
- [ ] Validate environment variable usage
- [ ] Review access logs and permissions

### Monthly Security Review
- [ ] Rotate all API credentials
- [ ] Review and update security documentation
- [ ] Audit third-party dependencies
- [ ] Test security incident response procedures
- [ ] Update team on security best practices

---

## 📞 Security Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| **Project Manager** | PM | Security incident coordination |
| **Lead Engineer** | LE | Technical security implementation |
| **DevOps Lead** | DevOps | Infrastructure security |
| **QA Director** | QA | Security testing and validation |

---

## 🔗 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Google Cloud Security](https://cloud.google.com/security)
- [YouTube API Security](https://developers.google.com/youtube/v3/guides/authentication)

---

**Remember: Security is everyone's responsibility. When in doubt, ask the team before committing sensitive data.**