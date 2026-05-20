#pragma once

#include <pthread.h>
#include <sched.h>
#include <thread>
#include <vector>

using namespace std;

enum class AffinityStrategy {
    Compact,
    Scatter,
    None
};

class SetAffinity
{
public:
    static void pinThreadsToCores(
        vector<thread>& threads,
        AffinityStrategy strategy);

private:
    static vector<int> cpu_ids_scatter(int n);
    static vector<int> cpu_ids_compact(int n);
};
