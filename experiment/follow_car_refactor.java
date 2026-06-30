// モーターピン
const int motor_r1 = 2;
const int motor_r2 = 3;
const int pwm_motor_r = 10;
const int motor_l1 = 4;
const int motor_l2 = 5;
const int pwm_motor_l = 11;

// 超音波センサーピン
const int leftTrig  = A4; const int leftEcho  = A5;
const int centerTrig = A2; const int centerEcho = A3;
const int rightTrig = A0; const int rightEcho = A1;

// チューニング済みモーター値
const int FWD_R = 140;
const int FWD_L = 200;

// strong curve（×1.108）
const int CURVE_L_STRONG_R = 211; const int CURVE_L_STRONG_L = 100;
const int CURVE_R_STRONG_R = 62;  const int CURVE_R_STRONG_L = 255;

// mild curve（×1.108）
const int CURVE_L_MILD_R = 196;   const int CURVE_L_MILD_L = 113;
const int CURVE_R_MILD_R = 115;   const int CURVE_R_MILD_L = 200;

// 制御閾値（各センサーの停止距離）
const int STOP_DIST_L = 5;   // 左センサー停止距離(cm)
const int STOP_DIST_C = 7;   // 中央センサー停止距離(cm)
const int STOP_DIST_R = 5;   // 右センサー停止距離(cm)
const int LOST_DIST   = 500;  // これより遠いと見失い(cm)
const int STEER_GENTLE = 10;  // 緩カーブ開始(cm)
const int STEER_SHARP  = 25;  // 鋭カーブ開始(cm)

void setup() {
    pinMode(motor_r1, OUTPUT);
    pinMode(motor_r2, OUTPUT);
    pinMode(pwm_motor_r, OUTPUT);
    pinMode(motor_l1, OUTPUT);
    pinMode(motor_l2, OUTPUT);
    pinMode(pwm_motor_l, OUTPUT);
    pinMode(leftTrig, OUTPUT);  pinMode(leftEcho, INPUT);
    pinMode(centerTrig, OUTPUT); pinMode(centerEcho, INPUT);
    pinMode(rightTrig, OUTPUT); pinMode(rightEcho, INPUT);
    Serial.begin(9600);
}

void printPad(long val, int width) {
    String s = String(val);
    while ((int)s.length() < width) s = " " + s;
    Serial.print(s);
}

long readCm(int trig, int echo) {
    digitalWrite(trig, LOW);
    delayMicroseconds(5);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);
    return (pulseIn(echo, HIGH) / 2) / 29.1;
}

void moveForward() {
    digitalWrite(motor_l1, HIGH); digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, FWD_L);
    analogWrite(pwm_motor_r, FWD_R);
}

void curveLeft(bool strong) {
    digitalWrite(motor_l1, HIGH); digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, strong ? CURVE_L_STRONG_L : CURVE_L_MILD_L);
    analogWrite(pwm_motor_r, strong ? CURVE_L_STRONG_R : CURVE_L_MILD_R);
}

void curveRight(bool strong) {
    digitalWrite(motor_l1, HIGH); digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, strong ? CURVE_R_STRONG_L : CURVE_R_MILD_L);
    analogWrite(pwm_motor_r, strong ? CURVE_R_STRONG_R : CURVE_R_MILD_R);
}

void stopMotors() {
    analogWrite(pwm_motor_l, 0);
    analogWrite(pwm_motor_r, 0);
}

void loop() {
    long centerCm = readCm(centerTrig, centerEcho);
    long leftCm   = readCm(leftTrig,   leftEcho);
    long rightCm  = readCm(rightTrig,  rightEcho);

    Serial.print("Left:"); printPad(leftCm, 4); Serial.print("cm  |  ");
    Serial.print("Center:"); printPad(centerCm, 4); Serial.print("cm  |  ");
    Serial.print("Right:"); printPad(rightCm, 4); Serial.print("cm");

    // 近すぎたら停止
    if (leftCm < STOP_DIST_L || centerCm < STOP_DIST_C || rightCm < STOP_DIST_R) {
        Serial.println(" → STOP");
        stopMotors();
        delay(100);
        return;
    }

    // 最小値のセンサー方向に進む
    if (centerCm <= leftCm && centerCm <= rightCm) {
        Serial.println(" → 直進");
        moveForward();
    } else if (rightCm < leftCm) {
        Serial.println(" → 右に曲がる→ (strong)");
        curveRight(true);
    } else {
        Serial.println(" → 左に曲がる (strong)");
        curveLeft(true);
    }

    delay(100);
}
