lang=java
task=transfer
dataset=translate
scope=all
style=16.1

# 'defect', 'clone', 'refine', 'translate', 'summarize'

# |0.5|
# |7.2|
# |8.1| 
# |9.1| 
# |2.1| (refine, 3.61) (summarize, 4.18)
# |11.3|
# |16.1| (clone, 0.85) (refine, 2.54) (summarize, 1.97)
# |17.2|
# |3.4| 
# |4.4|
# |10.7|
# |12.4|


cd ..
python transfer.py \
    --lang  ${lang} \
    --task  ${task} \
    --dataset ${dataset} \
    --scope ${scope} \
    --style ${style}    
wait