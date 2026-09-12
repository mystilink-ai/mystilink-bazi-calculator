#include <stdio.h>
#include <stdlib.h>

#include "../../bindings/c/mystilink_bazi.h"

int main(void) {
    char err[512];
    err[0] = '\0';
    char *json = mystilink_bazi_calculate("1990-05-15", 12, 0, NULL, 0.0, 0, err, sizeof(err));
    if (!json) {
        fprintf(stderr, "error: %s\n", err);
        return 1;
    }
    fputs(json, stdout);
    fputc('\n', stdout);
    mystilink_bazi_free(json);
    return 0;
}
