#include <iostream>
#include "InputGen.cpp"

int main(int argc, char *argv[])
{
    auto inputgen = InputGen();
    auto random = inputgen.generateInput(100);
    cout << "Generated " << random.size() << " random pairs:" << endl;
    for (const auto &pair : random)
    {
        cout << "ID: " << pair.first << ", Payload: " << pair.second << endl;
    }
}