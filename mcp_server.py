"""
MCP Server for CyberGuard
Provides URL reputation scanning via VirusTotal API
"""
import os
import base64
import requests
import dns.resolver
import urllib.parse
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("SecurityTools")

@mcp.tool()
def scan_url_reputation(url: str) -> str:
    """
    Scan a URL's reputation using VirusTotal API.
    
    Args:
        url: The URL to scan (e.g., "https://example.com")
    
    Returns:
        A safety assessment string
    """
    try:
        api_key = os.getenv("VIRUSTOTAL_API_KEY")
        if not api_key:
            return "Error: VirusTotal API key not configured"
        
        # Encode URL to base64 (VirusTotal requirement)
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        
        # Call VirusTotal API
        headers = {
            "accept": "application/json",
            "x-apikey": api_key
        }
        
        response = requests.get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 404:
            return f"URL not found in VirusTotal database. This could mean it's new or rarely visited. Proceed with caution."
        
        if response.status_code != 200:
            return f"Error scanning URL: HTTP {response.status_code}"
        
        data = response.json()
        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        undetected = stats.get("undetected", 0)
        
        total_scans = malicious + suspicious + harmless + undetected
        
        if malicious > 0:
            return f"⚠️ MALICIOUS: {malicious}/{total_scans} security vendors flagged this URL as dangerous. DO NOT VISIT!"
        elif suspicious > 0:
            return f"⚠️ SUSPICIOUS: {suspicious}/{total_scans} vendors found suspicious activity. Exercise caution."
        elif harmless > 10:
            return f"✅ SAFE: {harmless}/{total_scans} vendors confirmed this URL is clean."
        else:
            return f"UNKNOWN: Limited data available ({total_scans} scans). Proceed carefully."
            
    except requests.RequestException as e:
        return f"Network error while scanning URL: {str(e)}"
    except Exception as e:
        return f"Error scanning URL: {str(e)}"
    
@mcp.tool()
def scan_domain_dns(domain_or_url: str) -> str:
    """
    Scan a domain's DNS records to check its legitimacy and email security (SPF/DMARC).
    Useful for verifying if an email address or website domain is spoofed or fake.
    
    Args:
        domain_or_url: The domain name (e.g., "google.com") or full URL.
    """
    try:
        # If the AI passes a full URL, extract just the domain
        if "://" in domain_or_url:
            domain = urllib.parse.urlparse(domain_or_url).netloc
        else:
            domain = domain_or_url.strip("/")

        results = [f"🔍 DNS Report for: {domain}\n"]

        # 1. Check A Records (Does the website actually exist?)
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            results.append(f"✅ Website IP Addresses found: {len(a_records)}")
        except Exception:
            results.append("⚠️ No Website IP found (This domain might not host a real website).")

        # 2. Check MX Records (Can this domain send/receive emails?)
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            results.append(f"✅ Mail Servers (MX) found: {len(mx_records)}")
        except Exception:
            results.append("⚠️ No Mail Servers found (Any email claiming to be from this domain is likely FAKE).")

        # 3. Check TXT Records (Look for SPF/DMARC anti-spoofing security)
        try:
            txt_records = dns.resolver.resolve(domain, 'TXT')
            txt_strings = [r.to_text() for r in txt_records]
            
            # Check for SPF (Sender Policy Framework)
            has_spf = any("v=spf1" in txt for txt in txt_strings)
            if has_spf:
                results.append("✅ SPF Email Security Record found (Harder to spoof).")
            else:
                results.append("⚠️ No SPF Record found (Emails from this domain can be easily forged by scammers).")
                
        except Exception:
            results.append("⚠️ No TXT security records found.")

        return "\n".join(results)

    except dns.resolver.NXDOMAIN:
        return f"❌ CRITICAL: The domain '{domain}' DOES NOT EXIST. This is absolutely a scam/fake link."
    except Exception as e:
        return f"Error scanning DNS for {domain_or_url}: {str(e)}"    


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
