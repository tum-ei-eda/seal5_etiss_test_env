#!/bin/bash

INP=$1

jq -r '
  (["jit","etiss_arch","num_tests","num_pass","num_fail","num_fail_expected","num_fail_filtered"] | @tsv),
  (.[] | [.jit,.etiss_arch,.num_tests,.num_pass,.num_fail,.num_fail_expected,.num_fail_filtered] | @tsv)
' $INP |
awk '
BEGIN { FS=OFS="\t" }
NR==1 {
    print "| "$1" | "$2" | "$3" | "$4" | "$5" | "$6" | "$7" |"
    print "|---|---|---|---|---|---|---|"
    next
}
{
    print "| "$1" | "$2" | "$3" | "$4" | "$5" | "$6" | "$7" |"
}'
