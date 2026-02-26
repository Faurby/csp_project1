CXX = g++
CXXFLAGS = -std=c++17 -pthread -Wall -Wextra -O2 -g

SRC = src/main.cpp src/Concurrent.cpp src/InputGen.cpp
OUT = out/main

all:
	mkdir -p out
	$(CXX) $(CXXFLAGS) $(SRC) -o $(OUT)

run: all
	./$(OUT)

clean:
	rm -rf out