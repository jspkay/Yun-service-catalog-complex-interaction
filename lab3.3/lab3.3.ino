#define INIT_BYTE 255
#define EXIT_BYTE 254
#define ESCP_BYTE 253


const int TEMP_PIN = A1;
//const int PIR_PIN = 6;
const int LED_PIN = 12;
const int INT_LED_PIN = 13;
const int B = 4275;
const long int R0 = 100000;

const String my_base_topic = "/tiot/0";

void serialSend(String msg){
  // Escaping the msg
  String escp_msg = "";
  for(char c : msg){
    if(c == EXIT_BYTE) escp_msg += (char) ESCP_BYTE;
    escp_msg += c;
  }
  msg = escp_msg;
  Serial.print("Serial writing... ");
  uint16_t l = msg.length(); // two bytes for the length
  Serial1.write(INIT_BYTE);
  Serial1.write(l & 0xFF00);
  Serial1.write(l & 0xFF);
  for(char c : msg){
     if(c == EXIT_BYTE) Serial1.write(ESCP_BYTE);
     Serial1.write(c);
  }
  Serial1.write(EXIT_BYTE);
  Serial.println("Done");
}

String serialReceive(){
  Serial.println("Receving serial...");
  uint8_t c;
  uint16_t len;
  byte b[100] = {0};
  uint8_t i = 0;

  if(Serial1.available() == 0){ 
    Serial.println("Nothing to read!");
    return "";
  }

  // First byte
  Serial1.readBytes(&c, 1);
  Serial.print("\tFirst byte: ");
  Serial.println((uint8_t)c);
  if(c != INIT_BYTE){
    Serial.println("Error! First byte is not 0xff");
    return "";
  }

  // 2 bytes for the length
  Serial1.readBytes((byte*)&len, 2);
  Serial.print("\tlen :");
  Serial.println(len);

  // actual message
  Serial1.readBytes(b, len);
  Serial.print("\tmessage: ");
  Serial.println((char*)b);

  // Last byte
  c = Serial1.read();
  Serial.print("\tLast Byte: ");
  Serial.println((uint8_t)c);
  if(c != EXIT_BYTE){
    Serial.println("Error! First byte is not 0xfe");
    return "";
  }
  Serial.println("Done!");

  // Escaping the message
  String msg = "";
  for(char c: b){
    if(c != ESCP_BYTE) msg += c;
  }

  Serial.print("escaped message: ");
  Serial.println(msg);
  return msg;
}

void process(String msg){
  if(msg == "") return;
  Serial.print("Processing command - ");
  int k = 0;
  String fields[5];
  for(int i=0; i<5; i++) fields[i] = String("");
  for(char c : msg){
    if(c != ':')
      fields[k] += c;
    else
      k++;
  }

  if(fields[0] == "L"){ // led processing
    uint8_t value = fields[1].toInt();
    if(value == 1){
      digitalWrite(LED_PIN, HIGH);
      Serial.println("Led going on!");
    }else if(value == 0){
      digitalWrite(LED_PIN, LOW);
      Serial.println("Led going off!");
    }
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println("Starting...");
  
  Serial1.begin(9600);
  Serial.println("Serial1 initialized!");
  
  pinMode(INT_LED_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(INT_LED_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(INT_LED_PIN, HIGH);
}

void loop() {
  String rec = serialReceive();
  process(rec);

  float secs = millis() / 1000.0;
  int a = analogRead(TEMP_PIN);
  float R = (1023.0/a-1.0)*R0;
  float temp = 1.0/(log(R/R0)/B+1/298.15)-273.15;
  char msg[100];
  sprintf(msg, "T:%s:%s", String(temp, 2).c_str(), "Cel");
  Serial.print("Temperature read. Sending ");
  Serial.println(msg);
  serialSend(msg);
  
  delay(2000);
}
