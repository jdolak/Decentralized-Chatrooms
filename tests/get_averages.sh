num=$(( $(ls ./logs/*.log | wc -l) / 2 - 1 ))
grep -R average ./logs/ | rev | cut -d ' ' -f 1-3 | rev > latency-low-$num.txt
#grep -R throughput ./logs/ | rev | cut -d ' ' -f 7 | rev> throughput-low-$num.txt