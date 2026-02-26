#ifndef INPUTGEN_HPP
#define INPUTGEN_HPP

#include "types.hpp"

class InputGen
{
public:
    TupleVector generateInput(int size);

private:
    uint64_t randomPayload();
};

#endif