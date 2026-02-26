#ifndef CONCURRENT_HPP
#define CONCURRENT_HPP

#include "types.hpp"
#include <vector>
#include <atomic>

class Concurrent
{
public:
    Concurrent(TupleVector& tuples, int num_partitions, int num_threads);

    void create_threads();
    void print_partitions() const;

private:
    TupleVector& tuples;
    std::vector<TupleVector> partitions;
    std::vector<std::atomic_int> partition_lastIndexes;
    const int NUM_THREADS;

    void hashing_and_insert(int start, int end);
};

#endif