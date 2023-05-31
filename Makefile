all:
	g++ -o cont containercpp.cpp -lboost_filesystem -lboost_system -lboost_iostreams

clean:
	rm *.o cont
