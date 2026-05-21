課題:前回作成した花の絵が,
キーボード操作で平行移動,回転,拡大・縮小するプログラムを作成すること
–ソースコードは整理して,適宜コメントを入れること.
変数名にも気を使うこと.
–ソースコード(.pyファイル)と実行結果(動画ファイル)の
両方を提出すること

• 注意事項
–ソースコードと実行結果のキャプチャ動画の2点を提出すること.
–動画のキャプチャ:

Windows:『Windows』+『G』ボタンhttps://www.pasoble.jp/windows/10/screen-
capture.html

Mac:https://support.apple.com/ja-jp/HT208721

• 〆切:5月19日 23時59分(日本時間)


glBegin(GL_TRIANGLES)
for i in range(3):
x = v[i][0]
y = v[i][1]
# translate(x方向に2,y方向に3)
tx = 2
ty = 3
# rotation(90度回転)
theta = 90.0 / 180.0 * np.pi
# ■TODO1:3x3の変換行列A1を用意する
A1 = np.array([[1, 0, 0],
[0, 1, 0],
[0, 0, 1]], dtype=np.float32)

# ■TODO2: [x', y', 1]^t = A * [x, y, 1]^tを計算してx'とy'を求める
# x_dash = ...
# y_dash = ...
# ■TODO3: OpenGLに座標を渡す
# glVertex2f(x_dash, y_dash)
glEnd()