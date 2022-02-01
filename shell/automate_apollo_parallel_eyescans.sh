#!/bin/bash
echo "This an automated script to run C2C eyescans, given the apollo#, CM#, and the C2C link"
echo "Username: "
read username
echo "Apollo ##: "
read apxx
echo "CM ##: "
read cmxx


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
ssh -T $_remote "bash -s ${apxx} ${binx} ${biny} ${max_prescale} ${timestamp}" <<'EOL'
        xx=$1 
        binx=$2 
        biny=$3
        max_prescale=$4
        time=$5
        cd peace/ApolloTool
        export BUTOOL_AUTOLOAD_LIBRARY_LIST=""
        ./c2c_parallel_eyescans_script ${xx} ${binx} ${biny} ${max_prescale} ${time} &> es_40_40_6_parallel_eyescans_apollo${xx}_${time}.log
        python /home/cms/peace/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_C2C1_PHY_apollo${xx}_${time}.txt
        python /home/cms/peace/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_C2C2_PHY_apollo${xx}_${time}.txt
        python /home/cms/peace/ApolloTool/plugins/ApolloSM_plugin/python/eyescan.py es_${binx}_${biny}_${max_prescale}_V_C2C_PHY_apollo${xx}_${time}.txt
EOL

rsync -avzhe ssh $_remote:peace/ApolloTool/es_${binx}_${biny}_${max_prescale}_C2C1_PHY_apollo${apxx}_${timestamp}.png /nfs/cms/hw/apollo/CM${cmxx}/${weekly}/ 
rsync -avzhe ssh $_remote:peace/ApolloTool/es_${binx}_${biny}_${max_prescale}_C2C2_PHY_apollo${apxx}_${timestamp}.png /nfs/cms/hw/apollo/CM${cmxx}/${weekly}/
rsync -avzhe ssh $_remote:peace/ApolloTool/es_${binx}_${biny}_${max_prescale}_V_C2C_PHY_apollo${apxx}_${timestamp}.png /nfs/cms/hw/apollo/CM${cmxx}/${weekly}/
rsync -avzhe ssh $_remote:peace/ApolloTool/es_${binx}_${biny}_${max_prescale}_parallel_eyescans_apollo${apxx}_${timestamp}.log /nfs/cms/hw/apollo/CM${cmxx}/${weekly}/
