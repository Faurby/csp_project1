#include "SetAffinity.hpp"
#include <iostream>

void SetAffinity::pinThreadsToCores(vector<thread>& threads, AffinityStrategy strategy)
{
    vector<int> core_ids;
    int n = threads.size();

    if (strategy == AffinityStrategy::Compact) {
        core_ids = cpu_ids_compact(n);
    } else if (strategy == AffinityStrategy::Scatter) {
        core_ids = cpu_ids_scatter(n);
    } else {
        return;
    }

    for (size_t i = 0; i < threads.size(); ++i) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(core_ids[i], &cpuset);
        int rc = pthread_setaffinity_np(threads[i].native_handle(), sizeof(cpu_set_t), &cpuset);
        if (rc != 0) {
            cerr << "Error calling pthread_setaffinity_np for thread " << i << ": " << rc << endl;
        }
    }
}

vector<int> SetAffinity::cpu_ids_scatter(int n)
{
    int total_cores = thread::hardware_concurrency();
    vector<int> cpu_ids;
    for (int i = 0; i < n; i++)
        cpu_ids.push_back(i % total_cores);
    return cpu_ids;
}

vector<int> SetAffinity::cpu_ids_compact(int n)
{
    int total_cores = thread::hardware_concurrency();
    int physical_cores = total_cores / 2; // assumes hyperthreading
    vector<int> cpu_ids;
    for (int i = 0; i < n; i++) {
        if (i % 2 == 0)
            cpu_ids.push_back((i / 2) % physical_cores);
        else
            cpu_ids.push_back((i / 2) % physical_cores + physical_cores);
    }
    return cpu_ids;
}
