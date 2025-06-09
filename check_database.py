#!/usr/bin/env python3
"""
Database Verification Script
Checks the Railway PostgreSQL database to verify marketing_checklist data
"""

import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

def check_database():
    """Check database connection and verify marketing_checklist data"""
    
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
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'marketing_checklist'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            print("❌ marketing_checklist table not found!")
            return
        
        print("✅ Connected successfully!")
        print("✅ marketing_checklist table exists!")
        print("\n" + "="*60)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist;")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total Properties: {total_count}")
        
        # Get website group distribution
        cursor.execute("""
            SELECT website_group, COUNT(*) 
            FROM marketing_checklist 
            GROUP BY website_group 
            ORDER BY COUNT(*) DESC;
        """)
        website_stats = cursor.fetchall()
        
        print(f"\n🌐 Properties by Website Group:")
        for website, count in website_stats:
            print(f"   {website}: {count} properties")
        
        # Get status distribution
        cursor.execute("""
            SELECT download_status, COUNT(*) 
            FROM marketing_checklist 
            GROUP BY download_status 
            ORDER BY COUNT(*) DESC;
        """)
        status_stats = cursor.fetchall()
        
        print(f"\n📈 Status Distribution:")
        for status, count in status_stats:
            print(f"   {status}: {count} properties")
        
        # Get visited distribution
        cursor.execute("""
            SELECT visited, COUNT(*) 
            FROM marketing_checklist 
            GROUP BY visited 
            ORDER BY COUNT(*) DESC;
        """)
        visited_stats = cursor.fetchall()
        
        print(f"\n👁️  Visited Distribution:")
        for visited, count in visited_stats:
            print(f"   {visited}: {count} properties")
        
        # Get downloaded distribution
        cursor.execute("""
            SELECT downloaded, COUNT(*) 
            FROM marketing_checklist 
            GROUP BY downloaded 
            ORDER BY COUNT(*) DESC;
        """)
        downloaded_stats = cursor.fetchall()
        
        print(f"\n⬇️  Downloaded Distribution:")
        for downloaded, count in downloaded_stats:
            print(f"   {downloaded}: {count} properties")
        
        # Show sample records
        cursor.execute("""
            SELECT website_group, property_name, property_url, visited, downloaded, download_status
            FROM marketing_checklist 
            ORDER BY property_number 
            LIMIT 5;
        """)
        sample_records = cursor.fetchall()
        
        print(f"\n📋 Sample Records:")
        print("   Website Group | Property Name | Visited | Downloaded | Status")
        print("   " + "-"*70)
        for record in sample_records:
            website = record[0][:20] + "..." if len(record[0]) > 20 else record[0]
            prop_name = record[1][:25] + "..." if len(record[1]) > 25 else record[1]
            print(f"   {website:<23} | {prop_name:<25} | {record[3]:<7} | {record[4]:<10} | {record[5]}")
        
        # Check for any records with errors
        cursor.execute("""
            SELECT COUNT(*) 
            FROM marketing_checklist 
            WHERE error_message IS NOT NULL AND error_message != '';
        """)
        error_count = cursor.fetchone()[0]
        
        if error_count > 0:
            print(f"\n⚠️  Records with Errors: {error_count}")
            cursor.execute("""
                SELECT website_group, property_name, error_message
                FROM marketing_checklist 
                WHERE error_message IS NOT NULL AND error_message != ''
                LIMIT 3;
            """)
            error_records = cursor.fetchall()
            for record in error_records:
                print(f"   {record[0]} - {record[1]}: {record[2][:50]}...")
        else:
            print(f"\n✅ No Error Records Found")
        
        # Check table schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'marketing_checklist'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        
        print(f"\n🗄️  Table Schema:")
        for col_name, data_type, nullable in columns:
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"   {col_name:<25} | {data_type:<20} | {nullable_str}")
        
        print("\n" + "="*60)
        print("✅ Database verification completed successfully!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🗄️  Railway PostgreSQL Database Verification")
    print("=" * 60)
    check_database() 