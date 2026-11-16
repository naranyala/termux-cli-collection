#include "disk.h"
#include "system.h"
#include "tree.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define VERSION "0.2.0"
#define MAX_DEPTH 16

static void print_help(const char *program) {
    printf("Usage: %s [disk-free | mem-info | line-count FILE | tree [PATH] [--depth N] | --version | --help]\n", program);
}

static int run_tree(int argc, char **argv) {
    const char *path = ".";
    int depth = 3;
    for (int index = 2; index < argc; index++) {
        if (strcmp(argv[index], "--depth") == 0) {
            if (index + 1 >= argc) {
                fprintf(stderr, "tree: --depth requires a value.\n");
                return 2;
            }
            depth = atoi(argv[++index]);
            if (depth < 1 || depth > MAX_DEPTH) {
                fprintf(stderr, "tree: depth must be between 1 and %d.\n", MAX_DEPTH);
                return 2;
            }
        } else if (argv[index][0] != '-') {
            path = argv[index];
        } else {
            fprintf(stderr, "tree: unknown option: %s\n", argv[index]);
            return 2;
        }
    }
    return print_tree(path, depth);
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
    if (strcmp(command, "tree") == 0) {
        return run_tree(argc, argv);
    }

    fprintf(stderr, "Invalid native action or arguments.\n");
    print_help(argv[0]);
    return 2;
}
