#!/bin/bash
echo "This an automated script to run a single C2C eyescan, given the apollo#, and the C2C link"
echo "Username: "
read username
echo "Apollo ##: "
read apxx
echo "ttydevice: "
read ttyname
echo "What's C2C link?(Type 1:C2C1_PHY 2:C2C2_PHY 3:K_C2C_PHY 4:V_C2C_PHY) "
read c2c

declare -A c2c_links
declare -A c2c_nodes

binx=40
biny=40
max_prescale=6

c2c_links['1']='C2C1_PHY'
c2c_links['2']='C2C2_PHY' 
c2c_links['3']='K_C2C_PHY'
c2c_links['4']='V_C2C_PHY'

c2c_nodes['1']='CM.CM_1.C2C_1.LINK_DEBUG.RX.LPM_EN'
c2c_nodes['2']='CM.CM_1.C2C_2.LINK_DEBUG.RX.LPM_EN'
c2c_nodes['3']='K_IO.C2C.DEBUG.RX.LPM_EN'
c2c_nodes['4']='V_IO.C2C.DEBUG.RX.LPM_EN'

c2c_link=${c2c_links[${c2c}]}
c2c_node=${c2c_nodes[${c2c}]}

echo "the c2c link to scan: ${c2c_link}"

_remote="cms@apollo${apxx}"
_user="${username}"

weekly="$(date '+week%W-%m-%Y')"
timestamp="$(date '+day-%d_time-%H.%M.%S')"
 
echo "Local system name: $HOSTNAME"
echo "Local date and time: $(date)"
 
echo
echo "*** Running commands on remote host named $_remote ***"
echo
ssh -T $_remote "bash -s ${apxx} ${_user} ${ttyname} ${c2c_link} ${c2c_node} ${binx} ${biny} ${max_prescale} ${timestamp}" <<'EOL'
        xx=$1 
        user=$2
	ttyname=$3
        link=$4
        node=$5
        binx=$6 
        biny=$7
        max_prescale=$8
        time=$9
        cd ${user}/ApolloTool
        export BUTOOL_AUTOLOAD_LIBRARY_LIST=""
        ./c2c_single_eyescan_script ${xx} ${link} ${node} ${binx} ${biny} ${max_prescale} ${time} &> es_${binx}_${biny}_${max_prescale}_${link}_apollo${xx}_${time}.log
        python /home/cms/${user}/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_${link}_apollo${xx}_${time}.txt
	cd ~/${user}/Cornell_CM_Production_Scripts/mcu_tools/python
	python minicom_commands_dump_to_txt.py ${ttyname} ${xx} ${time}
EOL

rsync -avzhe ssh $_remote:$_user/Cornell_CM_Production_Scripts/mcu_tools/data/dump_text_${ttyname}_apollo${apxx}_${timestamp}.txt ../data/    
rsync -avzhe ssh $_remote:$_user/ApolloTool/es_${binx}_${biny}_${max_prescale}_${c2c_link}_apollo${apxx}_${timestamp}.png ../data/ 
rsync -avzhe ssh $_remote:$_user/ApolloTool/es_${binx}_${biny}_${max_prescale}_${c2c_link}_apollo${apxx}_${timestamp}.log ../data/

python ../python/check_cm_id_to_mkdir.py ${ttyname} ${apxx} ${timestamp}
