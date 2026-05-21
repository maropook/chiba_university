// 修正版
const int motor_r1 = 2; //後輪側
const int motor_r2 = 3; //前輪側
const int pwm_motor_r = 10;
const int motor_l1 = 4;//後輪側
const int motor_l2 = 5;//前輪側
const int pwm_motor_l = 11;
const int sensorR = A3;
const int sensorL = A4;
const int sensorM = A5;

int threshR = 600;
int threshL = 600;
int delay_time = 7000;

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

int forwardR = 168;
int forwardL = 200; 
void moveForward() { //Validated
    // 左：正転
    digitalWrite(motor_l1, HIGH); // 左正転
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  // 右後転
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, forwardL);
    analogWrite(pwm_motor_r, forwardR);
}


int moveLeftR = 255;
int moveLeftL = 150;

void turnLeft() {
    digitalWrite(motor_l1, LOW); // 左後転
    digitalWrite(motor_l2, HIGH);
    digitalWrite(motor_r1, LOW); // 右正転
    digitalWrite(motor_r2, HIGH);

    analogWrite(pwm_motor_l, moveLeftL);
    analogWrite(pwm_motor_r, moveLeftR);
}

int curveLeftR = 150;
int curveLeftL = 90;
void curveLeft(){
    digitalWrite(motor_l1, HIGH); // 左正転
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  // 右正転
    digitalWrite(motor_r2, HIGH);

    analogWrite(pwm_motor_l, curveLeftL);
    analogWrite(pwm_motor_r, curveLeftR);
}



int turnRightR = 150;
int turnRightL = 255;

void turnRight() {
    digitalWrite(motor_l1, HIGH); // 左正転
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, HIGH);  // 右後転
    digitalWrite(motor_r2, LOW);

    analogWrite(pwm_motor_l, turnRightL);
    analogWrite(pwm_motor_r, turnRightR);
}

int curveRightR = 60;
int curveRightL = 200;
void curveRight(){
    digitalWrite(motor_l1, HIGH); // 左正転
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  // 右正転
    digitalWrite(motor_r2, HIGH);

    analogWrite(pwm_motor_l, curveRightL);
    analogWrite(pwm_motor_r, curveRightR);
}

void loop() {
    //bool blackR = isR_Black();
    //bool blackL = isL_Black();

    // moveForward(); // Validated
    // turnLeft();
    // turnRight();
    // curveLeft();
     curveRight();

/*    if (!blackR && !blackL) {
        moveForward();
    } else if (blackR && !blackL) {
        moveRight();  // 右が黒なら左へ（ラインを跨ぐ制御の場合）
    } else if (!blackR && blackL) {
        moveLeft(); // 左が黒なら右へ
    } else {
        moveForward(); // 両方黒（交差点など）
    } */
    delay(delay_time); 
}