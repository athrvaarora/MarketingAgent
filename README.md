# Marketing Package Agent

An AI-powered browser automation system that systematically downloads marketing packages from real estate websites with a beautiful web interface for monitoring and control.

![Marketing Package Agent](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **🤖 AI Browser Automation**: Uses GPT-4o and browser-use framework for intelligent web navigation
- **💜 Beautiful Web Interface**: Modern neon purple/white themed dashboard with real-time updates
- **🗄️ PostgreSQL Database**: Railway cloud database for persistent progress tracking
- **🔄 Real-time Updates**: WebSocket-powered live progress monitoring
- **📁 Multi-site Support**: Handles Levy Retail, Tag Industrial, and Net Lease Advisory Group
- **🎭 Headless Mode**: Optional headless browser operation for background processing
- **📊 Progress Analytics**: Detailed statistics and completion tracking
- **📱 Responsive Design**: Mobile-friendly interface with modern animations

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Flask Backend   │    │ Marketing Agent │
│   (Vue.js)      │◄──►│  (Python)        │◄──►│ (Browser-use)   │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • API Endpoints  │    │ • GPT-4o        │
│ • Real-time UI  │    │ • WebSocket      │    │ • Playwright    │
│ • Job Control   │    │ • Job Management │    │ • PDF Download  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │ Railway         │
                        │ PostgreSQL      │
                        │ Database        │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ 
- OpenAI API Key
- Railway PostgreSQL Database
- Chrome/Chromium browser (for automation)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd marketing-package-agent
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or use uv (recommended)
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

### 3. Environment Configuration

Create `marketing_agent.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Levy Retail Contact Information
LEVYRETAIL_NAME=John Smith
LEVYRETAIL_EMAIL=john@example.com
LEVYRETAIL_PHONE=555-123-4567

# Tag Industrial Contact Information
TAG_INDUSTRIAL_FIRST_NAME=John
TAG_INDUSTRIAL_LAST_NAME=Smith
TAG_INDUSTRIAL_COMPANY=Real Estate Investor
TAG_INDUSTRIAL_PHONE=555-123-4567
TAG_INDUSTRIAL_EMAIL=john@example.com
TAG_INDUSTRIAL_CONTACT_TYPE=Investor

# Net Lease Advisory Group Contact Information
NETLEASEADVISORYGROUP_FIRST_NAME=John
NETLEASEADVISORYGROUP_LAST_NAME=Smith
NETLEASEADVISORYGROUP_EMAIL=john@example.com
```

### 4. Database Setup

```bash
# Run the database creation script
python3 create_supabase_table.py
```

### 5. Launch Web Interface

```bash
# Start the Flask web server
python3 app.py
```

**🎉 Open your browser to: http://localhost:5001**

## 📖 Detailed Setup Guide

### Database Setup (Railway PostgreSQL)

1. **Create Railway Account**: Go to [railway.app](https://railway.app)
2. **Create PostgreSQL Database**: 
   - Click "New Project" → "Add PostgreSQL"
   - Copy the connection URL
3. **Update Environment**: Add the DATABASE_URL to your `marketing_agent.env`
4. **Initialize Database**: Run `python3 create_supabase_table.py`

### Contact Information Setup

The system uses different contact forms for each website:

- **Levy Retail**: Name, Email, Phone
- **Tag Industrial**: First/Last Name, Company, Phone, Email, Contact Type
- **Net Lease Advisory Group**: First/Last Name, Email

Update the contact information in `marketing_agent.env` with your details.

### OpenAI API Key

1. Get your API key from [OpenAI Platform](https://platform.openai.com)
2. Add it to `marketing_agent.env` as `OPENAI_API_KEY`

## 🖥️ Web Interface Guide

### Home Page
- **Control Panel**: Submit jobs with filters and options
- **Progress Overview**: Real-time statistics by website group
- **Live Output**: Terminal-style job monitoring
- **Recent Downloads**: Quick access to downloaded PDFs

### Downloads Page
- **PDF Grid**: Organized by website groups
- **Search & Filter**: Find specific marketing packages
- **File Details**: Size, date, and direct access
- **Click-to-Open**: PDFs open in new tabs

### Database Page
- **Real-time Table**: All properties with live status updates
- **Advanced Filtering**: Filter by status, website group
- **Status Badges**: Visual progress indicators
- **Property Links**: Direct access to source URLs

## 📸 Screenshots

### Home Dashboard
![Home Dashboard](Screenshots/Home.png)
*The main control panel with job submission form, real-time progress overview, live output terminal, and recent downloads section*

### Downloads Page
![Downloads Page](Screenshots/Downloads.png)
*PDF grid view organized by website groups with search functionality, file details, and direct PDF access*

### Database Management
![Database Page](Screenshots/Database.png)
*Real-time property tracking with status indicators, filtering options, and comprehensive property information*

## 🔧 Command Line Usage

### Basic Commands

```bash
# Process all properties
python3 marketing_package_agent.py

# Process specific website group
python3 marketing_package_agent.py -g LR    # Levy Retail
python3 marketing_package_agent.py -g TI    # Tag Industrial
python3 marketing_package_agent.py -g NLAG  # Net Lease Advisory Group

# Limit number of properties
python3 marketing_package_agent.py -g LR -m 5

# Run in headless mode
python3 marketing_package_agent.py --headless

# Combine options
python3 marketing_package_agent.py -g TI -m 10 --headless
```

### Reset Database

```bash
# Reset all properties to initial state
python3 reset_database.py
```

## 📁 Project Structure

```
marketing-package-agent/
├── app.py                          # Flask web application
├── marketing_package_agent.py      # Main automation script
├── create_supabase_table.py       # Database setup script
├── reset_database.py              # Database reset utility
├── download_pdf.py                 # PDF download helper
├── marketing_agent.env             # Environment configuration
├── requirements.txt                # Python dependencies
├── marketing_packages/             # Downloaded PDFs
│   ├── levyretail/                # Levy Retail PDFs
│   ├── tag-industries/            # Tag Industrial PDFs
│   └── netleaseadvisorygroup/     # NLAG PDFs
└── templates/                      # HTML templates
    ├── base.html                  # Base template
    ├── home.html                  # Dashboard page
    ├── downloads.html             # Downloads page
    └── database.html              # Database page
```

## 🎛️ Configuration Options

### Website Group Codes
- `LR` - Levy Retail (www.levyretail.com)
- `TI` - Tag Industrial (tag-industrial.com)  
- `NLAG` - Net Lease Advisory Group (netleaseadvisorygroup.com)

### Job Options
- **Website Group**: Filter by specific website or process all
- **Max Properties**: Limit processing or run unlimited
- **Headless Mode**: Run browser in background without GUI

### Browser Settings
- **Timeout**: 300 seconds per property (5 minutes)
- **Delay**: 2 seconds between properties (rate limiting)
- **Downloads**: Auto-organized in subfolders by website

## 🔍 Monitoring & Troubleshooting

### Real-time Monitoring
- **Live Output**: Watch job progress in real-time
- **Progress Stats**: Track completion percentages
- **Database View**: Monitor property status updates

### Common Issues

1. **Browser Not Found**: Install Chrome/Chromium
2. **Database Connection**: Check Railway PostgreSQL URL
3. **API Rate Limits**: Increase delay between requests
4. **PDF Download Fails**: Check internet connection and website accessibility

### Logs & Debugging
- All output is captured in the web interface
- Check browser console for frontend issues
- Database operations are logged with status updates

## 🛠️ Development

### Dependencies

```bash
# Core dependencies
browser-use              # AI browser automation
flask                   # Web framework
flask-socketio          # Real-time updates
psycopg2-binary        # PostgreSQL adapter
python-dotenv          # Environment management
langchain-openai       # OpenAI integration
pandas                 # Data processing
```

### Adding New Websites

1. **Create Agent Method**: Add `create_[website]_agent()` method
2. **Update Website Codes**: Add to `website_group_codes` dictionary
3. **Add Contact Info**: Define contact form fields
4. **Update Database**: Add properties to marketing_checklist table

### Custom Modifications

- **Timeouts**: Modify `timeout_seconds` in MarketingPackageAgent
- **Contact Info**: Update form fields in agent creation methods
- **UI Theme**: Modify CSS custom properties in base.html
- **Database Schema**: Update create_supabase_table.py

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home dashboard |
| `/downloads` | GET | Downloads page |
| `/database` | GET | Database view |
| `/api/progress` | GET | Progress statistics |
| `/api/properties` | GET | All properties data |
| `/api/pdfs` | GET | Local PDF files |
| `/api/submit_job` | POST | Submit processing job |
| `/pdf/<path>` | GET | Serve PDF files |

## 🔒 Security Notes

- Environment variables for sensitive data
- PDF serving with path validation
- Database connection with prepared statements
- Rate limiting to protect target websites

## 📈 Performance

- **Concurrent Processing**: One property at a time (respects rate limits)
- **Database Optimization**: Indexed columns for fast queries
- **Real-time Updates**: Efficient WebSocket communication
- **File Management**: Organized folder structure for PDFs

