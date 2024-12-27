import subprocess

def nslookup(domain, dns_server):
    # Construct the nslookup command
    command = ['nslookup', '-type=ns', domain, dns_server]
    
    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Return the output
    return result.stdout

# Domain and DNS server to use
domain = '0penrlce.com'
dns_server = '8.8.8.8'

# Perform nslookup and print the result
output = nslookup(domain, dns_server)
print(output)