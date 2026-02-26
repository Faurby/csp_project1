#include "Concurrent.hpp"
#include <thread>
#include <iostream>

using namespace std;

Concurrent::Concurrent(TupleVector& tuples,
                       int num_partitions,
                       int num_threads)
    : tuples(tuples),
      partitions(num_partitions,
                 TupleVector((tuples.size() / num_partitions) * 1.1)),
      partition_lastIndexes(num_partitions),
      NUM_THREADS(num_threads)
{
}

void Concurrent::create_threads()
{
    vector<thread> threads(NUM_THREADS);

    const int TUPLES_PER_THREAD = tuples.size() / NUM_THREADS;

    for (int i = 0; i < NUM_THREADS; i++)
    {
        int start = i * TUPLES_PER_THREAD;
        int end = (i == NUM_THREADS - 1)
                  ? tuples.size()
                  : start + TUPLES_PER_THREAD;

        threads[i] = thread([this, start, end]
        {
            hashing_and_insert(start, end);
        });
    }

    for (auto& t : threads)
        t.join();
}

void Concurrent::print_partitions() const
{
    for (size_t i = 0; i < partitions.size(); i++)
    {
        cout << "Partition " << i
             << " (" << partition_lastIndexes[i].load() << " items)\n"
             << "----------------------------------\n";

        int count = partition_lastIndexes[i].load();

        for (int j = 0; j < count; j++)
        {
            const auto& [key, value] = partitions[i][j];
            cout << "  [" << j << "] ("
                 << key << ", " << value << ")\n";
        }

        cout << "\n";
    }
}

void Concurrent::hashing_and_insert(int start, int end)
{
    for (int i = start; i < end; i++)
    {
        auto [key, value] = tuples[i];

        int partition = key % partitions.size();
        int hash_index = partition_lastIndexes[partition].fetch_add(1);

        partitions[partition][hash_index] = tuples[i];
    }
}