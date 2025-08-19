#!/usr/bin/env python3
"""
PDF Scraper for Data Center Technical Documentation
Main execution module
"""

import os
import time
from pdf_downloader import PDFDownloader
from search_terms import get_search_categories

def main():
    """Main execution function"""
    print("Starting PDF download process for data center documentation...")
    
    # Initialize downloader
    downloader = PDFDownloader()
    
    # Get search categories
    categories = get_search_categories()
    
    # Process each category
    for category, searches in categories.items():
        print(f"\n{'='*50}")
        print(f"Processing category: {category}")
        print(f"{'='*50}")
        
        success_count = 0
        total_count = len(searches)
        
        for search_term in searches:
            print(f"\nSearching for: {search_term}")
            try:
                result = downloader.search_and_download_pdfs(search_term, category)
                if result:
                    success_count += 1
                    print(f"✓ Successfully processed: {search_term}")
                else:
                    print(f"✗ No results for: {search_term}")
                
                # Rate limiting to be respectful to servers
                time.sleep(3)
                
            except Exception as e:
                print(f"✗ Error processing {search_term}: {str(e)}")
                continue
        
        print(f"\nCategory '{category}' completed: {success_count}/{total_count} successful")
    
    # Generate summary report
    downloader.generate_summary_report()
    print(f"\n🎉 Download complete! Check the '{downloader.base_path}' folder on your Desktop.")

if __name__ == "__main__":
    main()