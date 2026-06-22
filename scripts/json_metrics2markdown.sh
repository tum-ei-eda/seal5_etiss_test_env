#!/bin/bash

INP=$1

jq -r '
  (["prog","toolchain","jit","etiss_arch","arch","abi","mips","sim_time","sim_cycles"] | @tsv),
  (.[] | [.prog,.toolchain,.jit,.etiss_arch,.arch,.abi,.mips,.Simulation_Time,.CPU_cycle] | @tsv)
' $INP |
awk '
BEGIN { FS=OFS="\t" }
NR==1 {
    print "| "$1" | "$2" | "$3" | "$4"/"$5" | "$6" | "$7" | "$8" | "$9" |"
    print "|---|---|---|---|---|---|---|---|"
    next
}
{
    print "| "$1" | "$2" | "$3" | "$4"/"$5" | "$6" | "$7"s | "$8" | "$9" |"
}'
