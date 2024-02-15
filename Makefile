clean: 
	find . -name '[0-9:]*\-[0-9:]*' | xargs rm -rf
	rm *.txt
	rm *.csv

remake:
	find . -name '[0-9:]*\-[0-9:]*' | xargs rm -rf
	rm *.csv