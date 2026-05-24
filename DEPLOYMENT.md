# Automated Deployment Setup

This project uses **GitHub Actions** to automatically deploy to Railway and configure environment variables.

## One-Time Setup

### 1. Get Railway Token
```bash
railway login
railway token
```

### 2. Add to GitHub Secrets
1. Go to: https://github.com/RishiR92/asmi-gtm-outreach/settings/secrets/actions
2. Click **New repository secret**
3. Name: `RAILWAY_TOKEN`
4. Value: `<paste your railway token from step 1>`
5. Save

### 3. That's It! 🚀

## What Happens on Each Git Push

✅ Automatic deployment to Railway  
✅ SERPAPI_KEY set in Railway environment  
✅ Backend service redeploys with new code  
✅ Scout triggered to populate communities with emails  
✅ 3-day schedule fills automatically  

## Manual Trigger (if needed)

```bash
git push origin main
```

This will automatically:
1. Deploy latest code to Railway
2. Set SERPAPI_KEY environment variable
3. Run the scout to find 154 communities with emails
4. Fill production database with 177 eligible leads

## No Local Steps Required

Everything happens automatically on Git push:
- Code deploys to production
- Environment variables are set
- Scout runs and populates communities
- Schedule fills for Monday/Tuesday/Wednesday sends
