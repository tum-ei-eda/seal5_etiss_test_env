#!/bin/bash

INP=$1

jq -r '
  (["prog","jit","etiss_arch","arch","abi","mips","sim_time [s]","sim_cycles"] | @tsv),
  (.[] | [.prog,.jit,.etiss_arch,.arch,.abi,.mips,.Simulation_Time,.CPU_cycle] | @tsv)
' $INP |
awk '
BEGIN { FS=OFS="\t" }
NR==1 {
    print "| "$1" | "$2" | "$3" | "$4"/"$5" | "$6" | "$7" | "$8" |"
    print "|---|---|---|---|---|---|---|"
    next
}
{
    print "| "$1" | "$2" | "$3" | "$4"/"$5" | "$6" | "$7" | "$8" |"
}'
