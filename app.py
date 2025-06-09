#!/usr/bin/env python3
"""
Marketing Package Agent Web Interface
Beautiful frontend for managing marketing package downloads with real-time database integration
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for
from flask_socketio import SocketIO, emit
import psycopg2
import os
import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv("marketing_agent.env")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'marketing_agent_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for tracking
active_processes = {}
download_progress = {}

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in marketing_agent.env")
    
    def get_connection(self):
        return psycopg2.connect(self.database_url)
    
    def get_all_properties(self):
        """Get all properties from database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, website_group, property_number, property_name, property_url,
                       visited, downloaded, marketing_files_found, download_status,
                       notes, last_attempt, error_message, created_at, updated_at
                FROM marketing_checklist 
                ORDER BY property_number;
            """)
            
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            properties = []
            for row in results:
                prop = dict(zip(columns, row))
                # Format datetime fields
                for field in ['last_attempt', 'created_at', 'updated_at']:
                    if prop[field]:
                        prop[field] = prop[field].strftime('%Y-%m-%d %H:%M:%S')
                properties.append(prop)
            
            cursor.close()
            conn.close()
            return properties
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def get_progress_stats(self):
        """Get progress statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN visited = 'YES' THEN 1 ELSE 0 END) as visited,
                    SUM(CASE WHEN downloaded = 'YES' THEN 1 ELSE 0 END) as downloaded,
                    SUM(CASE WHEN download_status = 'SUCCESS' THEN 1 ELSE 0 END) as successful
                FROM marketing_checklist;
            """)
            
            total, visited, downloaded, successful = cursor.fetchone()
            
            # Get stats by website group
            cursor.execute("""
                SELECT website_group, 
                       COUNT(*) as total,
                       SUM(CASE WHEN downloaded = 'YES' THEN 1 ELSE 0 END) as completed
                FROM marketing_checklist 
                GROUP BY website_group;
            """)
            
            group_stats = {}
            for row in cursor.fetchall():
                group_stats[row[0]] = {
                    'total': row[1],
                    'completed': row[2],
                    'percentage': (row[2] / row[1] * 100) if row[1] > 0 else 0
                }
            
            cursor.close()
            conn.close()
            
            return {
                'total': total,
                'visited': visited,
                'downloaded': downloaded,
                'successful': successful,
                'overall_percentage': (successful / total * 100) if total > 0 else 0,
                'groups': group_stats
            }
        except Exception as e:
            print(f"Database error: {e}")
            return {}

db_manager = DatabaseManager()

def get_local_pdfs():
    """Get list of local PDF files organized by website group"""
    pdf_structure = {
        'levyretail': [],
        'tag-industries': [],
        'netleaseadvisorygroup': []
    }
    
    download_folder = "marketing_packages"
    
    for subfolder in pdf_structure.keys():
        folder_path = os.path.join(download_folder, subfolder)
        if os.path.exists(folder_path):
            pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
            for pdf_file in pdf_files:
                file_info = {
                    'name': os.path.basename(pdf_file),
                    'path': pdf_file,
                    'size': os.path.getsize(pdf_file),
                    'modified': datetime.fromtimestamp(os.path.getmtime(pdf_file)).strftime('%Y-%m-%d %H:%M:%S')
                }
                pdf_structure[subfolder].append(file_info)
    
    return pdf_structure

@app.route('/')
def home():
    """Home page with form"""
    progress_stats = db_manager.get_progress_stats()
    local_pdfs = get_local_pdfs()
    return render_template('home.html', progress_stats=progress_stats, local_pdfs=local_pdfs)

@app.route('/downloads')
def downloads():
    """Downloads page showing all PDFs"""
    local_pdfs = get_local_pdfs()
    return render_template('downloads.html', local_pdfs=local_pdfs)

@app.route('/database')
def database():
    """Database page showing real-time data"""
    properties = db_manager.get_all_properties()
    return render_template('database.html', properties=properties)

@app.route('/api/progress')
def api_progress():
    """API endpoint for progress data"""
    return jsonify(db_manager.get_progress_stats())

@app.route('/api/properties')
def api_properties():
    """API endpoint for all properties"""
    return jsonify(db_manager.get_all_properties())

@app.route('/api/pdfs')
def api_pdfs():
    """API endpoint for local PDFs"""
    return jsonify(get_local_pdfs())

@app.route('/api/submit_job', methods=['POST'])
def submit_job():
    """Submit marketing package job"""
    data = request.json
    
    website_group = data.get('website_group')
    max_properties = data.get('max_properties')
    headless = data.get('headless', False)
    
    # Convert max_properties to integer if it's not None
    if max_properties is not None:
        try:
            max_properties = int(max_properties)
        except (ValueError, TypeError):
            max_properties = None
    
    # Build command
    cmd = ['python3', 'marketing_package_agent.py']
    
    if website_group and website_group != 'ALL':
        cmd.extend(['-g', website_group])
    
    if max_properties and max_properties > 0:
        cmd.extend(['-m', str(max_properties)])
    
    if headless:
        cmd.append('--headless')
    
    # Generate job ID
    job_id = f"job_{int(time.time())}"
    
    # Start the process in a thread
    thread = threading.Thread(
        target=run_marketing_agent,
        args=(cmd, job_id, headless)
    )
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'command': ' '.join(cmd)
    })

def run_marketing_agent(cmd, job_id, headless):
    """Run marketing agent in separate thread"""
    try:
        # Set environment for headless mode
        env = os.environ.copy()
        if headless:
            env['BROWSER_HEADLESS'] = 'true'
        
        # Emit job started
        socketio.emit('job_started', {
            'job_id': job_id,
            'command': ' '.join(cmd),
            'timestamp': datetime.now().isoformat()
        })
        
        # Run the process with combined stdout and stderr
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout to avoid duplication
            text=True,
            env=env,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        active_processes[job_id] = process
        
        # Stream output
        for line in iter(process.stdout.readline, ''):
            if line:
                socketio.emit('job_output', {
                    'job_id': job_id,
                    'line': line.strip(),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Wait for completion
        process.wait()
        
        # Emit completion
        socketio.emit('job_completed', {
            'job_id': job_id,
            'return_code': process.returncode,
            'timestamp': datetime.now().isoformat()
        })
        
        # Clean up
        if job_id in active_processes:
            del active_processes[job_id]
            
    except Exception as e:
        socketio.emit('job_error', {
            'job_id': job_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/pdf/<path:filename>')
def serve_pdf(filename):
    """Serve PDF files"""
    try:
        # Security check - ensure file is in marketing_packages directory
        file_path = os.path.join('marketing_packages', filename)
        if os.path.exists(file_path) and file_path.startswith('marketing_packages/'):
            return send_file(file_path)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {e}", 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to Marketing Agent'})

@socketio.on('request_progress')
def handle_progress_request():
    """Handle progress data request"""
    progress_stats = db_manager.get_progress_stats()
    emit('progress_update', progress_stats)

@socketio.on('request_database_update')
def handle_database_update():
    """Handle database update request"""
    properties = db_manager.get_all_properties()
    emit('database_update', properties)

if __name__ == '__main__':
    # Ensure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🚀 Starting Marketing Package Agent Web Interface")
    print("📱 Open your browser to: http://localhost:5001")
    print("🎨 Theme: Neon Purple & White")
    print("🗄️  Database: Railway PostgreSQL")
    print("📁 Downloads: marketing_packages/")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001) 