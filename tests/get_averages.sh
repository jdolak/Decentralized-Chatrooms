num=$(( $(ls ./logs/ | wc -l) - 2 ))
grep -R average ./logs/ | rev | cut -d ' ' -f 1-3 | rev > latency-low-$num.txt