"""
PDF Downloader Core Module
Real web-wide search for technical documentation
"""

import os
import requests
import time
from urllib.parse import urljoin, urlparse, quote_plus, unquote
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import random

class PDFDownloader:
    def __init__(self):
        """Initialize the PDF downloader"""
        self.base_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'DataCenter_PDF_Library')
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.downloaded_files = []
        
        # Create base directory
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def _get_random_headers(self):
        """Get random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
    
    def search_and_download_pdfs(self, search_term, category, max_results=10):
        """Search the entire web for PDFs"""
        category_path = os.path.join(self.base_path, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        print(f"  🌐 Web-wide search for: {search_term}")
        
        # Multiple search engines and methods
        pdf_urls = []
        
        # 1. DuckDuckGo (most permissive for automated searches)
        pdf_urls.extend(self._search_duckduckgo(search_term, max_results//3))
        
        # 2. Bing search (less restrictive than Google)
        pdf_urls.extend(self._search_bing(search_term, max_results//3))
        
        # 3. Yandex search (alternative search engine)
        pdf_urls.extend(self._search_yandex(search_term, max_results//4))
        
        # 4. Archive.org search
        pdf_urls.extend(self._search_archive_org(search_term, max_results//4))
        
        # 5. Academic and repository sites
        pdf_urls.extend(self._search_academic_sites(search_term, max_results//4))
        
        # 6. Technical documentation aggregators
        pdf_urls.extend(self._search_doc_aggregators(search_term, max_results//4))
        
        # Remove duplicates and validate
        unique_urls = list(set(pdf_urls))
        print(f"    📋 Found {len(unique_urls)} unique PDF candidates")
        
        downloaded_count = 0
        for i, url in enumerate(unique_urls[:max_results]):
            print(f"    📥 Processing {i+1}/{min(len(unique_urls), max_results)}: {url[:80]}...")
            
            if self._download_pdf(url, category_path, search_term):
                downloaded_count += 1
            
            # Random delay to be respectful
            time.sleep(random.uniform(1, 3))
        
        return downloaded_count > 0
    
    def _search_duckduckgo(self, search_term, limit=5):
        """Search DuckDuckGo for PDFs"""
        urls = []
        try:
            self.session.headers.update(self._get_random_headers())
            
            # DuckDuckGo search with filetype filter
            search_query = f"{search_term} filetype:pdf"
            encoded_query = quote_plus(search_query)
            ddg_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(ddg_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find result links
                links = soup.find_all('a', {'class': 'result__a'})
                
                for link in links[:limit*2]:
                    href = link.get('href')
                    if href and self._is_pdf_url(href):
                        # Clean DuckDuckGo redirect URL
                        if '/l/?uddg=' in href:
                            clean_url = unquote(href.split('/l/?uddg=')[1].split('&')[0])
                            urls.append(clean_url)
                        elif href.startswith('http'):
                            urls.append(href)
                            
            print(f"    🦆 DuckDuckGo found {len(urls)} PDFs")
            
        except Exception as e:
            print(f"    ⚠️  DuckDuckGo error: {e}")
        
        return urls[:limit]
    
    def _search_bing(self, search_term, limit=5):
        """Search Bing for PDFs"""
        urls = []
        try:
            self.session.headers.update(self._get_random_headers())
            
            search_query = f"{search_term} filetype:pdf"
            encoded_query = quote_plus(search_query)
            bing_url = f"https://www.bing.com/search?q={encoded_query}"
            
            response = self.session.get(bing_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Bing result links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    if href and self._is_pdf_url(href) and 'bing.com' not in href:
                        urls.append(href)
                        if len(urls) >= limit:
                            break
                            
            print(f"    🔍 Bing found {len(urls)} PDFs")
            
        except Exception as e:
            print(f"    ⚠️  Bing error: {e}")
        
        return urls[:limit]
    
    def _search_yandex(self, search_term, limit=3):
        """Search Yandex for PDFs"""
        urls = []
        try:
            self.session.headers.update(self._get_random_headers())
            
            search_query = f"{search_term} filetype:pdf"
            encoded_query = quote_plus(search_query)
            yandex_url = f"https://yandex.com/search/?text={encoded_query}"
            
            response = self.session.get(yandex_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    if href and self._is_pdf_url(href) and 'yandex.' not in href:
                        urls.append(href)
                        if len(urls) >= limit:
                            break
                            
            print(f"    🔴 Yandex found {len(urls)} PDFs")
            
        except Exception as e:
            print(f"    ⚠️  Yandex error: {e}")
        
        return urls[:limit]
    
    def _search_archive_org(self, search_term, limit=3):
        """Search Internet Archive for technical documentation"""
        urls = []
        try:
            self.session.headers.update(self._get_random_headers())
            
            # Archive.org search
            search_query = quote_plus(f"{search_term} AND mediatype:texts")
            archive_url = f"https://archive.org/search.php?query={search_query}&and[]=format%3A%22PDF%22"
            
            response = self.session.get(archive_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for download links
                download_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                
                for link in download_links[:limit]:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            full_url = f"https://archive.org{href}"
                        else:
                            full_url = href
                        urls.append(full_url)
                        
            print(f"    📚 Archive.org found {len(urls)} PDFs")
            
        except Exception as e:
            print(f"    ⚠️  Archive.org error: {e}")
        
        return urls[:limit]
    
    def _search_academic_sites(self, search_term, limit=3):
        """Search academic and research sites"""
        urls = []
        
        # Known academic repositories with technical documentation
        academic_sites = [
            "https://www.researchgate.net",
            "https://arxiv.org",
            "https://ieeexplore.ieee.org",
            "https://dl.acm.org"
        ]
        
        try:
            for site in academic_sites:
                site_urls = self._search_specific_site(site, search_term, limit//len(academic_sites))
                urls.extend(site_urls)
                
            print(f"    🎓 Academic sites found {len(urls)} PDFs")
            
        except Exception as e:
            print(f"    ⚠️  Academic search error: {e}")
        
        return urls[:limit]
    
    def _search_doc_aggregators(self, search_term, limit=3):
        """Search documentation aggregator sites"""
        urls = []
        
        # Sites that aggregate technical documentation
        doc_sites = [
            ("https://manualslib.com", "manual documentation"),
            ("https://fccid.io", "FCC equipment documentation"),
            ("https://www.manualsdir.com", "technical manuals")
        ]
        
        for site_url, description in doc_sites:
            try:
                self.session.headers.update(self._get_random_headers())
                
                # Search within the site
                search_url = f"{site_url}/search?q={quote_plus(search_term)}"
                
                response = self.session.get(search_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                    
                    for link in pdf_links[:limit//len(doc_sites)]:
                        href = link.get('href')
                        if href:
                            full_url = urljoin(site_url, href)
                            urls.append(full_url)
                            
            except Exception as e:
                continue
        
        print(f"    📋 Documentation sites found {len(urls)} PDFs")
        return urls[:limit]
    
    def _search_specific_site(self, site_url, search_term, limit=2):
        """Search a specific site for PDFs"""
        urls = []
        try:
            # Use site-specific search if available
            search_query = f"site:{site_url} {search_term} filetype:pdf"
            ddg_search = f"https://duckduckgo.com/html/?q={quote_plus(search_query)}"
            
            self.session.headers.update(self._get_random_headers())
            response = self.session.get(ddg_search, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', {'class': 'result__a'})
                
                for link in links[:limit]:
                    href = link.get('href')
                    if href and self._is_pdf_url(href):
                        if '/l/?uddg=' in href:
                            clean_url = unquote(href.split('/l/?uddg=')[1].split('&')[0])
                            urls.append(clean_url)
                        elif href.startswith('http'):
                            urls.append(href)
                            
        except Exception as e:
            pass
        
        return urls[:limit]
    
    def _is_pdf_url(self, url):
        """Check if URL likely points to a PDF"""
        if not url or not isinstance(url, str):
            return False
        
        url_lower = url.lower()
        
        # Direct PDF extension
        if url_lower.endswith('.pdf'):
            return True
        
        # PDF in URL path
        if '.pdf' in url_lower:
            return True
        
        # Common PDF URL patterns
        pdf_patterns = [
            'download.pdf',
            'manual.pdf',
            'guide.pdf',
            'documentation.pdf',
            'doc.pdf'
        ]
        
        return any(pattern in url_lower for pattern in pdf_patterns)
    
    def _download_pdf(self, url, category_path, search_term):
        """Download a PDF file with comprehensive error handling"""
        try:
            # Update headers for each download
            self.session.headers.update(self._get_random_headers())
            
            print(f"      📥 Downloading: {url}")
            
            # Handle redirects and get final URL
            response = self.session.get(url, timeout=30, allow_redirects=True, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            # Read content in chunks for large files
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                
            # Verify it's a PDF
            is_pdf = (
                'application/pdf' in content_type or
                url.lower().endswith('.pdf') or
                content.startswith(b'%PDF') or
                b'PDF' in content[:100]
            )
            
            if not is_pdf:
                print(f"      ⚠️  Not a PDF file (Content-Type: {content_type})")
                return False
            
            # Check file size
            content_length = len(content)
            if content_length < 1024:  # Less than 1KB
                print(f"      ⚠️  File too small ({content_length} bytes)")
                return False
            
            # Log large files
            if content_length > 50 * 1024 * 1024:  # More than 50MB
                print(f"      📚 Large file ({content_length / (1024*1024):.1f} MB)")
            
            # Generate filename
            filename = self._generate_filename(url, search_term)
            filepath = os.path.join(category_path, filename)
            
            # Don't download if file already exists
            if os.path.exists(filepath):
                print(f"      ✅ File already exists: {filename}")
                return True
            
            # Save the PDF
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # Track download
            self.downloaded_files.append({
                'filename': filename,
                'url': url,
                'category': os.path.basename(category_path),
                'search_term': search_term,
                'size': content_length,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"      ✅ SUCCESS: {filename} ({content_length / 1024:.1f} KB)")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"      ❌ Network error: {str(e)[:100]}")
            return False
        except Exception as e:
            print(f"      ❌ Download error: {str(e)[:100]}")
            return False
    
    def _generate_filename(self, url, search_term):
        """Generate a safe filename for the PDF"""
        # Extract filename from URL
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        original_name = os.path.basename(path)
        
        # Clean the filename
        if original_name and '.' in original_name:
            name = original_name.split('?')[0].split('#')[0]
            if not name.lower().endswith('.pdf'):
                name += '.pdf'
        else:
            # Generate from search term
            safe_term = re.sub(r'[^\w\s-]', '', search_term)
            name = f"{safe_term.replace(' ', '_')}.pdf"
        
        # Ensure filename is filesystem-safe
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name[:100]  # Limit length
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%m%d_%H%M")
        name_parts = name.rsplit('.', 1)
        if len(name_parts) == 2:
            final_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            final_name = f"{name}_{timestamp}.pdf"
        
        return final_name
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        report_path = os.path.join(self.base_path, 'download_report.json')
        
        total_size = sum(f['size'] for f in self.downloaded_files)
        
        summary = {
            'total_files': len(self.downloaded_files),
            'total_size_mb': total_size / (1024 * 1024),
            'categories': {},
            'files': self.downloaded_files,
            'generated_at': datetime.now().isoformat(),
            'search_summary': {
                'total_searches': len(set(f['search_term'] for f in self.downloaded_files)),
                'successful_downloads': len(self.downloaded_files)
            }
        }
        
        # Group by category
        for file_info in self.downloaded_files:
            category = file_info['category']
            if category not in summary['categories']:
                summary['categories'][category] = {'count': 0, 'size_mb': 0}
            summary['categories'][category]['count'] += 1
            summary['categories'][category]['size_mb'] += file_info['size'] / (1024 * 1024)
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"📁 Total files downloaded: {summary['total_files']}")
        print(f"💾 Total size: {summary['total_size_mb']:.1f} MB")
        print(f"🔍 Search terms processed: {summary['search_summary']['total_searches']}")
        
        for category, stats in summary['categories'].items():
            print(f"  📂 {category}: {stats['count']} files ({stats['size_mb']:.1f} MB)")
            
        print(f"\n📊 Detailed report: {report_path}")
        print(f"📁 Files location: {self.base_path}")
