# Contributing to GST Billing Web App

Thank you for your interest in contributing to the GST Billing Web App! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear title and description
- Steps to reproduce the problem
- Expected vs actual behavior
- Screenshots if applicable
- System information (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome! Please include:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test your changes**
   - Ensure all existing tests pass
   - Add new tests for new features
   - Test manually in development environment

5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of your changes"
   ```
   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Refactor:` for code refactoring
   - `Docs:` for documentation changes

6 **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide clear title and description
   - Reference any related issues
   - Wait for review and address feedback

## Development Setup

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Local Development
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/WinderInvoice.git
cd WinderInvoice

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
uvicorn app.main:app --reload
```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Comment complex logic

### Python Code Example
```python
def calculate_gst(amount: float, tax_rate: float, is_interstate: bool) -> dict:
    """
    Calculate GST components for an invoice item.
    
    Args:
        amount: Taxable amount
        tax_rate: GST rate (e.g., 18 for 18%)
        is_interstate: True for IGST, False for CGST/SGST
    
    Returns:
        Dictionary with CGST, SGST, and IGST values
    """
    gst_amount = (amount * tax_rate) / 100
    
    if is_interstate:
        return {"cgst": 0, "sgst": 0, "igst": gst_amount}
    else:
        half_gst = gst_amount / 2
        return {"cgst": half_gst, "sgst": half_gst, "igst": 0}
```

## Project Structure

```
GST-App/
├── app/
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic
│   ├── templates/      # HTML templates
│   ├── static/         # CSS, JS, images
│   ├── models.py       # Database models
│   └── main.py         # Application entry point
├── tests/              # Test files
├── docs/               # Documentation
└── requirements.txt    # Dependencies
```

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Test both success and failure cases

## Documentation

- Update README.md for significant changes
- Add inline comments for complex code
- Update CHANGELOG.md
- Create/update API documentation if needed

## Questions?

Feel free to create an issue for any questions or clarifications needed.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to making GST Billing Web App better!
