#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os
import re
import subprocess


def vulscan_popen(cmd):
    try:
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        print str(e)
        return ""

def fdisk():

    result = vulscan_popen('fdisk -l')
    for line in result:
        try:
            diskname = re.search(r'Disk\s*/dev/([a-z]+d[a-z]+):\s*(.*?),', line, re.S).group(1)
            with open('/usr/lib/tj-app-pkgdir/disk_list.txt', 'a') as f:
                f.write(diskname + '\n')
        except:
            pass

if __name__ == '__main__':
    if not os.access('/usr/lib/tj-app-pkgdir/disk_list.txt', os.F_OK):
        fdisk()