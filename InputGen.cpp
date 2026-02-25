#include <vector>
#include <cstdint>
#include <cstdlib>
#include <utility>
#include <algorithm>
#include <random>
#include <iostream>
#include "types.hpp"

using namespace std;
auto rng = std::default_random_engine();

class InputGen
{
public:
    TupleVector generateInput(int size)
    {
        TupleVector result(size);
        for (uint64_t i = 0; i < size; i++)
        {
            auto payload = randomPayload();
            result[i] = make_pair(i, payload);
        }
        shuffle(result.begin(), result.end(), rng);
        return result;
    }

private:
    uint64_t randomPayload()
    {
        return ((uint64_t)rand() << 32) | rand();
    }
};