import requests
import os
from urllib.parse import urlparse

def download_pdf(url, filename=None, download_dir=None):
    """
    Download a PDF file from a URL
    
    Args:
        url (str): URL of the PDF to download
        filename (str): Optional custom filename. If None, uses original filename from URL
        download_dir (str): Directory to save the file. If None, saves to current directory
    """
    
    try:
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Send GET request to download the file
        print(f"Downloading PDF from: {url}")
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Determine filename
        if filename is None:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith('.pdf'):
                filename += '.pdf'
        
        # Ensure filename ends with .pdf
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Handle download directory
        if download_dir:
            # Create directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            filepath = os.path.join(download_dir, filename)
        else:
            filepath = filename
        
        # Write the file
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"✅ Successfully downloaded: {filepath}")
        print(f"📁 File size: {os.path.getsize(filepath):,} bytes")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading file: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    import sys
    
    # Check if URL is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python3 download_pdf.py <PDF_URL> [download_directory]")
        print("Example: python3 download_pdf.py 'https://example.com/file.pdf' '/path/to/download/folder'")
        sys.exit(1)
    
    # Get URL from command line
    pdf_url = sys.argv[1]
    
    # Get download directory from command line (optional)
    download_directory = None
    if len(sys.argv) >= 3:
        download_directory = sys.argv[2]
    
    # Download the PDF
    download_pdf(pdf_url, download_dir=download_directory)