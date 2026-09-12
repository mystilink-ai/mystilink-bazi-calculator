#ifndef MYSTILINK_BAZI_H
#define MYSTILINK_BAZI_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Run mystilink-bazi with argc/argv-style arguments (excluding program name).
 * On success, returns a heap-allocated JSON string (caller must free with
 * mystilink_bazi_free). On failure, returns NULL and optionally writes an
 * error message into errbuf (if errbuf and errbuf_len are provided).
 *
 * CLI path: environment MYSTILINK_BAZI_CLI, else "mystilink-bazi".
 */
char *mystilink_bazi_run(int argc, const char *const *argv, char *errbuf, int errbuf_len);

/** Convenience: calculate --date ... [--hour ...] [--minute ...] */
char *mystilink_bazi_calculate(
    const char *date_yyyy_mm_dd,
    int hour,
    int minute,
    const char *timezone_or_null,
    double longitude,
    int use_longitude,
    char *errbuf,
    int errbuf_len
);

/** Convenience: dayun --date ... --gender ... [--count ...] */
char *mystilink_bazi_dayun(
    const char *date_yyyy_mm_dd,
    const char *gender,
    int count,
    char *errbuf,
    int errbuf_len
);

/** Convenience: liunian --year ... */
char *mystilink_bazi_liunian(
    int year,
    const char *day_stem_or_null,
    const char *pillars_json_or_null,
    char *errbuf,
    int errbuf_len
);

/** Free a string returned by the API. */
void mystilink_bazi_free(char *p);

#ifdef __cplusplus
}
#endif

#endif /* MYSTILINK_BAZI_H */
