#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import re
import subprocess

def vulscan_popen(cmd):
    try:
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        print str(e)
        return


def fdisk():
    disklists = []
    res_list = []
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
            if diskname not in disklists:
                u_cmd="fdisk -l | grep -Eo \"{0}[0-9]\"".format(diskname)
		u_name=vulscan_popen(u_cmd)
		diskname=u_name[-1].replace("\n","")
                res_list.append(diskname)
        except:
            pass
    print res_list 
if __name__ == '__main__':
    fdisk()
