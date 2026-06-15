# 🎬 Parth Edits — Portfolio & Booking Platform

A full-stack portfolio website for a professional video editor, featuring a cinematic design, admin dashboard, blog, pricing, and client enquiry system.

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML, CSS, Vanilla JS |
| **Backend** | Python, FastAPI, SQLAlchemy |
| **Database** | SQLite (dev) |
| **Auth** | JWT (HS256) with bcrypt password hashing |
| **Email** | Gmail SMTP (optional) |
| **Deployment** | Vercel (frontend) + Render (backend) |

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
| `SMTP_USER` | ❌ | Gmail address for sending email notifications |
| `SMTP_PASSWORD` | ❌ | Gmail App Password ([generate here](https://support.google.com/accounts/answer/185833)) |
| `EMAIL_FROM` | ❌ | Sender email address |
| `EMAIL_TO` | ❌ | Recipient email for enquiry notifications |
| `CORS_ORIGINS` | ❌ | Comma-separated allowed origins. Default: `*` |

---

## 🌐 Deployment

### Frontend → Vercel

1. Push this repository to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project → Select your repo
3. Vercel will auto-detect the `vercel.json` configuration
4. **Important**: Update `vercel.json` to replace `YOUR-BACKEND-URL` with your actual Render backend URL
5. Deploy!

### Backend → Render

1. Go to [render.com](https://render.com) → New Web Service → Connect your repo
2. Render will auto-detect the `render.yaml` configuration
3. Set the following environment variables in the Render dashboard:
   - `SECRET_KEY` — generate a strong random key
   - `ADMIN_USERNAME` — your admin username
   - `ADMIN_PASSWORD` — a strong admin password
   - `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO` — if using email notifications
4. Deploy!

### Post-Deployment

After both are deployed:

1. Update `vercel.json`: Replace `https://YOUR-BACKEND-URL.onrender.com` with your actual Render URL
2. Update `CORS_ORIGINS` on Render to include your Vercel frontend URL
3. Redeploy both services

---

## 📁 Project Structure

```
portfolio/
├── app/                    # FastAPI backend
│   ├── core/
│   │   ├── auth.py         # JWT authentication
│   │   ├── config.py       # Settings (from env vars)
│   │   ├── database.py     # SQLAlchemy setup
│   │   └── email.py        # SMTP email sender
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
