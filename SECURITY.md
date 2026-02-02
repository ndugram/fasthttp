# Security Policy

## 🔒 Reporting Security Vulnerabilities

We take the security of FastHTTP seriously. If you discover a security vulnerability, please report it responsibly.

### 📧 How to Report

**Do NOT** create public GitHub issues for security vulnerabilities.

Instead, please email us directly at: **n7for8572@gmail.com**

### 📝 What to Include

Please include the following information in your report:

- **Description** - A clear description of the vulnerability
- **Reproduction** - Steps to reproduce the issue
- **Impact** - Potential impact of the vulnerability
- **Environment** - Python version, OS, FastHTTP version
- **Proof of Concept** - If applicable, provide a proof of concept

### 🕐 Response Timeline

- **Initial Response** - Within 48 hours
- **Investigation** - Within 7 days
- **Resolution** - Timeline depends on complexity, typically 30-90 days
- **Public Disclosure** - Coordinated disclosure after fix

## 🛡️ Security Measures

### Code Security

- **Input Validation** - All user inputs are validated
- **Error Handling** - No sensitive information in error messages
- **Dependencies** - Regular security updates for all dependencies
- **Code Review** - All changes reviewed by maintainers

### Dependencies

We monitor our dependencies for security vulnerabilities:

- **aiohttp** - Core HTTP client library
- **annotated-doc** - Documentation tool
- **Development Tools** - pytest, ruff, mypy

### Logging Security

- No sensitive data logged
- Request/response bodies are not logged by default
- Debug mode can be disabled in production

## 🔍 Security Best Practices

### For Users

#### 1. Keep Updated
```bash
pip install --upgrade fasthttp
```

#### 2. Secure Configuration
```python
# ✅ Good: Use environment variables
import os
app = FastHTTP(
    get_request={
        "headers": {"Authorization": f"Bearer {os.getenv('API_TOKEN')}"},
        "timeout": 10,
    },
)

# ❌ Bad: Hardcoded credentials
app = FastHTTP(
    get_request={
        "headers": {"Authorization": "Bearer my-secret-token"},
    },
)
```

#### 3. Timeout Configuration
```python
# Always set appropriate timeouts
app = FastHTTP(get_request={"timeout": 30})

# Prevent DoS with reasonable limits
app = FastHTTP(get_request={"timeout": 10})  # 10 seconds max
```

#### 4. Input Validation
```python
@app.post(url="https://api.example.com/data", json=data)
async def create_data(resp: Response):
    # Validate response
    if resp.status != 200:
        return f"Error: {resp.status}"
    
    try:
        result = resp.json()
        # Validate response structure
        if not isinstance(result, dict):
            return "Invalid response format"
        return "Success"
    except Exception:
        return "Invalid JSON response"
```

#### 5. Error Handling
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=False)  # Disable debug in production

@app.get(url="https://api.example.com/data")
async def safe_request(resp: Response):
    try:
        if resp.status == 200:
            return resp.json()
        else:
            # Don't expose internal details
            return f"Request failed with status {resp.status}"
    except Exception:
        # Generic error message
        return "Request processing failed"
```

### For Developers

#### 1. Development Environment
```bash
# Use virtual environments
python -m venv venv
source venv/bin/activate

# Install dependencies securely
pip install -e ".[dev]"
```

#### 2. Security Testing
```bash
# Run security checks
pip install safety bandit

# Check for known vulnerabilities
safety check

# Static security analysis
bandit -r fasthttp/
```

#### 3. Code Review Checklist
- [ ] No hardcoded credentials
- [ ] Input validation present
- [ ] Error messages don't leak info
- [ ] Timeouts configured appropriately
- [ ] Dependencies are up to date

## 🚨 Known Security Considerations

### 1. Timeout Configuration
**Issue**: Without timeouts, requests can hang indefinitely.

**Solution**: Always configure timeouts:
```python
app = FastHTTP(get_request={"timeout": 30})
```

### 2. Debug Mode in Production
**Issue**: Debug mode may expose sensitive information in logs.

**Solution**: Disable debug in production:
```python
# Production
app = FastHTTP(debug=False)

# Development only
app = FastHTTP(debug=True)
```

### 3. Certificate Validation
**Issue**: Disabling SSL verification can expose to MITM attacks.

**Solution**: Always verify SSL certificates (default behavior).

### 4. Information Disclosure
**Issue**: Error messages might reveal internal information.

**Solution**: Use generic error messages in production.

## 🔄 Security Updates

### Automatic Updates
We regularly release security updates. Enable notifications:

- Watch the GitHub repository
- Subscribe to releases on GitHub
- Follow our security advisories

### Manual Updates
```bash
# Check for updates
pip list --outdated | grep fasthttp

# Update to latest version
pip install --upgrade fasthttp
```

## 📊 Security Audit

### Last Audit Date
- **Date**: February 2026
- **Scope**: Core functionality, dependencies, configuration
- **Result**: No critical vulnerabilities found
- **Next Audit**: August 2026

### Audit Scope
- [x] Input validation
- [x] Error handling
- [x] Logging security
- [x] Dependency security
- [x] Configuration security
- [x] Documentation security

## 🆘 Emergency Procedures

### Critical Vulnerability Response
1. **Immediate Assessment** - Within 4 hours
2. **Emergency Patch** - Within 24 hours
3. **Security Advisory** - Within 48 hours
4. **Public Disclosure** - After patch deployment

### Contact Information
- **Security Email**: security@fasthttp.dev
- **Maintainer**: @ndugram (GitHub)
- **Response Time**: 48 hours maximum

## 📋 Security Checklist

### For Contributors
- [ ] No credentials in code
- [ ] Input validation implemented
- [ ] Error handling secure
- [ ] Tests include security cases
- [ ] Documentation updated

### For Users
- [ ] Using latest version
- [ ] Timeouts configured
- [ ] Debug mode disabled in production
- [ ] Environment variables for secrets
- [ ] Regular dependency updates

## 🔗 Useful Resources

### Security Tools
- **Safety** - Dependency vulnerability scanner
- **Bandit** - Security linter for Python
- **Semgrep** - Static analysis security scanner

### Best Practices
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Guidelines](https://python.org/dev/security/)
- [aiohttp Security Notes](https://docs.aiohttp.org/en/stable/client_reference.html#security)

## 📝 Changelog

### Security Fixes
- **v0.1.0** - Initial release with basic security measures
- Future versions will include security fixes in CHANGELOG.md

---

**Thank you for helping keep FastHTTP secure!** 🔒

If you have questions about this security policy, please contact us at security@fasthttp.dev
