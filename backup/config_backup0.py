import time
import sys
import logging
import re
import getpass
import ftplib
import netmiko
import threading
import schedule
import smtplib

# Create a file named 'test.log' in your current directory for debugging. It will log all reads and writes on the SSH channel.
logging.basicConfig(filename='debugging.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")


# Define the backup procedure as a thread, so we can run multiple devices simultaneously.
def backup(X, timestr, failed_device, success_device):
    # Connect to device and handle exceptions.
    print("\n%s: Logging into device..." % X['ip'])
    try:
        net_connect = netmiko.ConnectHandler(**X)
    except Exception as Any_Exception:
        return(failed_device.append(X['ip'] + ': ' + str(Any_Exception)))

    # Get hostname and device version.
    a = net_connect.send_command("show run | in hostname")
    hostname = str.split(a)[-1]  # split with "". Get the last word as hostname
    print("%s: Device connected. Hostname: %s. Copying running config to FTP..." % (X['ip'], hostname))
    e = net_connect.send_command("show version | in Cisco IOS XR")
    version = str.split(e)[-1]

    # Copy config to FTP. Press "ENTER" for prompts.
    b = net_connect.send_command_timing("copy running-config ftp://cisco:cisco@10.66.70.170;mgmt/asofrani/Backup_script/" + timestr + "/" + hostname + ".txt")
    if 'Host' in b:
        c = net_connect.send_command_timing("\n", strip_command=False, strip_prompt=False)
    if 'Destination' in c:
        d = net_connect.send_command_timing("\n", strip_command=False, strip_prompt=False)
        print("%s %s: Running config copied to FTP." % (X['ip'], hostname))

    # Disconnect.
    net_connect.disconnect()
    print("%s %s: Logged out of device." % (X['ip'], hostname))
    return(success_device.append(X['ip'] + '\t' + hostname + '\t' + version))

# Define the backup job to run repeatedly.
def job():
    # Connect to FTP.
    timestr = time.strftime("%Y%m%d")
    ftp = ftplib.FTP('10.66.70.170')
    ftp.login('cisco', 'cisco')
    ftp.cwd("asofrani/Backup_script/")
    username = "cisco"   #---- > use this when u log into the router
    passw = ''
    message = """From: XR Config Backup Script <global-tac-syd-iox@cisco.com>
To: XR Lab Admin <global-tac-syd-iox@cisco.com>
Subject: SYD XR Static Lab Config Backup Result: """ + timestr

    # Find current password. Set "password + 1" as new password.
    for line in ftp.nlst():
        pass_match = re.search(r'current_password:cisco!(\d+)', line)   ###-- > current_password:cisco!124
        if pass_match:
            pass_key = pass_match.group(1)   # --- > 124
            passw = "cisco!" + pass_key #--- > cisco!124
            new_pass_key = str(int(pass_key) + 1) #---- > new_pass_key = 125
            new_passw = "cisco!" + new_pass_key  #--- > cisco!125
            print(passw)
            print(new_passw)
    if not passw:
        ftp.quit()
        message += "\n\nDidn't find current password under FTP folder. Abort job."
        return(message)

    devices = [
        {'device_type': 'cisco_xr', 'ip': "10.66.70.76", 'username': username, 'password': passw}, #login with old pw
        {'device_type': 'cisco_xr', 'ip': "10.66.70.79", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.82", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.65", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.68", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.60", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.45", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.48", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.51", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.52", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.53", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.54", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.44", 'username': username, 'password': passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.110", 'username': username, 'password': passw},
    ]
    failed_device = []
    success_device = []
    # Make dir based on current date.
    if timestr not in ftp.nlst():
        ftp.mkd(timestr)

    print("Backup config will be saved to FTP server 10.66.70.170. Folder: asofrani/Backup_script/%s" % timestr)

    # Open one thread for every router. Add all the threads to router_threads so we can keep track of them.
    router_threads = []
    for X in devices:
        thread = threading.Thread(target=backup, args=(X, timestr, failed_device, success_device, ))
        thread.start()
        router_threads.append(thread)

    # Wait for all the threads to close. Then close FTP.
    for thread in router_threads:
        thread.join()

    if failed_device:
        message += ("\n\n***ERROR: Backup script failed to connect to these device(s). Please check connectivity manually.***")
        for i in failed_device:
            message += ("\n\n"+str(i))

    message += ("\n\n***Backup script successfully connected to these devices.***")
    if success_device:
        for i in success_device:
            message += ("\n"+str(i))

    message += ("\n\n***Below config files were added to FTP server 10.66.70.170. Folder: asofrani/Backup_script/%s***\n" % timestr)
    ftp.cwd(timestr)
    for i in ftp.nlst():
        message += ("\n" + str(i))
    ftp.quit()

    print(message)

    sender = 'tiali2@cisco.com'
    receivers = ['global-tac-syd-iox@cisco.com']
    try:
        smtpObj = smtplib.SMTP('mail.cisco.com')
        smtpObj.sendmail(sender, receivers, message)
        print("Successfully sent email")
    except Exception as Any_Exception:
        print("Error: unable to send email")
        print(Any_Exception)

job()

# schedule.every(1).minute.do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(10)
