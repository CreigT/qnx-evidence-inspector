/* MIT License. QNX OS 8.0 wake-up timing capture; no elevated privileges. */
#include <sys/neutrino.h>
#include <sys/utsname.h>
#include <time.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#if !defined(__QNXNTO__) || !defined(_NTO_VERSION) || _NTO_VERSION < 800 || _NTO_VERSION >= 810
#error "This probe requires QNX SDP 8.0 target headers"
#endif
#define SAMPLES 1000
#define PERIOD_NS UINT64_C(10000000)

/* Escape all strings even though uname fields normally contain plain ASCII. */
static void json_string(const char *s) {
    putchar('"');
    for (; *s; ++s) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') { putchar('\\'); putchar(c); }
        else if (c < 32 || c >= 127) printf("\\u%04x", (unsigned)c);
        else putchar(c);
    }
    putchar('"');
}
int main(void) {
    struct utsname u;
    struct _clockperiod cp = {0};
    uint64_t scheduled[SAMPLES], actual[SAMPLES];
    if (uname(&u) == -1 || ClockPeriod(CLOCK_MONOTONIC, NULL, &cp, 0) == -1) {
        perror("QNX metadata"); return 1;
    }
    if (strcmp(u.sysname, "QNX") != 0 || strncmp(u.release, "8.0", 3) != 0) {
        fprintf(stderr, "QNX OS 8.0 required\n"); return 1;
    }
    uint64_t next = clock_gettime_mon_ns();
    for (int i = 0; i < SAMPLES; ++i) {
        next += PERIOD_NS;
        struct timespec wake = { .tv_sec = (time_t)(next / UINT64_C(1000000000)),
                                 .tv_nsec = (long)(next % UINT64_C(1000000000)) };
        int rc;
        do { rc = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &wake, NULL); } while (rc == EINTR);
        if (rc != 0) { fprintf(stderr, "clock_nanosleep: %s\n", strerror(rc)); return 1; }
        scheduled[i] = next;
        actual[i] = clock_gettime_mon_ns();
    }
    printf("{\"schema\":\"qnx-probe-v1\",\"sysname\":"); json_string(u.sysname);
    printf(",\"release\":"); json_string(u.release);
    printf(",\"machine\":"); json_string(u.machine);
    printf(",\"clock_api\":\"clock_gettime_mon_ns\",\"clock_period_ns\":%" PRIu32
           ",\"period_ns\":%" PRIu64 ",\"samples\":%d}\n", cp.nsec, PERIOD_NS, SAMPLES);
    puts("sample,scheduled_ns,actual_ns");
    for (int i = 0; i < SAMPLES; ++i)
        printf("%d,%" PRIu64 ",%" PRIu64 "\n", i, scheduled[i], actual[i]);
    return ferror(stdout) ? 1 : 0;
}
