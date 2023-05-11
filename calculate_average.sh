#!/bin/bash

read -p "Enter the num of times to run the script: " num_times
#read -p "Enter the name of the script to run: " script_name

output=$(for i in {1..$num_times}; do python test.py; done)

times=$(echo "$output" | grep -o 'Finished in [0-9.]\+ seconds' | grep -o '[0-9.]\+')

# calc avg of times
sum=0
count=0
for time in $times; do
	sum=$(echo "$sum + $time" | bc)
	((count++))
done

avg=$(echo "scale=4; $sum / $count" | bc)

echo "Average time: $avg seconds."
