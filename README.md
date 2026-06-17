# 🎬 NPJ Productions — Portfolio & Booking Platform

A production-ready full-stack portfolio website for NPJ Productions (a videography and video editing studio), featuring a cinematic design, automated asset minification/build step, client-side & server-side honeypot spam protection, customizable SMTP notifications, admin dashboard, blog, pricing, and a client enquiry system.

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML, CSS, Vanilla JS (Minified via custom build step) |
| **Backend** | Python, FastAPI, SQLAlchemy |
| **Database** | SQLite (dev) |
| **Auth** | JWT (HS256) with bcrypt password hashing |
| **Storage** | Local filesystem, AWS S3, or Cloudinary CDN |
| **Email** | SMTP / TLS (Gmail, Resend, SendGrid, etc.) |
| **Deployment** | Vercel (monorepo frontend server + python API routes) |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/ShahParth29/portfolio.git
cd portfolio

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your real values (see Environment Variables section)

# 5. Run the development server
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000` to view the site.

---

## 🔐 Environment Variables

All sensitive configuration is managed through environment variables. **Never commit real values to git.**

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | Database connection string. Default: `sqlite:///./portfolio.db` |
| `SECRET_KEY` | ✅ | JWT signing key. Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ADMIN_USERNAME` | ✅ | Admin dashboard login username |
| `ADMIN_PASSWORD` | ✅ | Admin dashboard login password (use a strong password!) |
| `SMTP_HOST` | ❌ | SMTP server host. Default: `smtp.gmail.com` |
| `SMTP_PORT` | ❌ | SMTP server port. Default: `587` |
| `SMTP_USER` | ❌ | SMTP login username/email for sending notifications |
| `SMTP_PASSWORD` | ❌ | SMTP login password or App Password |
| `SMTP_USE_TLS` | ❌ | Connect securely using TLS. Default: `true` |
| `EMAIL_FROM` | ❌ | Sender email address |
| `EMAIL_TO` | ❌ | Recipient email for enquiry notifications |
| `CORS_ORIGINS` | ❌ | Comma-separated allowed origins. Default: `*` |
| `STORAGE_BACKEND` | ❌ | `local` (default), `cloudinary`, or `s3` |
| `CLOUDINARY_CLOUD_NAME` | ❌* | Cloudinary cloud name (*required if using Cloudinary) |
| `CLOUDINARY_API_KEY` | ❌* | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | ❌* | Cloudinary API secret |

---

## 🌐 Deployment

This application is fully compatible with Vercel serverless deployment (handling the frontend assets and python backend API as serverless routes).

### Quick Vercel Setup

1. **Push this repository to GitHub**
2. **Import to Vercel**: Connect your repo on [Vercel](https://vercel.com).
3. **Configure Settings**:
   - Vercel automatically detects the configuration in `vercel.json`.
   - Set the build command to `python build.py` (handles HTML/CSS/JS minification).
   - Set the output directory to `dist` (holds optimized static files).
4. **Environment Variables**: Add your production env keys (`ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SECRET_KEY`, `SMTP_USER`, etc.) in the Vercel project settings.
5. **Deploy!** Vercel will build the frontend assets using Python, minify them, and mount the FastAPI backend on the `/api/*` pathways.

---

## 📁 Project Structure

```
portfolio/
├── app/                    # FastAPI backend
│   ├── core/
│   │   ├── auth.py         # JWT authentication
│   │   ├── config.py       # Settings (from env vars)
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── email.py        # SMTP email sender
│   │   └── storage.py      # File storage (local / Cloudinary)
│   ├── models/
│   │   └── models.py       # Database models
│   ├── routers/
│   │   ├── blog.py         # Blog CRUD endpoints
│   │   ├── contact.py      # Enquiry & auth endpoints
│   │   ├── pricing.py      # Pricing CRUD endpoints
│   │   ├── settings.py     # Site settings endpoints
│   │   └── videos.py       # Video CRUD + upload
│   ├── schemas/
│   │   └── schemas.py      # Pydantic validation schemas
│   └── main.py             # App entry point + seed data
├── frontend/               # Static frontend
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js          # API client + site settings
│   │   ├── admin.js        # Admin dashboard logic
│   │   └── gallery.js      # Portfolio gallery
│   ├── index.html          # Home page
│   ├── portfolio.html      # Portfolio gallery
│   ├── about.html          # About page
│   ├── pricing.html        # Pricing page
│   ├── blog.html           # Blog listing
│   ├── post.html           # Single blog post
│   ├── contact.html        # Contact / booking form
│   └── admin.html          # Admin dashboard
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── render.yaml             # Render deployment config
├── vercel.json             # Vercel deployment config
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🔒 Security Features

- **JWT Authentication** — Admin endpoints protected with Bearer tokens
- **bcrypt Password Hashing** — Passwords never stored in plain text at rest
- **Rate Limiting** — Login attempts limited to 5 per minute per IP
- **Security Headers** — X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **CORS Protection** — Configurable allowed origins
- **Admin Panel Hidden from Search Engines** — `noindex, nofollow` meta tag
- **Environment-Based Config** — No credentials in source code

---

## 📄 License

MIT License — feel free to fork and customize for your own portfolio.
