#include <iostream>
#include "InputGen.hpp"
#include "Concurrent.hpp"
#include "CountThenMove.cpp"
#include "SetAffinity.hpp"
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
    string affinity_arg = argv[4];
    AffinityStrategy affinity;

    if (affinity_arg == "scatter") {
        affinity = AffinityStrategy::Scatter;
    } else if (affinity_arg == "compact") {
        affinity = AffinityStrategy::Compact;
    } else {
        affinity = AffinityStrategy::None;
    }

    if (algorithm == 1)
    {
        Concurrent concurrent(random, num_partitions, num_threads);
        auto concurrent_timer = concurrent.create_threads_and_run(affinity);
        cout << concurrent_timer << "\n";
        return 0;
    } else if (algorithm == 2)
    {
        CountThenMove count(random, num_partitions, num_threads);
        auto count_timer = count.create_threads_and_run(affinity);
        cout << count_timer << "\n";
        return 0;
    }

    return 0;
}
