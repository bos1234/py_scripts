import ftplib
import time
import re

def change_password():
    # Connect to FTP.
    timestr = time.strftime("%Y%m%d")
    ftp = ftplib.FTP('10.66.70.170')
    ftp.login('cisco', 'cisco')
    ftp.cwd("asofrani/Backup_script/")

    message = """From: XR Config Backup Script <pganesha@cisco.com>
    To: XR Lab Admin <pganesha@cisco.com>
    Subject: SYD XR Static Lab Config Backup Result: """ + timestr

    # Find current password. Set "password + 1" as new password.
    for line in ftp.nlst():
        pass_match = re.search(r'current_password:cisco!(\d+)', line)   ###-- > current_password:cisco!124
        if pass_match:
            pass_key = pass_match.group(1)   # --- > 124
            passw = "cisco!" + pass_key #--- > cisco!124. Current password that will be used to login to the box
            new_pass_key = str(int(pass_key) + 1) #---- > new_pass_key = 125
            new_passw = "cisco!" + new_pass_key  #--- > cisco!125
            print(ftp.pwd())

            old_filename = 'current_password:' + passw
            new_filename = 'current_password:' + new_passw
            print(old_filename)
            print(new_filename)
            ftp.rename(old_filename, new_filename)
            # ftp.sendcmd('RNFR ' +  old_filename)
            # ftp.sendcmd('RNTO ' +  new_filename)


    if not passw:
        ftp.quit()
        message += "\n\nDidn't find current password under FTP folder. Abort job."
        return(message)

    return(passw, new_passw, timestr, ftp, message)



(old_passw, new_passw, timestr, ftp, message) = change_password()
