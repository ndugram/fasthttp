# Contributing to FastHTTP

Thank you for your interest in contributing to FastHTTP! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/ndugram/fasthttp.git
cd fasthttp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## 📝 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write clean, readable code
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fasthttp

# Run specific test file
pytest tests/test_client.py
```

### 4. Code Quality
```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Type checking
mypy fasthttp/
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📋 Coding Standards

### Code Style
- Follow PEP 8 guidelines
- Use type annotations
- Write descriptive docstrings
- Use meaningful variable names

### Commit Messages
Use conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

### Example:
```bash
git commit -m "feat: add support for custom headers in POST requests"
git commit -m "fix: resolve timeout issue in async client"
git commit -m "docs: update quick start guide with new examples"
```

## 🧪 Testing Guidelines

### Writing Tests
- Write tests for all new features
- Include both positive and negative test cases
- Use descriptive test names
- Mock external dependencies

### Test Categories
- **Unit tests** - Test individual functions/methods
- **Integration tests** - Test component interactions
- **End-to-end tests** - Test complete workflows

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_client.py

# With verbose output
pytest -v

# Skip slow tests
pytest -m "not slow"
```

## 📚 Documentation

### When to Update Documentation
- Adding new features
- Changing existing functionality
- Fixing bugs that affect user experience
- Adding new configuration options

### Documentation Types
- **README.md** - Overview and basic usage
- **API Reference** - Detailed method documentation
- **Examples** - Real-world use cases
- **Configuration Guide** - Advanced settings

## 🐛 Reporting Issues

### Bug Reports
Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Python version and environment
- Relevant error messages

### Feature Requests
- Describe the problem you're trying to solve
- Explain how this feature would help users
- Provide examples of how it would work

## 🔍 Code Review Process

### For Contributors
- Keep PRs focused and small
- Write clear PR descriptions
- Respond to feedback promptly
- Update tests and documentation

### For Reviewers
- Be constructive and respectful
- Check code quality and tests
- Verify documentation updates
- Test locally when possible

## 📦 Release Process

1. **Version Bump** - Update version in `pyproject.toml`
2. **Changelog** - Update `CHANGELOG.md`
3. **Tests** - Ensure all tests pass
4. **Documentation** - Verify docs are up to date
5. **Release** - Create GitHub release and publish to PyPI

## ❓ Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Documentation** - Check existing docs first

## 📋 Pull Request Checklist

Before submitting a PR:

- [ ] Code follows project style guidelines
- [ ] Tests added/updated for changes
- [ ] Documentation updated
- [ ] All tests pass locally
- [ ] Code is properly typed
- [ ] Commit messages are clear
- [ ] PR description explains changes

## 🎯 Areas for Contribution

### Beginner Friendly
- Documentation improvements
- Bug fixes
- Test coverage improvements
- Code formatting

### Advanced
- New HTTP methods
- Performance optimizations
- New features
- Security enhancements

## 🙏 Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors page
- Release notes for major features

Thank you for contributing to FastHTTP! 🚀
