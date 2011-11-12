for f in milestone2/*.alice 
do
    echo "Compiling $f"
    python main.py $f
    if [ -f output.asm ]
    then
    echo "Running $f" 
    nasm -f elf64 output.asm ; gcc -m64 -o output output.o ; ./output
    rm output.asm output.o
    fi
    echo "++++++++++++++++++\n++++++++++++++++++"
done
