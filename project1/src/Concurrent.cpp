#include "Concurrent.hpp"
#include <thread>
#include <iostream>
#include <barrier>
using namespace std;
using namespace std::chrono;

Concurrent::Concurrent(TupleVector &tuples,
                       int num_partitions,
                       int num_threads)
    : tuples(tuples),
      partitions(num_partitions,
                 TupleVector((tuples.size() / num_partitions) * 1.1)),
      partition_lastIndexes(num_partitions),
      NUM_THREADS(num_threads),
      NUM_PARTITIONS(num_partitions)
{
}

long long Concurrent::create_threads_and_run(AffinityStrategy strategy)
{
    vector<thread> threads;
    threads.reserve(NUM_THREADS);
    const int TUPLES_PER_THREAD = tuples.size() / NUM_THREADS;

    std::barrier<> sync_barrier(NUM_THREADS + 1);

    for (int i = 0; i < NUM_THREADS; i++)
    {
        int start = i * TUPLES_PER_THREAD;
        int end = (i == NUM_THREADS - 1)
                      ? (int)tuples.size()
                      : start + TUPLES_PER_THREAD;

        threads.emplace_back([this, start, end, &sync_barrier]()
        {
            sync_barrier.arrive_and_wait();
            hashing_and_insert(start, end);
        });
    }

    SetAffinity::pinThreadsToCores(threads, strategy);

    auto timer_start = high_resolution_clock::now();
    sync_barrier.arrive_and_wait(); // release all workers

    for (auto &t : threads)
        t.join();

    auto timer_end = high_resolution_clock::now();
    return duration_cast<milliseconds>(timer_end - timer_start).count();
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
            const auto &[key, value] = partitions[i][j];
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
        auto [key, _] = tuples[i];
        int partition = key % NUM_PARTITIONS;
        int hash_index = partition_lastIndexes[partition].fetch_add(1);
        partitions[partition][hash_index] = tuples[i];
    }
}
