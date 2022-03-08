# [Raspberry Pi RFID Project](https://github.com/Rodney-Smith/rc522-mqtt)

Raspberry Pi RFID Reader to MQTT[](https://github.com/ondryaso/pi-rc522)

## Connect RFID-RC522 to the Raspberry Pi
Connecting RC522 module to SPI is pretty easy. You can use [this neat website](http://pi.gadgetoid.com/pinout) for reference.

| Board pin name | Board pin | Physical RPi pin | RPi pin name | Beaglebone Black pin name |
|----------------|-----------|------------------|--------------| --------------------------|
| SDA            | 1         | 24               | GPIO8, CE0   | P9\_17, SPI0\_CS0         |
| SCK            | 2         | 23               | GPIO11, SCKL | P9\_22, SPI0\_SCLK        |
| MOSI           | 3         | 19               | GPIO10, MOSI | P9\_18, SPI0\_D1          |
| MISO           | 4         | 21               | GPIO9, MISO  | P9\_21, SPI0\_D0          |
| IRQ            | 5         | 18               | GPIO24       | P9\_15, GPIO\_48          |
| GND            | 6         | 6, 9, 20, 25     | Ground       | Ground                    |
| RST            | 7         | 22               | GPIO25       | P9\_23, GPIO\_49          |
| 3.3V           | 8         | 1,17             | 3V3          | VDD\_3V3                  |

```
sudo mkdir /opt/scripts
sudo chown pi:root /opt/scripts
cd /opt/scripts
git clone https://github.com/Rodney-Smith/rc522-mqtt.git
```

## Install dependencies
```
sudo apt-get update && sudo apt-get install -y build-essential git python3-dev python3-pip python3-smbus python3-libgpiod python3-pil python3-setuptools
sudo pip3 install -r requirements.txt
```

## config.json
```
cd /opt/scripts/rc522-mqtt
mv config.example.json config.json
nano config.json
{
    "mqtt": {
        "clientid":"unique-id",
        "topic":"rc522",
        "event_topic":"rc522/events",
        "status_topic":"rc522/status",
        "broker":"mqttbroker.local",
        "port":1883,
        "user":"mqttusername",
        "password":"mqttpassword"
    }
}
```

## Enable and start the service
```
sudo cp /opt/scripts/rc522-mqtt/rc522-daemon.service /etc/systemd/system/rc522-daemon.service
sudo systemctl daemon-reload
sudo systemctl enable rc522-daemon.service
sudo systemctl start rc522-daemon.service
systemctl status rc522-daemon.service
```
