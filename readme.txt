"""
PDF Scraper Setup and Requirements
Installation and configuration instructions
"""

# requirements.txt content:
REQUIREMENTS = """
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
urllib3>=1.26.0
"""

# setup.py for package installation
SETUP_INSTRUCTIONS = """
Data Center PDF Scraper Setup Instructions
==========================================

1. Install Required Packages:
   pip install requests beautifulsoup4 lxml urllib3

2. File Structure:
   pdf_scraper/
   ├── main.py              # Main execution module
   ├── pdf_downloader.py    # Core downloader class  
   ├── search_terms.py      # Search categories configuration
   └── requirements.txt     # Python dependencies

3. Usage:
   python main.py

4. Output:
   - Creates 'DataCenter_PDF_Library' folder on Desktop
   - Organizes PDFs into category subfolders
   - Generates download_report.json with summary

5. Customization:
   - Modify search_terms.py to add/remove categories
   - Adjust max_results in main.py for more/fewer downloads
   - Update vendor URLs in pdf_downloader.py

6. Legal Considerations:
   - Only downloads publicly available PDFs
   - Respects robots.txt and rate limiting
   - For educational/professional use only
   - Review terms of service for each source site

7. API Integration (Optional Enhancement):
   - Google Custom Search API for better results
   - Vendor API keys for direct documentation access
   - Academic database APIs for research papers
"""

def create_requirements_file():
    """Create requirements.txt file"""
    with open('requirements.txt', 'w') as f:
        f.write(REQUIREMENTS.strip())
    print("Created requirements.txt")

def print_setup_instructions():
    """Print setup instructions"""
    print(SETUP_INSTRUCTIONS)

if __name__ == "__main__":
    create_requirements_file()
    print_setup_instructions()