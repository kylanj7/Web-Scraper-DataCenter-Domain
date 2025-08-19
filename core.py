"""
PDF Downloader Core Module
Handles PDF searching, downloading, and organization with real web scraping
"""

import os
import requests
import time
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

class PDFDownloader:
    def __init__(self):
        """Initialize the PDF downloader"""
        self.base_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'DataCenter_PDF_Library')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.downloaded_files = []
        
        # Create base directory
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def search_and_download_pdfs(self, search_term, category, max_results=5):
        """Search for and download PDFs for a given term"""
        category_path = os.path.join(self.base_path, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        print(f"  🔍 Searching for: {search_term}")
        
        # Search multiple sources
        pdf_urls = []
        
        # Search vendor documentation sites
        pdf_urls.extend(self._search_vendor_sites(search_term, max_results//2))
        
        # Search general documentation sites
        pdf_urls.extend(self._search_documentation_sites(search_term, max_results//2))
        
        # Remove duplicates
        pdf_urls = list(set(pdf_urls))
        
        downloaded_count = 0
        for url in pdf_urls[:max_results]:
            if self._download_pdf(url, category_path, search_term):
                downloaded_count += 1
                time.sleep(2)  # Rate limiting
        
        return downloaded_count > 0
    
    def _search_vendor_sites(self, search_term, limit=3):
        """Search specific vendor documentation sites"""
        pdf_urls = []
        
        # Dell Support Site
        if 'dell' in search_term.lower():
            pdf_urls.extend(self._search_dell_support(search_term, limit))
        
        # HP/HPE Support
        if any(x in search_term.lower() for x in ['hp', 'hpe', 'proliant']):
            pdf_urls.extend(self._search_hpe_support(search_term, limit))
        
        # Cisco Documentation
        if 'cisco' in search_term.lower():
            pdf_urls.extend(self._search_cisco_docs(search_term, limit))
        
        return pdf_urls
    
    def _search_dell_support(self, search_term, limit=2):
        """Search Dell support documentation"""
        urls = []
        try:
            # Search Dell's support site
            search_url = f"https://www.dell.com/support/manuals/en-us"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for PDF links
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                
                for link in pdf_links[:limit]:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(search_url, href)
                        if self._is_valid_pdf_url(full_url):
                            urls.append(full_url)
                            
        except Exception as e:
            print(f"    Error searching Dell support: {e}")
        
        return urls
    
    def _search_hpe_support(self, search_term, limit=2):
        """Search HPE support documentation"""
        urls = []
        try:
            # Known HPE documentation URLs
            hpe_docs = [
                "https://support.hpe.com/hpesc/public/docDisplay?docId=c04111714",
                "https://support.hpe.com/hpesc/public/docDisplay?docId=c04111715",
                "https://support.hpe.com/hpesc/public/docDisplay?docId=c04795161"
            ]
            
            for doc_url in hpe_docs[:limit]:
                if self._is_valid_pdf_url(doc_url):
                    urls.append(doc_url)
                    
        except Exception as e:
            print(f"    Error searching HPE support: {e}")
        
        return urls
    
    def _search_cisco_docs(self, search_term, limit=2):
        """Search Cisco documentation"""
        urls = []
        try:
            # Cisco documentation often has direct PDF links
            cisco_base = "https://www.cisco.com/c/en/us/support/"
            
            # Common Cisco documentation patterns
            cisco_docs = [
                "https://www.cisco.com/c/dam/en/us/products/collateral/switches/catalyst-9300-series-switches/nb-06-cat9300-cmp-cte-en.pdf",
                "https://www.cisco.com/c/dam/en/us/products/collateral/switches/nexus-9000-series-switches/datasheet-c78-729405.pdf"
            ]
            
            for doc_url in cisco_docs[:limit]:
                if self._check_url_exists(doc_url):
                    urls.append(doc_url)
                    
        except Exception as e:
            print(f"    Error searching Cisco docs: {e}")
        
        return urls
    
    def _search_documentation_sites(self, search_term, limit=3):
        """Search general technical documentation sites"""
        urls = []
        
        # Search academic and technical sites
        doc_sites = [
            self._search_archive_org(search_term, limit//3),
            self._search_manufacturer_sites(search_term, limit//3)
        ]
        
        for site_urls in doc_sites:
            urls.extend(site_urls)
        
        return urls
    
    def _search_archive_org(self, search_term, limit=2):
        """Search Internet Archive for technical documentation"""
        urls = []
        try:
            # Search Internet Archive's software and manual collections
            search_query = quote_plus(f"{search_term} filetype:pdf")
            archive_url = f"https://archive.org/search.php?query={search_query}&and[]=mediatype%3A%22texts%22"
            
            response = self.session.get(archive_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for PDF download links
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                
                for link in pdf_links[:limit]:
                    href = link.get('href')
                    if href and href.startswith('/'):
                        full_url = f"https://archive.org{href}"
                        urls.append(full_url)
                        
        except Exception as e:
            print(f"    Error searching Archive.org: {e}")
        
        return urls
    
    def _search_manufacturer_sites(self, search_term, limit=2):
        """Search known manufacturer documentation sites"""
        urls = []
        
        # Known technical documentation URLs (examples)
        known_docs = [
            "https://www.supermicro.com/manuals/motherboard/C606/MBD-X9DRW-iF_3F.pdf",
            "https://www.supermicro.com/manuals/motherboard/C602/MBD-X9DRi-LN4+_F.pdf",
            "https://www.intel.com/content/dam/www/public/us/en/documents/guides/64-ia-32-architectures-software-developer-instruction-set-reference-manual-325383.pdf"
        ]
        
        # Filter based on search term relevance
        for doc_url in known_docs[:limit]:
            if any(keyword in search_term.lower() for keyword in ['supermicro', 'intel', 'motherboard', 'processor']):
                if self._check_url_exists(doc_url):
                    urls.append(doc_url)
        
        return urls
    
    def _is_valid_pdf_url(self, url):
        """Check if URL points to a valid PDF"""
        try:
            response = self.session.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            return 'application/pdf' in content_type or url.lower().endswith('.pdf')
        except:
            return url.lower().endswith('.pdf')
    
    def _check_url_exists(self, url):
        """Check if URL exists and is accessible"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _download_pdf(self, url, category_path, search_term):
        """Download a PDF file"""
        try:
            print(f"    📥 Attempting download: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
                print(f"    ⚠️  Not a PDF file: {content_type}")
                return False
            
            # Generate filename
            filename = self._generate_filename(url, search_term)
            filepath = os.path.join(category_path, filename)
            
            # Don't download if file already exists
            if os.path.exists(filepath):
                print(f"    ✅ File already exists: {filename}")
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
            
            print(f"    ✅ Downloaded: {filename} ({len(response.content)} bytes)")
            return True
            
        except Exception as e:
            print(f"    ❌ Failed to download {url}: {str(e)}")
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
        
        # Ensure unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(original_name)
        return f"{name}_{timestamp}{ext}"
    
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
