#!/bin/bash
echo "This is an automated script to make a directory for a weekly(Mon-SU) report of the C2C and Firefly eyescans"
echo "Please enter the following information only if initiate a new weekly report"
echo "Username: "
read username
echo "Apollo ##: "
read xx
echo "ttydevice: "
read ttyname

_remote="cms@apollo${xx}"
_user="$username"
 
echo "Local system name: $HOSTNAME"
echo "Local date and time: $(date)"
echo "remote: $_remote"
echo "username: $_user"

echo
echo "*** Running commands on remote host named $_remote ***"
echo
ssh -T $_remote "bash -s $ttyname" <<'EOL'
        ttyname=$1
        cd peace/Cornell_CM_Production_Scripts/mcu_tools/python
        python minicom_id_dump_to_txt.py ${ttyname}
        
EOL


rsync -avzhe ssh $_remote:peace/Cornell_CM_Production_Scripts/mcu_tools/data/dump_id_${ttyname}.txt ../data/
python ../python/check_cm_id_to_mkdir.py ${ttyname}

