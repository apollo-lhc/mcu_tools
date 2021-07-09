#!/bin/bash
sdiff -l ../data/dump_text_apollo09_ttyUL1.txt $1 | cat -n | grep -v -e '($' > ../data/dump_diff_from_apollo09.txt 

