#include <stdio.h>

int main() {
    int n = 5;
    float f;
    char c = 'A';
    char *p = "Hola";
    char s[] = "Mundo";

    printf("n=%d, c=%c, s=%s\n", n, c, s);
    printf("literal: %s", "ok");
    printf("%d + %d = %d", 2, 3, 2+3);

    return 0;
}
