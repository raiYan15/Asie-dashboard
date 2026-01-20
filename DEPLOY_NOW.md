# ⚡ Quick Deployment Commands

## 🔥 FASTEST PATH (Copy-Paste Ready)

### Step 1: Push to GitHub (2 minutes)

```bash
# 1. Create repo on GitHub: https://github.com/new (name it: asie-dashboard)

# 2. Run these commands (replace YOUR_USERNAME):
cd "c:\Users\dashi\OneDrive\Desktop\New folder (2)"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/asie-dashboard.git
git push -u origin main
```

---

### Step 2: Deploy Backend to Render (5 minutes)

**Option A: One-Click Deploy**

Click this button after creating your GitHub repo:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Option B: Manual Deploy**

1. Go to https://dashboard.render.com
2. Click **"New +" → "Web Service"**
3. Connect GitHub → Select `asie-dashboard`
4. Settings:
   ```
   Name: asie-backend
   Runtime: Python 3
   Build: pip install -r requirements.txt
   Start: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```
5. Click **Deploy** → Wait 5 mins
6. Copy URL: `https://asie-backend-xxxx.onrender.com`

---

### Step 3: Deploy Frontend to Vercel (3 minutes)

**Option A: Command Line (Fastest)**

```bash
cd dashboard
npm install -g vercel
vercel login
vercel --prod
```

When prompted:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing? **N**
- Project name? **asie-dashboard**
- Directory? **./dashboard**
- Override settings? **N**

**Option B: GitHub Integration**

1. Go to https://vercel.com/new
2. Import `asie-dashboard` repo
3. Settings:
   ```
   Root Directory: dashboard
   Framework: Vite
   Build: npm run build
   Output: dist
   ```
4. Add Environment Variable:
   ```
   VITE_API_URL = https://asie-backend-xxxx.onrender.com
   ```
5. Deploy → Get URL: `https://asie-dashboard.vercel.app`

---

## 🎯 Your Live Links

After deployment, you'll have:

- **Frontend**: https://asie-dashboard.vercel.app
- **Backend API**: https://asie-backend-xxxx.onrender.com
- **API Docs**: https://asie-backend-xxxx.onrender.com/docs

---

## 🔄 Auto-Deploy Setup (Optional)

Both Render and Vercel will auto-deploy when you push to GitHub:

```bash
# Make a change
git add .
git commit -m "Update feature"
git push

# Both services will automatically redeploy!
```

---

## 🧪 Test Your Deployment

```bash
# Test backend
curl https://asie-backend-xxxx.onrender.com/api/meta

# Test frontend (open in browser)
start https://asie-dashboard.vercel.app
```

---

## ⏱️ Total Time: ~10 minutes

| Step | Time | Platform |
|------|------|----------|
| Push to GitHub | 2 min | GitHub |
| Deploy Backend | 5 min | Render |
| Deploy Frontend | 3 min | Vercel |
| **Total** | **10 min** | - |

---

## 💡 Pro Tips

1. **Free Tier Limits**:
   - Render: 750 hours/month, sleeps after 15 min inactivity
   - Vercel: Unlimited deploys, 100GB bandwidth/month

2. **Keep Services Awake**:
   - Use a service like UptimeRobot to ping your backend every 5 minutes

3. **Custom Domain** (optional):
   - Vercel: Add custom domain in project settings
   - Render: Add custom domain in service settings

4. **Environment Variables**:
   - Store sensitive data in platform dashboards
   - Never commit API keys to GitHub

---

## 🆘 Quick Fixes

**Backend won't start?**
```bash
# Check logs in Render dashboard
# Verify requirements.txt has all packages
```

**Frontend shows errors?**
```bash
# Update API URL in Vercel env variables
# Redeploy
```

**CORS errors?**
```python
# Update api/main.py CORS origins to include your Vercel URL
```

---

**Ready to deploy?** Follow Steps 1-3 above! 🚀
