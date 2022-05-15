# Arduino Yùn MQTT interaction with Service catalog

## General description
Since the ATMega 32U4 is not enough powerfull to handle an MQTT client, an HTTP client and a json parser all togheter, the simple choise was to put all the logic to the Atheros AR9331 and outsource the ATMega to the mere hardware control.

So the schema is something like this:

                  WLAN               serial               wires
 	Server <--------> Atheros <----------> ATMega <----------> Hardware

### Serial communication
In order to achieve a good serial communication (even though not a reliable one) it was necessary to introduce a little serial protocol which ensures the exchange of every format in burst of 0xFFFF bytes (given the peripheral buffer is large enough). 

   +------+------------+--- -- -- -- -- ---+------+
   | INIT |     LEN    |       MESSAGE     | EXIT |
   +------+------------+--- -- -- -- -- ---+------+


Where INIT and EXIT are particular bytes which denote the start and the end of the message:
```
INIT -> 255 (0xFF)
EXIT -> 254 (0xFE)
```
and LEN consists of 2 bytes which describe the length of MESSAGE in bytes. LEN might be in both network byte order and host byte order. In this implementation, indeed, the Atheros sends in network byte order, while the ATMega send in host byte order, just for convenience of code.

The last thing to say is that a special byte exist, which is the ESCP byte
```
ESCP -> 253 (0xFD)
```
This byte prevents the premature end of the trasmission. The ESCP byte is counted while computing the value of LEN.

## File description
```
.
|-- lab3.3  		Arduino sketch for the communication
|   `-- lab3.3.ino
|-- server		Service catalog file
|   |-- catalog.py
|   `-- serviceMQTT.py
`-- root		Files to be copied with scp over the Atheros
    |-- configure.sh
    |-- deviceMQTT.py
    |-- email6
    |-- paho
    |-- requests
    |-- serial
    `-- urllib3
```

The files inside `root/` are the necessary (modified) libraries (plus the software logic `deviceMQTT.py`) which need to be in the Atheros ROM. 
These files include:
 - a heavily modified requests library, in order to get the requests library on such a small rom
 - a modified urllib3, which tryied to import thread and dummythread instead of threading and dummy_threading

## Setup
To make the setup working just a few steps are needed:
 1. copy the root files to the Atheros (in the root directory) with `scp -r /path/to/root/* root@<Yun IP>:~/`
 2. (using ssh) execute the script `configure.sh` thourgh the command `./configure.sh`, it will install the necessary libraries, including python
 3. (using ssh) modify the HOST_NAME parameter of the file `deviceMQTT.py`, with the correct IP of the service catalog.

Then you need to upload the sketch to the ATMega (nothing fancy here)

Finally, you need to modify the parameters of the file catalog.py
 - HOSTNAME, which is the ip of the service catalog itself
 - SUBSCRIPTION, you need to put the correct parameters (i.e. if you want to use test.mosquitto.org)

At this point you'll only need to run everything.

A command can be sent to switch the led on and off:
```
$ mosquitto_pub -h <Service catalog IP> -t 'tiot/prova/catalog/devices/subscription/<DEVICE ID>/command' -m  '{"e":[{"n":"led", "v":0}]}' -p 1883
```


