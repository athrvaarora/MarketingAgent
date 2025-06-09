# Marketing Package Download Agent

An AI-powered browser automation system for systematically downloading marketing packages from real estate websites.

## 🎯 Overview

This system uses browser-use with Gemini 2.0 Flash to automatically:
1. Read property URLs from a checklist CSV
2. Visit each property page
3. Fill out contact forms
4. Download marketing packages (PDFs)
5. Track progress and handle errors

## 📋 Files Created

### Core System Files:
- `marketing_agent.py` - Main agent script
- `marketing_agent.env` - Configuration file (update this!)
- `marketing_checklist_20250607_231412.csv` - Property tracking checklist
- `test_agent.py` - Setup verification script

### Data Files:
- `sitemap_combined.json` - Source property data (197 properties across 5 websites)
- `marketing_packages/` - Download destination folder

## ⚙️ Setup Instructions

### 1. Configure Environment Variables

Edit `marketing_agent.env` and update:

```bash
# REQUIRED: Add your Gemini API key
GOOGLE_API_KEY="your-actual-gemini-api-key-here"

# UPDATE: Contact information for Levy Retail
LEVY_NAME="Your Name"
LEVY_EMAIL="your.email@domain.com"  
LEVY_PHONE="555-123-4567"

# OPTIONAL: Adjust settings
DOWNLOAD_FOLDER="marketing_packages"
TIMEOUT_SECONDS=300
```

### 2. Test Setup

```bash
source .venv/bin/activate
python test_agent.py
```

Expected output:
- ✅ Checklist file found (197 properties)
- ✅ Environment file found  
- ✅ Google API key is set
- ✅ Levy contact info configured
- ✅ Download folder created

## 🚀 Running the Agent

### Start Download Session:

```bash
source .venv/bin/activate
python marketing_agent.py
```

### What Happens:

1. **Reads Checklist**: Finds first unvisited property
2. **Opens Browser**: Visible browser window (headless=False)
3. **Navigates**: Goes to property URL
4. **Fills Form**: Clicks "VIEW PACKAGE", fills contact info
5. **Downloads**: Clicks direct download link for PDF
6. **Updates Tracking**: Marks visited=YES, downloaded=YES
7. **Repeats**: Processes next property

## 📊 Progress Tracking

The system tracks progress in `marketing_checklist_20250607_231412.csv`:

| Column | Purpose |
|--------|---------|
| `visited` | YES/NO - Has page been visited |
| `downloaded` | YES/NO - Was package downloaded |
| `download_status` | PENDING/IN_PROGRESS/SUCCESS/FAILED |
| `marketing_files_found` | Description of files found |
| `notes` | Success/failure details |
| `error_message` | Error details if failed |
| `last_attempt` | Timestamp of last processing |

## 🏢 Website Groups

Currently implemented:
- ✅ **www.levyretail.com** (48 properties) - Levy Retail workflow

Planned for future:
- ⏳ **tag-industrial.com** (24 properties)
- ⏳ **securenetlease.com** (5 properties) 
- ⏳ **cegadvisors.com** (29 properties)
- ⏳ **themansourgroup.com** (91 properties)

## 🔧 Levy Retail Workflow

The Levy Retail implementation follows this specific process:

1. **Navigate** to property page
2. **Find** red "VIEW PACKAGE" button (left side)
3. **Click** button to open modal form
4. **Fill** form fields:
   - Name: From `LEVY_NAME` env var
   - Email: From `LEVY_EMAIL` env var (intentionally fake)
   - Phone: From `LEVY_PHONE` env var
5. **Submit** form
6. **Wait** for "Thank you!" confirmation
7. **Click** "TO DOWNLOAD THE PACKAGE DIRECTLY, CLICK HERE."
8. **Download** PDF file directly (don't rely on email)

## 📁 File Organization

Downloads are saved as:
```
marketing_packages/
├── www_levyretail_com_314_south_main.pdf
├── www_levyretail_com_abrams_forest_shopping_center.pdf
└── ...
```

Naming convention: `{website_group}_{property_name}.pdf`

## 🛠️ Troubleshooting

### Common Issues:

**"Google API key needs to be configured"**
- Update `GOOGLE_API_KEY` in `marketing_agent.env`

**"Agent completed but file not found"**
- Browser successfully ran but download failed
- Check browser download folder
- Verify PDF actually downloaded

**Timeout errors**
- Increase `TIMEOUT_SECONDS` in env file
- Some properties may take longer to process

**Form filling failures**
- Website structure may have changed
- Agent will retry once automatically

### Recovery:

The system is designed to resume from where it left off:
- Processed properties are marked `visited=YES`
- Failed properties can be retried by changing `visited=NO`
- Check `download_status` and `error_message` for details

## 🎮 Testing the Workflow

1. **Single Property Test**:
   ```bash
   # Runs on first unvisited property only
   python marketing_agent.py
   ```

2. **Check Progress**:
   ```bash
   # View the updated checklist
   head -5 marketing_checklist_20250607_231412.csv
   ```

3. **Monitor Downloads**:
   ```bash
   # Check download folder
   ls -la marketing_packages/
   ```

## 🔄 Resume Capability

The agent automatically resumes from the first unvisited property:

- **Fresh Start**: All properties have `visited=NO`
- **Resume**: Start from first property with `visited=NO`
- **Selective Retry**: Manually change specific properties to `visited=NO`

## ⚡ Performance Settings

Default settings (adjustable in `marketing_agent.env`):
- **Timeout**: 300 seconds per property
- **Max Steps**: 15 browser actions per property
- **Max Properties**: 1 (for testing, remove limit for full run)
- **Retry Logic**: 1 automatic retry on failure

## 🚨 Important Notes

1. **Fake Email**: The email addresses are intentionally fake/bogus
2. **Direct Download**: Always use "CLICK HERE" direct download link
3. **Visible Browser**: Browser runs in visible mode for monitoring
4. **Fresh Context**: New browser instance per property (avoids context issues)
5. **Progress Tracking**: All activity logged in CSV checklist

## 🎯 Ready to Test!

Your marketing package download agent is ready. To test the workflow:

1. ✅ Update your Gemini API key in `marketing_agent.env`
2. ✅ Verify contact information is correct
3. ✅ Run `python test_agent.py` to confirm setup
4. ✅ Run `python marketing_agent.py` to start downloading

The system will process the first Levy Retail property and demonstrate the complete workflow! 