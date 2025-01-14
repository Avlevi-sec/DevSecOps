#query multiple domains using ipwhois repo to print out all IP list entities/names

from pprint import pprint
from ipwhois import IPWhois

infile = "domains.txt"
nondup_domains = []

# get domains from file
with open(infile, 'r') as f:
    domains = [line.rstrip() for line in f if line.rstrip()]
    print(domains)

for domain in domains:
    print(domain)
    try:
        domain_list = IPWhois(domain).lookup_rdap()['asn_description']
        pprint(domain_list)
        nondup_domains.append(domain_list)
    except:
        print("error {domain}")
print(list(set(nondup_domains)))

    
    
