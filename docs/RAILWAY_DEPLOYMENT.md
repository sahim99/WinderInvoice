# Deploying GST Billing App to Railway.app

This guide will help you deploy the GST Billing Web App to Railway.app with PostgreSQL database.

## Prerequisites

- Railway.app account ([railway.app](https://railway.app))
- GitHub account with your repository
- (Optional) S3-compatible storage for file uploads (recommended for production)

---

## Quick Start Deployment

### 1. Create New Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `WinderInvoice` repository
5. Railway will detect the Dockerfile and start building

### 2. Add PostgreSQL Database

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be injected automatically

### 3. Configure Environment Variables

In Railway project settings, add these environment variables:

#### Required Variables:

```bash
# Security (CRITICAL - generate a strong random key!)
SECRET_KEY=<generate-random-string-here>

# Environment
ENVIRONMENT=production
DEBUG=false

# Storage (Recommended: S3 for production)
STORAGE_PROVIDER=s3  # or "local" for testing

# If using S3 (Recommended):
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
# Optional: Use Cloudflare R2 (free tier available)
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com

# PDF Engine
PDF_ENGINE=xhtml2pdf

# Port (Railway sets this automatically)
PORT=8000
```

#### Generate SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy!

1. Click **"Deploy"** in Railway dashboard
2. Wait for build to complete (~5-10 minutes first time)
3. Railway will provide you a URL: `https://your-app.up.railway.app`

---

## Storage Configuration

### Option A: S3-Compatible Storage (Recommended)

**Why S3?** Railway doesn't provide persistent file storage. Using S3 ensures your uploads (logos, QR codes) are safe.

#### Cloudflare R2 (Recommended - Free Tier):

1. Create Cloudflare account
2. Go to R2 Object Storage
3. Create a new bucket
4. Generate API tokens
5. Add credentials to Railway environment variables:

```bash
STORAGE_PROVIDER=s3
S3_BUCKET=your-bucket-name
S3_REGION=auto
S3_ACCESS_KEY_ID=your-r2-access-key
S3_SECRET_ACCESS_KEY=your-r2-secret-key
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

#### AWS S3:

```bash
STORAGE_PROVIDER=s3
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-aws-access-key
S3_SECRET_ACCESS_KEY=your-aws-secret-key
```

### Option B: Local Storage (Not Recommended for Production)

```bash
STORAGE_PROVIDER=local
```

⚠️ **Warning**: Files will be lost when Railway restarts your service!

---

## Database Migrations

The app automatically creates tables on startup using the `entrypoint.sh` script.

### Manual Migration (if needed):

```bash
# Connect to Railway shell
railway run python

# In Python shell:
from app.database import engine, Base
from app import models
Base.metadata.create_all(bind=engine)
```

---

## Initial Setup After Deployment

### 1. Create Admin User

Visit: `https://your-app.up.railway.app/auth/setup`

This will create:
- Default shop
- Admin user: `admin@example.com` / `admin123`

### 2. Change Default Password

1. Login with default credentials
2. Go to Settings → Profile
3. Change password immediately

### 3. Configure Shop Details

1. Go to Settings → Shop Settings
2. Upload logo
3. Add bank details
4. Configure QR code for payments

---

## Monitoring & Logs

### View Logs:

1. In Railway dashboard, go to your project
2. Click on **"web"** service
3. Click **"Deployments"** tab
4. Click on latest deployment
5. View logs in real-time

### Common Issues:

**Database Connection Failed:**
- Ensure PostgreSQL database is added
- Check `DATABASE_URL` is set

**File Uploads Not Working:**
- Verify `STORAGE_PROVIDER=s3`
- Check S3 credentials are correct
- Test S3 bucket permissions

**PDF Generation Issues:**
- Check Chromium is installed in Docker
- Verify fonts are available
- Check entrypoint.sh logs

---

## Custom Domain

1. In Railway dashboard, go to Settings
2. Click **"Domains"**
3. Click **"Custom Domain"**
4. Add your domain (e.g., `invoice.yourdomain.com`)
5. Add CNAME record in your DNS:
   ```
   CNAME  invoice  <railway-domain>.up.railway.app
   ```

---

## Scaling & Performance

### Vertical Scaling:
Railway automatically allocates resources based on your plan.

### Horizontal Scaling:
Add more web workers in `entrypoint.sh`:

```bash
--workers 8  # Increase from 4 to 8
```

### Database Optimization:
- Add indexes to frequently queried columns
- Use connection pooling (already configured)
- Monitor query performance

---

## Backup Strategy

### Database Backups:

Railway provides automatic PostgreSQL backups. To create manual backup:

```bash
# Connect via Railway CLI
railway connect postgres

# Create backup
pg_dump $DATABASE_URL > backup.sql
```

### File Backups:

If using S3, configure lifecycle policies in your S3 bucket.

---

## Cost Estimation

- **Railway Starter Plan**: $5/month (includes PostgreSQL)
- **Cloudflare R2**: Free for up to 10GB storage
- **Total**: ~$5/month for small-medium business

---

## Security Checklist

- [ ] Changed default admin password
- [ ] Set strong SECRET_KEY
- [ ] Configured S3 with proper permissions
- [ ] Enabled HTTPS (automatic with Railway)
- [ ] Reviewed CORS settings
- [ ] Set DEBUG=false in production
- [ ] Configured database backups

---

## Support

For Railway-specific issues:
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

For app-specific issues:
- Check application logs
- Review README.md
- Open issue on GitHub

---

## Useful Railway CLI Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run python manage.py

# Open deployed app
railway open
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes (Auto) | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | Application secret key |
| `ENVIRONMENT` | No | development | Environment name |
| `DEBUG` | No | false | Debug mode |
| `PORT` | No (Auto) | 8000 | Application port |
| `STORAGE_PROVIDER` | No | local | Storage backend (local/s3) |
| `S3_BUCKET` | If S3 | - | S3 bucket name |
| `S3_REGION` | If S3 | us-east-1 | S3 region |
| `S3_ACCESS_KEY_ID` | If S3 | - | S3 access key |
| `S3_SECRET_ACCESS_KEY` | If S3 | - | S3 secret key |
| `S3_ENDPOINT_URL` | If R2/MinIO | - | Custom S3 endpoint |
| `PDF_ENGINE` | No | xhtml2pdf | PDF generation engine |

---

## Next Steps

After successful deployment:

1. ✅ Test invoice creation
2. ✅ Generate sample PDF
3. ✅ Upload shop logo
4. ✅ Configure email notifications (if needed)
5. ✅ Set up monitoring/alerting
6. ✅ Configure backups
7. ✅ Add custom domain

Your GST Billing App is now live! 🚀
