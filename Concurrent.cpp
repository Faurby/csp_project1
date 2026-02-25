#include <vector>
#include <utility>
#include <cstdint>
#include <atomic>
#include "types.hpp"
#include <thread>
#include <iostream>

using namespace std;

class Concurrent
{
public:
    Concurrent(TupleVector &tuples, int num_partitions, int num_threads)
        : tuples(tuples),
          partitions(num_partitions, TupleVector((tuples.size() / num_partitions) * 1.1)),
          partition_lastIndexes(num_partitions),
          NUM_THREADS(num_threads)
    {
    }

    void create_threads()
    {
        thread threads[NUM_THREADS];

        const int TUPLES_PER_THREAD = tuples.size() / NUM_THREADS;

        for (int i = 0; i < NUM_THREADS; i++)
        {
            int start = i * TUPLES_PER_THREAD;
            int end = (start + TUPLES_PER_THREAD);

            if (i == NUM_THREADS - 1)
            {
                end = tuples.size();
            }

            threads[i] = thread([this, start, end]
                                { hashing_and_insert(start, end); });
        }

        for (int i = 0; i < NUM_THREADS; i++)
        {
            threads[i].join();
        }
    }

    void print_partitions() const
    {
        for (size_t i = 0; i < partitions.size(); i++)
        {
            cout << "Partition " << i
                 << " (" << partition_lastIndexes[i].load() << " items)"
                 << "\n----------------------------------\n";

            int count = partition_lastIndexes[i].load();

            for (int j = 0; j < count; j++)
            {
                const auto &[key, value] = partitions[i][j];
                cout << "  [" << j << "] "
                     << "(" << key << ", " << value << ")\n";
            }

            cout << "\n";
        }
    }

private:
    TupleVector &tuples;
    vector<TupleVector> partitions;
    vector<atomic_int> partition_lastIndexes;
    const int NUM_THREADS;

    void hashing_and_insert(int start, int end)
    {
        for (int i = start; i < end; i++)
        {
            auto [key, value] = tuples[i];

            // hashing
            int partition = key % partitions.size();

            auto hash_index = partition_lastIndexes[partition].fetch_add(1);

            partitions[partition][hash_index] = tuples[i];
        }
    }
};