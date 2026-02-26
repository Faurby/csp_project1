#include <iostream>
#include "InputGen.hpp"
#include "Concurrent.hpp"
#include "CountThenMove.cpp"
#include <cmath>

int main(int argc, char *argv[])
{
    if (argc != 5)
    {
        cout << "Usage: <thread_size> <hashbits> <algorithm> <core_affinity>\n";
        return 1;
    }

    InputGen inputgen;

    const uint64_t tuple_size = pow(2, 24);
    TupleVector random = inputgen.generateInput(tuple_size);
    
    int num_threads = atoi(argv[1]);
    int num_partitions = pow(2, atoi(argv[2]));
    int algorithm = atoi(argv[3]);
    int core_affinity = atoi(argv[4]);

    if (algorithm == 1)
    {
        Concurrent concurrent(random, num_partitions, num_threads);
        auto concurrent_timer = concurrent.create_threads_and_run();
        cout << "Concurrent: " << concurrent_timer << " ms\n";
        return 0;
    } else if (algorithm == 2)
    {
        CountThenMove count(random, num_partitions, num_threads);
        auto count_timer = count.create_threads_and_run();
        cout << "CountThenMove: " << count_timer << " ms\n";
        return 0;
    }

    return 0;
}