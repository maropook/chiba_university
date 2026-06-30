const int motor_r1 = 2;
const int motor_r2 = 3;
const int pwm_motor_r = 10;
const int motor_l1 = 4;
const int motor_l2 = 5;
const int pwm_motor_l = 11;

void setup() {
    pinMode(motor_r1, OUTPUT);
    pinMode(motor_r2, OUTPUT);
    pinMode(pwm_motor_r, OUTPUT);
    pinMode(motor_l1, OUTPUT);
    pinMode(motor_l2, OUTPUT);
    pinMode(pwm_motor_l, OUTPUT);
    delay(1000);
}

void loop() {
    digitalWrite(motor_l1, HIGH);
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, 180);  // 外輪L (平均142固定、差30%減)
    analogWrite(pwm_motor_r, 104);  // 内輪R (平均142固定、差30%減)
}
