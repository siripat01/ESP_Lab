#include "BluetoothSerial.h"
#include "Wire.h"
#include "SHT2x.h"

BluetoothSerial SerialBT;
SHT2x sht;

void setup() {
  Serial.begin(115200);

  if (!btStart()) {
    Serial.println("BT failed");
    while (1)
      ;
  }

  SerialBT.begin("ESP32_Son");

  Wire.begin(21, 22);
  sht.begin();

  Serial.println("Bluetooth Started");
}

void loop() {
  sht.read();

  uint32_t timestamp = millis();
  float temp = sht.getTemperature();
  float hum = sht.getHumidity();

  // ส่งข้อมูล format เดิม
  SerialBT.print(timestamp);
  SerialBT.print(" ");
  SerialBT.print(temp, 1);
  SerialBT.print(" ");
  SerialBT.println(hum, 1);

  Serial.print("\t");
  Serial.print(timestamp);
  Serial.print("\t");
  Serial.print(temp, 1);
  Serial.print("\t");
  Serial.println(hum, 1);

  delay(1000);
}
