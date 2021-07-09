#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import sys
import re
import subprocess
from subprocess import Popen,PIPE,STDOUT
from time import sleep

def vulscan_popen(cmd):
    try:
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        print str(e)
        return ""

def disk_partition(diskname):
    try:
        path = '/dev/'+diskname
        p = Popen(['fdisk', path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = p.communicate(input='n\np\n1\n\n\nt\n8e\nw\nq\n')
        print output[0]
    except Exception,e:
        print str(e)

def disk_expand(diskname):
    try:
        inputs = 'pvcreate /dev/'+diskname+'1\nvgextend VolGroup /dev/'+diskname+'1\nlvextend -l +96%FREE /dev/VolGroup/lv_opt\nquit\n'
        p = Popen('lvm', stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = p.communicate(input=inputs)
        print output[0]
    except Exception,e:
        print str(e)

def dfh():
    result = vulscan_popen('df -m')
    result_dict = {}
    for i in range(len(result)):
        try:
            filesystem = re.search(r'(VolGroup\-lv\S+)', result[i], re.S).group(1)
            size = re.search(r'(\d+\.?\d*)\s*', result[i+1], re.S).group(1)
            result_dict[filesystem] = size
        except:
            pass

    return result_dict['VolGroup-lv_opt']

if __name__ == '__main__':
    diskname = sys.argv[1]
    try:
        optsize_first = float(dfh())
        disk_partition(diskname)
        sleep(3)
        cmd = 'mkfs.xfs -f /dev/' + str(diskname) + '1'
        p = subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        p.wait()
        disk_expand(diskname)
        sleep(3)
        cmd1 = 'xfs_growfs /dev/VolGroup/lv_opt'
        q = subprocess.Popen(cmd1, shell=True, close_fds=True, bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        q.wait()
        optsize_last = float(dfh())
    except Exception,e:
        print str(e)
    if (optsize_last - optsize_first) > 5000:
        with open('/usr/lib/tj-app-pkgdir/disk_list.txt', 'a') as f:
            f.write(diskname + '\n')
            
            
