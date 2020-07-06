#!/bin/sh

# Generate data
[ -f /tmp/100000.json ] || ./streamson-bench generate -u 50000 -g 50000 -o /tmp/100000.json
[ -f /tmp/500000.json ] || ./streamson-bench generate -u 250000 -g 250000 -o /tmp/500000.json
[ -f /tmp/1000000.json ] || ./streamson-bench generate -u 500000 -g 500000 -o /tmp/1000000.json

for strategy in stdlib hyperjson streamson ijson-yajl2 ijson-yajl2_c ijson-yajl2_cffi ijson-python
do
	echo "##### ${strategy} #####"
	for count in 100000 500000 1000000
	do
		echo "----- ${count} -----"
		./streamson-bench time -i "/tmp/${count}.json" -s "${strategy}"
		./streamson-bench memory -i "/tmp/${count}.json" -s "${strategy}"
	done
done
