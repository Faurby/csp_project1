#include "types.hpp"
#include <vector>
#include <thread>
#include <iostream>
#include <chrono>

using namespace std;
using namespace std::chrono;

class CountThenMove
{
public:
    CountThenMove(TupleVector &tuples, int num_partitions, int num_threads)
        : tuples(tuples),
          NUM_THREADS(num_threads),
          buffer(tuples.size()),
          NUM_PARTITIONS(num_partitions),
          partition_start_index(NUM_PARTITIONS),
          thread_partition_start_index(NUM_THREADS, vector<int>(NUM_PARTITIONS)),
          total_elements_per_partition(NUM_PARTITIONS) {};

    long long create_threads_and_run()
    {
        thread threads[NUM_THREADS];
        const int TUPLES_PER_THREAD = tuples.size() / NUM_THREADS;
        vector<vector<int>> elements_per_thread(NUM_THREADS, vector<int>(NUM_PARTITIONS));

        auto timer_start = high_resolution_clock::now();

        // Count elements each thread puts in each partition
        for (int i = 0; i < NUM_THREADS; i++)
        {
            int start = i * TUPLES_PER_THREAD;
            int end = (i == NUM_THREADS - 1) ? tuples.size() : start + TUPLES_PER_THREAD;

            auto &elements_in_partition = elements_per_thread[i];
            threads[i] = thread([this, start, end, &elements_in_partition]
                                { count(elements_in_partition, start, end); });
        }

        // Calculate total elements per partition, based on each threads partition elements
        for (int i = 0; i < NUM_THREADS; i++)
        {
            threads[i].join();
            for (int j = 0; j < NUM_PARTITIONS; j++)
            {
                total_elements_per_partition[j] += elements_per_thread[i][j];
            }
        }

        // Calculate each thread start index in each partition

        for (int partition = 0; partition < NUM_PARTITIONS; partition++)
        {
            int partition_index = 0;
            if (partition > 0)
            {
                partition_index = total_elements_per_partition[partition - 1] + partition_start_index[partition - 1];
            }
            partition_start_index[partition] = partition_index;

            for (int thread = 0; thread < NUM_THREADS; thread++)
            {
                int thread_partition_index;
                if (thread == 0)
                {
                    thread_partition_index = partition_start_index[partition];
                }
                else
                {
                    thread_partition_index = thread_partition_start_index[thread - 1][partition] + elements_per_thread[thread - 1][partition];
                }

                thread_partition_start_index[thread][partition] = thread_partition_index;
            }
        }

        for (int i = 0; i < NUM_THREADS; i++)
        {
            int start = i * TUPLES_PER_THREAD;
            int end = (i == NUM_THREADS - 1) ? tuples.size() : start + TUPLES_PER_THREAD;

            auto &thread_start_indexes = thread_partition_start_index[i];
            threads[i] = thread([this, start, end, &thread_start_indexes]
                                { move(thread_start_indexes, start, end); });
        }

        for (auto &t : threads)
        {
            t.join();
        }

        auto timer_end = high_resolution_clock::now();

        return duration_cast<milliseconds>(timer_end - timer_start).count();
    }

    void print_partitions() const
    {
        cout << "\n========= Partitioned Buffer =========\n\n";

        for (int p = 0; p < NUM_PARTITIONS; p++)
        {
            int start = partition_start_index[p];
            int count = total_elements_per_partition[p];

            cout << "Partition " << p
                 << " | Start: " << start
                 << " | Count: " << count << "\n";

            cout << "--------------------------------------\n";

            for (int i = 0; i < count; i++)
            {
                const auto &[key, value] = buffer[start + i];
                cout << "  [" << i << "] (" << key << ", " << value << ")\n";
            }

            cout << "\n";
        }

        cout << "======================================\n";
    }

private:
    TupleVector &tuples;
    const int NUM_THREADS;
    TupleVector buffer;
    const int NUM_PARTITIONS;
    vector<int> partition_start_index;
    vector<vector<int>> thread_partition_start_index;
    vector<int> total_elements_per_partition;

    void count(vector<int> &elements_in_partition, int start, int end)
    {
        for (int i = start; i < end; i++)
        {
            auto [key, _] = tuples[i];
            int partition = key % NUM_PARTITIONS;
            elements_in_partition[partition]++;
        }
    }

    void move(vector<int> &thread_partition_insert_index, int start, int end)
    {
        for (int i = start; i < end; i++)
        {
            auto [key, _] = tuples[i];
            int partition = key % NUM_PARTITIONS;
            int &partition_index = thread_partition_insert_index[partition];
            buffer[partition_index] = tuples[i];
            partition_index++;
        }
    }
};