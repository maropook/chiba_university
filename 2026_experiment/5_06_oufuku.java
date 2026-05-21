
// 修正版8（T字路・1回のみ180度ターン / 復路の全白は直進）
//　次回課題,回転しすぎ、moveForward弱すぎて摩擦に勝てない問題

const int motor_r1 = 2; 
const int motor_r2 = 3; 
const int pwm_motor_r = 10; 
const int motor_l1 = 4;
const int motor_l2 = 5;
const int pwm_motor_l = 11;
const int sensorR = A3;
const int sensorL = A4;
const int sensorM = A5;

int threshR = 300;
int threshL = 300;
int threshM = 300;
int delay_time = 10;

// ----- 全白判定・1回制限用の追加変数 -----
unsigned long allWhiteStartTime = 0; 
bool isAllWhite = false;             
const unsigned long ALL_WHITE_THRESH = 500; 
bool hasTurned180 = false; // すでに180度回転したかを記録するフラグ

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
bool isM_Black() { return analogRead(sensorM) > threshM; } 

// --- 移動関数群 ---
int forwardR = 100;
int forwardL = 150; 
void moveForward() {
    digitalWrite(motor_l1, HIGH); 
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, forwardL);
    analogWrite(pwm_motor_r, forwardR);
}

int moveLeftR = 255;
int moveLeftL = 150;
void turnLeft() {
    digitalWrite(motor_l1, LOW); 
    digitalWrite(motor_l2, HIGH);
    digitalWrite(motor_r1, LOW); 
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, moveLeftL);
    analogWrite(pwm_motor_r, moveLeftR);
}

int curveLeftR = 130;
int curveLeftL = 70;
void curveLeft(){
    digitalWrite(motor_l1, HIGH); 
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, curveLeftL);
    analogWrite(pwm_motor_r, curveLeftR);
}

int turnRightR = 150;
int turnRightL = 255;
void turnRight() {
    digitalWrite(motor_l1, HIGH); 
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, HIGH);  
    digitalWrite(motor_r2, LOW);
    analogWrite(pwm_motor_l, turnRightL);
    analogWrite(pwm_motor_r, turnRightR);
}

int curveRightR = 40;
int curveRightL = 180;
void curveRight(){
    digitalWrite(motor_l1, HIGH); 
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, LOW);  
    digitalWrite(motor_r2, HIGH);
    analogWrite(pwm_motor_l, curveRightL);
    analogWrite(pwm_motor_r, curveRightR);
}

// 180度ターン関数
void turn180() {
    Serial.println("全白継続を確認！180度ターン実行！");
    
    digitalWrite(motor_l1, HIGH); 
    digitalWrite(motor_l2, LOW);
    digitalWrite(motor_r1, HIGH); 
    digitalWrite(motor_r2, LOW);

    analogWrite(pwm_motor_l, 160); 
    analogWrite(pwm_motor_r, 255);

    delay(900); 

    // ターン完了後にモーターを一旦停止
    analogWrite(pwm_motor_l, 0);
    analogWrite(pwm_motor_r, 0);
    delay(1000); 
}

void loop() {
    bool blackR = isR_Black();
    bool blackL = isL_Black();
    bool blackM = isM_Black(); 

    // --- 全白（行き止まり・ゴール）判定 ---
    if (!blackR && !blackL && !blackM) {
        
        // 【1回目の全白】指定時間待ってから180度ターン
        if (!hasTurned180) {
            if (!isAllWhite) {
                isAllWhite = true;
                allWhiteStartTime = millis();
                Serial.println("1回目の全白検知開始..."); 
            } else {
                if (millis() - allWhiteStartTime >= ALL_WHITE_THRESH) {
                    turn180();
                    hasTurned180 = true; // 回転済みフラグを立てる
                    isAllWhite = false;  // フラグをリセット
                    Serial.println("復路スタート");
                }
            }
        } 
        // 【2回目以降の全白】ただまっすぐ進む（コースを突き抜ける）
        else {
            Serial.println("全白(回転済み)：直進して突破");
            moveForward();
        }
    } 
    // --- 通常のライントレース ---
    else {
        // 1つでも黒を検知した場合は、「全白ではない」としてフラグをリセット
        if (isAllWhite) {
            isAllWhite = false;
            Serial.println("黒を再検知（全白リセット）"); 
        }

        if (!blackR && !blackL) { 
            Serial.println("直進");
            moveForward();
        } else if (blackR && !blackL) { 
            Serial.println("右へ");
            curveRight();  
        } else if (!blackR && blackL) { 
            Serial.println("左へ");
            curveLeft(); 
        } 
    }
    
    delay(delay_time); 
}

