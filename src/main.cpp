#include <iostream>
#include "InputGen.hpp"
#include "Concurrent.hpp"
#include "CountThenMove.cpp"
#include <cmath>

int main()
{
    InputGen inputgen;

    const uint64_t tuple_size = pow(2, 24);
    TupleVector random = inputgen.generateInput(tuple_size);

    int num_partitions = 1024;
    int num_threads = 16;

    Concurrent concurrent(random, num_partitions, num_threads);
    auto concurrent_timer = concurrent.create_threads_and_run();
    
    CountThenMove count(random, num_partitions, num_threads);
    auto count_timer = count.create_threads_and_run();

    cout << "Concurrent: " << concurrent_timer << " ms\n";
    cout << "CountThenMove: " << count_timer << " ms\n";

    return 0;
}