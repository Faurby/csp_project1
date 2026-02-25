#include <iostream>
#include "InputGen.cpp"
#include "Concurrent.cpp"

int main()
{
    InputGen inputgen;

    TupleVector random = inputgen.generateInput(100);

    int num_partitions = 4;
    int num_threads = 4;

    Concurrent concurrent(random, num_partitions, num_threads);

    concurrent.create_threads();

    concurrent.print_partitions();

    return 0;
}