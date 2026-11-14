#include "disk.h"
#include "system.h"

#include <stdio.h>
#include <string.h>

#define VERSION "0.2.0"

static void print_help(const char *program) {
    printf("Usage: %s [disk-free | mem-info | line-count FILE | --version | --help]\n", program);
}

int main(int argc, char **argv) {
    const char *command = argc > 1 ? argv[1] : "disk-free";

    if (strcmp(command, "--help") == 0 || strcmp(command, "-h") == 0) {
        if (argc > 2) {
            fprintf(stderr, "Unexpected argument: %s\n", argv[2]);
            return 2;
        }
        print_help(argv[0]);
        return 0;
    }
    if (strcmp(command, "--version") == 0 || strcmp(command, "-v") == 0) {
        if (argc > 2) {
            fprintf(stderr, "Unexpected argument: %s\n", argv[2]);
            return 2;
        }
        puts(VERSION);
        return 0;
    }
    if (strcmp(command, "disk-free") == 0 && argc == 2) {
        return print_disk_free();
    }
    if (strcmp(command, "mem-info") == 0 && argc == 2) {
        return print_memory_info();
    }
    if (strcmp(command, "line-count") == 0 && argc == 3) {
        return print_line_count(argv[2]);
    }

    fprintf(stderr, "Invalid native action or arguments.\n");
    print_help(argv[0]);
    return 2;
}
