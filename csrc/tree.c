#include "tree.h"

#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define MAX_ENTRIES 1024
#define MAX_PATH_LEN 4096
#define DEFAULT_DEPTH 3
#define MAX_DEPTH 16

static int compare_names(const void *left, const void *right) {
    const char *const *first = left;
    const char *const *second = right;
    return strcmp(*first, *second);
}

static int is_directory(const char *path) {
    struct stat info;
    /* lstat keeps symlinks from being followed, avoiding cycles. */
    if (lstat(path, &info) != 0) {
        return 0;
    }
    return S_ISDIR(info.st_mode) != 0;
}

static void print_tree_level(const char *path, const char *prefix, int level,
                             int max_depth, int unicode, int *warnings) {
    DIR *dir = opendir(path);
    if (dir == NULL) {
        fprintf(stderr, "tree: cannot open %s: %s\n", path, strerror(errno));
        (*warnings)++;
        return;
    }

    char *names[MAX_ENTRIES];
    size_t count = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        if (count >= MAX_ENTRIES) {
            fprintf(stderr, "tree: %s has more than %d entries; remaining entries are hidden\n",
                    path, MAX_ENTRIES);
            (*warnings)++;
            break;
        }
        names[count] = strdup(entry->d_name);
        if (names[count] == NULL) {
            continue;
        }
        count++;
    }
    closedir(dir);
    qsort(names, count, sizeof(char *), compare_names);

    for (size_t index = 0; index < count; index++) {
        int last = (index + 1 == count);
        char child[MAX_PATH_LEN];
        if (snprintf(child, sizeof(child), "%s/%s", path, names[index]) >= (int)sizeof(child)) {
            fprintf(stderr, "tree: path too long: %s/%s\n", path, names[index]);
            (*warnings)++;
            free(names[index]);
            continue;
        }
        int directory = is_directory(child);
        const char *connector;
        const char *child_prefix;
        if (last) {
            connector = unicode ? "\u2514\u2500\u2500 " : "`-- ";
            child_prefix = "   ";
        } else {
            connector = unicode ? "\u251C\u2500\u2500 " : "|-- ";
            child_prefix = unicode ? "\u2502  " : "|  ";
        }
        printf("%s%s%s%s\n", prefix, connector, names[index], directory ? "/" : "");
        if (directory && level < max_depth) {
            char next_prefix[MAX_PATH_LEN];
            if (snprintf(next_prefix, sizeof(next_prefix), "%s%s", prefix, child_prefix)
                < (int)sizeof(next_prefix)) {
                print_tree_level(child, next_prefix, level + 1, max_depth, unicode, warnings);
            }
        }
        free(names[index]);
    }
}

int print_tree(const char *root, int max_depth) {
    struct stat info;
    if (lstat(root, &info) != 0) {
        perror(root);
        return 1;
    }
    if (!S_ISDIR(info.st_mode)) {
        printf("%s\n", root);
        return 0;
    }

    int warnings = 0;
    int unicode = isatty(1) ? 1 : 0;
    printf("%s\n", root);
    print_tree_level(root, "", 1, max_depth, unicode, &warnings);
    return 0;
}
