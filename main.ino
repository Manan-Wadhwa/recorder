#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;
const int flexPins[5] = {A0, A1, A2, A3, A4};  // Flex sensor pins
int prevFlex[5] = {0}; // Store previous flex values

bool isStable(int flexValues[]) {
    for (int i = 0; i < 5; i++) {
        if (abs(flexValues[i] - prevFlex[i]) > 20) {  // Stability threshold
            return false;
        }
    }
    return true;
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
    
    if (!mpu.begin()) {
        Serial.println("MPU6050 not found!");
        while (1);
    }
}

void loop() {
    int flexValues[5];
    for (int i = 0; i < 5; i++) {
        flexValues[i] = analogRead(flexPins[i]);
    }

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    if (isStable(flexValues)) {
        Serial.print("FLEX,");
        for (int i = 0; i < 5; i++) {
            Serial.print(flexValues[i]);
            Serial.print(",");
            prevFlex[i] = flexValues[i];
        }
        
        Serial.print("GYRO,");
        Serial.print(g.gyro.x);
        Serial.print(",");
        Serial.print(g.gyro.y);
        Serial.print(",");
        Serial.println(g.gyro.z);

        delay(500);  // Avoid duplicate readings
    }
}
