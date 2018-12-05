#!/usr/bin/env python

from netmiko import ConnectHandler
import time
import logging
logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

ios_xrv = {
    'device_type': 'cisco_xr',
    'ip': '10.70.69.60',
    'username': 'pganesha',
    'password': 'cisco',
}

switchover = 0

net_connect = ConnectHandler(**ios_xrv)

time.sleep(3)
net_connect.clear_buffer()

while switchover < 101:
    print(switchover)
    time.sleep(3)
    net_connect.clear_buffer()
    red_switchover = net_connect.send_command('redundancy switchover', expect_string = r'Proceed')
    time.sleep(3)
    send_yes = net_connect.send_command('\n', expect_string=r'Initiating switch-over')

    switchover = switchover + 1
    time.sleep(220)
    # connect to the box again
    net_connect = ConnectHandler(**ios_xrv)
    xr_prompt = net_connect.base_prompt

    #collect outputs and store in file
    admin_mode = net_connect.send_command('admin', expect_string = r'sysadmin')
    time.sleep(3)
    net_connect.clear_buffer()
    os_level = net_connect.send_command('run ssh 10.0.2.2', expect_string = r'host')
    time.sleep(3)
    net_connect.clear_buffer()


    with open('test.txt','a') as f:
        show_command = net_connect.send_command('dmesg -T |grep -e sysadmin -e Starting -e Stopping', expect_string = r'host')
        time.sleep(3)
        net_connect.clear_buffer()
        f.write(xr_prompt)
        f.write(show_command)
        f.write('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    #exit out of admin mode back to xr-plane
    exit_os_mode = net_connect.send_command('exit', expect_string = r'sysadmin')
    time.sleep(3)
    exit_admin_mode = net_connect.send_command('exit', expect_string = r'davey')
    time.sleep(3)
