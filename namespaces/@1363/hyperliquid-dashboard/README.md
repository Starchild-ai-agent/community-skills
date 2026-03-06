# 📊 Hyperliquid Dashboard — Deployment Guide

Quick deployment options for your position monitoring dashboard.

---

## 🚀 Deploy to Vercel (Recommended)

### Method 1: Vercel CLI
```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to dashboard folder
cd skills/hyperliquid-dashboard

# Deploy
vercel deploy --prod

# You'll get a URL like: https://hl-dashboard-xyz.vercel.app
```

### Method 2: Drag & Drop (No CLI)
1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Drag the `hyperliquid-dashboard` folder into the upload area
4. Click "Deploy"
5. Done! Get your URL instantly

### Method 3: GitHub + Auto-Deploy
```bash
# Initialize git (if not already)
git init
git add skills/hyperliquid-dashboard
git commit -m "Add HL dashboard"

# Push to GitHub
git remote add origin git@github.com:yourusername/hl-dashboard.git
git push -u origin main

# Connect to Vercel:
# 1. Go to vercel.com
# 2. Import your GitHub repo
# 3. Auto-deploys on every push
```

---

## 🌐 Access Your Dashboard

Once deployed, you can access it:
- **On desktop:** Open the Vercel URL in any browser
- **On mobile:** Bookmark the URL or add to home screen
- **In workspace:** Use the local preview URL

**Example URLs:**
- `https://your-dashboard.vercel.app`
- `https://hl-monitor.vercel.app`

---

## 🔧 Custom Domain (Optional)

Want a custom domain like `positions.yourdomain.com`?

1. In Vercel dashboard, go to your project settings
2. Click "Domains"
3. Add your domain
4. Update DNS records as instructed
5. Done!

---

## 📱 Mobile Optimization

The dashboard is already mobile-responsive. For best experience:
1. Open on mobile browser
2. Tap "Share" → "Add to Home Screen"
3. Opens like a native app

---

## 🔒 Security Notes

- **Public data only** — Dashboard only shows publicly available Hyperliquid data
- **No authentication** — Anyone with the URL can view any wallet
- **Don't share sensitive wallets** — Only monitor wallets you're comfortable being public
- **Rate limiting** — Vercel may rate-limit very frequent requests

---

## 💡 Pro Tips

1. **Multiple dashboards** — Deploy separate instances for different wallets
2. **Custom refresh rates** — Edit `index.html` to change default intervals
3. **Add alerts** — Integrate with Telegram/email for PnL thresholds
4. **White-label** — Change colors/logo in `index.html` for branding

---

**Need help?** Check the main `SKILL.md` for full documentation.
