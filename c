#!/bin/bash
nasm -f elf64 $1.asm ; gcc -m64 -o $1 $1.o ; rm $1.o ; ./$1
