import os, logging
import json
import socket
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
from functions.excel import read_excel_to_list, write_list_to_excel
from functions.subprocess_utils import nslookup, c_url

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("output/log.txt"),
    logging.StreamHandler()
])

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

def process_url(url, dns_server):
    data_block = { "url": url }
    data_block[dns_server + " cURL"] = c_url(url)
    data_block[dns_server + " NSLOOKUP"] = nslookup(url, dns_server)
    return data_block

def main():
    logging.info("Execute (Test multithreading) IoC Validation (cURL & NSLOOKUP)")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'url_ioc_list.xlsx')
    file_data = read_excel_to_list(file_path)

    dns_servers = ['8.8.8.8', '1.1.1.1']
    output = [None] * len(file_data)  # Pre-allocate list with None

    for dns_server in dns_servers:
        # Setup DNS resolver
        logging.info(f"Set DNS to {dns_server}")
        socket.getaddrinfo = lambda host, port, family=0, type=0, proto=0, flags=0: custom_getaddrinfo(host, port, dns_server, family, type, proto, flags)
        # Don't check duplicates
        checked_domains = set()
        with ThreadPoolExecutor() as executor:
            futures = {}
            for url_idx, url in enumerate(file_data):
                url = remove_after_first_slash(url["URL"].strip())
                if url in checked_domains:
                    logging.info(f"Skipping {url} (already checked)")
                    output[url_idx] = {}
                    continue
                checked_domains.add(url)
                futures[executor.submit(process_url, url, dns_server)] = url_idx

            for future in as_completed(futures):
                url_idx = futures[future]
                data_block = future.result()
                if output[url_idx] is None:
                    output[url_idx] = data_block
                else:
                    output[url_idx].update(data_block)

    # Remove empty dicts due to duplicates
    filtered_output = [d for d in output if d]
    # Write to file
    output_dir = os.path.join(script_dir, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(output_dir, 'raw.json')
    with open(file_path, 'w') as file:
        json.dump(filtered_output, file, indent=4)

    write_list_to_excel(filtered_output)
    logging.info("Script complete. Output written to output/outputfile.xlsx.")

if __name__ == "__main__":
    main()