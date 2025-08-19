# Public PDF Scraper

A responsible, ethical PDF scraping tool designed for data center technicians and IT professionals to collect publicly available technical documentation, troubleshooting guides, and certification materials.

## 🎯 Purpose

This tool helps data center technicians and IT professionals discover and collect publicly available PDF documentation including:

- Server hardware troubleshooting guides
- Vendor-specific service manuals (Dell, HP, IBM, Quanta, etc.)
- Network infrastructure documentation
- Storage system troubleshooting procedures
- Certification study materials
- Data center operations procedures

## ✨ Features

- **Ethical & Legal Compliance**: Respects robots.txt, X-Robots-Tag headers, and copyright notices
- **Smart License Detection**: Automatically identifies Creative Commons, Public Domain, and government works
- **Rate Limiting**: Built-in delays to be respectful to target servers
- **Comprehensive Coverage**: 1000+ search terms focused on data center operations
- **Multiple Discovery Methods**: Bing API integration + web crawling
- **Detailed Logging**: Complete audit trail of all activities
- **Content Validation**: Ensures downloaded files are actually PDFs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Bing Web Search API key (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pdf-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Bing API (optional)**
   ```bash
   export BING_API_KEY="your_bing_api_key_here"
   ```
   Or create a `.env` file:
   ```
   BING_API_KEY=your_bing_api_key_here
   ```

### Basic Usage

```bash
python main.py
```

The scraper will:
1. Search for PDFs using predefined technical search terms
2. Evaluate each PDF for public availability and licensing
3. Download approved PDFs to the `public_pdfs/` directory
4. Log all activities to `manifest.csv` and `scrape.log`

## 📋 Configuration

### Search Terms

The search terms are organized into focused categories in `SearchTerms.py`:

- **Server Hardware Troubleshooting**: General server diagnostics and repair
- **Vendor-Specific Guides**: Dell, HP/HPE, Quanta, IBM/Lenovo documentation
- **Network Infrastructure**: Switch, router, and network troubleshooting
- **Storage Systems**: SAN, NAS, and storage array documentation
- **Power & Cooling**: UPS, PDU, HVAC troubleshooting
- **Certification Materials**: CompTIA, vendor certifications, advanced technical certs

### Rate Limiting

Default settings are conservative and respectful:

```python
REQUESTS_PER_MIN = 10          # Global rate limit
PER_DOMAIN_DELAY = 10.0        # Seconds between requests to same domain
```

### Allowed Domains (Optional)

You can restrict scraping to specific domains by adding to `SearchTerms.py`:

```python
ALLOWED_DOMAINS = [
    ".gov",           # Government sites
    ".edu",           # Educational institutions
    "dell.com",       # Vendor documentation
    "hpe.com",
    # Add more as needed
]
```

## 🛡️ Ethical Guidelines

This tool is designed with strong ethical principles:

### What Gets Downloaded
- ✅ Creative Commons licensed content
- ✅ Public Domain materials
- ✅ U.S. Government works (17 USC 105)
- ✅ Open Government License content
- ✅ Documents from likely-public domains (.gov, .mil, .edu) without restrictive language

### What Gets Rejected
- ❌ Content with "All Rights Reserved" notices
- ❌ Explicit copyright restrictions
- ❌ Sites with X-Robots-Tag: noindex/noarchive/noai
- ❌ Content blocked by robots.txt
- ❌ Files larger than 40MB

### Respectful Behavior
- Honors robots.txt for all domains
- Implements substantial delays between requests
- Uses descriptive User-Agent string
- Logs all activities for transparency
- Fails conservatively when licensing is unclear

## 📊 Output Structure

### Downloaded Files
```
public_pdfs/
├── a1b2c3d4e5f6__server_troubleshooting_guide.pdf
├── f6e5d4c3b2a1__network_configuration_manual.pdf
└── ...
```

Files are named with:
- First 12 characters of SHA256 hash (for uniqueness)
- Sanitized original filename

### Manifest CSV
Tracks all scraping activity:

| Column | Description |
|--------|-------------|
| timestamp | ISO timestamp of processing |
| source_url | Original PDF URL |
| status | saved/rejected/skipped/error |
| reason | Detailed explanation |
| http_status | HTTP response code |
| content_type | Server-reported content type |
| saved_path | Local file path (if saved) |
| sha256 | File hash (for deduplication) |

### Log File
Detailed activity log in `scrape.log` with timestamps and status information.

## 🔧 Advanced Usage

### Custom Search Terms

Add your own search categories to `SearchTerms.py`:

```python
def get_search_categories():
    categories = {
        'Custom_Category': [
            'your custom search term 1',
            'your custom search term 2',
            # ...
        ],
        # ... existing categories
    }
    return categories
```

### Seed URL Crawling

Add specific pages to crawl for PDF links:

```python
SEED_URLS = [
    "https://example.com/documentation",
    "https://vendor.com/support/manuals",
    # ...
]
```

### Environment Variables

```bash
export BING_API_KEY="your_api_key"
export REQUESTS_PER_MIN="5"        # Lower rate limit
export PER_DOMAIN_DELAY="15.0"     # Longer delays
```

## 📁 Project Structure

```
pdf-scraper/
├── main.py              # Main scraping logic
├── SearchTerms.py       # Search term definitions
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── public_pdfs/        # Downloaded PDFs (created on first run)
├── manifest.csv        # Activity log (created on first run)
├── scrape.log         # Detailed logging (created on first run)
└── .env               # Environment variables (optional)
```

## 🚨 Legal Considerations

- **Review Local Laws**: Ensure compliance with your jurisdiction's copyright and computer access laws
- **Respect Copyright**: This tool attempts to identify freely available content, but you are responsible for ensuring compliance
- **Commercial Use**: Be especially careful about commercial use of downloaded content
- **Terms of Service**: Some websites may have terms that restrict automated access even for public content

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional vendor-specific search terms
- Better license detection algorithms
- Support for more search engines
- Enhanced content validation
- Improved error handling

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

## ⚠️ Disclaimer

This tool is provided for educational and professional development purposes. Users are responsible for ensuring their use complies with all applicable laws, terms of service, and ethical guidelines. The authors are not responsible for any misuse of this software.

## 📞 Support

- Check the logs in `scrape.log` for debugging information
- Review the manifest CSV for detailed status of each URL
- Ensure your Bing API key is valid if using API-based discovery
- Verify network connectivity and firewall settings

---

**Happy learning!** 📚🔧
