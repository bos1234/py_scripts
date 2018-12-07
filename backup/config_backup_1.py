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
import change_password as cp

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

    commit_password(net_connect)

    # Disconnect.
    net_connect.disconnect()
    print("%s %s: Logged out of device." % (X['ip'], hostname))
    return(success_device.append(X['ip'] + '\t' + hostname + '\t' + version))


#######end backup function##############

def commit_password(net_connect):
    router_prompt = net_connect.find_prompt()
    print(router_prompt)
    config_commands = ["username cisco secret {}".format(cp.new_passw), 'show config', 'commit', 'show config failed']
    net_connect.send_config_set(config_commands)

# Define the backup job to run repeatedly.
def job():
    username = "cisco"

    cp.change_password()

    devices = [
        {'device_type': 'cisco_xr', 'ip': "10.66.70.76", 'username': username, 'password': cp.old_passw}, #login with old pw
        {'device_type': 'cisco_xr', 'ip': "10.66.70.79", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.82", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.65", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.68", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.60", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.45", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.48", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.51", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.52", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.53", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.54", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.44", 'username': username, 'password': cp.old_passw},
        {'device_type': 'cisco_xr', 'ip': "10.66.70.110", 'username': username, 'password': cp.old_passw},
    ]
    failed_device = []
    success_device = []
    # Make dir based on current date.
    if cp.timestr not in cp.ftp.nlst():
        cp.ftp.mkd(cp.timestr)

    print("Backup config will be saved to FTP server 10.66.70.170. Folder: asofrani/Backup_script/%s" % cp.timestr)

    # Open one thread for every router. Add all the threads to router_threads so we can keep track of them.
    router_threads = []
    for X in devices:
        thread = threading.Thread(target=backup, args=(X, cp.timestr, failed_device, success_device, ))
        thread.start()
        router_threads.append(thread)

    # Wait for all the threads to close. Then close FTP.
    for thread in router_threads:
        thread.join()

    if failed_device:
        cp.message += ("\n\n***ERROR: Backup script failed to connect to these device(s). Please check connectivity manually.***")
        for i in failed_device:
            cp.message += ("\n\n"+str(i))

    cp.message += ("\n\n***Backup script successfully connected to these devices.***")
    if success_device:
        for i in success_device:
            cp.message += ("\n"+str(i))

    cp.message += ("\n\n***Below config files were added to FTP server 10.66.70.170. Folder: asofrani/Backup_script/%s***\n" % cp.timestr)
    cp.ftp.cwd(cp.timestr)
    for i in cp.ftp.nlst():
        cp.message += ("\n" + str(i))
    cp.ftp.quit()

    print(cp.message)

    sender = 'pganesha@cisco.com'
    receivers = ['pganesha@cisco.com']
    try:
        smtpObj = smtplib.SMTP('mail.cisco.com')
        smtpObj.sendmail(sender, receivers, cp.message)
        print("Successfully sent email")
    except Exception as Any_Exception:
        print("Error: unable to send email")
        print(Any_Exception)

##############end job function ##############









if __name__ == "__main__":
    job()
    print(cp.old_passw)


# schedule.every(1).minute.do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(10)
