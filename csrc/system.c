#include "system.h"

#include <stdio.h>
#include <string.h>

int print_memory_info(void) {
    FILE *file = fopen("/proc/meminfo", "r");
    char line[256];
    if (file == NULL) {
        perror("/proc/meminfo");
        return 1;
    }

    puts("Memory information");
    while (fgets(line, sizeof(line), file) != NULL) {
        if (strncmp(line, "MemTotal:", 9) == 0 ||
            strncmp(line, "MemAvailable:", 13) == 0 ||
            strncmp(line, "MemFree:", 8) == 0 ||
            strncmp(line, "SwapTotal:", 10) == 0 ||
            strncmp(line, "SwapFree:", 9) == 0) {
            fputs("  ", stdout);
            fputs(line, stdout);
        }
    }
    fclose(file);
    return 0;
}

int print_line_count(const char *path) {
    FILE *file = fopen(path, "rb");
    unsigned long long bytes = 0;
    unsigned long long lines = 0;
    int character;

    if (file == NULL) {
        perror(path);
        return 1;
    }
    while ((character = fgetc(file)) != EOF) {
        bytes++;
        if (character == '\n') {
            lines++;
        }
    }
    if (ferror(file)) {
        perror(path);
        fclose(file);
        return 1;
    }
    fclose(file);
    printf("%s: %llu lines, %llu bytes\n", path, lines, bytes);
    return 0;
}
