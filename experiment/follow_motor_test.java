const int motor_r1 = 2;
const int motor_r2 = 3;
const int pwm_motor_r = 10;
const int motor_l1 = 4;
const int motor_l2 = 5;
const int pwm_motor_l = 11;

const int forwardR = 126;  // 105 * 1.2
const int forwardL = 180;  // 150 * 1.2

// 元のライントレース車の値を起点に前後±で試す
// curveLeft:  外輪R, 内輪L
// curveRight: 外輪L, 内輪R
int testCurveLeftR[]  = {190, 179, 168};
int testCurveLeftL[]  = { 90, 100, 110};
int testCurveRightR[] = { 56,  66,  75};
int testCurveRightL[] = {230, 220, 209};
const int CURVE_COUNT = 3;

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

void runCurveLeft(int outerR, int innerL) {
    digitalWrite(motor_l1, HIGH);
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, innerL);
    analogWrite(pwm_motor_r, outerR);
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
        Serial.print("Left ");  Serial.print(i + 1);
        Serial.print(": R="); Serial.print(testCurveLeftR[i]);
        Serial.print(" L="); Serial.println(testCurveLeftL[i]);
        runCurveLeft(testCurveLeftR[i], testCurveLeftL[i]);
        delay(3000);
        stopMotors();
        delay(500);

        Serial.print("Right "); Serial.print(i + 1);
        Serial.print(": R="); Serial.print(testCurveRightR[i]);
        Serial.print(" L="); Serial.println(testCurveRightL[i]);
        runCurveRight(testCurveRightR[i], testCurveRightL[i]);
        delay(3000);
        stopMotors();
        delay(2000);
    }

    Serial.println("全テスト完了。リセットで再実行。");
    done = true;
}


