main:
	touch compile; echo "python main.py" >> compile; chmod +x compile;
clean:
	rm -rf *pyc compile
