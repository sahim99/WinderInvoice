# Local Development Quick Start

This guide will help you run the GST Billing App locally using Docker.

## Prerequisites

- Docker Desktop installed
- Docker Compose installed
- Git

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/sahim99/WinderInvoice.git
cd WinderInvoice
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - Other settings as needed
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

This will start:
- PostgreSQL database on port 5432
- Web application on port 8000

### 4. Access Application

Open your browser: `http://localhost:8000`

### 5. Initial Setup

Visit: `http://localhost:8000/auth/setup`

This creates:
- Default shop
- Admin user: `admin@example.com` / `admin123`

## Development Without Docker

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database

```bash
# For SQLite (easier for local dev)
# Set in .env:
DATABASE_URL=sqlite:///./gst_billing.db
```

### 4. Run Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build

# Access database
docker-compose exec db psql -U gst_user -d gst_billing

# Access app shell
docker-compose exec web bash

# Reset everything
docker-compose down -v  # Removes volumes (data loss!)
```

## Development Tips

### Hot Reload

The docker-compose.yml is configured for hot reload. Changes to Python files will automatically restart the server.

### Database Migrations

```bash
# If you modify models.py, restart the service
docker-compose restart web
```

### Debugging

View detailed logs:
```bash
docker-compose logs web
docker-compose logs db
```

### Testing PDF Generation

1. Create an invoice
2. Click "Download PDF"
3. Check if PDF renders correctly

If issues:
- Check Chromium is installed: `docker-compose exec web chromium --version`
- Check fonts: `docker-compose exec web fc-list | grep DejaVu`

## File Structure

```
GST-App/
├── app/
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── templates/        # HTML templates
│   ├── static/           # CSS, JS, images
│   │   └── uploads/      # User uploads (local dev)
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   ├── models.py         # SQLAlchemy models
│   ├── storage.py        # File storage abstraction
│   └── main.py           # FastAPI app
├── Dockerfile            # Production Docker image
├── docker-compose.yml    # Local development setup
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── entrypoint.sh         # Container startup script
```

## Common Issues

### Port Already in Use

```bash
# Change port in docker-compose.yml:
ports:
  - "8001:8000"  # Use 8001 instead
```

### Database Connection Failed

```bash
# Restart database
docker-compose restart db

# Check database is healthy
docker-compose ps
```

### File Upload Not Working

For local development:
- Ensure `STORAGE_PROVIDER=local` in .env
- Directory `app/static/uploads/` should be writable

## Next Steps

- Read [README.md](README.md) for features
- Check [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for production deployment
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
