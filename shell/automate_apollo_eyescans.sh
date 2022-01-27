#!/bin/bash
echo "This an automated script to run C2C eyescans, given the apollo#, CM#, and the C2C link"
echo "Username: "
read username
echo "Apollo ##: "
read apxx
echo "CM ##: "
read cmxx
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
ssh -T $_remote "bash -s ${apxx} ${c2c_link} ${c2c_node} ${binx} ${biny} ${max_prescale} ${timestamp}" <<'EOL'
        xx=$1 
        link=$2
        node=$3
        binx=$4 
        biny=$5
        max_prescale=$6
        time=$7
        cd peace/ApolloTool
        export BUTOOL_AUTOLOAD_LIBRARY_LIST=""
        ./c2c_single_eyescan_script ${xx} ${link} ${node} ${binx} ${biny} ${max_prescale} ${time} &> es_40_40_6_${link}_apollo${xx}_${time}.log
        python /home/cms/peace/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_40_40_6_${link}_apollo${xx}_${time}.txt
EOL

rsync -avzhe ssh $_remote:peace/ApolloTool/*.png /nfs/cms/hw/apollo/CM${cmxx}/${weekly}/ 
rsync -avzhe ssh $_remote:peace/ApolloTool/*.log /nfs/cms/hw/apollo/CM${cmxx}/${weekly}/
