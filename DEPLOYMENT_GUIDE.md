# 🚀 ASIE Deployment Guide

## 📋 Prerequisites

✅ Git repository initialized
✅ Code committed (65 files, 4896 lines)
✅ Project structure ready

## Option 1: Quick Deploy with Render + Vercel (RECOMMENDED)

### Step 1: Push to GitHub

```bash
# Create a new repository on GitHub: https://github.com/new
# Name it: asie-dashboard
# Then run:

cd "c:\Users\dashi\OneDrive\Desktop\New folder (2)"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/asie-dashboard.git
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. Go to https://render.com (sign up/login with GitHub)
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repository: `asie-dashboard`
4. Configure:
   - **Name**: `asie-backend`
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Root Directory**: leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
5. Add Environment Variable:
   - `PYTHON_VERSION` = `3.11.0`
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. Copy your backend URL: `https://asie-backend.onrender.com`

### Step 3: Update Frontend API URL

Before deploying frontend, update the API base URL:

```bash
# Edit dashboard/src/lib/api.js
# Change baseURL from 'http://127.0.0.1:8000' to your Render URL
```

### Step 4: Deploy Frontend to Vercel

```bash
cd dashboard
npm install -g vercel  # Install Vercel CLI

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Or use Vercel Dashboard:
1. Go to https://vercel.com (sign up/login with GitHub)
2. Click **"Add New..." → "Project"**
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `dashboard`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Click **"Deploy"**
6. Your dashboard will be live at: `https://asie-dashboard.vercel.app`

---

## Option 2: Deploy with Railway (Fullstack)

Railway can host both frontend and backend in one place.

### Step 1: Push to GitHub (same as Option 1)

### Step 2: Deploy to Railway

1. Go to https://railway.app (sign up/login with GitHub)
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Select `asie-dashboard`
4. Railway will detect both services:
   - Backend (Python FastAPI)
   - Frontend (Node.js)

5. Configure Backend:
   - Click on the service
   - Add Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variable: `PYTHON_VERSION=3.11.0`
   - Generate Domain

6. Configure Frontend:
   - Click on the service
   - Set Root Directory: `dashboard`
   - Build Command: `npm run build && npm run preview`
   - Generate Domain

7. Update frontend API URL in `dashboard/src/lib/api.js` to Railway backend URL
8. Redeploy frontend

---

## Option 3: Manual Deploy with Heroku

### Backend to Heroku

```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create asie-backend
git push heroku main
heroku open
```

### Frontend to Netlify

```bash
cd dashboard
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

---

## 🔧 Post-Deployment Configuration

### 1. Update Frontend API URL

After deploying backend, update `dashboard/src/lib/api.js`:

```javascript
const API_BASE_URL = 'https://your-backend-url.onrender.com';
```

### 2. Configure CORS (if needed)

Update `api/main.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Environment Variables

For production, consider adding:
- `API_BASE_URL` (frontend)
- `DATABASE_URL` (if using database)
- `SECRET_KEY` (for authentication)

---

## 🧪 Test Deployment

After deployment, test these endpoints:

**Backend:**
- https://your-backend-url.onrender.com/api/meta
- https://your-backend-url.onrender.com/api/geo/states
- https://your-backend-url.onrender.com/docs (API documentation)

**Frontend:**
- https://your-frontend-url.vercel.app
- Test state dropdown
- Test metric buttons
- Test time-series chart
- Test anomaly detection

---

## 📊 Deployment Status Checklist

- [ ] GitHub repository created and code pushed
- [ ] Backend deployed (Render/Railway/Heroku)
- [ ] Frontend API URL updated
- [ ] Frontend deployed (Vercel/Netlify/Railway)
- [ ] CORS configured
- [ ] All API endpoints tested
- [ ] Dashboard UI fully functional

---

## 🆘 Troubleshooting

### Backend not starting
- Check Render/Railway logs
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` uses correct command
- Check Python version (3.11)

### Frontend build errors
- Run `npm install` in dashboard folder
- Verify `package.json` has all dependencies
- Check Node.js version compatibility

### API 404 errors
- Verify backend URL in `api.js`
- Check CORS settings
- Ensure all routes have `/api` prefix

### Data not loading
- Check if parquet files are in git (should be included)
- Verify file paths in `api/main.py`
- Check backend logs for errors

---

## 🎯 Next Steps

1. **Create GitHub repository**: https://github.com/new
2. **Choose deployment platform**:
   - Render + Vercel (easiest, free tier)
   - Railway (fullstack, unified dashboard)
   - Heroku + Netlify (established platforms)
3. **Follow steps above** for your chosen platform
4. **Share the live URLs** with your team

---

**Estimated Deployment Time**: 15-30 minutes
**Cost**: Free tier available on all platforms
**Maintenance**: Auto-deploy on git push (CI/CD enabled)
