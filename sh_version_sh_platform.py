from __future__ import unicode_literals, absolute_import, print_function

import re
import bdblib

network_device = {}
show_platform = {}

def task(env, system_tech):
    """
    test
    """
    
    f = open(system_tech, 'r')
    system_tech_data = f.read()
    f.close()
    
    network_device['show_version'] = parser(r"Version (.+?\..+?\..+?)", system_tech_data)
    network_device['uptime'] = parser(r'uptime is (.+)', system_tech_data)
    network_device['chassis'] = parser(r'(.+) Chassis (.+)', system_tech_data)
    extract_show_platform(r'^\++ admin show platform .+', system_tech_data)
    
    basic_info = ('show_version', 'uptime', 'chassis')
    
    for item in basic_info:
        print ("{}: {}".format(item, network_device[item]))
    
    return None
    

def parser(pattern, data):
    '''
    Extract the appropriate fields using the incoming regex
    pattern and data
    '''
    data = data.split('\n')
    
    for line in data:
        match = re.search(pattern, line)
        if match:
            return match.group(1)

    return ""

    
    
def extract_show_platform(pattern, data):
    platform_details = []
    copy = False
    
    data = data.split('\n')
    
    for line in data:
        if re.search(pattern, line):
            copy = True
        elif re.search(r'-+ admin show platform', line):
            copy = False
        elif copy:
            platform_details.append(line)
            print (line)

    return ''
