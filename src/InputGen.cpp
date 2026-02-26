#include "InputGen.hpp"
#include <algorithm>
#include <random>
#include <cstdlib>

static std::default_random_engine rng;

TupleVector InputGen::generateInput(int size)
{
    TupleVector result(size);
    for (int i = 0; i < size; i++)
    {
        result[i] = {i, randomPayload()};
    }

    std::shuffle(result.begin(), result.end(), rng);
    return result;
}

uint64_t InputGen::randomPayload()
{
    return ((uint64_t)rand() << 32) | rand();
}