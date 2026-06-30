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
const int FWD_R = 126;
const int FWD_L = 180;

// strong curve（test1の値）
const int CURVE_L_STRONG_R = 190; const int CURVE_L_STRONG_L = 90;
const int CURVE_R_STRONG_R = 56;  const int CURVE_R_STRONG_L = 230;

// mild curve（平均速度固定、diff/avg比率0.535で左右バランス）
const int CURVE_L_MILD_R = 177;   const int CURVE_L_MILD_L = 102;
const int CURVE_R_MILD_R = 104;   const int CURVE_R_MILD_L = 180;

// 制御閾値
const int STOP_DIST   = 7;   // これより近いと停止(cm)
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

    Serial.print(" ←L:"); Serial.print(leftCm);
    Serial.print(" C:"); Serial.print(centerCm);
    Serial.print(" R→:"); Serial.print(rightCm);

    // 近すぎたら停止
    if (centerCm < STOP_DIST) {
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
