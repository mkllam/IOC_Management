import subprocess
import requests
import dns.resolver

def nslookup(domain, dns_server):
    # Construct the nslookup command
    command = ['nslookup', '-type=ns', domain+".", dns_server]
    
    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Return the output
    for line in result.stdout.split('\n'):
        if "server = " in line:
            return line
    return "-"

def c_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        response = requests.head(url, timeout=10)
        return response.status_code
    except:
        return "-"