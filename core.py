"""
PDF Downloader Core Module
Handles PDF searching, downloading, and organization
"""

import os
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
from datetime import datetime

class PDFDownloader:
    def __init__(self):
        """Initialize the PDF downloader"""
        self.base_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'DataCenter_PDF_Library')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded_files = []
        
        # Create base directory
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def search_and_download_pdfs(self, search_term, category, max_results=10):
        """Search for and download PDFs for a given term"""
        category_path = os.path.join(self.base_path, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        # Search multiple sources
        pdf_urls = []
        pdf_urls.extend(self._search_google_filetype(search_term, max_results//3))
        pdf_urls.extend(self._search_vendor_sites(search_term, max_results//3))
        pdf_urls.extend(self._search_educational_sites(search_term, max_results//3))
        
        # Remove duplicates
        pdf_urls = list(set(pdf_urls))
        
        downloaded_count = 0
        for url in pdf_urls[:max_results]:
            if self._download_pdf(url, category_path, search_term):
                downloaded_count += 1
        
        return downloaded_count > 0
    
    def _search_google_filetype(self, search_term, limit=5):
        """Search Google for PDF files using filetype operator"""
        # Note: This is a simplified approach. In production, use Google Custom Search API
        search_query = f"{search_term} filetype:pdf"
        print(f"  Searching: {search_query}")
        
        # This would typically use Google Custom Search API or similar
        # For demonstration, returning common manual URLs patterns
        return self._get_common_manual_urls(search_term)
    
    def _get_common_manual_urls(self, search_term):
        """Get URLs for common vendor manual sites"""
        urls = []
        
        # Common vendor documentation patterns (examples)
        vendor_patterns = {
            'dell': 'https://www.dell.com/support/manuals/',
            'hp': 'https://support.hpe.com/hpesc/public/docDisplay',
            'cisco': 'https://www.cisco.com/c/en/us/support/',
            'ibm': 'https://www.ibm.com/docs/',
            'supermicro': 'https://www.supermicro.com/manuals/'
        }
        
        # This is a placeholder - real implementation would scrape these sites
        return []
    
    def _search_vendor_sites(self, search_term, limit=3):
        """Search specific vendor documentation sites"""
        vendor_urls = []
        
        # Major server/networking vendors
        vendors = [
            'dell.com/support',
            'hpe.com/support', 
            'cisco.com/support',
            'juniper.net/documentation',
            'supermicro.com/manuals'
        ]
        
        # Placeholder for vendor-specific searching
        return vendor_urls
    
    def _search_educational_sites(self, search_term, limit=2):
        """Search educational and certification sites"""
        edu_urls = []
        
        # Common educational resources
        edu_sites = [
            'comptia.org',
            'cisco.com/learning',
            'redhat.com/training'
        ]
        
        # Placeholder for educational site searching
        return edu_urls
    
    def _download_pdf(self, url, category_path, search_term):
        """Download a PDF file"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            if 'application/pdf' not in response.headers.get('content-type', ''):
                return False
            
            # Generate filename
            filename = self._generate_filename(url, search_term)
            filepath = os.path.join(category_path, filename)
            
            # Don't download if file already exists
            if os.path.exists(filepath):
                print(f"    File already exists: {filename}")
                return True
            
            # Save the PDF
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Track download
            self.downloaded_files.append({
                'filename': filename,
                'url': url,
                'category': os.path.basename(category_path),
                'search_term': search_term,
                'size': len(response.content),
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"    ✓ Downloaded: {filename} ({len(response.content)} bytes)")
            return True
            
        except Exception as e:
            print(f"    ✗ Failed to download {url}: {str(e)}")
            return False
    
    def _generate_filename(self, url, search_term):
        """Generate a descriptive filename for the PDF"""
        # Extract filename from URL
        parsed_url = urlparse(url)
        original_name = os.path.basename(parsed_url.path)
        
        if not original_name or not original_name.endswith('.pdf'):
            # Generate name from search term
            safe_term = "".join(c for c in search_term if c.isalnum() or c in (' ', '-', '_')).rstrip()
            original_name = f"{safe_term.replace(' ', '_')}.pdf"
        
        return original_name
    
    def generate_summary_report(self):
        """Generate a summary report of all downloads"""
        report_path = os.path.join(self.base_path, 'download_report.json')
        
        summary = {
            'total_files': len(self.downloaded_files),
            'categories': {},
            'files': self.downloaded_files,
            'generated_at': datetime.now().isoformat()
        }
        
        # Group by category
        for file_info in self.downloaded_files:
            category = file_info['category']
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary Report:")
        print(f"Total files downloaded: {summary['total_files']}")
        for category, count in summary['categories'].items():
            print(f"  {category}: {count} files")
        print(f"Report saved to: {report_path}")