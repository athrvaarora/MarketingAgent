# 🏢 Marketing Package Download System

## Comprehensive Guide: Property Data Pipeline & Automated Marketing

This system provides end-to-end automation for extracting real estate property data and systematically downloading marketing packages using AI-powered browser automation.

## 📋 Table of Contents
- [🚀 Quick Start](#-quick-start)
- [🔧 Installation & Setup](#-installation--setup)
- [📁 Repository Structure](#-repository-structure)
- [🔍 Data Extraction Pipeline](#-data-extraction-pipeline)
- [🤖 Marketing Automation](#-marketing-automation)
- [📊 Current Status](#-current-status)

---

## 🚀 Quick Start

**What This System Does:**
1. **Extracts property URLs** from real estate websites using multiple methods
2. **Combines data** into a unified tracking spreadsheet
3. **Automates marketing package downloads** using AI browser agents
4. **Tracks progress** with detailed status reporting

**Current Integrations:**
- ✅ **Levy Retail:** 47 properties (5 downloaded)
- ✅ **Tag Industries:** 24 properties (5 downloaded)
- ✅ **Net Lease Advisory Group:** 96 properties (3 downloaded)

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Chrome/Chromium browser
- OpenAI API key (GPT-4o)

### Step 1: Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd browser-use-main

# Create virtual environment using uv
uv venv --python 3.11
source .venv/bin/activate

# Install dependencies
uv sync

# Install browser dependencies
playwright install
playwright install-deps
```

### Step 2: Configuration
```bash
# Copy environment template
cp marketing_agent.env.example marketing_agent.env

# Edit with your details
nano marketing_agent.env
```

Required configuration:
```env
OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"
LEVYRETAIL_NAME="Your Name"
LEVYRETAIL_EMAIL="your-email@example.com"
TAG_INDUSTRIAL_FIRST_NAME="Your First Name"
TAG_INDUSTRIAL_COMPANY="Your Company"
NETLEASEADVISORYGROUP_EMAIL="your-email@example.com"
```

### Step 3: Verify Installation
```bash
# Test the main agent
python marketing_package_agent.py --help

# Quick test run
python marketing_package_agent.py -g LR -m 1
```

---

## 📁 Repository Structure

```
browser-use-main/
├── 📄 marketing_package_agent.py          # Main automation agent (853 lines)
├── 📄 marketing_agent.env.example         # Configuration template  
├── 📄 marketing_checklist_20250607_231412.csv  # Property tracking (167 properties)
├── 📄 download_pdf.py                     # PDF download utility
├── 
├── 📁 marketing_packages/                 # Downloaded files
│   ├── 📁 levyretail/                    # Levy Retail PDFs (5 files)
│   ├── 📁 tag-industries/                # Tag Industries PDFs (5 files)
│   └── 📁 netleaseadvisorygroup/         # NLAG PDFs (3 files)
│
├── 📁 Property_Extractors/               # Data extraction tools
│   ├── 📄 sitemap_generator.py          # Multi-website crawler (603 lines)
│   ├── 📄 netlease_advisory_browser_agent.py  # NLAG extractor (356 lines)
│   ├── 📄 levy_retail_browser_agent.py  # Levy Retail extractor (336 lines)
│   ├── 📄 extract_tag_industrial_properties.py  # XML parser (88 lines)
│   ├── 📄 combine_all_properties.py     # Data combiner (183 lines)
│   └── 📄 create_marketing_checklist.py # CSV generator (164 lines)
│
├── 📁 browser_use/                       # Core framework
├── 📄 pyproject.toml                     # Project config
└── 📄 uv.lock                           # Dependencies
```

---

## 🔍 Data Extraction Pipeline

The property extraction pipeline uses multiple specialized tools to gather comprehensive property data:

### Phase 1: Property URL Discovery

#### 🌐 Sitemap Generator (`sitemap_generator.py`)
**Purpose:** Fast website crawling to discover property URLs  
**Method:** HTTP requests + BeautifulSoup parsing  
**Lines:** 603

**Key Features:**
- Multi-website configuration support
- Smart filtering with URL patterns
- Pagination handling for complex sites
- Output formats: JSON, TXT, XML

**Configuration Example:**
```python
websites = [
    {
        "url": "https://www.levyretail.com/",
        "filter": "/property/",
        "max_pages": 300,
        "special_handling": "levy_retail_paginated"
    },
    {
        "url": "https://securenetlease.com/properties/",
        "filter": "/properties/", 
        "max_pages": 200
    }
]
```

**Usage:**
```bash
cd Property_Extractors
python sitemap_generator.py
# Output: sitemap_combined_TIMESTAMP.json
```

#### 🤖 Net Lease Advisory Browser Agent (`netlease_advisory_browser_agent.py`)
**Purpose:** AI-powered extraction for JavaScript-heavy sites  
**Method:** Browser automation with GPT-4o  
**Lines:** 356

**Key Features:**
- Handles infinite scroll and dynamic content
- Intelligent navigation with error recovery
- Extracts 96+ property URLs
- Visible browser mode for monitoring

**Workflow:**
1. Navigate to https://netleaseadvisorygroup.com/listings/
2. AI scrolls slowly through all property listings
3. Identifies and extracts property URLs
4. Saves results with timestamps

**Usage:**
```bash
cd Property_Extractors
python netlease_advisory_browser_agent.py
# Output: netlease_advisory_browser_agent_results_TIMESTAMP.txt
```

#### 🏪 Levy Retail Browser Agent (`levy_retail_browser_agent.py`)
**Purpose:** Specialized extractor for paginated property listings  
**Method:** Browser automation with Gemini AI  
**Lines:** 336

**Key Features:**
- Handles paginated navigation (pages 5-13)
- Gemini 2.5 Pro AI for complex interactions
- Extraction of 47+ property URLs
- Special pagination logic

**Pagination Handling:**
```python
for page_num in range(5, 14):  # Pages 5-13
    url = f"https://www.levyretail.com/multi-tenant-properties/#paged={page_num}"
    # Extract property links from each page
```

**Usage:**
```bash
cd Property_Extractors  
python levy_retail_browser_agent.py
# Output: levy_retail_browser_agent_results_TIMESTAMP.txt
```

#### 🗂️ TAG Industrial XML Parser (`extract_tag_industrial_properties.py`)
**Purpose:** Extract properties from XML sitemaps  
**Method:** XML parsing with ElementTree  
**Lines:** 88

**Key Features:**
- Fast XML sitemap processing
- URL filtering for property paths
- Clean property name extraction
- Handles large XML files efficiently

**Core Logic:**
```python
def extract_tag_industrial_properties():
    tree = ET.parse('tag-industrial.xml')
    root = tree.getroot()
    
    for url_elem in root.findall('.//ns:url', namespace):
        url = loc_elem.text
        if 'https://tag-industrial.com/properties/' in url:
            property_urls.append(url)
```

**Usage:**
```bash
cd Property_Extractors
python extract_tag_industrial_properties.py
# Requires: tag-industrial.xml
# Output: tag_industrial_properties_TIMESTAMP.txt
```

### Phase 2: Data Aggregation

#### 🔗 Property Data Combiner (`combine_all_properties.py`)
**Purpose:** Merge extracted data into unified structure  
**Method:** JSON aggregation with deduplication  
**Lines:** 183

**Data Sources:**
- Levy Retail browser agent results
- TAG Industrial XML extraction
- Net Lease Advisory Group browser results
- Sitemap generator outputs

**Output Structure:**
```json
{
    "crawled_at": "2025-01-07T...",
    "total_websites": 3,
    "total_urls": 167,
    "websites": {
        "www.levyretail.com": {
            "source": "browser_agent_extraction",
            "url_count": 47,
            "urls": [...],
            "filter_pattern": "/property/"
        }
    }
}
```

**Usage:**
```bash
cd Property_Extractors
python combine_all_properties.py
# Output: sitemap_combined.json
```

### Phase 3: Marketing Checklist Creation

#### 📋 Checklist Generator (`create_marketing_checklist.py`)
**Purpose:** Convert property data into trackable CSV format  
**Method:** JSON to CSV transformation with tracking columns  
**Lines:** 164

**Generated CSV Structure:**
```csv
website_group,property_number,property_name,property_url,visited,downloaded,
marketing_files_found,download_status,notes,last_attempt,error_message
```

**Generated Files:**
- `marketing_checklist_TIMESTAMP.csv` - Main tracking spreadsheet
- `website_summary_TIMESTAMP.csv` - Statistics by website
- `marketing_checklist_summary_TIMESTAMP.txt` - Human-readable summary

**Usage:**
```bash
python create_marketing_checklist.py
# Input: sitemap_combined.json
# Output: marketing_checklist_20250607_231412.csv (167 properties)
```

### Complete Pipeline Execution

```bash
# 1. Extract property URLs from all sources
cd Property_Extractors

# Web crawling for multiple sites
python sitemap_generator.py

# AI browser automation for complex sites
python netlease_advisory_browser_agent.py
python levy_retail_browser_agent.py

# XML parsing for structured data
python extract_tag_industrial_properties.py

# 2. Combine all extracted data
python combine_all_properties.py

# 3. Generate trackable marketing checklist
python create_marketing_checklist.py

# 4. Start automated marketing package downloads
cd ..
python marketing_package_agent.py
```

**Data Flow:**
```
Property Websites → Specialized Extractors → Combined JSON → Marketing CSV → Automation Agent
```

---

## 🤖 Marketing Automation

The main automation system processes the generated checklist to systematically download marketing packages using website-specific AI agents.

### Core System (`marketing_package_agent.py`)
**Lines:** 853  
**Purpose:** Automated marketing package downloads  
**AI Model:** OpenAI GPT-4o

### Website-Specific Workflows

#### 🏪 Levy Retail Agent
**Success Rate:** 5/5 attempts (100%)  
**Average Time:** ~3-4 minutes per property

**Workflow:**
1. Navigate to property page
2. Scroll to find "VIEW PACKAGE" button
3. Fill contact form (name, email, phone)
4. Submit → "Thank you!" page
5. Click direct download link
6. PDF downloads automatically

#### 🏭 Tag Industries Agent  
**Success Rate:** 5/9 attempts (56%)  
**Average Time:** ~5-6 minutes per property

**Workflow:**
1. Navigate to property page
2. Slow scroll to find "Marketing Package" button
3. Fill detailed form (6 fields)
4. Select "Principal" from dropdown
5. Check Terms & Conditions
6. Submit → Download button appears
7. Click "Download Marketing Package"

**Recent Improvements:**
- Slower scrolling with up/down search pattern
- Better button detection algorithms
- Faster form completion sequence

#### 🏢 Net Lease Advisory Group Agent
**Success Rate:** 3/5 attempts (60%)  
**Average Time:** ~4-5 minutes per property

**Workflow:**
1. Navigate to property page
2. Find "DOWNLOAD BROCHURE" button
3. Click → popup appears
4. Click "DOWNLOAD NOW" (no form filling)
5. Extract PDF URL from browser
6. Use download_pdf.py script for download

### Progress Tracking

**CSV Status Values:**
- `PENDING` - Not yet processed
- `IN_PROGRESS` - Currently being processed
- `SUCCESS` - Downloaded successfully  
- `TIMEOUT` - Process timed out
- `DOWNLOAD_FAILED` - PDF download failed
- `ERROR` - General error occurred

**Real-time Updates:**
```python
# Example CSV entry after successful download
www.levyretail.com,5,broad-street-marketplace,https://...,YES,YES,PDF package,
SUCCESS,Successfully completed download workflow,2025-06-08 16:14:19,
```

### Usage Examples

```bash
# Process all properties (167 total)
python marketing_package_agent.py

# Target specific website groups
python marketing_package_agent.py -g LR   # Levy Retail (47 properties)
python marketing_package_agent.py -g TI   # Tag Industries (24 properties)  
python marketing_package_agent.py -g NLAG # Net Lease Advisory (96 properties)

# Limit processing count
python marketing_package_agent.py -g LR -m 5  # Max 5 properties
python marketing_package_agent.py -m 1        # Test with 1 property

# Resume interrupted sessions (automatic)
python marketing_package_agent.py -g TI
# Skips completed properties, continues from last unprocessed
```

---

## 📊 Current Status

### Overall Progress
**Total Properties:** 167  
**Successfully Downloaded:** 13 (7.8%)  
**In Progress/Failed:** 9 (5.4%)  
**Pending:** 145 (86.8%)

### By Website Group

#### ✅ Levy Retail (www.levyretail.com)
- **Total Properties:** 47
- **Downloaded:** 5 (11%)
- **Status:** Working reliably
- **Files:** `marketing_packages/levyretail/` (5 PDFs)

**Downloaded Properties:**
1. 314-south-main
2. abrams-forest-shopping-center  
3. bandera-festival-shopping-center
4. broad-street-marketplace
5. cedar-rapids-shopping-center

#### ✅ Tag Industries (tag-industrial.com)
- **Total Properties:** 24
- **Downloaded:** 5 (21%)
- **Status:** Optimizations in progress
- **Files:** `marketing_packages/tag-industries/` (5 PDFs)

**Downloaded Properties:**
1. 11918-adel-road
2. 1227-martha-truman-road
3. 1360-west-state-highway-71
4. 2117-greenleaf-street
5. 23315-south-youngs-road

#### ✅ Net Lease Advisory Group (netleaseadvisorygroup.com)
- **Total Properties:** 96
- **Downloaded:** 3 (3%)
- **Status:** PDF extraction method working
- **Files:** `marketing_packages/netleaseadvisorygroup/` (3 PDFs)

**Downloaded Properties:**
1. brakes-plus-slb-liberty-hill-tx
2. houston-gas-station-new-caney-tx-2
3. hawaiian-bros-liberty-mo

### Performance Metrics

**Average Processing Times:**
- Levy Retail: 3-4 minutes per property
- Tag Industries: 5-6 minutes per property
- Net Lease Advisory Group: 4-5 minutes per property

**Success Rates:**
- Levy Retail: 100% (5/5)
- Tag Industries: 56% (5/9) - improving with recent optimizations
- Net Lease Advisory Group: 60% (3/5)

### Error Analysis

**Common Issues:**
1. **Button Detection:** Slow scrolling improvements implemented
2. **Form Filling:** Timeout optimizations for complex forms  
3. **PDF Downloads:** Reliable extraction method for NLAG
4. **Rate Limiting:** 2-second delays between properties

**Recent Fixes:**
- Tag Industries: Improved scrolling strategy with up/down search
- NLAG: Switched to URL extraction + download_pdf.py script
- All: Better error reporting and resume capability

---

## 🔄 Future Data Pipeline Runs

The established pipeline can be reused for:

1. **New Property Discovery:** Re-run extractors to find new listings
2. **Additional Websites:** Add new real estate sites to sitemap_generator.py
3. **Data Refresh:** Update existing property information
4. **Quality Assurance:** Verify downloaded marketing materials

### Next Steps

1. **Complete Current Processing:** Finish remaining 154 properties
2. **Performance Optimization:** Implement parallel processing
3. **New Website Integration:** Add more real estate sites
4. **Data Analysis:** Extract insights from downloaded marketing materials

---

This comprehensive system provides a solid foundation for scalable real estate marketing automation with detailed tracking and reliable error handling. B