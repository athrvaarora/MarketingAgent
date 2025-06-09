#!/usr/bin/env python3
"""
Recent Updates Checker
Shows detailed information about recently processed properties in the database
"""

import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

def check_recent_updates():
    """Check for recent updates in the database"""
    
    # Load environment variables
    load_dotenv("marketing_agent.env")
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in marketing_agent.env")
        return
    
    try:
        # Connect to database
        print("🔌 Connecting to Railway PostgreSQL database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        print("\n" + "="*80)
        
        # Get recently updated properties (last 24 hours)
        cursor.execute("""
            SELECT website_group, property_name, visited, downloaded, download_status,
                   marketing_files_found, notes, last_attempt, updated_at
            FROM marketing_checklist 
            WHERE last_attempt IS NOT NULL 
            ORDER BY last_attempt DESC
            LIMIT 10;
        """)
        
        recent_updates = cursor.fetchall()
        
        if recent_updates:
            print(f"📅 Recently Processed Properties ({len(recent_updates)} found):")
            print("-" * 80)
            
            for i, record in enumerate(recent_updates, 1):
                website, prop_name, visited, downloaded, status, files, notes, last_attempt, updated_at = record
                
                print(f"\n🔹 Property #{i}:")
                print(f"   Website Group: {website}")
                print(f"   Property Name: {prop_name}")
                print(f"   Status: {status}")
                print(f"   Visited: {visited}")
                print(f"   Downloaded: {downloaded}")
                print(f"   Marketing Files: {files or 'None'}")
                print(f"   Notes: {notes or 'None'}")
                print(f"   Last Attempt: {last_attempt}")
                print(f"   Updated At: {updated_at}")
        else:
            print("📭 No recently processed properties found")
        
        # Get current status summary
        print(f"\n" + "="*80)
        print("📊 Current Status Summary:")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN visited = 'YES' THEN 1 ELSE 0 END) as visited,
                SUM(CASE WHEN downloaded = 'YES' THEN 1 ELSE 0 END) as downloaded,
                SUM(CASE WHEN download_status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN download_status = 'PENDING' THEN 1 ELSE 0 END) as pending
            FROM marketing_checklist;
        """)
        
        summary = cursor.fetchone()
        total, visited, downloaded, successful, pending = summary
        
        print(f"   Total Properties: {total}")
        print(f"   Visited: {visited}")
        print(f"   Downloaded: {downloaded}")
        print(f"   Successful: {successful}")
        print(f"   Pending: {pending}")
        
        # Get next properties to process by website group
        print(f"\n" + "="*80)
        print("🎯 Next Properties to Process by Website Group:")
        
        for website_code, website_name in [
            ('LR', 'www.levyretail.com'),
            ('TI', 'tag-industrial.com'),
            ('NLAG', 'netleaseadvisorygroup.com')
        ]:
            cursor.execute("""
                SELECT property_name
                FROM marketing_checklist 
                WHERE website_group = %s 
                  AND visited = 'NO' 
                  AND download_status = 'PENDING'
                ORDER BY property_number
                LIMIT 3;
            """, (website_name,))
            
            next_properties = cursor.fetchall()
            
            print(f"\n🔹 {website_code} ({website_name}):")
            if next_properties:
                for prop in next_properties:
                    print(f"   • {prop[0]}")
                
                # Count remaining
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM marketing_checklist 
                    WHERE website_group = %s 
                      AND visited = 'NO' 
                      AND download_status = 'PENDING';
                """, (website_name,))
                
                remaining = cursor.fetchone()[0]
                print(f"   → {remaining} properties remaining")
            else:
                print("   ✅ All properties processed!")
        
        print(f"\n" + "="*80)
        print("✅ Recent updates check completed!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("📊 Recent Updates Checker - Railway PostgreSQL Database")
    print("=" * 80)
    check_recent_updates() 