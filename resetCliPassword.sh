cliUserName=`cat /opt/smc/hardware/conf/management.ini |grep 'cli_usr'| awk -F'=' '{print $2}'`
cliEncryptPassword=`cat /opt/smc/hardware/conf/management.ini |grep 'cli_dft'| awk -F'=' '{print $2}'`
cliDecyptPassword=`/opt/smc/hardware/sbin/decypt ${cliEncryptPassword}`
companyName=`cat /opt/smc/web/tomcat/webapps/SMCConsole/WEB-INF/classes/conf/SMCConsole.properties|grep company_name|awk -F'=' '{print $2}'`
if [[ ${companyName} =~ '聚铭' ]]
then
     sed -i "s/cli_pwd.*/cli_pwd=/g"  /opt/smc/hardware/conf/management.ini > /dev/null 2>&1
	 sync
else
     sed -i "/cli_pwd/d" /opt/smc/hardware/conf/management.ini > /dev/null 2>&1
	 sync
     sed -i "/cli_dft/a\\cli_pwd=${cliEncryptPassword}"  /opt/smc/hardware/conf/management.ini > /dev/null 2>&1
	 sync
fi
echo ${cliDecyptPassword}|passwd --stdin ${cliUserName} > /dev/null 2>&1
if [ $? != 0 ]
then
     echo "false"
else
     echo "true"
fi
