#include <stdio.h>
#include "my_import.h"

int main() {
    int x;
    x = 0;
    if (x < 10) x = x + 1;

    while (x < 5) {
    x = x + 1;
    }

    for (x = 0; x < 3; x = x + 1) {
    int y;
    y = x * 2;
    }
    return 0;
}