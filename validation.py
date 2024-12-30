# This script returns the cURL and NSLOOKUP results of a list of domains from urls.txt
import os
import json
import socket
import dns.resolver
from functions.excel import read_excel_to_list, write_list_to_excel
from functions.subprocess_utils import nslookup, c_url

# Override the default DNS resolver
def custom_getaddrinfo(host, port, dns_server, family=0, type=0, proto=0, flags=0):
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

# 1. Read list of URLs
# 2. For each dns server
# 3. For each url, NSLOOKUP and cURL
# 4. use output to generate excel table
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'url_ioc_list.xlsx')
    file_data = read_excel_to_list(file_path)

    dns_servers = ['8.8.8.8', '1.1.1.1']
    output = []

    for dns_server in dns_servers:
        # Setup DNS resolver
        print(f"Set DNS to {dns_server}")
        socket.getaddrinfo = lambda host, port, family=0, type=0, proto=0, flags=0: custom_getaddrinfo(host, port, dns_server, family, type, proto, flags)
        # Don't check duplicates
        checked_domains = set()
        for url_idx, url in enumerate(file_data):
            url = remove_after_first_slash(url["URL"].strip())
            if url in checked_domains:
                print(f"Skipping {url} (already checked)")
                output.append({})
                continue
            checked_domains.add(url)
            # Start Test 
            print(f"Testing {url}")
            data_block = { "url": url }
            data_block[dns_server + " cURL"] = c_url(url)
            data_block[dns_server + " NSLOOKUP"] = nslookup(url, dns_server)
            if len(output) > url_idx:
                output[url_idx].update(data_block)
            else:
                output.append(data_block)

    # Write to file
    output_dir = os.path.join(script_dir, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(script_dir, 'output/raw.json')
    with open(file_path, 'w') as file:
        json.dump(output, file, indent=4)

    write_list_to_excel(output)



if __name__ == "__main__":
    main()