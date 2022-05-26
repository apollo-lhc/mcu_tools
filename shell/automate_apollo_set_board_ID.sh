#!/bin/bash
echo "This an automated script is called because your board has not set up an ID"
echo "Username: "
read username

echo "You entered ID: ${4}"

_remote="cms@apollo${2}"
_user="${username}"

weekly="$(date '+week%W-%m-%Y')"
 
echo "Local system name: $HOSTNAME"
echo "Local date and time: $(date)"
 
echo
echo "*** Running commands on remote host named $_remote ***"
echo
ssh -T $_remote "bash -s ${2} ${_user} ${1} ${4} ${3}" <<'EOL'
        xx=$1 
	user=$2
        ttyname=$3
        id=$4
        time=$5
	cd ~/${user}/Cornell_CM_Production_Scripts/mcu_tools/python
        python get_cm_id_to_set.py ${ttyname} ${xx} ${time} ${id}  
EOL


rsync -avzhe ssh $_remote:$_user/Cornell_CM_Production_Scripts/mcu_tools/data/dump_setid_${1}_apollo${2}_${3}.txt ../data/
 
