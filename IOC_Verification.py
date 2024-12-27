# This script returns the cURL and NSLOOKUP results of a list of domains from urls.txt
import requests
import time
import socket
import subprocess
import dns.resolver

# Define the DNS server
dns_server = '8.8.8.8'

# Override the default DNS resolver
def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    answers = resolver.resolve(host)
    return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', (str(answers[0]), port))]

def remove_after_first_slash(url):
    dot_position = url.find('.')
    slash_position = url.find('/', dot_position)
    if slash_position != -1:
        return url[:slash_position]
    return url

def nslookup(domain, dns_server):
    # Construct the nslookup command
    command = ['nslookup', '-type=ns', domain+".", dns_server]
    
    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Return the output
    stdout = result.stdout.split("\n\n")
    stderr = result.stderr.strip()
    return stdout[0] + "\n" + stderr + "\n" + stdout[-1]

def c_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        response = requests.head(url, timeout=10)
        return response.headers, response.status_code
    except requests.RequestException as e:
        return str(e), "N/A"
    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN) as e:
        return str(e), "N/A"
    except Exception as e:
        return str(e), f"Error handling {url}"

def main():
    if dns_server:
        socket.getaddrinfo = custom_getaddrinfo
    with open('urls.txt', 'r') as file:
        urls = file.readlines()
    checked_domains = set()
    with open('results.log', 'w') as log:
        try:
            for url in urls:
                url = remove_after_first_slash(url.strip())
                if url in checked_domains:
                    print(f"Skipping {url} (already checked)")
                    continue
                checked_domains.add(url)
                print(f"Testing {url}")
                log.write(nslookup(url, dns_server))
                head, status = c_url(url)
                log.write(f"{url} - {status} - {head}\n--------------------\n")
                time.sleep(2)
        except KeyboardInterrupt:
            print("Script interrupted. Exiting early.")
            log.write("Script interrupted. Exiting early.\n")

if __name__ == "__main__":
    main()