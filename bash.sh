#!/bin/bash
echo "Training backoff n=1..."
{ time -p python languagemodeling/scripts/train.py -m backoff -n 1 -o b1 & >> train_output.txt ;} 



echo "Training backoff n=2..."
{ time -p python languagemodeling/scripts/train.py -m backoff -n 2 -o b2 & >> train_output.txt ;} 



echo "Training backoff n=3..."
{ time -p python languagemodeling/scripts/train.py -m backoff -n 3 -o b3 & >> train_output.txt ;} 



echo "Training backoff n=4..."
{ time -p python languagemodeling/scripts/train.py -m backoff -n 4 -o b4 & >> train_output.txt ;} 
