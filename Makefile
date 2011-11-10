main:
	echo "python main.py" > compile; chmod +x compile;
	echo "nasm -f elf64 output.asm ; gcc -m64 -o output output.o ; ./output" >> compile

clean:
	rm -rf *pyc compile parsetab.py parser.out output.*
