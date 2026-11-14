#include "disk.h"

#include <stdio.h>
#include <sys/statvfs.h>

int print_disk_free(void) {
    struct statvfs stats;
    if (statvfs(".", &stats) != 0) {
        perror("statvfs");
        return 1;
    }

    unsigned long long block = (unsigned long long)stats.f_frsize;
    unsigned long long total = (unsigned long long)stats.f_blocks * block;
    unsigned long long available = (unsigned long long)stats.f_bavail * block;
    unsigned long long used = total - ((unsigned long long)stats.f_bfree * block);

    puts("Native disk usage (current directory)");
    printf("  Total:     %llu bytes\n", total);
    printf("  Used:      %llu bytes\n", used);
    printf("  Available: %llu bytes\n", available);
    return 0;
}
