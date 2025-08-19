"""
Search Terms Configuration Module
Data Center Technician-Focused Documentation
Optimized for server hardware/software troubleshooting and operations
"""

def get_search_categories():
    """Return dictionary of search categories and terms focused on data center technician needs"""
    
    categories = {
        'Server_Hardware_Troubleshooting': [
            'data center server hardware troubleshooting',
            'server POST error codes troubleshooting',
            'server memory failure diagnostics',
            'server CPU overheating troubleshooting',
            'server power supply failure diagnosis',
            'server motherboard troubleshooting guide',
            'server hard drive failure diagnosis',
            'rack server hardware diagnostics',
            'server fan failure troubleshooting',
            'server BIOS configuration troubleshooting'
        ],
        
        'Dell_Server_Troubleshooting': [
            'Dell PowerEdge hardware troubleshooting',
            'Dell server error codes manual',
            'Dell iDRAC troubleshooting guide',
            'Dell PowerEdge diagnostic procedures',
            'Dell server component replacement',
            'Dell PERC RAID troubleshooting',
            'Dell server thermal issues',
            'Dell PowerEdge service manual',
            'Dell server LED error codes',
            'Dell OpenManage troubleshooting'
        ],
        
        'HP_HPE_Server_Troubleshooting': [
            'HP ProLiant hardware troubleshooting',
            'HPE server error codes manual',
            'HP iLO troubleshooting guide',
            'HPE server diagnostic procedures',
            'HP SmartArray RAID troubleshooting',
            'HPE server thermal management',
            'HP ProLiant service manual',
            'HPE server LED diagnostics',
            'HP Insight Manager troubleshooting',
            'HPE OneView troubleshooting'
        ],
        
        'Quanta_Server_Troubleshooting': [
            'Quanta server hardware troubleshooting',
            'Quanta server service manual',
            'Quanta server error codes',
            'Quanta BMC troubleshooting guide',
            'Quanta server diagnostic procedures',
            'Quanta motherboard troubleshooting',
            'Quanta server thermal management',
            'Quanta BIOS configuration guide',
            'Quanta server component replacement',
            'Quanta server LED diagnostics',
            'Quanta rack server manual',
            'Quanta server installation guide',
            'Quanta server power troubleshooting',
            'Quanta server memory diagnostics',
            'Quanta server RAID configuration'
        ],
        
        'IBM_Lenovo_Server_Troubleshooting': [
            'IBM server hardware troubleshooting',
            'Lenovo ThinkSystem troubleshooting',
            'IBM IMM troubleshooting guide',
            'IBM server error codes manual',
            'Lenovo XClarity troubleshooting',
            'IBM server diagnostic procedures',
            'IBM RAID controller troubleshooting',
            'Lenovo server service manual',
            'IBM server thermal issues',
            'Lenovo server component diagnostics'
        ],
        
        'Network_Infrastructure_Troubleshooting': [
            'data center network troubleshooting',
            'switch port failure diagnosis',
            'network cable testing procedures',
            'VLAN configuration troubleshooting',
            'network connectivity issues datacenter',
            'switch configuration troubleshooting',
            'network performance issues diagnosis',
            'fiber optic troubleshooting datacenter',
            'network redundancy failure recovery',
            'datacenter network monitoring'
        ],
        
        'Storage_System_Troubleshooting': [
            'SAN troubleshooting procedures',
            'NAS failure diagnosis',
            'RAID array troubleshooting',
            'storage performance issues',
            'disk array failure recovery',
            'backup system troubleshooting',
            'storage controller diagnostics',
            'data center storage monitoring',
            'storage network troubleshooting',
            'disk replacement procedures'
        ],
        
        'Power_Cooling_Infrastructure': [
            'data center power troubleshooting',
            'UPS failure diagnosis procedures',
            'PDU troubleshooting guide',
            'server rack power issues',
            'data center cooling troubleshooting',
            'HVAC system failure diagnosis',
            'server thermal management',
            'power distribution troubleshooting',
            'environmental monitoring issues',
            'data center power outage procedures'
        ],
        
        'Hardware_Component_Troubleshooting': [
            'server memory module troubleshooting',
            'server hard drive failure diagnosis',
            'server network card troubleshooting',
            'server expansion card issues',
            'server cable troubleshooting',
            'server connector diagnostics',
            'server backplane troubleshooting',
            'server riser card issues',
            'server peripheral troubleshooting',
            'server component compatibility issues'
        ],
        
        'Remote_Management_Troubleshooting': [
            'BMC troubleshooting procedures',
            'IPMI connection issues',
            'out-of-band management problems',
            'remote console troubleshooting',
            'KVM over IP issues',
            'serial console troubleshooting',
            'remote power control problems',
            'management network issues',
            'BMC firmware troubleshooting',
            'remote access security issues'
        ],
        
        'Operating_System_Troubleshooting': [
            'Linux server boot troubleshooting',
            'Windows Server crash analysis',
            'server OS performance issues',
            'kernel panic troubleshooting',
            'blue screen diagnosis procedures',
            'server OS driver issues',
            'system service failure diagnosis',
            'OS update troubleshooting',
            'server login issues diagnosis',
            'system log analysis procedures'
        ],
        
        'Data_Center_Operations_Procedures': [
            'server deployment procedures',
            'hardware replacement workflows',
            'data center maintenance procedures',
            'server decommissioning guide',
            'rack and stack procedures',
            'cable management best practices',
            'server inventory management',
            'change management procedures',
            'incident response procedures',
            'escalation procedures datacenter'
        ],
        
        'Monitoring_Alerting_Systems': [
            'data center monitoring setup',
            'server health monitoring',
            'SNMP monitoring configuration',
            'alert escalation procedures',
            'monitoring system troubleshooting',
            'performance baseline establishment',
            'threshold configuration guide',
            'monitoring dashboard setup',
            'log aggregation procedures',
            'automated alerting configuration'
        ],
        
        'Security_Compliance_Procedures': [
            'data center security procedures',
            'server hardening checklist',
            'access control procedures',
            'security audit procedures',
            'compliance documentation',
            'vulnerability assessment procedures',
            'patch management procedures',
            'security incident response',
            'data center physical security',
            'network security procedures'
        ],
        
        'Intel_Processor_Systems': [
            'Intel server processor troubleshooting',
            'Intel Xeon processor diagnostics',
            'Intel CPU thermal throttling issues',
            'Intel processor error codes',
            'Intel Xeon server performance tuning',
            'Intel CPU overheating troubleshooting',
            'Intel processor cache errors',
            'Intel server CPU replacement procedures',
            'Intel Xeon memory controller issues',
            'Intel processor microcode updates',
            'Intel CPU stress testing procedures',
            'Intel processor socket troubleshooting',
            'Intel Xeon power management issues',
            'Intel CPU frequency scaling problems',
            'Intel CPU instruction set diagnostics',
            'Intel server chipset troubleshooting',
            'Intel CPU fan speed control',
            'Intel processor BIOS settings',
            'Intel Xeon multi-socket configuration',
            'Intel CPU performance monitoring'
        ],
        
        'Disaster_Recovery_Procedures': [
            'data center disaster recovery',
            'backup verification procedures',
            'system recovery procedures',
            'failover testing procedures',
            'business continuity planning',
            'data restoration procedures',
            'emergency response procedures',
            'recovery time objectives',
            'backup system testing',
            'disaster recovery documentation'
        ]
    }
    
    return categories

def get_certification_categories():
    """Return certification-focused categories for technician development"""
    
    cert_categories = {
        'CompTIA_DataCenter_Focus': [
            'CompTIA A+ data center scenarios',
            'CompTIA Network+ datacenter networking',
            'CompTIA Security+ datacenter security',
            'CompTIA Server+ troubleshooting',
            'A+ hardware troubleshooting scenarios',
            'Network+ enterprise networking',
            'Security+ infrastructure protection'
        ],
        
        'Vendor_Certifications': [
            'Dell EMC data center certification',
            'HPE server certification guide',
            'Cisco data center certification',
            'VMware data center certification',
            'Microsoft datacenter certification',
            'Red Hat datacenter certification'
        ]
    }
    
    return cert_categories