#!/usr/bin/env python3
"""
Marketing Package Download Agent
Systematically downloads marketing packages from real estate websites using browser automation.

Features:
- Reads from Railway PostgreSQL database to track progress
- Uses environment variables for contact information per website group
- Downloads PDFs with proper naming convention
- Updates database with progress tracking
- Handles different website procedures
- Uses fresh browser instances to avoid context issues
- Supports selective processing by website group (LR, TI, etc.)
"""

import asyncio
import csv
import os
import shutil
import argparse
import re
import requests
import subprocess
import psycopg2
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dotenv import load_dotenv

# Browser-use imports
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from langchain_openai import ChatOpenAI

class MarketingPackageAgent:
    def __init__(self, checklist_file: str = None, headless: bool = False):
        """Initialize the marketing package download agent"""
        self.checklist_file = checklist_file  # Keep for backward compatibility but not used
        self.download_folder = "marketing_packages"
        self.timeout_seconds = 300  # 5 minutes per property
        self.request_delay = 2  # 2 seconds between properties to avoid rate limits
        self.headless = headless  # Browser headless mode
        
        # Website group codes for selective processing
        self.website_group_codes = {
            "LR": "www.levyretail.com",
            "TI": "tag-industrial.com",
            "NLAG": "netleaseadvisorygroup.com"
        }
        
        # Load environment variables
        load_dotenv("marketing_agent.env")
        self._load_config()
        self._setup_directories()
        self._setup_database()
        
    def _load_config(self):
        """Load configuration from environment variables"""
        
        # API Configuration
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in marketing_agent.env")
            
        # Database Configuration
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in marketing_agent.env")
            
        # Contact information for different website groups
        self.contact_info = {
            "www.levyretail.com": {
                "name": os.getenv('LEVYRETAIL_NAME', 'John Smith'),
                "email": os.getenv('LEVYRETAIL_EMAIL', 'test@example.com'),
                "phone": os.getenv('LEVYRETAIL_PHONE', '555-123-4567')
            },
            "tag-industrial.com": {
                "first_name": os.getenv('TAG_INDUSTRIAL_FIRST_NAME', 'John'),
                "last_name": os.getenv('TAG_INDUSTRIAL_LAST_NAME', 'Smith'),
                "company": os.getenv('TAG_INDUSTRIAL_COMPANY', 'Real Estate Investor'),
                "phone": os.getenv('TAG_INDUSTRIAL_PHONE', '555-123-4567'),
                "email": os.getenv('TAG_INDUSTRIAL_EMAIL', 'test@example.com'),
                "contact_type": os.getenv('TAG_INDUSTRIAL_CONTACT_TYPE', 'Investor'),
                # Legacy combined name field for backward compatibility
                "name": os.getenv('TAG_INDUSTRIAL_NAME', 'John Smith')
            },
            "netleaseadvisorygroup.com": {
                "first_name": os.getenv('NETLEASEADVISORYGROUP_FIRST_NAME', 'John'),
                "last_name": os.getenv('NETLEASEADVISORYGROUP_LAST_NAME', 'Smith'),
                "email": os.getenv('NETLEASEADVISORYGROUP_EMAIL', 'test@example.com')
            }
        }
        
    def _setup_database(self):
        """Setup database connection and verify table exists"""
        try:
            # Test database connection
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Verify marketing_checklist table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'marketing_checklist'
                );
            """)
            
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                raise ValueError("marketing_checklist table not found in database. Please run create_supabase_table.py first.")
                
            cursor.close()
            conn.close()
            print(f"🗄️  Connected to Railway PostgreSQL database successfully")
            
        except Exception as e:
            raise ValueError(f"Database connection failed: {e}")
        
    def _setup_directories(self):
        """Create necessary directories including subfolders for each website group"""
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Create subfolders for each website group
        subfolders = {
            "www.levyretail.com": "levyretail",
            "tag-industrial.com": "tag-industries",
            "netleaseadvisorygroup.com": "netleaseadvisorygroup"
        }
        
        for website, subfolder in subfolders.items():
            subfolder_path = os.path.join(self.download_folder, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
            
        print(f"📁 Download folder structure created: {self.download_folder}/")
        for subfolder in subfolders.values():
            print(f"   📁 {subfolder}/")
        
    def get_next_property(self, website_group_filter: str = None) -> Optional[Dict]:
        """Get the next property to process from the database"""
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Build query with optional website group filter
            base_query = """
                SELECT website_group, property_number, property_name, property_url 
                FROM marketing_checklist 
                WHERE UPPER(visited) = 'NO' AND UPPER(download_status) = 'PENDING'
            """
            
            if website_group_filter:
                query = base_query + " AND website_group = %s ORDER BY property_number LIMIT 1"
                cursor.execute(query, (website_group_filter,))
            else:
                query = base_query + " ORDER BY property_number LIMIT 1"
                cursor.execute(query)
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'website_group': result[0],
                    'property_number': result[1],
                    'property_name': result[2],
                    'property_url': result[3]
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error reading from database: {e}")
            return None
            
    def update_checklist(self, property_info: Dict, visited: bool = False, downloaded: bool = False, 
                        marketing_files: str = "", status: str = "", notes: str = "", error: str = ""):
        """Update the database with processing results"""
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            if visited:
                update_fields.append("visited = %s")
                values.append('YES')
            if downloaded:
                update_fields.append("downloaded = %s")
                values.append('YES')
            if marketing_files:
                update_fields.append("marketing_files_found = %s")
                values.append(str(marketing_files))
            if status:
                update_fields.append("download_status = %s")
                values.append(str(status))
            if notes:
                update_fields.append("notes = %s")
                values.append(str(notes))
            if error:
                update_fields.append("error_message = %s")
                values.append(str(error))
                
            # Always update timestamp and updated_at
            update_fields.append("last_attempt = %s")
            update_fields.append("updated_at = %s")
            values.extend([datetime.now(), datetime.now()])
            
            # Add WHERE clause values
            values.extend([property_info['website_group'], property_info['property_name']])
            
            query = f"""
                UPDATE marketing_checklist 
                SET {', '.join(update_fields)}
                WHERE website_group = %s AND property_name = %s
            """
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"📝 Updated database for {property_info['property_name']}")
            
        except Exception as e:
            print(f"Error updating database: {e}")
            
    def get_subfolder_name(self, website_group: str) -> str:
        """Get subfolder name for a website group"""
        subfolder_map = {
            "www.levyretail.com": "levyretail",
            "tag-industrial.com": "tag-industries",
            "netleaseadvisorygroup.com": "netleaseadvisorygroup"
        }
        return subfolder_map.get(website_group, 'unknown')
    
    def get_download_filename(self, property_info: Dict) -> str:
        """Generate expected download filename with subfolder structure"""
        
        subfolder = self.get_subfolder_name(property_info['website_group'])
        website_clean = property_info['website_group'].replace('.', '_')
        property_clean = property_info['property_name'].replace(' ', '_').replace('-', '_')
        filename = f"{website_clean}_{property_clean}.pdf"
        
        return os.path.join(self.download_folder, subfolder, filename)
    
    def get_download_path(self, website_group: str) -> str:
        """Get absolute download path for a website group"""
        subfolder = self.get_subfolder_name(website_group)
        subfolder_path = os.path.join(self.download_folder, subfolder)
        return os.path.abspath(subfolder_path)
        
    def download_pdf_from_url(self, pdf_url: str, property_info: Dict) -> bool:
        """Download PDF from URL using the working download_pdf.py script as subprocess"""
        try:
            print(f"🔗 Calling download_pdf.py script with URL: {pdf_url}")
            
            # Get the target directory for netleaseadvisorygroup
            target_dir = os.path.join(self.download_folder, self.get_subfolder_name(property_info['website_group']))
            target_dir = os.path.abspath(target_dir)
            
            print(f"📂 Target directory: {target_dir}")
            
            # Call download_pdf.py as subprocess
            cmd = ["python3", "download_pdf.py", pdf_url, target_dir]
            print(f"🤖 Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Check if the subprocess was successful
            if result.returncode == 0:
                print(f"✅ download_pdf.py completed successfully")
                print(f"📄 Output: {result.stdout.strip()}")
                
                # Verify the download by checking for files in the target directory
                expected_filename = pdf_url.split('/')[-1]
                expected_filepath = os.path.join(target_dir, expected_filename)
                
                if os.path.exists(expected_filepath) and os.path.getsize(expected_filepath) > 1000:
                    file_size = os.path.getsize(expected_filepath)
                    print(f"✅ PDF file verified: {expected_filepath}")
                    print(f"📄 File size: {file_size:,} bytes")
                    return True
                else:
                    print(f"❌ PDF file not found or too small after download_pdf.py")
                    return False
            else:
                print(f"❌ download_pdf.py failed with return code: {result.returncode}")
                print(f"❌ Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ download_pdf.py timed out after 120 seconds")
            return False
        except Exception as e:
            print(f"❌ Error calling download_pdf.py script: {e}")
            return False
    
    async def create_levy_retail_agent(self, property_info: Dict) -> Agent:
        """Create browser agent specifically for Levy Retail workflow"""
        
        contact = self.contact_info.get(property_info['website_group'], {})
        property_url = property_info['property_url']
        download_path = self.get_download_filename(property_info)
        
        # Get absolute path for specific subfolder
        abs_download_path = self.get_download_path(property_info['website_group'])
        
        # Set up GPT-4o model
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=self.api_key,
            temperature=0.1
        )
        
        # Create fresh browser context using WebKit/Safari engine  
        # Force WebKit by setting environment variable before browser creation
        import os
        original_browser = os.environ.get('BROWSER')
        os.environ['BROWSER'] = 'webkit'
        
        try:
            browser = Browser(
                config=BrowserConfig(
                    headless=self.headless,  # Use agent's headless setting
                    disable_security=False,
                    downloads_path=abs_download_path,  # Set download directory
                    accept_downloads=True,
                    channel=None,  # Force default channel
                    executable_path=None  # Let system find WebKit
                )
            )
        finally:
            # Restore original browser setting
            if original_browser:
                os.environ['BROWSER'] = original_browser
            elif 'BROWSER' in os.environ:
                del os.environ['BROWSER']
        
        # Comprehensive task instructions for Levy Retail
        task = f"""
You are a marketing package download agent for Levy Retail properties.

CURRENT PROPERTY:
- Name: {property_info['property_name']}
- URL: {property_url}
- Download Path: {download_path}

CONTACT INFORMATION TO USE:
- Name: {contact['name']}
- Email: {contact['email']}
- Phone: {contact['phone']}

STEP-BY-STEP WORKFLOW:

1. NAVIGATE TO PROPERTY:
   - Go to: {property_url}
   - Wait for page to fully load
   - Verify you're on the correct property page

2. FIND AND CLICK VIEW PACKAGE:
   - First, look for red "VIEW PACKAGE" button on the current view (usually on left side)
   - If not visible, scroll down SLOWLY in small increments (one scroll at a time)
   - After each scroll, STOP and look for the button before scrolling more
   - The button is typically in the upper portion of the page, NOT at the bottom
   - Once you see the button, click it to open download form modal

3. FILL OUT THE FORM:
   - Fill "Your Name" field with: {contact['name']}
   - Fill "Your Email" field with: {contact['email']}
   - Fill "Your Phone" field with: {contact['phone']}
   - Click "Submit" button

4. HANDLE THANK YOU PAGE:
   - After submitting, you'll see a "Thank you!" message
   - Look for link text "TO DOWNLOAD THE PACKAGE DIRECTLY, CLICK HERE."
   - Click that link to download the PDF directly
   - DO NOT rely on email - use the direct download link

5. DOWNLOAD VERIFICATION:
   - After clicking the download link, the PDF should start downloading
   - Mark the task as complete once the download link is clicked
   - Do not wait for file verification - that will be handled separately

IMPORTANT NOTES:
- The email provided will be bogus/fake - that's intentional
- ALWAYS use the direct download link, not email
- If any step fails, try again once before reporting error
- Take your time and wait for elements to load
- Downloads will be automatically saved to the levyretail subfolder
- SCROLLING STRATEGY: The VIEW PACKAGE button is usually visible after 1-2 small scrolls
- DO NOT scroll to the bottom of the page - the button is in the upper/middle section
- If you scroll more than 3-4 times without finding the button, try scrolling back up

SUCCESS CRITERIA:
- Successfully navigate to the property page
- Successfully click the VIEW PACKAGE button
- Successfully fill out and submit the contact form
- Successfully click the direct download link
- Report completion once download link is clicked

Report your progress and any issues encountered.
"""

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser
        )
        
        return agent

    async def create_tag_industrial_agent(self, property_info: Dict) -> Agent:
        """Create browser agent specifically for Tag Industrial workflow"""
        
        contact = self.contact_info.get(property_info['website_group'], {})
        property_url = property_info['property_url']
        download_path = self.get_download_filename(property_info)
        
        # Get absolute path for specific subfolder
        abs_download_path = self.get_download_path(property_info['website_group'])
        
        # Set up GPT-4o model
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=self.api_key,
            temperature=0.1
        )
        
        # Create fresh browser context
        browser = Browser(
            config=BrowserConfig(
                headless=self.headless,  # Use agent's headless setting
                disable_security=False,
                downloads_path=abs_download_path,  # Set download directory
                accept_downloads=True,
                channel=None,
                executable_path=None
            )
        )
        
        # Comprehensive task instructions for Tag Industrial
        task = f"""
You are a marketing package download agent for Tag Industrial properties.

CURRENT PROPERTY:
- Name: {property_info['property_name']}
- URL: {property_url}
- Download Path: {download_path}

CONTACT INFORMATION TO USE:
- First Name: {contact['first_name']}
- Last Name: {contact['last_name']}
- Company Name: {contact['company']}
- Phone Number: {contact['phone']}
- Email Address: {contact['email']}
- Contact Type: {contact['contact_type']}

STEP-BY-STEP WORKFLOW:

1. NAVIGATE TO PROPERTY:
   - Go to: {property_url}
   - Wait for page to fully load
   - Verify you're on the correct property page

2. FIND AND CLICK MARKETING PACKAGE BUTTON:
   - FIRST: Look carefully for "Marketing Package" button in the current visible area
   - If not visible, scroll down SLOWLY (half-page scrolls, not full page)
   - After EACH scroll, STOP and carefully scan the entire page for the button
   - Try maximum 3-4 slow scrolls down
   - IF BUTTON NOT FOUND after scrolling down: SCROLL BACK UP gradually
   - When scrolling up: Start from current position and scroll up slowly (small increments)
   - Check after each upward scroll - the button might be in the middle area
   - The button should be findable within this careful up/down search pattern
   - Once you see the "Marketing Package" button, click it to open the form modal

3. FILL OUT THE CONTACT FORM (WORK EFFICIENTLY):
   - Fill "First Name" field with: {contact['first_name']}
   - Fill "Last Name" field with: {contact['last_name']}
   - Fill "Company Name" field with: {contact['company']}
   - Fill "Phone Number" field with: {contact['phone']}
   - Fill "Email Address" field with: {contact['email']}
   - For "Contact Type" dropdown: 
     * Click on the dropdown field to open it
     * Click directly on "Principal" from the list
   - Click the "I accept the Terms and Conditions" checkbox IMMEDIATELY
   - Click "Submit" button RIGHT AFTER checking the checkbox
   - COMPLETE THE ENTIRE FORM IN ONE SMOOTH SEQUENCE

4. DOWNLOAD THE PACKAGE:
   - After submitting the form, look for "Download Marketing Package" button
   - Click the "Download Marketing Package" button to start the download
   - The PDF should start downloading automatically

5. DOWNLOAD VERIFICATION:
   - After clicking the download button, the PDF should start downloading
   - Mark the task as complete once the download button is clicked
   - Do not wait for file verification - that will be handled separately

IMPORTANT NOTES:
- The email provided will be bogus/fake - that's intentional
- Take your time and wait for elements to load
- CRITICAL: Use SLOW half-page scrolls (not full page) when looking for Marketing Package button
- If button not found after scrolling down, SCROLL BACK UP gradually to find it
- The button might be in the middle area that gets passed over with fast scrolling
- For the Contact Type dropdown: DO NOT use select_dropdown_option - CLICK on the dropdown, then CLICK on "Principal"
- WORK FAST on the checkbox: Click it immediately after dropdown selection
- DO NOT overthink the form - fill, check, submit in quick succession
- Downloads will be automatically saved to the tag-industries subfolder
- If any form field is marked as required, make sure to fill it out
- If any step fails, try again once before reporting error

BUTTON SEARCH STRATEGY:
- Step 1: Check current visible area thoroughly
- Step 2: Scroll down slowly (3-4 half-page scrolls max)
- Step 3: If not found, scroll back up slowly from current position
- Step 4: Check each area carefully as you scroll up
- Step 5: The button should be found using this up/down pattern

SUCCESS CRITERIA:
- Successfully navigate to the property page
- Successfully find and click the Marketing Package button using the search strategy
- Successfully fill out and submit the contact form
- Successfully click the Download Marketing Package button
- Report completion once download button is clicked

Report your progress and any issues encountered.
"""

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser
        )
        
        return agent

    async def create_netleaseadvisorygroup_agent(self, property_info: Dict) -> Agent:
        """Create browser agent specifically for Net Lease Advisory Group workflow"""
        
        contact = self.contact_info.get(property_info['website_group'], {})
        property_url = property_info['property_url']
        download_path = self.get_download_filename(property_info)
        
        # Get absolute path for specific subfolder
        abs_download_path = self.get_download_path(property_info['website_group'])
        
        # Set up GPT-4o model
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=self.api_key,
            temperature=0.1
        )
        
        # Detect platform for correct keyboard shortcuts
        import platform
        is_mac = platform.system() == 'Darwin'
        save_shortcut = "Cmd+S" if is_mac else "Ctrl+S"
        save_alt_shortcut = "Cmd+Shift+S" if is_mac else "Ctrl+Shift+S"
        platform_name = "Mac" if is_mac else "Windows/Linux"
        
        # Create fresh browser context with enhanced download settings
        browser = Browser(
            config=BrowserConfig(
                headless=self.headless,  # Use agent's headless setting
                disable_security=False,
                downloads_path=abs_download_path,  # Set download directory
                accept_downloads=True,
                channel=None,
                executable_path=None,
                # Add extra args to handle PDFs and downloads better
                extra_chromium_args=[
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--no-pdf-header-footer',
                    '--disable-pdf-tagging'
                ]
            )
        )
        
        # Comprehensive task instructions for Net Lease Advisory Group
        task = f"""
You are a marketing package download agent for Net Lease Advisory Group properties.

CURRENT PROPERTY:
- Name: {property_info['property_name']}
- URL: {property_url}
- Download Path: {download_path}

STEP-BY-STEP WORKFLOW:

1. NAVIGATE TO PROPERTY:
   - Go to: {property_url}
   - Wait for page to fully load
   - Verify you're on the correct property page

2. FIND AND CLICK DOWNLOAD BROCHURE BUTTON:
   - Scroll down slowly to find the "DOWNLOAD BROCHURE" button
   - The button should be visible after scrolling down a little bit
   - After each scroll, STOP and look for the button before scrolling more
   - Once you see the "DOWNLOAD BROCHURE" button, click it to open the popup modal

3. HANDLE THE POPUP FORM:
   - A popup window will open with a form
   - DO NOT fill out any fields in the form
   - Look for the "DOWNLOAD NOW" button at the bottom of the popup
   - Click the "DOWNLOAD NOW" button directly without filling any form fields

4. EXTRACT PDF URL FOR PYTHON DOWNLOAD:
   After clicking "DOWNLOAD NOW", the PDF will open in browser. Follow this process:

   STEP A - Extract PDF URL:
   - Wait 5-6 seconds for PDF to fully load in browser (PDF needs time to render completely)
   - Look at the browser address bar - it should now show the direct PDF URL
   - The URL will be something like: https://netleaseadvisorygroup.com/wp-content/uploads/YYYY/MM/filename.pdf
   - Extract this complete PDF URL from the address bar
   - IMPORTANT: Make sure you have the complete URL starting with https://

   STEP B - Return PDF URL:
   - Once you have successfully extracted the PDF URL, your task is complete
   - Return the PDF URL in your final response using this exact format:
   - "PDF_URL_EXTRACTED: [complete_pdf_url_here]"
   - Example: "PDF_URL_EXTRACTED: https://netleaseadvisorygroup.com/wp-content/uploads/2022/07/property-brochure.pdf"
   - The Python code will handle the actual download using this URL

5. TASK COMPLETION:
   - Mark task as complete once you have successfully extracted and returned the PDF URL
   - DO NOT attempt to download the PDF yourself
   - The Python code will handle the download process using the extracted URL

IMPORTANT NOTES:
- NO form filling required - just click DOWNLOAD NOW directly
- Focus ONLY on extracting the correct PDF URL from browser address bar
- Your job is complete once you return the PDF URL in the correct format
- The PDF URL extraction is critical - wait for page to fully load
- Python code will handle the actual download to the netleaseadvisorygroup subfolder
- Make sure to return the URL in the exact format: "PDF_URL_EXTRACTED: [url]"

STEP-BY-STEP PROCESS:
1. PDF opens in browser after clicking DOWNLOAD NOW
2. Wait 5-6 seconds for PDF to fully load and URL to stabilize
3. Extract the complete PDF URL from browser address bar
4. Return the URL in the specified format
5. Task complete - Python will handle download

SUCCESS CRITERIA:
- Successfully navigate to the property page
- Successfully find and click the DOWNLOAD BROCHURE button
- Successfully click the DOWNLOAD NOW button in the popup
- Successfully extract PDF URL from browser address bar
- Successfully return PDF URL in format: "PDF_URL_EXTRACTED: [url]"
- Report completion once PDF URL is extracted and returned

TROUBLESHOOTING:
- If popup is blocked, look for popup blocker notification and allow it
- If PDF doesn't load after clicking DOWNLOAD NOW, wait longer (up to 10 seconds)
- If PDF URL looks incomplete or wrong, wait longer for page to fully load
- Make sure the extracted URL starts with https:// and ends with .pdf
- If URL extraction fails, report the issue clearly

Report your progress and return the PDF URL using the exact format specified.
"""

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser
        )
        
        return agent

    async def process_property(self, property_info: Dict) -> bool:
        """Process a single property download"""
        
        print(f"\n🚀 PROCESSING: {property_info['website_group']} - {property_info['property_name']}")
        print(f"🔗 URL: {property_info['property_url']}")
        
        # Mark as visited immediately
        self.update_checklist(property_info, visited=True, status="IN_PROGRESS")
        
        try:
            # Create agent based on website group
            if property_info['website_group'] == "www.levyretail.com":
                agent = await self.create_levy_retail_agent(property_info)
            elif property_info['website_group'] == "tag-industrial.com":
                agent = await self.create_tag_industrial_agent(property_info)
            elif property_info['website_group'] == "netleaseadvisorygroup.com":
                agent = await self.create_netleaseadvisorygroup_agent(property_info)
            else:
                print(f"⚠️  Website group {property_info['website_group']} not yet implemented")
                self.update_checklist(property_info, status="SKIPPED", 
                                    notes="Website group not yet implemented")
                return False
                
            # Run the agent with timeout
            print(f"🤖 Starting browser agent...")
            result = await asyncio.wait_for(
                agent.run(),
                timeout=self.timeout_seconds
            )
            
            # Handle netleaseadvisorygroup separately - extract PDF URL and download
            if property_info['website_group'] == "netleaseadvisorygroup.com":
                # Extract PDF URL from agent result
                pdf_url = None
                if result:
                    # Convert result to string and look for PDF URL
                    result_str = str(result)
                    
                    # Look for PDF_URL_EXTRACTED pattern
                    url_match = re.search(r'PDF_URL_EXTRACTED:\s*([^\s\]]+)', result_str)
                    if url_match:
                        pdf_url = url_match.group(1).strip()
                        print(f"🔗 Extracted PDF URL: {pdf_url}")
                    else:
                        # Fallback: look for any https URL ending in .pdf
                        url_match = re.search(r'https://[^\s\]]+\.pdf', result_str)
                        if url_match:
                            pdf_url = url_match.group(0).strip()
                            print(f"🔗 Found PDF URL (fallback): {pdf_url}")
                
                if pdf_url:
                    # Clean up the URL - remove any extra characters
                    pdf_url = pdf_url.strip().rstrip("',\"").strip()
                    print(f"🔗 Cleaned PDF URL: {pdf_url}")
                    
                    # Brief wait before using download_pdf.py script (which works reliably)
                    print(f"⏳ Waiting 5 seconds before download...")
                    await asyncio.sleep(5)
                    
                    # Download PDF using Python requests
                    download_success = self.download_pdf_from_url(pdf_url, property_info)
                    if download_success:
                        print(f"✅ SUCCESS: PDF downloaded for {property_info['property_name']}")
                        self.update_checklist(property_info, downloaded=True, status="SUCCESS",
                                            marketing_files=f"PDF package ({pdf_url})", 
                                            notes=f"Successfully extracted URL and downloaded PDF")
                        return True
                    else:
                        print(f"❌ FAILED: PDF download failed for {property_info['property_name']}")
                        self.update_checklist(property_info, status="DOWNLOAD_FAILED",
                                            error=f"Failed to download PDF from URL: {pdf_url}")
                        return False
                else:
                    print(f"❌ FAILED: Could not extract PDF URL from agent result")
                    self.update_checklist(property_info, status="URL_EXTRACTION_FAILED",
                                        error="Agent did not return PDF URL in expected format")
                    return False
            
            # Handle other website groups (original logic)
            else:
                # Mark as successful regardless of agent status (browser automation completed)
                print(f"✅ SUCCESS: Agent completed workflow for {property_info['property_name']}")
                subfolder = self.get_subfolder_name(property_info['website_group'])
                self.update_checklist(property_info, downloaded=True, status="SUCCESS",
                                    marketing_files="PDF package", 
                                    notes=f"Successfully completed download workflow - PDF should be in {subfolder}/ folder")
                return True
                
        except asyncio.TimeoutError:
            print(f"⏰ TIMEOUT: Property took longer than {self.timeout_seconds} seconds")
            self.update_checklist(property_info, status="TIMEOUT",
                                error=f"Timeout after {self.timeout_seconds} seconds")
            return False
            
        except Exception as e:
            print(f"❌ ERROR processing property: {e}")
            self.update_checklist(property_info, status="ERROR", error=str(e))
            return False
            
    async def run_download_session(self, max_properties: int = None, website_group_filter: str = None):
        """Run a download session processing properties from the database"""
        
        print("🎯 MARKETING PACKAGE DOWNLOAD AGENT")
        print("=" * 70)
        print(f"🗄️  Database: Railway PostgreSQL")
        print(f"📁 Downloads: {self.download_folder}/")
        print(f"🎭 Browser Mode: {'Headless' if self.headless else 'Visible'}")
        print(f"⏱️  Timeout: {self.timeout_seconds} seconds per property")
        print(f"⏳ Delay: {self.request_delay} seconds between properties (rate limit protection)")
        if website_group_filter:
            print(f"🎯 Filter: Only processing {website_group_filter} properties")
        print("=" * 70)
        
        processed = 0
        successful = 0
        
        while True:
            # Check if we've reached the limit
            if max_properties and processed >= max_properties:
                print(f"🎯 Reached maximum properties limit: {max_properties}")
                break
                
            # Get next property to process
            property_info = self.get_next_property(website_group_filter)
            if not property_info:
                if website_group_filter:
                    print(f"✅ No more {website_group_filter} properties to process!")
                else:
                    print("✅ No more properties to process!")
                break
                
            # Process the property
            success = await self.process_property(property_info)
            processed += 1
            if success:
                successful += 1
                
            print(f"\n📊 SESSION PROGRESS: {processed} processed, {successful} successful")
            
            # Delay between properties to avoid rate limits
            if max_properties is None or processed < max_properties:
                print(f"⏳ Waiting {self.request_delay} seconds before next property...")
                await asyncio.sleep(self.request_delay)
            
        print(f"\n🏁 SESSION COMPLETE!")
        print(f"📊 Total Processed: {processed}")
        print(f"✅ Successful Downloads: {successful}")
        print(f"❌ Failed Downloads: {processed - successful}")
        print(f"📁 Downloads saved to: {self.download_folder}/")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Marketing Package Download Agent')
    parser.add_argument('--group', '-g', 
                        choices=['LR', 'TI', 'NLAG'],
                        help='Website group to process: LR (Levy Retail), TI (Tag Industries), NLAG (Net Lease Advisory Group)')
    parser.add_argument('--max-properties', '-m', type=int,
                        help='Maximum number of properties to process')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode (no GUI)')
    
    return parser.parse_args()

async def main():
    """Main function to run the marketing package agent"""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Create agent with headless setting
    agent = MarketingPackageAgent(headless=args.headless)
    
    # Convert group code to website group name
    website_group_filter = None
    if args.group:
        website_group_filter = agent.website_group_codes.get(args.group)
        if not website_group_filter:
            print(f"❌ Unknown group code: {args.group}")
            return
    
    # Process properties
    await agent.run_download_session(
        max_properties=args.max_properties,
        website_group_filter=website_group_filter
    )

if __name__ == "__main__":
    print("🤖 Marketing Package Download Agent")
    print("🗄️  Now using Railway PostgreSQL database instead of CSV file")
    print("💡 Make sure to update marketing_agent.env with your DATABASE_URL and contact settings")
    print("🔧 Usage examples:")
    print("   python marketing_package_agent.py                    # Process all properties from database")
    print("   python marketing_package_agent.py -g LR              # Process only Levy Retail properties")
    print("   python marketing_package_agent.py -g TI              # Process only Tag Industries properties")
    print("   python marketing_package_agent.py -g NLAG            # Process only Net Lease Advisory Group properties")
    print("   python marketing_package_agent.py -g LR -m 5         # Process max 5 Levy Retail properties")
    print("   python marketing_package_agent.py --headless          # Run in headless mode (no browser window)")
    print("   python marketing_package_agent.py -g LR --headless   # Levy Retail headless mode")
    print("🚀 Starting download session...\n")
    
    asyncio.run(main()) 