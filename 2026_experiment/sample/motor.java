const int motor_r1 = 2;
const int motor_r2 = 3;
const int pwm_motor_r = 10;
const int motor_l1 = 4;
const int motor_l2 = 5;
const int pwm_motor_l = 11;
const int sensorR = A3;
const int sensorL = A4;
const int sensorM = A5;

int threshR = 600;
int threshL = 600;

void setup() {
    pinMode(motor_r1, OUTPUT);
    pinMode(motor_r2, OUTPUT);
    pinMode(pwm_motor_r, OUTPUT);
    pinMode(motor_l1, OUTPUT);
    pinMode(motor_l2, OUTPUT);
    pinMode(pwm_motor_l, OUTPUT);
    Serial.begin(9600);
}

// 判定関数
bool isR_Black() { return analogRead(sensorR) > threshR; }
bool isL_Black() { return analogRead(sensorL) > threshL; }

void moveForward() {
    // 左：正転
    digitalWrite(motor_l1, HIGH);
    digitalWrite(motor_l2, LOW);
    analogWrite(pwm_motor_l, 100); 

    digitalWrite(motor_r1, HIGH);
    digitalWrite(motor_r2, LOW);
    analogWrite(pwm_motor_r, 100);
}

void moveRight() {
    digitalWrite(motor_l1, LOW); // 左停止
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, HIGH); // 右正転
    digitalWrite(motor_r2, LOW);
    analogWrite(pwm_motor_r, 255);
    analogWrite(pwm_motor_l, 255);

}

void moveLeft() {
    digitalWrite(motor_l1, LOW); // 左正転
    digitalWrite(motor_l2, HIGH);
    digitalWrite(motor_r1, LOW);  // 右停止
    digitalWrite(motor_r2, LOW);
    analogWrite(pwm_motor_l, 200);
}

void loop() {
    //bool blackR = isR_Black();
    //bool blackL = isL_Black();
   // moveLeft();
      moveRight();

/*    if (!blackR && !blackL) {
        moveForward();
    } else if (blackR && !blackL) {
        moveRight();  // 右が黒なら左へ（ラインを跨ぐ制御の場合）
    } else if (!blackR && blackL) {
        moveLeft(); // 左が黒なら右へ
    } else {
        moveForward(); // 両方黒（交差点など）
    } */
    delay(20); 
}