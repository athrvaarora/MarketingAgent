# 🚀 Deployment Guide

This guide covers how to deploy the Marketing Package Agent to various platforms.

## 📋 Pre-Deployment Checklist

- [ ] ✅ Code pushed to GitHub: [MarketingAgent Repository](https://github.com/athrvaarora/MarketingAgent)
- [ ] 🔑 OpenAI API Key obtained
- [ ] 🗄️ PostgreSQL database ready (Railway recommended)
- [ ] 📝 Environment variables configured
- [ ] 🧪 Local testing completed

---

## 🚀 Railway Deployment (Recommended)

Railway is the best option since you likely already have PostgreSQL there.

### 1. Connect GitHub Repository

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose `athrvaarora/MarketingAgent`

### 2. Configure Environment Variables

In Railway dashboard, go to your project → **Variables** tab:

```env
# Required Variables
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
DATABASE_URL=postgresql://username:password@host:port/database

# Contact Information
LEVYRETAIL_NAME=John Smith
LEVYRETAIL_EMAIL=john@yourcompany.com
LEVYRETAIL_PHONE=555-123-4567

TAG_INDUSTRIAL_FIRST_NAME=John
TAG_INDUSTRIAL_LAST_NAME=Smith
TAG_INDUSTRIAL_COMPANY=Your Company Name
TAG_INDUSTRIAL_PHONE=555-123-4567
TAG_INDUSTRIAL_EMAIL=john@yourcompany.com
TAG_INDUSTRIAL_CONTACT_TYPE=Principal

NETLEASEADVISORYGROUP_FIRST_NAME=John
NETLEASEADVISORYGROUP_LAST_NAME=Smith
NETLEASEADVISORYGROUP_EMAIL=john@yourcompany.com
```

### 3. Configure Build Settings

Railway should auto-detect Python. If not, add:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Port**: `5001` (or Railway auto-assigns)

### 4. Deploy

Railway will automatically deploy when you push to GitHub!

**🎉 Your app will be available at: `https://your-app-name.railway.app`**

---

## 🔧 Heroku Deployment

### 1. Prepare Heroku Files

Create `Procfile` in your repository:
```
web: python app.py
```

Create `runtime.txt`:
```
python-3.11.9
```

### 2. Deploy to Heroku

```bash
# Install Heroku CLI first: https://devcenter.heroku.com/articles/heroku-cli

# Login and create app
heroku login
heroku create your-marketing-agent

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-proj-your-key
heroku config:set DATABASE_URL=postgresql://...
# ... add all other env vars

# Deploy
git push heroku main
```

---

## 🌊 DigitalOcean App Platform

### 1. Create App

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Connect your GitHub repository

### 2. Configure App

```yaml
# .do/app.yaml (add to your repo)
name: marketing-agent
services:
- name: web
  source_dir: /
  github:
    repo: athrvaarora/MarketingAgent
    branch: main
  run_command: python app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    value: ${OPENAI_API_KEY}
  - key: DATABASE_URL
    value: ${DATABASE_URL}
  http_port: 5001
```

---

## 🏗️ Render Deployment

### 1. Connect Repository

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### 2. Configure Service

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Environment**: `Python 3`

### 3. Add Environment Variables

Add all required environment variables in Render dashboard.

---

## 🔍 Post-Deployment Verification

### 1. Check Application Health

Visit your deployed URL and verify:

- [ ] ✅ Home page loads with dashboard
- [ ] 🗄️ Database connection works (check database page)
- [ ] 🔄 Real-time updates function
- [ ] 📊 Progress statistics display
- [ ] 🤖 Can submit test jobs

### 2. Test Core Functionality

```bash
# Test API endpoints
curl https://your-app.railway.app/api/progress
curl https://your-app.railway.app/api/properties
```

### 3. Database Setup

Make sure to run the database setup script once:

```bash
# SSH into your deployment or run locally pointing to production DB
python create_supabase_table.py
```

---

## 🛠️ Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for GPT-4o | `sk-proj-...` |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `LEVYRETAIL_NAME` | ✅ Yes | Contact name for Levy Retail | `John Smith` |
| `LEVYRETAIL_EMAIL` | ✅ Yes | Contact email for Levy Retail | `john@company.com` |
| `LEVYRETAIL_PHONE` | ✅ Yes | Contact phone for Levy Retail | `555-123-4567` |
| `TAG_INDUSTRIAL_*` | ✅ Yes | Contact info for Tag Industrial | See example above |
| `NETLEASEADVISORYGROUP_*` | ✅ Yes | Contact info for NLAG | See example above |

---

## 🚨 Troubleshooting

### Common Issues

**❌ Database Connection Error**
```
Solution: Check DATABASE_URL format and network connectivity
```

**❌ OpenAI API Error**
```
Solution: Verify API key is correct and has credits
```

**❌ Browser/Playwright Issues**
```
Solution: Platform may not support browser automation
Recommendation: Use Railway or VPS with full OS support
```

**❌ File Storage Issues**
```
Solution: Check write permissions in deployment environment
Note: Downloaded files may not persist on some platforms
```

### Platform Limitations

| Platform | Browser Support | File Storage | WebSocket | Cost |
|----------|----------------|--------------|-----------|------|
| **Railway** | ✅ Full | ✅ Persistent | ✅ Yes | 💰 Low |
| **Heroku** | ⚠️ Limited | ❌ Ephemeral | ✅ Yes | 💰 Medium |
| **Render** | ✅ Full | ⚠️ Limited | ✅ Yes | 💰 Low |
| **DigitalOcean** | ✅ Full | ✅ Persistent | ✅ Yes | 💰 Medium |

**🎯 Railway is recommended** for full functionality including browser automation and file persistence.

---

## 📱 Mobile & Responsive Design

The web interface is fully responsive and works on:

- 📱 Mobile phones (iOS/Android)
- 📟 Tablets 
- 💻 Laptops
- 🖥️ Desktop computers

---

## 🔒 Security Considerations

- 🔐 Never commit `marketing_agent.env` to version control
- 🔑 Use environment variables for all sensitive data
- 🌐 Consider implementing basic authentication for production
- 🛡️ Use HTTPS in production (most platforms provide this automatically)
- 📊 Monitor API usage and costs
- 🚨 Set up error monitoring and alerting

---

## 📈 Scaling Considerations

- 🔄 Current design processes one property at a time
- 📊 Database can handle thousands of properties
- ⚡ Consider Redis for session storage in high-traffic scenarios
- 🔀 Add load balancing for multiple instances
- 📱 API rate limiting to prevent abuse

---

## 🤝 Support

- 📚 Check the [main README](README.md) for detailed documentation
- 🐛 Report issues on [GitHub Issues](https://github.com/athrvaarora/MarketingAgent/issues)
- 💬 For deployment help, include platform details and error logs

**Happy Deploying! 🚀** 