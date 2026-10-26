/* Candidate ESP-IDF 6.x ESP32-S3 logger for the PR #7 capture contract.
   NOT built/flashed on physical hardware in this research run.
   SDA GPIO8, SCL GPIO9, BH1750 0x23, SCD40 0x62, 100 kHz I2C.
   Emits only newly ready sensor samples; failures are logged, not imputed. */
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "driver/i2c_master.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_random.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "telemetry_wire.h"

#define SDA_GPIO 8
#define SCL_GPIO 9
#define BH1750_ADDR 0x23
#define SCD40_ADDR 0x62
#define I2C_TIMEOUT_MS 1000
static const char *TAG = "dual_sensor_capture";

static esp_err_t scd_cmd(i2c_master_dev_handle_t dev, uint16_t command) {
    uint8_t b[2] = {(uint8_t)(command >> 8), (uint8_t)command};
    return i2c_master_transmit(dev, b, sizeof b, I2C_TIMEOUT_MS);
}
static esp_err_t scd_read(i2c_master_dev_handle_t dev, uint16_t command,
                          uint8_t *result, size_t len) {
    esp_err_t err = scd_cmd(dev, command);
    if (err != ESP_OK) return err;
    vTaskDelay(pdMS_TO_TICKS(2));  /* datasheet command processing >=1 ms */
    return i2c_master_receive(dev, result, len, I2C_TIMEOUT_MS);
}
static bool scd_word_crc(const uint8_t *bytes) {
    return scd_crc8(bytes, 2) == bytes[2];
}
static void emit(const char *boot, const char *sensor, uint32_t seq,
                 uint64_t elapsed_ms, double value, const char *unit) {
    char line[128];
    if (!iotcsv_format(line, sizeof line, boot, sensor, seq, elapsed_ms, value, unit)) {
        ESP_LOGE(TAG, "telemetry formatting failure");
        return;
    }
    fputs(line, stdout);
    fflush(stdout);
}

void app_main(void) {
    i2c_master_bus_config_t bus_cfg = {
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .i2c_port = I2C_NUM_0,
        .sda_io_num = SDA_GPIO,
        .scl_io_num = SCL_GPIO,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    i2c_master_bus_handle_t bus;
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_cfg, &bus));
    i2c_device_config_t bh_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = BH1750_ADDR, .scl_speed_hz = 100000,
    };
    i2c_device_config_t scd_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = SCD40_ADDR, .scl_speed_hz = 100000,
    };
    i2c_master_dev_handle_t bh, scd;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &bh_cfg, &bh));
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &scd_cfg, &scd));
    ESP_ERROR_CHECK(i2c_master_probe(bus, BH1750_ADDR, I2C_TIMEOUT_MS));
    ESP_ERROR_CHECK(i2c_master_probe(bus, SCD40_ADDR, I2C_TIMEOUT_MS));

    /* No Wi-Fi, credentials, identity strings or network transmission. */
    char boot[17];
    snprintf(boot, sizeof boot, "%08" PRIx32 "%08" PRIx32, esp_random(), esp_random());
    uint8_t bh_on = 0x01, bh_mode = 0x10; /* power on; continuous high-res */
    ESP_ERROR_CHECK(i2c_master_transmit(bh, &bh_on, 1, I2C_TIMEOUT_MS));
    ESP_ERROR_CHECK(i2c_master_transmit(bh, &bh_mode, 1, I2C_TIMEOUT_MS));

    /* Clear any previously running SCD40 periodic session. A failed stop is
       logged; start must still succeed or the run aborts. */
    esp_err_t stop = scd_cmd(scd, 0x3f86);
    if (stop != ESP_OK) ESP_LOGW(TAG, "SCD40 stop command failed: %s", esp_err_to_name(stop));
    vTaskDelay(pdMS_TO_TICKS(500));
    ESP_ERROR_CHECK(scd_cmd(scd, 0x21b1)); /* normal 5-second periodic mode */

    uint32_t bh_seq = 0, scd_seq = 0;
    int64_t started_us = esp_timer_get_time();
    /* First BH1750 conversion requires settling; first SCD40 result ~5 s. */
    vTaskDelay(pdMS_TO_TICKS(200));
    while (true) {
        uint64_t elapsed_ms = (uint64_t)((esp_timer_get_time() - started_us) / 1000);
        uint8_t lux_bytes[2];
        if (i2c_master_receive(bh, lux_bytes, sizeof lux_bytes, I2C_TIMEOUT_MS) == ESP_OK) {
            uint16_t raw = ((uint16_t)lux_bytes[0] << 8) | lux_bytes[1];
            emit(boot, "BH1750", bh_seq++, elapsed_ms, (double)raw / 1.2, "lux");
        } else {
            ESP_LOGW(TAG, "BH1750 read failed; missing sample is not filled");
        }

        uint8_t ready[3];
        if (scd_read(scd, 0xe4b8, ready, sizeof ready) == ESP_OK && scd_word_crc(ready)) {
            uint16_t status = ((uint16_t)ready[0] << 8) | ready[1];
            if ((status & 0x07ffu) != 0u) {
                uint8_t data[9];
                if (scd_read(scd, 0xec05, data, sizeof data) == ESP_OK &&
                    scd_word_crc(data) && scd_word_crc(data + 3) && scd_word_crc(data + 6)) {
                    uint16_t ppm = ((uint16_t)data[0] << 8) | data[1];
                    /* Timestamp after read, not when measurement was internally taken. */
                    elapsed_ms = (uint64_t)((esp_timer_get_time() - started_us) / 1000);
                    emit(boot, "SCD40", scd_seq++, elapsed_ms, (double)ppm, "ppm");
                } else {
                    ESP_LOGW(TAG, "SCD40 read/CRC failure; no value emitted");
                }
            }
        } else {
            ESP_LOGW(TAG, "SCD40 readiness/CRC failure; no value emitted");
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
