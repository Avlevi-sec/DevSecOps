#Used in Qualys/Tenable, splits IP-IP format into single IPs in a list

import pyperclip

def expand_ip_ranges(ip_string):
    ip_list = ip_string.split(',')
    expanded_ips = []
    for ip in ip_list:
        if '-' in ip:
            ip_range = ip.split('-')
            start_ip = list(map(int, ip_range[0].split('.')))
            end_ip = list(map(int, ip_range[1].split('.')))
            for i in range(start_ip[3], end_ip[3] + 1):
                expanded_ips.append('.'.join(map(str, start_ip[:3] + [i])))
        else:
            expanded_ips.append(ip)
    return expanded_ips

ip_string = "172.17.130.18-172.17.130.19,172.17.198.79,172.17.130.60,172.17.133.31-172.17.133.32,172.17.133.201,172.17.133.243-172.17.133.244,172.17.134.1-172.17.134.4,172.17.134.12-172.17.134.13,172.17.134.102,172.17.196.21,172.17.196.31-172.17.196.35,172.17.196.40,172.17.196.42-172.17.196.49,172.17.197.37-172.17.197.38,172.17.197.47,172.17.197.49,172.17.197.67,172.17.197.75,172.17.197.190-172.17.197.199,172.17.197.237,172.17.197.239,172.17.198.79,172.17.200.7,172.17.207.250-172.17.207.251"
result = expand_ip_ranges(ip_string)
result = list(set(result))
for ip in result:
    print(ip)

