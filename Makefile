
main:
	echo 'python main.py $$1' > compile; chmod +x compile;
	echo "if [ -f output.asm ]" >> compile;
	echo "then " >> compile;
	echo "nasm -f elf64 output.asm ; gcc -m64 -o output output.o ; ./output" >> compile
	echo "rm output.asm, output.o"
	echo "fi" >> compile;
		

clean:
	rm -rf *pyc compile parsetab.py parser.out output.*
