# Changelog

All notable changes to the GST Billing Web App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-02

### Added
- Initial release of GST Billing Web App
- Multi-tenant architecture with shop management
- Secure authentication system with JWT tokens
- Customer and product master data management
- Professional invoice generation with dynamic line items
- Automatic GST calculation (CGST/SGST/IGST)
- PDF invoice generation using xhtml2pdf
- Web print preview with optimized layout
- QR code integration for payment
- Bank details and terms & conditions in invoices
- Invoice listing and search functionality
- GST summary reports
- Customer ledger tracking
- Settings management for shop profile, logo, and bank details
- Support for multiple tax rates (5%, 12%, 18%, 28%)
- Discount management (Advance Cash Discount)
- Number to words conversion for amounts
- Previous and current balance tracking
- E-way bill information support
- Professional invoice layout matching Indian GST standards

### Technical Features
- FastAPI backend with async support
- SQLAlchemy ORM with migration support
- Jinja2 templating engine
- Responsive design with modern CSS
- PostgreSQL support for production
- SQLite for local development
- Comprehensive error handling and validation
- Password hashing with bcrypt
- CORS middleware configuration

### Documentation
- Comprehensive README with setup instructions
- Deployment guide (DEPLOYMENT.md)
- Project architecture documentation
- Environment configuration examples

## [Unreleased]

### Planned
- Email invoice delivery
- SMS notifications
- Advanced analytics dashboard
- Multi-currency support
- Inventory management integration
- Payment gateway integration
- Mobile app support

---

## Version History

**[1.0.0]** - Initial Release (December 2, 2025)
