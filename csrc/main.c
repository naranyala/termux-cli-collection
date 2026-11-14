#include "disk.h"

#include <stdio.h>
#include <string.h>

#define VERSION "0.2.0"

static void print_help(const char *program) {
    printf("Usage: %s [disk-free | --version | --help]\n", program);
}

int main(int argc, char **argv) {
    const char *command = argc > 1 ? argv[1] : "disk-free";

    if (argc > 2) {
        fprintf(stderr, "Unexpected argument: %s\n", argv[2]);
        return 2;
    }
    if (strcmp(command, "--help") == 0 || strcmp(command, "-h") == 0) {
        print_help(argv[0]);
        return 0;
    }
    if (strcmp(command, "--version") == 0 || strcmp(command, "-v") == 0) {
        puts(VERSION);
        return 0;
    }
    if (strcmp(command, "disk-free") == 0) {
        return print_disk_free();
    }

    fprintf(stderr, "Unknown action: %s\n", command);
    print_help(argv[0]);
    return 2;
}
