/* Portable framing and Sensirion CRC; no device authentication. */
#ifndef IOT_TELEMETRY_WIRE_H
#define IOT_TELEMETRY_WIRE_H
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

static inline uint8_t scd_crc8(const uint8_t *bytes, size_t len) {
    uint8_t crc = 0xff;
    for (size_t i = 0; i < len; ++i) {
        crc ^= bytes[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            if (crc & 0x80u) crc = (uint8_t)((crc << 1) ^ 0x31u);
            else crc = (uint8_t)(crc << 1);
        }
    }
    return crc;
}

/* Only call with fixed sensor/unit labels and a generated boot identifier.
   Returns 0 on truncation; never emits an incomplete telemetry row. */
static inline size_t iotcsv_format(char *out, size_t capacity,
                                   const char *boot, const char *sensor,
                                   uint32_t seq, uint64_t elapsed_ms,
                                   double value, const char *unit) {
    if (!out || !capacity || !boot || !sensor || !unit) return 0;
    int n = snprintf(out, capacity,
                     "IOTCSV,%s,%s,%u,%llu,%.2f,%s,1\n",
                     boot, sensor, (unsigned)seq,
                     (unsigned long long)elapsed_ms, value, unit);
    return n > 0 && (size_t)n < capacity ? (size_t)n : 0;
}
#endif
