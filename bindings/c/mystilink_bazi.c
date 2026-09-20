#include "mystilink_bazi.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#define POPEN _popen
#define PCLOSE _pclose
#else
#define POPEN popen
#define PCLOSE pclose
#endif

static const char *cli_path(void) {
    const char *env = getenv("MYSTILINK_BAZI_CLI");
    return (env && env[0]) ? env : "bazi";
}

static void set_err(char *errbuf, int errbuf_len, const char *msg) {
    if (!errbuf || errbuf_len <= 0) {
        return;
    }
    snprintf(errbuf, (size_t)errbuf_len, "%s", msg ? msg : "unknown error");
}

static char *read_all(FILE *fp) {
    size_t cap = 4096;
    size_t len = 0;
    char *buf = (char *)malloc(cap);
    if (!buf) {
        return NULL;
    }
    for (;;) {
        if (len + 1024 >= cap) {
            cap *= 2;
            char *nbuf = (char *)realloc(buf, cap);
            if (!nbuf) {
                free(buf);
                return NULL;
            }
            buf = nbuf;
        }
        size_t n = fread(buf + len, 1, 1024, fp);
        len += n;
        if (n < 1024) {
            break;
        }
    }
    buf[len] = '\0';
    return buf;
}

static char *shell_quote(const char *s) {
    /* Simple single-quote wrapping for POSIX shells. */
    size_t len = strlen(s);
    /* worst case: every char is ' -> '\'' */
    char *out = (char *)malloc(len * 4 + 3);
    if (!out) {
        return NULL;
    }
    char *p = out;
    *p++ = '\'';
    for (size_t i = 0; i < len; i++) {
        if (s[i] == '\'') {
            memcpy(p, "'\\''", 4);
            p += 4;
        } else {
            *p++ = s[i];
        }
    }
    *p++ = '\'';
    *p = '\0';
    return out;
}

char *mystilink_bazi_run(int argc, const char *const *argv, char *errbuf, int errbuf_len) {
    if (argc < 1 || !argv) {
        set_err(errbuf, errbuf_len, "no arguments");
        return NULL;
    }

    size_t cmd_cap = 256;
    char *cmd = (char *)malloc(cmd_cap);
    if (!cmd) {
        set_err(errbuf, errbuf_len, "out of memory");
        return NULL;
    }
    cmd[0] = '\0';

    const char *cli = cli_path();
    char *qcli = shell_quote(cli);
    if (!qcli) {
        free(cmd);
        set_err(errbuf, errbuf_len, "out of memory");
        return NULL;
    }
    snprintf(cmd, cmd_cap, "%s", qcli);
    free(qcli);

    for (int i = 0; i < argc; i++) {
        char *qa = shell_quote(argv[i]);
        if (!qa) {
            free(cmd);
            set_err(errbuf, errbuf_len, "out of memory");
            return NULL;
        }
        size_t need = strlen(cmd) + 1 + strlen(qa) + 1;
        if (need > cmd_cap) {
            while (cmd_cap < need) {
                cmd_cap *= 2;
            }
            char *ncmd = (char *)realloc(cmd, cmd_cap);
            if (!ncmd) {
                free(qa);
                free(cmd);
                set_err(errbuf, errbuf_len, "out of memory");
                return NULL;
            }
            cmd = ncmd;
        }
        strcat(cmd, " ");
        strcat(cmd, qa);
        free(qa);
    }

    /* Redirect stderr to stdout so callers see errors in the buffer when needed.
       Prefer capturing stdout only for success JSON. */
    {
        size_t need = strlen(cmd) + 16;
        if (need > cmd_cap) {
            char *ncmd = (char *)realloc(cmd, need);
            if (!ncmd) {
                free(cmd);
                set_err(errbuf, errbuf_len, "out of memory");
                return NULL;
            }
            cmd = ncmd;
            cmd_cap = need;
        }
        strcat(cmd, " 2>/dev/null");
    }

    FILE *fp = POPEN(cmd, "r");
    free(cmd);
    if (!fp) {
        set_err(errbuf, errbuf_len, "failed to start bazi");
        return NULL;
    }

    char *out = read_all(fp);
    int status = PCLOSE(fp);
    if (!out) {
        set_err(errbuf, errbuf_len, "failed to read CLI output");
        return NULL;
    }
    if (status != 0) {
        set_err(errbuf, errbuf_len, out[0] ? out : "bazi failed");
        free(out);
        return NULL;
    }
    return out;
}

char *mystilink_bazi_calculate(
    const char *date_yyyy_mm_dd,
    int hour,
    int minute,
    const char *timezone_or_null,
    double longitude,
    int use_longitude,
    char *errbuf,
    int errbuf_len
) {
    char hour_buf[16];
    char minute_buf[16];
    char lon_buf[64];
    snprintf(hour_buf, sizeof(hour_buf), "%d", hour);
    snprintf(minute_buf, sizeof(minute_buf), "%d", minute);

    const char *argv_store[12];
    int n = 0;
    argv_store[n++] = "calculate";
    argv_store[n++] = "--date";
    argv_store[n++] = date_yyyy_mm_dd;
    argv_store[n++] = "--hour";
    argv_store[n++] = hour_buf;
    argv_store[n++] = "--minute";
    argv_store[n++] = minute_buf;
    if (timezone_or_null && timezone_or_null[0] && use_longitude) {
        snprintf(lon_buf, sizeof(lon_buf), "%.6f", longitude);
        argv_store[n++] = "--timezone";
        argv_store[n++] = timezone_or_null;
        argv_store[n++] = "--longitude";
        argv_store[n++] = lon_buf;
    }
    return mystilink_bazi_run(n, argv_store, errbuf, errbuf_len);
}

char *mystilink_bazi_dayun(
    const char *date_yyyy_mm_dd,
    const char *gender,
    int count,
    char *errbuf,
    int errbuf_len
) {
    char count_buf[16];
    snprintf(count_buf, sizeof(count_buf), "%d", count);
    const char *argv_store[8];
    int n = 0;
    argv_store[n++] = "dayun";
    argv_store[n++] = "--date";
    argv_store[n++] = date_yyyy_mm_dd;
    argv_store[n++] = "--gender";
    argv_store[n++] = gender;
    argv_store[n++] = "--count";
    argv_store[n++] = count_buf;
    return mystilink_bazi_run(n, argv_store, errbuf, errbuf_len);
}

char *mystilink_bazi_liunian(
    int year,
    const char *day_stem_or_null,
    const char *pillars_json_or_null,
    char *errbuf,
    int errbuf_len
) {
    char year_buf[16];
    snprintf(year_buf, sizeof(year_buf), "%d", year);
    const char *argv_store[8];
    int n = 0;
    argv_store[n++] = "liunian";
    argv_store[n++] = "--year";
    argv_store[n++] = year_buf;
    if (day_stem_or_null && day_stem_or_null[0]) {
        argv_store[n++] = "--day-stem";
        argv_store[n++] = day_stem_or_null;
    }
    if (pillars_json_or_null && pillars_json_or_null[0]) {
        argv_store[n++] = "--pillars-json";
        argv_store[n++] = pillars_json_or_null;
    }
    return mystilink_bazi_run(n, argv_store, errbuf, errbuf_len);
}

void mystilink_bazi_free(char *p) {
    free(p);
}
