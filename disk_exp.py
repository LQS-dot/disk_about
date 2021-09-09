#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import sys,os
import re
import subprocess
import shutil
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
        if int(disk_size_int) > int(2000):
            p = Popen(['parted', path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            output = p.communicate(input='mklabel\ngpt\nmkpart\n1\next3\n0%\n100%\nquit\n')
        else:
            p = Popen(['fdisk', path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            output = p.communicate(input='n\np\n1\n\n\nt\n8e\nw\nq\n')
        print output[0]
    except Exception,e:
        print str(e)

def disk_expand(diskname):
    try:
        if raid1_tag:
            inputs = 'pvcreate /dev/'+diskname+'1\nvgextend VolGroup /dev/'+diskname+'1\nlvextend -l +96%FREE /dev/VolGroup/lv_raid1_data\nquit\n'
        elif is_data:
            inputs = 'pvcreate /dev/'+diskname+'1\nvgextend VolGroup /dev/'+diskname+'1\nlvextend -l +96%FREE /dev/VolGroup/lv_origdata\nquit\n'
        else:
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
    if is_data:
        return result_dict['VolGroup-lv_origdata']
    else: 
        return result_dict['VolGroup-lv_opt']


def del_raid1():
    with open("/usr/lib/tj-app-pkgdir/disk_list.txt","r") as f:
        with open("/usr/lib/tj-app-pkgdir/disk_list.txt.new","w") as g:
            for line in f.readlines():
                if "md" not in line:
                    g.write(line)
 
    shutil.move("/usr/lib/tj-app-pkgdir/disk_list.txt.new","/usr/lib/tj-app-pkgdir/disk_list.txt")


if __name__ == '__main__':
    # 判断设备是否存在raid1
    raid1_tag=0
    p = Popen("df -h",stdout=subprocess.PIPE,shell=True)
    disk_out = p.communicate()
    disk_out=list(filter(None,disk_out))
    for disk_info in disk_out:
        if "VolGroup-lv_raid1_data" in disk_info:
            with open("/usr/lib/tj-app-pkgdir/disk_list.txt") as f:
                for disk in f.readlines():
                     if re.search("md\dp\d",disk.replace("\n","")):
                         raid1_tag=1
                         diskname=disk.replace("\n","")
                         disk_expand(diskname)
                         # 卷扩容
                         resize2fs /dev/VolGroup/lv_raid1_data
                         # 删除raid1分区名
                         del_raid1()
                sys.exit()

    diskname = sys.argv[1]
     
    diskname_line = os.popen("fdisk -l | grep -E \"Disk.*?{0}\"".format(diskname))
    if not diskname_line:
        sys.exit()
    disk_size = diskname_line.read().replace("\n","")
    # 获取扩容磁盘大小
    disk_size = disk_size.split(" ")[4].strip()
    disk_size_int = int(disk_size)/1000/1000/1000
    
    # 硬盘小于500G或者存在数据不处理
    all_diskname="/dev/"+ diskname
    if os.popen("/sbin/parted -s \"%s\" print|sed -ne '/^Number/,$p'|grep -v ^Number|awk '{print $1}'|grep \"^[0-9]\""%(all_diskname)).read() or disk_size_int < 500:
        print ("App Data partition Exist data or disk less than 500G")
        sys.exit()    

    # 磁盘是否为/data
    is_data = os.popen("df -h | grep \"VolGroup-lv_origdata\"").read().replace("\n","")
    try:
        optsize_first = float(dfh())
        disk_partition(diskname)
        sleep(3)
        cmd = 'mkfs.xfs -f /dev/' + str(diskname) + '1'
        p = subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        p.wait()
        disk_expand(diskname)
        sleep(3)
        with open("/etc/fstab","r") as f:
            f = f.read()
        if re.findall(r".*?/data\s+xfs",f):
            cmd1 = 'xfs_growfs /dev/VolGroup/lv_origdata'
        elif re.findall(r".*?/data\s+ext4",f):
            cmd1 = 'resize2fs /dev/VolGroup/lv_origdata'
        elif is_data and int(disk_size_int) >= int(2000):
            cmd1 = 'resize2fs /dev/VolGroup/lv_origdata'
        elif is_data:
            cmd1 = 'xfs_growfs /dev/VolGroup/lv_origdata'
        else:
            cmd1 = 'xfs_growfs /dev/VolGroup/lv_opt'
        q = subprocess.Popen(cmd1, shell=True, close_fds=True, bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        q.wait()
        optsize_last = float(dfh())
    except Exception,e:
        print str(e)
    if (optsize_last - optsize_first) > 5000:
        with open('/usr/lib/tj-app-pkgdir/disk_list.txt', 'a') as f:
            f.write(diskname + '\n')
            
            
