import time
import json
from google import genai
import speech_recognition as sr
import pyaudio
from gpiozero import LED
from matrix import MAX7219

# Google GenAI SDKのAPIキーとモデルIDを設定
YOUR_API_KEY = "YOUR_API_KEY"
MODEL_ID = "models/gemini-2.5-flash"

# ALSA関連のエラーログが出るためPyAudioで一度出力する。
audio = pyaudio.PyAudio()
try:
    stream = audio.open(
        format=pyaudio.paInt16,  # S16_LE (16bit PCM) に対応
        rate=16000,  # 16kHz (音声認識に最適)
        channels=1,  # モノラル (1チャンネル)
        input_device_index=2,  # hw:2,0 の「2」に相当
        input=True,
        frames_per_buffer=1024,  # バッファサイズ（一般的な値）
    )
except Exception as e:
    print(f"エラー: オーディオストリームの初期化に失敗しました。{str(e)}")
    audio.terminate()
    exit()
time.sleep(1)

# Google GenAIクライアントの初期化
client = genai.Client(api_key=YOUR_API_KEY)
print(f"タスク抽出AI: {MODEL_ID}")

# 音声認識の初期化
r = sr.Recognizer()

# LEDマトリクスの初期化
display = MAX7219(bus=0, device=0)

red = LED(17)
yellow = LED(27)
green = LED(22)
blue = LED(23)

MODE_LED = 1
MODE_DOT = 2


def read_system_instruction(mode):
    system_instruction = ""
    if mode == MODE_LED:
        system_instruction = "system_led_rules.md"
    else:
        system_instruction = "system_dot_rules.md"

    try:
        with open(system_instruction, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"エラー: システム指示の読み込みに失敗しました。{str(e)}")
        return ""


def analyze_text(user_input, system_instruction):
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_input,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
            },
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}


def dot_init():
    display.brightness(1)
    display.clear()
    display.show()


def dot_final():
    display.clear()
    display.show()
    display.close()


def dot_on():
    display.fill(1)
    display.show()
    time.sleep(1)
    display.fill(0)
    display.show()


def dot_control(pattern_str):
    try:
        bytes_data = [int(val.strip(), 16) for val in pattern_str.split(",")]
    except ValueError:
        raise ValueError("Invalid format.(e.g., '0x00, 0xFF')")

    if len(bytes_data) != 8:
        raise ValueError("Pattern must contain exactly 8 bytes.")

    for y, byte in enumerate(bytes_data):
        for x in range(8):
            # ビット演算で特定のビットが1か0かを確認
            # (1 << (7 - x)) により、左端（MSB）から順にチェック
            if byte & (1 << x):
                # 描画位置を 7 - x にすることで、左右を反転
                display.dot(7 - y, 7 - x, color=1)
            else:
                display.dot(7 - y, 7 - x, color=0)
    display.show()


def led_init():
    red.off()
    yellow.off()
    green.off()
    blue.off()


def led_on():
    red.on()
    yellow.on()
    green.on()
    blue.on()
    time.sleep(1)
    led_init()


def led_control(data):
    # リスト形式の場合は各要素を処理
    if isinstance(data, list):
        for item in data:
            led_control_single(item)
    else:
        led_control_single(data)


def led_control_single(data):
    # 単一のJSONオブジェクトに基づいてLEDを制御する関数
    color = data.get("color")
    status = data.get("status")
    number = data.get("number")

    led_map = {"赤": red, "黄": yellow, "緑": green, "青": blue}

    led = led_map.get(color)
    if not led:
        return

    if status == "点灯":
        led.on()
    elif status == "消灯":
        led.off()
    elif status == "点滅":
        led.blink(on_time=1, off_time=1, n=number, background=True)


def toggle_mode():
    global mode, SYSTEM_INSTRUCTION
    if mode == MODE_LED:
        mode = MODE_DOT
        dot_on()
    else:
        mode = MODE_LED
        led_on()
    SYSTEM_INSTRUCTION = read_system_instruction(mode)
    print(f"モード切替: {'LED' if mode == MODE_LED else 'MAX7219'}")


# メイン処理
dot_init()
led_init()
mode = MODE_DOT
toggle_mode()

print("音声入力を待機しています... (Ctrl+C で終了)")

try:
    while True:
        # マイクから音声を入力
        with sr.Microphone() as source:
            print("何か話してください...")
            # 周囲のノイズを調整
            r.adjust_for_ambient_noise(source)
            recognized_audio = r.listen(source)

        try:
            # Google Web Speech APIで音声認識（日本語指定）
            text = r.recognize_google(recognized_audio, language="ja-JP")
            if text is None:
                print("聞き取れませんでした。もう一度話してください。")
                continue
            elif text == "終了":
                break
            elif text == "スイッチ":
                toggle_mode()
                continue
            print(f"入力文字: {text}")

        except sr.UnknownValueError:
            print("音声が認識できませんでした。")
            continue
        except sr.RequestError as e:
            print(f"サービスに接続できませんでした: {e}")
            break

        print("解析中...")
        result = analyze_text(text, SYSTEM_INSTRUCTION)
        print("解析結果：")
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # 解析結果に基づいてLEDやドットマトリクスを制御
        if mode == MODE_LED:
            led_control(result)
        else:
            dot_control(result)

except KeyboardInterrupt:
    print("")
finally:
    print("\n終了します...")
    dot_final()
    led_init()
    audio.terminate()
