#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os
import re
import subprocess
from string import digits

def vulscan_popen(cmd):
    try:
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        print str(e)
        return ""


def fdisk():
    disklists = []
    result_dict = {}
    try:
        with open('/usr/lib/tj-app-pkgdir/disk_list.txt','r') as f:
            for line in f:
                disklists.append(line.replace('\n',''))
    except Exception, e:
        print str(e)

    result = vulscan_popen('fdisk -l')
    for line in result:
        try:
            diskname = re.search(r'Disk\s*/dev/([a-z]+d[a-z]+):\s*(.*?),', line, re.S).group(1)
            if diskname in disklists:
                continue
            disksize = re.search(r'Disk\s*/dev/([a-z]+d[a-z]+):\s*(.*?),', line, re.S).group(2)
            result_dict[diskname] = disksize
        except:
            pass
    u_disk = os.popen("python /opt/smc/web/tomcat/webapps/SMCConsole/script/disk/uDiskList.py").read()
    u_disk = u_disk.replace("\n","")
    u_disk = u_disk.replace("\'","")
    u_disk = u_disk.replace(" ","")
    u_disk = u_disk[1:-1].split(",")
    for disk in u_disk:
        disk=disk.translate(None,digits)
        if disk in result_dict.keys():
            del result_dict[disk]
    print result_dict


def dfh():
    result = vulscan_popen('df -h')
    result_dict = {}
    for i in range(len(result)):
        try:
            filesystem = re.search(r'(VolGroup\-lv\S+)', result[i], re.S).group(1)
            size = re.search(r'(\d+\.?\d*\s*[a-zA-Z]+)', result[i+1], re.S).group(1)
            result_dict[filesystem] = size
        except:
            pass
    print result_dict

if __name__ == '__main__':
    fdisk()
    dfh()
