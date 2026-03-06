"""
MCP Server for CyberGuard
Provides URL reputation scanning via VirusTotal API
"""
import re
import os
import base64
import requests
import dns.resolver
import urllib.parse
import email.utils
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
def detect_scam_patterns(text: str) -> str:
    """
    Analyzes text for common scam indicators like urgency, 
    poor grammar, and suspicious formatting.
    """
    try:
        # 1. Define high-risk patterns
        urgency_words = ["urgent", "immediately", "action required", "suspended", "blocked", "last warning"]
        scam_keywords = ["gift card", "bitcoin", "refund", "overdue", "unauthorized", "inheritance"]
        
        text_lower = text.lower()
        
        # 2. Use 're' to find exact word matches (ignoring punctuation)
        # The \b ensures we match 'urgent' but NOT 'detergent'
        urgency_matches = [word for word in urgency_words if re.search(rf'\b{word}\b', text_lower)]
        keyword_matches = [word for word in scam_keywords if re.search(rf'\b{word}\b', text_lower)]
        
        # 3. Use 're' to detect excessive capitalization ("SHOUTING")
        # Finds every individual uppercase letter
        caps_matches = re.findall(r'[A-Z]', text)
        caps_ratio = len(caps_matches) / len(text) if len(text) > 0 else 0
        
        # 4. Calculate Risk Score
        risk_score = 0
        if urgency_matches: risk_score += 30
        if len(caps_matches) > 10 and caps_ratio > 0.25: risk_score += 20
        if keyword_matches: risk_score += 40
        
        # 5. Determine Verdict
        if risk_score >= 70:
            verdict = "🔴 HIGH RISK: This message has many hallmarks of a scam."
        elif risk_score >= 40:
            verdict = "🟡 MEDIUM RISK: Some suspicious language was detected."
        else:
            verdict = "🟢 LOW RISK: No obvious scam patterns found."
            
        return f"""
        [Scam Pattern Analysis]
        Urgency Detected: {', '.join(urgency_matches) if urgency_matches else 'None'}
        Scam Keywords: {', '.join(keyword_matches) if keyword_matches else 'None'}
        Formatting: {'⚠️ Excessive Capitalization' if caps_ratio > 0.25 else 'Normal'}
        
        Final Verdict: {verdict}
        
        Note: This is an automated check. Scammers are clever; always stay cautious!
        """
        
    except Exception as e:
        return f"Error analyzing text patterns: {str(e)}"

@mcp.tool()
def unshorten_url(short_url: str) -> str:
    """
    Follows redirects to find the final destination of a shortened link.
    Use this if a user provides a tiny or suspicious short link before scanning it with other tools.
    """
    try:
        # We use a HEAD request so we don't download the whole page, just check the destination
        # allow_redirects=True tells requests to follow the chain to the very end
        response = requests.head(short_url, allow_redirects=True, timeout=10)
        final_url = response.url
        
        if final_url.rstrip('/') == short_url.rstrip('/'):
            return f"The link is not shortened. Destination: {final_url}"
            
        return f"⚠️ This is a shortened link! It actually leads to: {final_url}"
        
    except Exception as e:
        return f"Could not follow the link: {str(e)}"
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

@mcp.tool()
def analyze_email_address(from_line: str) -> str:
    """
    Parses a 'From' line (e.g., 'Amazon Support <scammer@gmail.com>') 
    to separate the display name from the actual email address.
    """
    try:
        name, address = email.utils.parseaddr(from_line)
        domain = address.split('@')[-1] if '@' in address else "Unknown"
        
        # Logic to flag generic domains claiming to be big brands
        trusted_brands = ["amazon.com", "microsoft.com", "google.com", "apple.com", "paypal.com"]
        is_suspicious = False
        if any(brand.split('.')[0] in name.lower() for brand in trusted_brands):
            if domain.lower() not in trusted_brands:
                is_suspicious = True

        status = "🚨 SUSPICIOUS: Name claims to be a brand but the email domain is different." if is_suspicious else "✅ Domain matches/No obvious spoofing."
        
        return f"""
        [Email Analysis]
        Display Name: {name}
        Actual Email: {address}
        Domain: {domain}
        Verdict: {status}
        """
    except Exception as e:
        return f"Error analyzing email: {str(e)}"
if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
