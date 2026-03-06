"""
MCP Server for CyberGuard
Provides URL reputation scanning via VirusTotal API
"""
import os
import base64
import requests
import dns.resolver
import urllib.parse
from datetime import datetime
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
def scan_domain_whois(domain: str) -> str:
    """
    Fetches WHOIS registration data to determine the age and owner of a domain.
    CRITICAL USE: Always use this to check suspicious links, URLs, or email domains. 
    If a domain is less than 30 days old but claims to be a trusted company, flag it as a scam.
    """
    try:
        # 1. Clean up the domain string just in case the AI passes a full URL
        if "://" in domain:
            import urllib.parse
            domain = urllib.parse.urlparse(domain).netloc
        domain = domain.replace("www.", "").strip("/")
        
        # 2. Use an HTTPS API to bypass University Port 43 Firewalls!
        import requests
        from datetime import datetime
        
        response = requests.get(f"https://networkcalc.com/api/dns/whois/{domain}", timeout=10)
        
        if response.status_code != 200:
            return f"WHOIS API Error: Could not fetch data for {domain}."
            
        data = response.json()
        if data.get("status") != "OK":
            return f"WHOIS Lookup Failed: Domain {domain} might not exist or is hidden."
            
        whois_data = data.get("whois", {})
        registrar = whois_data.get("registrar", "Unknown")
        creation_date_str = whois_data.get("creation_date")
        
        # --- NEW FALLBACK LOGIC ---
        # If the API fails to find the date (common for domains like facebook.com),
        # fallback to the local Python 'whois' library.
        if not creation_date_str:
            try:
                # Make the Python script look like a normal Google Chrome browser
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/rdap+json"
                }
                rdap_response = requests.get(f"https://rdap.org/domain/{domain}", headers=headers, timeout=10)
                
                if rdap_response.status_code == 200:
                    rdap_data = rdap_response.json()
                    
                    # RDAP stores dates in an 'events' list, so we search for the registration event
                    for event in rdap_data.get("events", []):
                        if event.get("eventAction") == "registration":
                            creation_date_str = event.get("eventDate")
                            # Try to grab the registrar from RDAP if the first API missed it
                            if not registrar or registrar == "Unknown":
                                for entity in rdap_data.get("entities", []):
                                    if "registrar" in entity.get("roles", []):
                                        registrar = entity.get("vcardArray", [[]])[1][1][3]
                            break
                else:
                    # This will print in your terminal so you can see if it's still blocking you
                    print(f"--- RDAP Blocked! HTTP Status: {rdap_response.status_code} ---")
            except Exception as e:
                print(f"--- RDAP Error: {str(e)} ---")

        # If it still can't find it after the fallback
        if not creation_date_str:
            return f"WHOIS Data for {domain}: Could not determine creation date. Treat with caution."
            
        # 3. Parse the date format safely
        clean_date_str = str(creation_date_str)[:10]
        creation_date = datetime.strptime(clean_date_str, "%Y-%m-%d")
        
        # 4. Calculate Age
        age_in_days = (datetime.now() - creation_date).days
        age_warning = "🚨 HIGH RISK (Brand new domain!)" if age_in_days < 30 else "✅ Established domain"
        
        return f"""
        [WHOIS Analysis for {domain}]
        Registrar: {registrar}
        Created On: {clean_date_str}
        Age: {age_in_days} days old
        Status: {age_warning}
        """
        
    except Exception as e:
        # Now the AI will actually tell us WHY it failed if it happens again!
        return f"WHOIS Lookup Failed for {domain}. Developer Error Details: {str(e)}"
        
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
