/* Host-only CRC/framing tests; not a hardware or ESP-IDF build. */
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "telemetry_wire.h"
int main(void) {
    const uint8_t co2[] = {0x01, 0xf4};
    const uint8_t status[] = {0x80, 0x00};
    assert(scd_crc8(co2, sizeof co2) == 0x7b);
    assert(scd_crc8(status, sizeof status) == 0xa2);
    char line[128];
    size_t n = iotcsv_format(line, sizeof line, "abcd", "BH1750",
                              2, 123456, 42.5, "lux");
    assert(n == strlen("IOTCSV,abcd,BH1750,2,123456,42.50,lux,1\n"));
    assert(strcmp(line, "IOTCSV,abcd,BH1750,2,123456,42.50,lux,1\n") == 0);
    assert(iotcsv_format(line, 8, "abcd", "SCD40", 1, 10, 500, "ppm") == 0);
    return 0;
}
