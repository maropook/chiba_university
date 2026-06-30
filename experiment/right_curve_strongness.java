const int motor_r1 = 2;
const int motor_r2 = 3;
const int pwm_motor_r = 10;
const int motor_l1 = 4;
const int motor_l2 = 5;
const int pwm_motor_l = 11;

// curveRight: 外輪L, 内輪R（内輪小・外輪大ほど鋭い）
int testCurveRightR[] = { 52,48, 42, 38, 30  };
int testCurveRightL[] = {255,255, 255,255,255};
const int CURVE_COUNT = 5;

bool done = false;

void setup() {
    pinMode(motor_r1, OUTPUT);
    pinMode(motor_r2, OUTPUT);
    pinMode(pwm_motor_r, OUTPUT);
    pinMode(motor_l1, OUTPUT);
    pinMode(motor_l2, OUTPUT);
    pinMode(pwm_motor_l, OUTPUT);
    Serial.begin(9600);
    delay(1000);
}

void runCurveRight(int innerR, int outerL) {
    digitalWrite(motor_l1, HIGH);
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, outerL);
    analogWrite(pwm_motor_r, innerR);
}

void stopMotors() {
    analogWrite(pwm_motor_l, 0);
    analogWrite(pwm_motor_r, 0);
}

void loop() {
    if (done) return;

    for (int i = 0; i < CURVE_COUNT; i++) {
        Serial.print("Right "); Serial.print(i + 1);
        Serial.print(": 内R="); Serial.print(testCurveRightR[i]);
        Serial.print(" 外L="); Serial.println(testCurveRightL[i]);
        runCurveRight(testCurveRightR[i], testCurveRightL[i]);
        delay(3000);
        stopMotors();
        delay(2000);
    }

    Serial.println("全テスト完了。リセットで再実行。");
    done = true;
}
