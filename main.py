import os
import time
import requests
from urllib.parse import quote_plus, urlparse, unquote
from bs4 import BeautifulSoup
import random
import re
import importlib.util
import sys

# Import the SearchTerms module
spec = importlib.util.spec_from_file_location("SearchTerms", "SearchTerms.py")
search_terms_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_terms_module)

# Get the search terms based on available attributes
if hasattr(search_terms_module, 'get_advanced_categories'):
    categories = search_terms_module.get_advanced_categories()
    print(f"Successfully imported search terms using get_advanced_categories()")
elif hasattr(search_terms_module, 'SEARCH_TERMS'):
    categories = search_terms_module.SEARCH_TERMS
    print(f"Successfully imported search terms using SEARCH_TERMS")
else:
    print("Could not find search terms in SearchTerms.py")
    sys.exit(1)

# Print summary of categories and terms
print(f"Found {len(categories)} categories with a total of {sum(len(terms) for terms in categories.values())} search terms")
for category, terms in categories.items():
    print(f"  - {category}: {len(terms)} terms")

# Setup base directory in the project folder
base_path = os.path.join(os.getcwd(), 'Google PDF Downloader')
if not os.path.exists(base_path):
    os.makedirs(base_path)

# List of user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
]

# List of search engines to try
SEARCH_ENGINES = [
    {
        'name': 'Google',
        'url': 'https://www.google.com/search?q={}&num=30',
        'selector': 'a[href]',
        'link_extractor': lambda link: link.get('href')
    },
    {
        'name': 'Bing',
        'url': 'https://www.bing.com/search?q={}&count=30',
        'selector': 'a[href]',
        'link_extractor': lambda link: link.get('href')
    },
    {
        'name': 'DuckDuckGo',
        'url': 'https://html.duckduckgo.com/html/?q={}',
        'selector': 'a.result__a',
        'link_extractor': lambda link: link.get('href')
    }
]

def get_random_headers():
    """Generate random headers for requests to avoid detection."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

def extract_real_url(redirect_url):
    """Extract the actual URL from search engine redirect URLs."""
    # Google redirect format
    if 'google.com' in redirect_url and '/url?q=' in redirect_url:
        match = re.search(r'/url\?q=([^&]+)', redirect_url)
        if match:
            return unquote(match.group(1))
    
    # Bing redirect format
    elif 'bing.com' in redirect_url and '/ck?' in redirect_url:
        match = re.search(r'u=([^&]+)', redirect_url)
        if match:
            return unquote(match.group(1))
    
    # DuckDuckGo redirect format
    elif 'duckduckgo.com' in redirect_url and '/l/?' in redirect_url:
        match = re.search(r'uddg=([^&]+)', redirect_url)
        if match:
            return unquote(match.group(1))
    
    # Return the original URL if we can't extract a redirect
    return redirect_url

def is_pdf_url(url):
    """Check if a URL points to a PDF file."""
    # Check if the URL ends with .pdf
    if url.lower().endswith('.pdf'):
        return True
    
    # Check if the URL contains pdf indicators
    pdf_indicators = ['/pdf/', 'type=pdf', 'format=pdf', 'document.pdf', '.pdf?']
    return any(indicator in url.lower() for indicator in pdf_indicators)

def search_for_pdfs(query, max_attempts=3):
    """
    Search for PDFs related to the query using multiple search engines.
    Returns a list of PDF URLs.
    """
    all_pdf_urls = []
    query_with_pdf = f"{query} filetype:pdf"
    
    # Try each search engine
    for engine in SEARCH_ENGINES:
        if len(all_pdf_urls) >= 10:  # Stop if we've found enough PDFs
            break
            
        for attempt in range(max_attempts):
            try:
                print(f"Searching {engine['name']} (attempt {attempt+1})...")
                
                # Construct search URL
                search_url = engine['url'].format(quote_plus(query_with_pdf))
                
                # Get search results with random headers and delay
                headers = get_random_headers()
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"  {engine['name']} returned status code {response.status_code}")
                    time.sleep(random.uniform(2, 5))
                    continue
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.select(engine['selector'])
                
                # Extract and process links
                for link in links:
                    href = engine['link_extractor'](link)
                    if not href:
                        continue
                        
                    # Get the real URL from redirects
                    real_url = extract_real_url(href)
                    
                    # Check if it's a PDF
                    if is_pdf_url(real_url) and real_url not in all_pdf_urls:
                        all_pdf_urls.append(real_url)
                        print(f"  Found PDF: {real_url}")
                
                # If we found PDFs, no need for more attempts with this engine
                if any(url for url in all_pdf_urls if engine['name'].lower() in url.lower()):
                    break
                    
                # Random delay between attempts
                time.sleep(random.uniform(3, 7))
                
            except Exception as e:
                print(f"  Error with {engine['name']}: {str(e)}")
                time.sleep(random.uniform(5, 10))
        
        # Random delay between search engines
        time.sleep(random.uniform(5, 10))
    
    # If we still haven't found PDFs, try direct search for PDFs
    if not all_pdf_urls:
        try:
            print("Searching for PDFs directly...")
            for site in ['site:edu', 'site:gov', 'site:org', 'site:com']:
                search_url = f"https://www.google.com/search?q={quote_plus(f'{query} {site} filetype:pdf')}&num=10"
                headers = get_random_headers()
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.select('a[href]')
                    
                    for link in links:
                        href = link.get('href')
                        if not href:
                            continue
                            
                        real_url = extract_real_url(href)
                        if is_pdf_url(real_url) and real_url not in all_pdf_urls:
                            all_pdf_urls.append(real_url)
                            print(f"  Found PDF: {real_url}")
                
                # Random delay
                time.sleep(random.uniform(5, 8))
        except Exception as e:
            print(f"  Error in direct PDF search: {str(e)}")
    
    # Verify each URL is actually a PDF by checking headers
    verified_pdf_urls = []
    for url in all_pdf_urls:
        try:
            # Send a HEAD request to check content type
            head_response = requests.head(url, headers=get_random_headers(), timeout=5)
            content_type = head_response.headers.get('Content-Type', '').lower()
            
            if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                verified_pdf_urls.append(url)
            else:
                print(f"  Not a PDF: {url} (Content-Type: {content_type})")
                
        except Exception as e:
            print(f"  Error verifying URL {url}: {str(e)}")
    
    print(f"Found {len(verified_pdf_urls)} verified PDF URLs")
    return verified_pdf_urls

def download_pdf(url, save_path):
    """
    Download a PDF from the given URL and save it to the specified path.
    """
    try:
        # Generate a unique filename based on the URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # Try to get a filename from the URL
        filename = next((part for part in reversed(path_parts) if part and '.' in part), None)
        
        # If no suitable filename found, generate one
        if not filename or not filename.lower().endswith('.pdf'):
            filename = f"document_{int(time.time())}_{hash(url) % 10000}.pdf"
        
        # Clean the filename to remove invalid characters
        filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
        
        # Ensure filename ends with .pdf
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        file_path = os.path.join(save_path, filename)
        
        # Download the PDF
        print(f"Downloading: {url} -> {filename}")
        response = requests.get(url, headers=get_random_headers(), timeout=30, stream=True)
        response.raise_for_status()
        
        # Save the PDF
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify the file size
        file_size = os.path.getsize(file_path)
        if file_size < 1000:  # Less than 1KB, probably not a valid PDF
            print(f"  Warning: Very small file ({file_size} bytes), might not be a valid PDF")
        
        print(f"  Downloaded: {filename} ({file_size/1024:.1f} KB)")
        return file_path
    
    except Exception as e:
        print(f"  Error downloading PDF from {url}: {str(e)}")
        return None

def download_and_organize_pdfs():
    """
    Download PDFs for each search term in the categories dictionary and organize them into folders.
    """
    total_downloads = 0
    max_pdfs_per_term = 5  # Limit PDFs per search term to avoid excessive downloads
    
    selected_categories = categories
    
    # Ask about max PDFs per term
    try:
        user_max = input("Maximum PDFs to download per search term (default: 5): ")
        if user_max.strip():
            max_pdfs_per_term = int(user_max)
    except:
        print(f"Using default limit of {max_pdfs_per_term} PDFs per search term")
    
    for category, searches in selected_categories.items():
        print(f"\nProcessing category: {category}")
        category_path = os.path.join(base_path, category)
        
        # Create category directory
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        # Process all terms in this category
        term_subset = searches
        
        for search in term_subset:
            print(f"\nSearching for PDFs related to: {search}")
            try:
                # Search for PDFs
                pdf_urls = search_for_pdfs(search)
                
                if not pdf_urls:
                    print(f"No PDF results found for: {search}")
                    continue
                
                # Limit the number of PDFs to download
                pdf_urls = pdf_urls[:max_pdfs_per_term]
                print(f"Found {len(pdf_urls)} PDF links for: {search}")
                
                # Create a subfolder for this search term
                search_folder = re.sub(r'[\\/*?:"<>|]', '_', search)
                search_folder = search_folder.replace(' ', '_')[:50]  # Limit folder name length
                search_path = os.path.join(category_path, search_folder)
                if not os.path.exists(search_path):
                    os.makedirs(search_path)
                
                # Download each PDF
                downloaded_count = 0
                for url in pdf_urls:
                    if download_pdf(url, search_path):
                        downloaded_count += 1
                        total_downloads += 1
                    
                    # Random delay between downloads
                    time.sleep(random.uniform(2, 5))
                
                print(f"Downloaded {downloaded_count} PDFs for: {search}")
                
                # Longer delay between search terms
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                print(f"Error processing search term '{search}': {str(e)}")
                continue
        
        # Count PDFs in category
        try:
            num_pdfs = sum(len([f for f in os.listdir(os.path.join(category_path, d)) 
                            if f.lower().endswith('.pdf')]) 
                        for d in os.listdir(category_path) 
                        if os.path.isdir(os.path.join(category_path, d)))
            print(f"\nCompleted {category} with {num_pdfs} PDFs")
        except Exception as e:
            print(f"Error counting PDFs in {category}: {str(e)}")
    
    return total_downloads

if __name__ == "__main__":
    print("Starting PDF download process...")
    
    # Start the main download process
    total_pdfs = download_and_organize_pdfs()
    
    print(f"\nDownload complete! Downloaded a total of {total_pdfs} PDFs.")
    print(f"Check the 'Google PDF Downloader' folder in the project directory.")
