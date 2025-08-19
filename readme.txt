# Google PDF Downloader

A comprehensive Python tool designed for data center technicians to automatically search and download technical documentation, troubleshooting guides, and certification materials from multiple search engines.

## Features

- **Multi-Engine Search**: Searches across Google, Bing, and DuckDuckGo for maximum coverage
- **Smart PDF Detection**: Automatically identifies and verifies PDF files
- **Organized Storage**: Downloads are organized by category and search term
- **Rate Limiting**: Built-in delays and user agent rotation to avoid detection
- **Comprehensive Categories**: Covers major server brands, networking, storage, and certification materials
- **Verification System**: Validates PDFs by checking content type headers

## Installation

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Basic Usage**:
```bash
python main.py
```

2. **Customize Download Limits**:
   - The script will prompt you for the maximum number of PDFs per search term (default: 5)
   - You can modify the search categories in `SearchTerms.py`

3. **Output Structure**:
```
Google PDF Downloader/
├── Server_Hardware_Troubleshooting/
│   ├── data_center_server_hardware_troubleshooting/
│   │   ├── document1.pdf
│   │   └── document2.pdf
│   └── server_POST_error_codes_troubleshooting/
├── Dell_Server_Troubleshooting/
├── HP_HPE_Server_Troubleshooting/
└── ...
```

## Search Categories

The tool includes extensive search categories covering:

### Hardware Troubleshooting
- **Server Hardware**: General server troubleshooting, POST errors, thermal management
- **Dell Servers**: PowerEdge series, iDRAC, PERC RAID controllers
- **HP/HPE Servers**: ProLiant series, iLO, SmartArray controllers
- **Quanta Servers**: QuantaGrid, QuantaPlex, hyperscale solutions
- **IBM/Lenovo**: ThinkSystem, Power Systems, XClarity management

### Infrastructure
- **Network Infrastructure**: Switch configuration, VLAN troubleshooting, fiber optics
- **Storage Systems**: SAN/NAS troubleshooting, RAID arrays, backup systems
- **Power & Cooling**: UPS systems, PDUs, HVAC troubleshooting
- **Hardware Components**: Memory, storage, network cards, cables

### Management & Operations
- **Remote Management**: BMC, IPMI, out-of-band management
- **Operating Systems**: Linux/Windows server troubleshooting
- **Monitoring & Alerting**: SNMP, system monitoring, performance baselines
- **Security & Compliance**: ISO 27001, SOC 2, security procedures

### Certifications
- **CompTIA**: A+, Network+, Security+, Server+, Linux+
- **Vendor Certifications**: Dell EMC, HPE, Cisco, VMware, Microsoft, Red Hat
- **Advanced Certifications**: ITIL, CISSP, cloud certifications

## Configuration

### Modifying Search Terms

Edit `SearchTerms.py` to customize search categories:

```python
def get_advanced_categories():
    return {
        'Your_Custom_Category': [
            'your search term 1',
            'your search term 2',
            # ... more terms
        ]
    }
```

### Search Engine Configuration

The tool uses multiple search engines with different selectors. You can modify the `SEARCH_ENGINES` list in `main.py` to add or remove search engines.

### User Agent Rotation

The script rotates between multiple user agents to avoid detection. Additional user agents can be added to the `USER_AGENTS` list.

## Advanced Features

### PDF Verification
- Sends HEAD requests to verify content type
- Filters out non-PDF responses
- Checks file size to avoid empty downloads

### Smart URL Extraction
- Handles search engine redirect URLs
- Extracts real URLs from Google, Bing, and DuckDuckGo
- Supports various PDF URL formats

### Rate Limiting
- Random delays between requests (2-10 seconds)
- Different delays for search engines vs. downloads
- User agent rotation for each request

## Error Handling

The script includes comprehensive error handling for:
- Network timeouts and connection errors
- Invalid PDF URLs
- Search engine rate limiting
- File system permissions
- Large file downloads

## Best Practices

1. **Respect Rate Limits**: The built-in delays help avoid IP blocking
2. **Monitor Downloads**: Check the console output for failed downloads
3. **Verify Content**: Review downloaded PDFs for relevance and quality
4. **Storage Management**: Regularly clean up unnecessary files
5. **Network Considerations**: Use on networks that allow automated downloads

## Troubleshooting

### Common Issues

**No PDFs Found**:
- Try different search terms
- Check internet connectivity
- Verify search engines are accessible

**Download Failures**:
- Some URLs may require authentication
- Corporate firewalls may block downloads
- Try running with different user agents

**Rate Limiting**:
- Increase delays between requests
- Use VPN if IP is temporarily blocked
- Run during off-peak hours

### Debug Mode

Add debug output by modifying the print statements or adding logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Legal Considerations

- Ensure compliance with website terms of service
- Respect copyright and intellectual property rights
- Use downloaded materials for educational/professional purposes only
- Be mindful of corporate policies regarding automated downloads

## Contributing

To add new search categories or improve functionality:

1. Fork the repository
2. Add new categories to `SearchTerms.py`
3. Test thoroughly with various search terms
4. Submit pull request with detailed description

## License

This tool is provided as-is for educational and professional use. Users are responsible for ensuring compliance with applicable laws and terms of service.

## Support

For issues or questions:
- Review the troubleshooting section
- Check that all dependencies are installed correctly
- Ensure you have proper network permissions
- Verify search terms are appropriate and specific

---

**Note**: This tool is designed for legitimate educational and professional use by data center technicians and IT professionals. Always respect website terms of service and copyright laws.
