# GST Billing Web App

A professional GST billing and invoicing application built with FastAPI and modern web technologies. Designed specifically for furniture shops and retail businesses in India, featuring comprehensive invoice management, PDF generation, and GST compliance.

## ✨ Features

### 🔐 Authentication & Multi-Tenancy
- Secure login/logout system for shop staff and admins
- Multi-tenant architecture supporting multiple shops (currently single shop enabled)
- Role-based access control

### 📊 Master Data Management
- **Customer Management**: Maintain customer database with GSTIN, billing/shipping addresses
- **Product Management**: Track products with HSN codes, pricing, and tax rates
- Comprehensive data validation and error handling

### 🧾 Advanced GST Invoicing
- Create professional invoices with dynamic line items
- Automatic GST calculation (CGST/SGST for intra-state, IGST for inter-state)
- Support for multiple tax rates (5%, 12%, 18%, 28%)
- Discount management (Advance Cash Discount)
- Number to words conversion for amount display
- Previous and current balance tracking
- E-way bill information support

### 🖨️ Professional Invoice Printing
- **Web Preview**: Responsive print-ready layout with modern styling
- **PDF Generation**: High-quality PDF output using xhtml2pdf
- **Layout Features**:
  - A4 size optimized layout
  - Company logo and branding
  - QR code integration for payments
  - Professional header with bordered box
  - Itemized table with proper column alignment
  - Bank details and terms & conditions
  - Signature sections (Receiver, Prepared By, Checked By, Authorized Signatory)
- **Customizable**: Logo position, border colors, and styling

### 📈 Reports & Analytics
- Invoice listing with search and filters
- GST summary reports
- Customer ledger tracking
- Transaction history

### ⚙️ Settings & Configuration
- Shop profile management
- Logo upload and customization
- Bank details configuration
- QR code integration
- Tax and business settings

## 🛠️ Tech Stack

- **Backend**: Python 3.9+ with FastAPI
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **ORM**: SQLAlchemy with Alembic migrations
- **Templating**: Jinja2 templates
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **PDF Generation**: xhtml2pdf
- **Authentication**: Passlib (bcrypt) + python-jose (JWT)

## 🚀 Local Setup

### Prerequisites
- Python 3.9 or higher
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GST-App
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and update:
   # - SECRET_KEY (generate a secure random key)
   # - DATABASE_URL (if using PostgreSQL)
   ```

5. **Initialize the database** (first-time setup)
   ```bash
   # The app will auto-create tables on first run
   # Or use Alembic for migrations:
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://localhost:8000`
   - **Initial Setup**: Visit `http://localhost:8000/auth/setup` to create the default shop and admin user
   - **Default Login**: `admin@example.com` / `admin123`

## 📁 Project Structure

```
GST-App/
├── app/
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic layer
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── invoices/     # Invoice templates (print, PDF)
│   │   └── ...
│   ├── static/           # Static assets (CSS, JS, images)
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   └── main.py           # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

## 🎨 Key Customizations

### Invoice Template
The invoice templates (`print.html` and `print_pdf.html`) support:
- Custom logo positioning (left/right)
- Adjustable border colors and thickness
- Flexible layout with responsive design
- Company branding elements

### Styling
- CSS located in `app/static/css/invoice_print.css`
- Optimized for both web preview and PDF generation
- Print-specific media queries

## 🔧 Configuration

### Shop Settings
Configure via the Settings page in the application:
- Business name and address
- GSTIN number
- Contact information
- Bank details
- Logo upload
- QR code for payments

### Environment Variables
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./gst_billing.db
# For PostgreSQL: postgresql://user:password@localhost/dbname
```

## 📦 Dependencies

Core packages:
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `xhtml2pdf` - PDF generation
- `jinja2` - Template engine
- `passlib` - Password hashing
- `python-jose` - JWT tokens

See `requirements.txt` for full list.

## 🚢 Deployment

### Production Deployment (Railway.app)

For detailed production deployment instructions with PostgreSQL and S3 storage:

📖 **See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** for complete Railway deployment guide

Quick steps:
1. Push code to GitHub
2. Create Railway project from GitHub repo
3. Add PostgreSQL database
4. Configure environment variables
5. Deploy automatically

### Local Development with Docker

For Docker-based local development setup:

📖 **See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** for complete Docker setup guide

Quick start:
```bash
docker-compose up --build
```

### Other Deployment Options

The app can be deployed to any platform supporting:
- Docker containers (Dockerfile included)
- Python WSGI servers (uses Gunicorn + Uvicorn)
- PostgreSQL database

Platforms tested:
- ✅ Railway.app (recommended)
- ✅ Heroku
- ✅ Digital Ocean App Platform
- ✅ AWS ECS/Fargate
- ✅ Google Cloud Run

## 🐛 Troubleshooting

### Common Issues

**PDF not generating?**
- Ensure `xhtml2pdf` is installed
- Check that logo files are accessible
- Verify CSS is properly embedded in PDF template

**Database errors?**
- Run migrations: `alembic upgrade head`
- Check database permissions
- Verify DATABASE_URL in `.env`

**Login not working?**
- Complete initial setup at `/auth/setup`
- Check if admin user exists in database
- Verify password hash compatibility

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

This is a private project. For questions or support, contact the development team.

## 📞 Support

For technical support or feature requests, please contact the project maintainer.

---

**Note**: This application is designed for Indian GST compliance. Ensure you comply with all local tax regulations and keep the software updated with the latest GST rules and rates.
