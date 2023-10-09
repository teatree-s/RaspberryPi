import cv2
import time

# カメラの初期化
cap = cv2.VideoCapture(0)  # 0はカメラのデバイス番号で、Raspberry Piのカメラモジュールは通常0です

if not cap.isOpened():
    print("カメラが正しく初期化されませんでした。")
    exit()

# カメラからフレームをキャプチャ
ret, frame = cap.read()

if not ret:
    print("フレームをキャプチャできませんでした。")
    exit()

# 画像を保存
image_filename = "captured.jpg"
cv2.imwrite(image_filename, frame)
print(f"{image_filename} に画像を保存しました。")

# カメラを解放
cap.release()
