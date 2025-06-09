import psycopg2
import csv
from datetime import datetime

# @file purpose: Creates a Railway database table from marketing_checklist CSV data
# This script connects to Railway PostgreSQL database and creates a marketing_checklist table
# with proper schema and imports all data from the CSV file

def create_railway_table():
    """
    Connect to Railway database and create marketing_checklist table with data
    """
    
    # Railway database connection URL
    database_url = "postgresql://postgres:PNfOjrNuJKHaduPikWLwfWNCstlsxubj@switchyard.proxy.rlwy.net:25064/railway"
    
    conn = None
    cursor = None
    
    try:
        # Connect to the database
        print("🔌 Connecting to Railway database...")
        print(f"   URL: {database_url.split('@')[0]}@***")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create table SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS marketing_checklist (
            id SERIAL PRIMARY KEY,
            website_group VARCHAR(100) NOT NULL,
            property_number INTEGER,
            property_name VARCHAR(200) NOT NULL,
            property_url TEXT NOT NULL,
            visited VARCHAR(10) DEFAULT 'NO',
            downloaded VARCHAR(10) DEFAULT 'NO',
            marketing_files_found TEXT,
            download_status VARCHAR(50) DEFAULT 'PENDING',
            notes TEXT,
            last_attempt TIMESTAMP,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        print("🏗️  Creating marketing_checklist table...")
        cursor.execute(create_table_sql)
        
        # Create indexes for better performance
        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_website_group ON marketing_checklist(website_group);",
            "CREATE INDEX IF NOT EXISTS idx_download_status ON marketing_checklist(download_status);",
            "CREATE INDEX IF NOT EXISTS idx_property_name ON marketing_checklist(property_name);"
        ]
        
        for index_sql in create_indexes_sql:
            cursor.execute(index_sql)
        
        print("📊 Creating indexes...")
        
        # Clear existing data (optional)
        cursor.execute("DELETE FROM marketing_checklist;")
        print("🧹 Cleared existing data...")
        
        # Insert data from CSV
        insert_sql = """
        INSERT INTO marketing_checklist 
        (website_group, property_number, property_name, property_url, visited, downloaded, 
         marketing_files_found, download_status, notes, last_attempt, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        print("📝 Reading and inserting CSV data...")
        
        # Read CSV file and insert data
        with open('marketing_checklist_20250607_231412.csv', 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            
            rows_inserted = 0
            for row in csv_reader:
                try:
                    # Handle empty values
                    property_number = int(row['property_number']) if row['property_number'] else None
                    last_attempt = None if not row['last_attempt'] else row['last_attempt']
                    
                    data = (
                        row['website_group'],
                        property_number,
                        row['property_name'],
                        row['property_url'],
                        row['visited'] or 'NO',
                        row['downloaded'] or 'NO',
                        row['marketing_files_found'] or None,
                        row['download_status'] or 'PENDING',
                        row['notes'] or None,
                        last_attempt,
                        row['error_message'] or None
                    )
                    
                    cursor.execute(insert_sql, data)
                    rows_inserted += 1
                    
                except Exception as e:
                    print(f"❌ Error inserting row: {row['property_name']} - {e}")
                    continue
        
        # Commit the transaction
        conn.commit()
        
        print(f"✅ Successfully created table and inserted {rows_inserted} rows!")
        
        # Display summary statistics
        cursor.execute("SELECT COUNT(*) FROM marketing_checklist;")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT website_group, COUNT(*) FROM marketing_checklist GROUP BY website_group ORDER BY COUNT(*) DESC;")
        website_stats = cursor.fetchall()
        
        cursor.execute("SELECT download_status, COUNT(*) FROM marketing_checklist GROUP BY download_status;")
        status_stats = cursor.fetchall()
        
        print(f"\n📊 Database Summary:")
        print(f"   Total properties: {total_count}")
        print(f"\n🌐 Properties by website:")
        for website, count in website_stats:
            print(f"   {website}: {count} properties")
        
        print(f"\n📈 Status distribution:")
        for status, count in status_stats:
            print(f"   {status}: {count} properties")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if the Railway URL is correct")
        print("   2. Verify the database credentials")
        print("   3. Check your internet connection")
        print("   4. Ensure Railway service is running")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("🔌 Database connection closed.")

if __name__ == "__main__":
    print("🚀 Starting Railway table creation process...")
    create_railway_table()
    print("✨ Process completed!") 