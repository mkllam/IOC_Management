import subprocess

def curl_head_request(domain, dns_server, output_file):
    # Construct the curl command
    command = [
        'curl', '-I', domain, '--dns-servers', dns_server
    ]
    
    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    
    print(result)

def main():
    # Domain and DNS server to use
    domain = 'google.com'
    dns_server = '8.8.8.8'
    output_file = 'curl_output.txt'

    # Perform the curl head request and write the result to a file
    curl_head_request(domain, dns_server, output_file)

    print(f"The curl output has been written to {output_file}.")

if __name__ == "__main__":
    main()