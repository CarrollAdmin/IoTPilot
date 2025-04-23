#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

// MMA8452Q I2C 地址
#define MMA8452Q_ADDRESS 0x1D

// 寄存器地址
#define REG_CTRL_REG1 0x2A
#define REG_XYZ_DATA_CFG 0x0E
#define REG_OUT_X_MSB 0x01

// 初始化 MMA8452Q
void initMMA8452Q(int file) {
    // 将 MMA8452Q 设置为待机模式
    i2c_smbus_write_byte_data(file, REG_CTRL_REG1, 0x00);
    // 设置量程（例如 +/- 2g）
    i2c_smbus_write_byte_data(file, REG_XYZ_DATA_CFG, 0x00);
    // 激活 MMA8452Q
    i2c_smbus_write_byte_data(file, REG_CTRL_REG1, 0x01);
}

// 读取加速度
void readAcceleration(int file, int *x, int *y, int *z) {
    int rawX = (i2c_smbus_read_byte_data(file, REG_OUT_X_MSB) << 8) | i2c_smbus_read_byte_data(file, REG_OUT_X_MSB + 1);
    int rawY = (i2c_smbus_read_byte_data(file, REG_OUT_X_MSB + 2) << 8) | i2c_smbus_read_byte_data(file, REG_OUT_X_MSB + 3);
    int rawZ = (i2c_smbus_read_byte_data(file, REG_OUT_X_MSB + 4) << 8) | i2c_smbus_read_byte_data(file, REG_OUT_X_MSB + 5);

    // 处理 12 位数据
    *x = (rawX >> 4);
    *y = (rawY >> 4);
    *z = (rawZ >> 4);

    // 如果值大于 2047，则表示负值，需要处理
    if (*x > 2047) *x -= 4096;
    if (*y > 2047) *y -= 4096;
    if (*z > 2047) *z -= 4096;
}

int main(void) {
    int file;
    char *filename = "/dev/i2c-1"; // 对于大多数树莓派设备

    // 打开 I2C 设备
    if ((file = open(filename, O_RDWR)) < 0) {
        perror("Failed to open the i2c bus");
        return 1;
    }

    // 与 MMA8452Q 通信
    if (ioctl(file, I2C_SLAVE, MMA8452Q_ADDRESS) < 0) {
        perror("Failed to acquire bus access and/or talk to slave");
        return 1;
    }

    // 初始化 MMA8452Q
    initMMA8452Q(file);

    int x, y, z;
    while (1) {
        // 读取加速度数据
        readAcceleration(file, &x, &y, &z);

        // 打印加速度数据
        printf("X: %d, Y: %d, Z: %d\n", x, y, z);

        // 延迟 500ms
        usleep(500000);
    }

    close(file);
    return 0;
}
