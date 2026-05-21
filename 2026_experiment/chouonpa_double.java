const int trigPinR = 6;
const int echoPinR = 7;
const int trigPinL = 8;
const int echoPinL = 9;

long cm_r, cm_l;

void setup() {
  Serial.begin(9600);
  pinMode(trigPinR, OUTPUT);
  pinMode(echoPinR, INPUT);
  pinMode(trigPinL, OUTPUT);
  pinMode(echoPinL, INPUT);
}

long readCm(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  return (duration / 2) / 29.1;
}

void loop() {
  cm_r = readCm(trigPinR, echoPinR);
  cm_l = readCm(trigPinL, echoPinL);

  Serial.print(cm_r);
  Serial.print("cm\t");
  Serial.print(cm_l);
  Serial.println("cm");

  delay(250);
}
