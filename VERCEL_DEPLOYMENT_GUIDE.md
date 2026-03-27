# VidyaGuru AI Learning Platform - Vercel & Render Deployment Guide

## 🚀 Complete Deployment Setup

This guide covers deploying the VidyaGuru platform with:
- **Frontend**: Next.js on Vercel
- **Backend**: FastAPI on Render
- **Database**: PostgreSQL on Render
- **Cache**: Redis on Render

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Vercel account (logged in)
- ✅ Render account (render.com)
- ✅ GitHub repository with your code pushed
- ✅ Google Gemini API key (from makersuite.google.com)
- ✅ Git installed locally

---

## Part 1: Backend Deployment on Render

### Step 1: Prepare Backend Code

1. Push your code to GitHub (main branch)
2. Verify Dockerfile exists in `/backend` directory
3. Check `backend/requirements.txt` has all dependencies

### Step 2: Create Render Account & Project

1. Go to https://render.com
2. Sign up / Log in
3. Click **"New +"** → **"Blueprint"**
4. Select **"Public Git repository"**
5. Paste your GitHub repository URL
6. Click **"Connect"**

### Step 3: Deploy with Blueprint

1. Render will read `render.yaml` automatically
2. Configure environment variables:
   - `DB_PASSWORD`: Generate a strong password (e.g., `openssl rand -base64 32`)
   - `REDIS_PASSWORD`: Generate a strong password
   - `SECRET_KEY`: Generate a strong key (use openssl or Python)
   - `GEMINI_API_KEY`: Paste your Google Gemini API key

3. Click **"Deploy Blueprint"**
4. Wait for all three services to deploy (usually 5-10 minutes)

### Step 4: Verify Backend Deployment

1. Once deployed, copy the backend URL: `https://vidyaguru-backend-xxxxx.onrender.com`
2. Test the health endpoint:
   ```
   curl https://vidyaguru-backend-xxxxx.onrender.com/health
   ```
3. Should return: `{"status":"healthy"}`

### Step 5: Note Backend URL

**Save this URL** - you'll need it for frontend deployment:
```
BACKEND_URL = https://vidyaguru-backend-xxxxx.onrender.com
```

⚠️ **Important**: Render's free tier has a 15-minute inactivity timeout. Deploy to a Hobby plan for production or add a pinger service.

---

## Part 2: Frontend Deployment on Vercel

### Step 1: Push Code to GitHub

```bash
# From your project root
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Import Project to Vercel

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Select **"Import Git Repository"**
4. Search and select your GitHub repository
5. Click **"Import"**

### Step 3: Configure Build Settings

In Vercel's project settings:

**Build & Development Settings:**
- **Framework Preset**: Next.js
- **Build Command**: `cd frontend && npm run build`
- **Output Directory**: `frontend/.next/standalone`
- **Install Command**: `cd frontend && npm install`

### Step 4: Add Environment Variables

1. Go to **Settings** → **Environment Variables**
2. Add the following:

```
NEXT_PUBLIC_API_URL = https://vidyaguru-backend-xxxxx.onrender.com
```

3. Click **"Save"**

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (usually 2-3 minutes)
3. Once deployed, you'll get a URL like: `https://vidyaguru-xxxxx.vercel.app`

### Step 6: Update Backend CORS

Your backend needs to know the frontend URL for CORS:

1. Go to Render Dashboard
2. Open the **backend** service
3. Go to **Settings** → **Environment Variables**
4. Update `CORS_ORIGINS`:
   ```
   ["https://vidyaguru-xxxxx.vercel.app"]
   ```
5. Click **"Save"** and the backend will redeploy

---

## Part 3: Post-Deployment Verification

### 1. Test Frontend

```
https://vidyaguru-xxxxx.vercel.app
```

- Page should load without errors
- Check browser console (F12) for any API errors

### 2. Test Authentication

```bash
# Register a new user
curl -X POST https://vidyaguru-backend-xxxxx.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

### 3. Test API Endpoints

```bash
# Get user profile (replace TOKEN with real JWT)
curl -X GET https://vidyaguru-backend-xxxxx.onrender.com/api/v1/users/profile \
  -H "Authorization: Bearer TOKEN"
```

### 4. Check Logs

**Vercel Logs:**
- Dashboard → Project → Deployments → Click deployment → Logs

**Render Logs:**
- Dashboard → backend service → Logs tab

---

## 🔒 Security Checklist

- [ ] All environment variables set (no hardcoded secrets)
- [ ] Database password is strong (20+ characters)
- [ ] JWT secret key is strong (32+ characters)
- [ ] CORS_ORIGINS matches your Vercel URL exactly
- [ ] GEMINI_API_KEY is valid and active
- [ ] Backend Dockerfile uses non-root user
- [ ] Frontend `.env.local` is in `.gitignore`
- [ ] SSL/TLS enabled (automatic on both platforms)

---

## 📊 Environment Variables Summary

### Backend (Render)
```
DATABASE_URL=postgresql://vidyaguru:PASSWORD@host:5432/vidyaguru
REDIS_URL=redis://:PASSWORD@host:6379
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-key-here
ENVIRONMENT=production
CORS_ORIGINS=["https://your-domain.vercel.app"]
LOG_LEVEL=INFO
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://vidyaguru-backend-xxxxx.onrender.com
```

---

## ⚙️ Configuration Files

### render.yaml
- Defines all three services (PostgreSQL, Redis, Backend API)
- Auto-creates and links services
- Handles environment variables

### vercel.json
- NextJob configuration for Vercel
- Build command and output directory
- Environment variable schema

---

## 🔧 Troubleshooting

### Issue: Frontend can't reach backend

**Solution:**
1. Check `NEXT_PUBLIC_API_URL` is correct in Vercel
2. Check `CORS_ORIGINS` in backend matches Vercel URL
3. Check browser console for CORS errors
4. Verify backend is running: curl the health endpoint

### Issue: Database connection error

**Solution:**
1. Check `DATABASE_URL` in Render backend service
2. Verify PostgreSQL service is running (check Render dashboard)
3. Check database credentials match
4. Run migrations manually if needed

### Issue: API returns 401 Unauthorized

**Solution:**
1. Verify JWT token is being sent
2. Check SECRET_KEY matches on backend
3. Ensure token wasn't expired
4. Check localStorage for valid token on frontend

### Issue: Gemini API errors

**Solution:**
1. Verify `GEMINI_API_KEY` is valid
2. Check quota limits on Google AI Studio
3. Ensure API is enabled in Google Cloud
4. Test API key locally first

---

## 📈 Monitoring & Scaling

### Render Scaling
- Upgrade from Free to Hobby plan ($7/month) for persistent database
- Use Render's auto-scaling for production workloads
- Monitor CPU/Memory in Render dashboard

### Vercel Scaling
- Automatic scaling included
- Pro plan ($20/month) for additional features
- Monitor functions in Vercel analytics

---

## 🚀 Next Steps

1. Test user registration and login flow
2. Test learning path enrollment
3. Test task completion and progress tracking
4. Monitor error logs in both platforms
5. Set up uptime monitoring (UptimeRobot, Render's built-in)
6. Configure custom domain (optional)

---

## 📞 Support Resources

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Next.js Deployment: https://nextjs.org/learn/deployment
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

---

## 🎉 Deployment Complete!

Your VidyaGuru platform is now live and accessible to users worldwide.

**Frontend**: https://vidyaguru-xxxxx.vercel.app
**Backend API**: https://vidyaguru-backend-xxxxx.onrender.com

Happy learning! 🚀
