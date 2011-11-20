
main:
	echo 'python main.py $$1' > compile;
	echo 'program=`basename $$1 .alice`' >> compile;
	echo 'if [ -f $$program.asm ]' >> compile;
	echo 'then ' >> compile;
	echo 'nasm -f elf64 $$program.asm ; gcc -m64 -o $$program $$program.o' >> compile
	echo 'rm $$program.asm $$program.o' >> compile
	echo 'fi' >> compile;
	chmod +x compile;
clean:
	rm -rf *pyc compile parsetab.py parser.out
