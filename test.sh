for f in milestone2/*.alice 
do
    fname=`basename $f`
    echo "Compiling $fname"
    python main.py $f
    if [ -f $f.asm ]
    then
    echo "Running $fname" 
    nasm -f elf64 $f.asm ; gcc -m64 -o $f $f.o ; ./$f
    rm $f.asm $f.o
    fi
    echo "++++++++++++++++++\n++++++++++++++++++"
done
