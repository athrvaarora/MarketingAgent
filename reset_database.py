#!/usr/bin/env python3
"""
Database Reset Script
Resets the marketing_checklist table to its initial state by clearing all tracking data.

This script will:
- Reset visited status to 'NO'
- Reset downloaded status to 'NO'
- Clear marketing_files_found
- Reset download_status to 'PENDING'
- Clear notes
- Clear last_attempt timestamp
- Clear error_message
- Update updated_at timestamp

@file purpose: Resets the Railway PostgreSQL database to initial state
"""

import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

def reset_database():
    """Reset the marketing_checklist table to initial state"""
    
    # Load environment variables
    load_dotenv("marketing_agent.env")
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in marketing_agent.env")
        return False
    
    conn = None
    cursor = None
    
    try:
        # Connect to the database
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get current stats before reset
        print("📊 Getting current database statistics...")
        
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist;")
        total_properties = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist WHERE UPPER(visited) = 'YES';")
        visited_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist WHERE UPPER(downloaded) = 'YES';")
        downloaded_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist WHERE download_status != 'PENDING';")
        processed_count = cursor.fetchone()[0]
        
        print(f"📈 Current Status:")
        print(f"   Total Properties: {total_properties}")
        print(f"   Visited: {visited_count}")
        print(f"   Downloaded: {downloaded_count}")
        print(f"   Processed: {processed_count}")
        
        # Confirm reset
        response = input("\n🔄 Are you sure you want to reset the database to initial state? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Reset cancelled.")
            return False
        
        # Reset all tracking columns to initial state
        reset_sql = """
        UPDATE marketing_checklist 
        SET 
            visited = 'NO',
            downloaded = 'NO',
            marketing_files_found = NULL,
            download_status = 'PENDING',
            notes = NULL,
            last_attempt = NULL,
            error_message = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE 
            visited != 'NO' OR 
            downloaded != 'NO' OR 
            marketing_files_found IS NOT NULL OR 
            download_status != 'PENDING' OR 
            notes IS NOT NULL OR 
            last_attempt IS NOT NULL OR 
            error_message IS NOT NULL;
        """
        
        print("🔄 Resetting database to initial state...")
        cursor.execute(reset_sql)
        
        # Get the number of rows that were updated
        updated_rows = cursor.rowcount
        
        # Commit the changes
        conn.commit()
        
        print(f"✅ Successfully reset {updated_rows} properties to initial state!")
        
        # Display final stats
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist WHERE download_status = 'PENDING';")
        pending_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT website_group, COUNT(*) FROM marketing_checklist GROUP BY website_group ORDER BY website_group;")
        website_stats = cursor.fetchall()
        
        print(f"\n📊 Final Status:")
        print(f"   Total Properties: {total_properties}")
        print(f"   Pending: {pending_count}")
        print(f"   Visited: 0")
        print(f"   Downloaded: 0")
        
        print(f"\n🏢 Properties by Website Group:")
        for website_group, count in website_stats:
            print(f"   {website_group}: {count}")
        
        print(f"\n🎯 Database has been reset to initial state!")
        print(f"   All properties are now ready for processing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🗄️  Database Reset Script")
    print("=" * 50)
    print("This script will reset the marketing_checklist table to its initial state.")
    print("All tracking data will be cleared and properties will be marked as PENDING.")
    print("=" * 50)
    
    success = reset_database()
    
    if success:
        print("\n🎉 Database reset completed successfully!")
        print("💡 You can now run the marketing agent to start fresh.")
    else:
        print("\n❌ Database reset failed!") 