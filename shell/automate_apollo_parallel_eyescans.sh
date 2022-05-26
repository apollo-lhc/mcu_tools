#!/bin/bash
echo "This an automated script to run C2C eyescans in parallel, given the apollo#"
echo "Username: "
read username
echo "Apollo ##: "
read apxx
echo "ttydevice: "
read ttyname

binx=40
biny=40
max_prescale=6

echo "Only three c2c links are working"

_remote="cms@apollo${apxx}"
_user="${username}"

weekly="$(date '+week%W-%m-%Y')"
timestamp="$(date '+day-%d_time-%H.%M.%S')"
 
echo "Local system name: $HOSTNAME"
echo "Local date and time: $(date)"
 
echo
echo "*** Running commands on remote host named $_remote ***"
echo
ssh -T $_remote "bash -s ${apxx} ${_user} ${ttyname} ${binx} ${biny} ${max_prescale} ${timestamp}" <<'EOL'
        xx=$1 
	user=$2
        ttyname=$3
        binx=$4
        biny=$5
        max_prescale=$6
        time=$7
        cd ${user}/ApolloTool
        export BUTOOL_AUTOLOAD_LIBRARY_LIST=""
        ./c2c_parallel_eyescans_script ${xx} ${binx} ${biny} ${max_prescale} ${time} &> es_${binx}_${biny}_${max_prescale}_parallel_eyescans_apollo${xx}_${time}.log
        python /home/cms/${user}/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_C2C1_PHY_apollo${xx}_${time}.txt
        python /home/cms/${user}/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_C2C2_PHY_apollo${xx}_${time}.txt
        python /home/cms/${user}/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_V_C2C_PHY_apollo${xx}_${time}.txt
	cd ~/${user}/Cornell_CM_Production_Scripts/mcu_tools/python
        python minicom_commands_dump_to_txt.py ${ttyname} ${xx} ${time}  
EOL


rsync -avzhe ssh $_remote:$_user/Cornell_CM_Production_Scripts/mcu_tools/data/dump_text_${ttyname}_apollo${apxx}_${timestamp}.txt ../data/
rsync -avzhe ssh $_remote:$_user/ApolloTool/es_${binx}_${biny}_${max_prescale}_C2C1_PHY_apollo${apxx}_${timestamp}.png ../data/
rsync -avzhe ssh $_remote:$_user/ApolloTool/es_${binx}_${biny}_${max_prescale}_C2C2_PHY_apollo${apxx}_${timestamp}.png ../data/
rsync -avzhe ssh $_remote:$_user/ApolloTool/es_${binx}_${biny}_${max_prescale}_V_C2C_PHY_apollo${apxx}_${timestamp}.png ../data/
rsync -avzhe ssh $_remote:$_user/ApolloTool/es_${binx}_${biny}_${max_prescale}_parallel_eyescans_apollo${apxx}_${timestamp}.log ../data/

python ../python/check_cm_id_to_mkdir.py ${ttyname} ${apxx} ${timestamp} 
