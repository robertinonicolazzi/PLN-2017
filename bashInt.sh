#!/bin/bash
echo "Training INTER n=1..."
{ time -p python languagemodeling/scripts/train.py -n 1 -m inter -o i1 >> eval_output_int.txt ;}
echo "eval INTER n=1..."
{ time -p python languagemodeling/scripts/eval.py -i i1 >> eval_output_int.txt ;} 

echo "Training INTER n=2..."
{ time -p python languagemodeling/scripts/train.py -n 2 -m inter -o i2 >> eval_output_int.txt ;} 
echo "eval INTER n=2..."
{ time -p python languagemodeling/scripts/eval.py -i i2 >> eval_output_int.txt ;} 


echo "Training INTER n=3..."
{ time -p python languagemodeling/scripts/train.py -n 3 -m inter -o i3 >> eval_output_int.txt ;} 
echo "eval INTER n=3..."
{ time -p python languagemodeling/scripts/eval.py -i i3 >> eval_output_int.txt ;} 


echo "Training INTER n=4..."
{ time -p python languagemodeling/scripts/train.py -n 4 -m inter -o i4 >> eval_output_int.txt ;} 
echo "eval INTER n=4..."
{ time -p python languagemodeling/scripts/eval.py -i i4 >> eval_output_int.txt ;} 