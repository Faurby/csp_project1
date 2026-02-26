#include <iostream>
#include "InputGen.hpp"
#include "Concurrent.hpp"
#include <cmath>

int main()
{
    InputGen inputgen;

    const uint64_t tuple_size = pow(2, 24);
    TupleVector random = inputgen.generateInput(tuple_size);

    int num_partitions = 1024;
    int num_threads = 16;

    Concurrent concurrent(random, num_partitions, num_threads);

    concurrent.create_threads();

    concurrent.print_partitions();

    return 0;
}