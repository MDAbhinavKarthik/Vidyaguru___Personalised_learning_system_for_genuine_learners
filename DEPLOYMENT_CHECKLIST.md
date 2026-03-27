# VidyaGuru Deployment Checklist

## Pre-Deployment ✅

### Code Preparation
- [ ] All changes committed to git
- [ ] Code pushed to GitHub (main branch)
- [ ] No hardcoded secrets in code
- [ ] .gitignore excludes .env files
- [ ] Dockerfile exists in /backend
- [ ] requirements.txt is up-to-date
- [ ] package.json is up-to-date

### Account Setup
- [ ] Vercel account created and logged in
- [ ] Render account created and logged in
- [ ] GitHub repository connected to both platforms
- [ ] Google Gemini API key obtained

### Configuration Files  
- [ ] vercel.json created in root
- [ ] render.yaml created in root
- [ ] .env.production template created
- [ ] VERCEL_DEPLOYMENT_GUIDE.md reviewed

---

## Backend Deployment (Render) 🔧

### Step 1: Create Services
- [ ] Go to https://render.com/dashboard
- [ ] Click "New +" → "Blueprint"
- [ ] Connect GitHub repository
- [ ] Render reads render.yaml automatically

### Step 2: Configure Secrets
- [ ] Generate DB_PASSWORD (use deploy.ps1 script)
- [ ] Generate REDIS_PASSWORD (use deploy.ps1 script)
- [ ] Generate SECRET_KEY (use deploy.ps1 script)
- [ ] Enter GEMINI_API_KEY from Google Makersuite
- [ ] Add all to Render environment variables

### Step 3: Deploy
- [ ] Click "Deploy Blueprint"
- [ ] PostgreSQL service deploying...
- [ ] Redis service deploying...
- [ ] Backend API service deploying...
- [ ] All three services show "Live" status

### Step 4: Verify Backend
- [ ] Copy backend URL: https://vidyaguru-backend-XXXXX.onrender.com
- [ ] Test health endpoint: curl backend-url/health
- [ ] Returns: {"status":"healthy"}
- [ ] **Save backend URL for next step**

---

## Frontend Deployment (Vercel) 🎨

### Step 1: Import Project
- [ ] Go to https://vercel.com/dashboard
- [ ] Click "Add New" → "Project"
- [ ] Search and select GitHub repository
- [ ] Click "Import"

### Step 2: Configure Build
- [ ] Framework Preset: Next.js (auto-detected)
- [ ] Build Command: `cd frontend && npm run build`
- [ ] Output Directory: `frontend/.next/standalone`
- [ ] Install Command: `cd frontend && npm install`

### Step 3: Add Environment Variables
- [ ] Add: NEXT_PUBLIC_API_URL = [backend-url-from-render]
- [ ] Save environment variables
- [ ] No need to add SECRET_KEY (backend only)

### Step 4: Deploy
- [ ] Click "Deploy"
- [ ] Wait for build to complete
- [ ] Deployment successful
- [ ] **Copy frontend URL: https://vidyaguru-XXXXX.vercel.app**

---

## Post-Deployment Configuration 🔗

### Update Backend CORS
- [ ] Go to Render dashboard
- [ ] Open backend service
- [ ] Go to Settings → Environment Variables
- [ ] Update CORS_ORIGINS with Vercel URL
- [ ] Save (backend will redeploy)
- [ ] Wait for backend to be "Live" again

---

## Testing & Verification 🧪

### Frontend Tests
- [ ] Navigate to https://vidyaguru-XXXXX.vercel.app
- [ ] Page loads without errors
- [ ] No console errors (press F12)
- [ ] Navigation works (sidebar, routing)

### Backend Tests
- [ ] Test health endpoint: curl https://backend-url/health
- [ ] Test registration: POST /api/v1/auth/register
- [ ] Test login: POST /api/v1/auth/login
- [ ] Test protected route: GET /api/v1/users/profile

### API Integration Tests
- [ ] Login on frontend
- [ ] No CORS errors in console
- [ ] Dashboard loads data (Learning Paths, Tasks, etc.)
- [ ] Can create new tasks
- [ ] Can view analytics
- [ ] Mentor chat works

### Database Tests
- [ ] Can register new user
- [ ] User data persists
- [ ] Can login with credentials
- [ ] Can enroll in learning path
- [ ] Task completion tracked

---

## Monitoring Setup 📊

### Vercel Monitoring
- [ ] Set up error tracking (in Vercel dashboard)
- [ ] Configure alerts for deployment failures
- [ ] Monitor analytics and performance

### Render Monitoring
- [ ] Check logs regularly for errors
- [ ] Monitor database connections
- [ ] Monitor Redis usage
- [ ] Set up uptime monitoring

### Error Tracking
- [ ] Both dashboards show deployment logs
- [ ] Can view error logs in real-time
- [ ] New Relic integration (optional)
- [ ] Sentry integration (optional)

---

## Security & Production 🔒

### Security Checklist
- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS enabled on both Vercel and Render
- [ ] CORS properly configured
- [ ] No database credentials in code
- [ ] API keys rotated and secure
- [ ] Rate limiting configured on backend
- [ ] Database backups enabled on Render
- [ ] SSH keys configured for database access

### Performance Optimization
- [ ] Frontend: Image optimization in Next.js
- [ ] Backend: Database query optimization
- [ ] Cache enabled (Redis)
- [ ] CDN enabled on Vercel (default)
- [ ] Compression enabled

### Backup Strategy
- [ ] Database automatic backups on Render
- [ ] Git repository backed up on GitHub
- [ ] Secrets management documented
- [ ] Disaster recovery plan in place

---

## Scaling & Upgrades 📈

### If Free Tier Is Insufficient

**Render Upgrades:**
- [ ] Upgrade database to Hobby plan ($7/month)
- [ ] Persistent database across redeploys
- [ ] Better resource allocation
- [ ] Community support

**Vercel Upgrades:**
- [ ] Pro plan ($20/month) for more functions/bandwidth
- [ ] Priority support
- [ ] Advanced analytics

### Performance Improvements
- [ ] Enable database indexing on frequently queried columns
- [ ] Implement query caching
- [ ] Optimize API responses
- [ ] Add CDN caching headers

---

## Success Criteria ✨

- ✅ Frontend accessible and responsive
- ✅ Backend API responding to requests
- ✅ Database persisting data
- ✅ Authentication working (register/login)
- ✅ Learning paths loading
- ✅ Tasks creating and tracking
- ✅ Analytics displaying data
- ✅ Mentor chat responding
- ✅ No console errors
- ✅ No hardcoded data showing

---

## Post-Launch Actions 🎉

- [ ] Share public URL with users
- [ ] Set up analytics/usage monitoring
- [ ] Configure custom domain (optional)
- [ ] Set up email notifications
- [ ] Daily log reviews
- [ ] Weekly performance reviews
- [ ] Monthly security audits

---

## Troubleshooting 🔧

### Common Issues & Solutions

**Issue**: Frontend can't reach backend
- Solution: Check NEXT_PUBLIC_API_URL is correct in Vercel env vars

**Issue**: CORS errors
- Solution: Update backend CORS_ORIGINS with Vercel URL

**Issue**: Database connection failed
- Solution: Check DATABASE_URL, restart PostgreSQL service on Render

**Issue**: Authentication not working
- Solution: Check SECRET_KEY is same on backend, tokens are being sent

**Issue**: Gemini API returning errors
- Solution: Verify GEMINI_API_KEY is valid, check API quota limits

---

## Support & Resources 📚

- Render Documentation: https://render.com/docs
- Vercel Documentation: https://vercel.com/docs
- Next.js Deployment: https://nextjs.org/docs/deployment
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- GitHub Actions: https://docs.github.com/en/actions

---

**Status**: [ ] All checks complete - Ready for production!
