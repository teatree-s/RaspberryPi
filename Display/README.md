<a name="readme-top"></a>

<!-- ABOUT THE PROJECT -->

# 1. ディスプレイ

- 7inch HDMI Display
- 7inch HDMI Display-H

Raspberry Pi で使用する時の「config.txt」ファイルの設定です。

```
hdmi_force_edid_audio=1 # HDMIから音声信号を強制的に出力する
max_usb_current=1 # USBポートへの給電能力を最大（1.2A）まで引き上げる
hdmi_force_hotplug=1 # HDMI接続を強制的に有効化する
config_hdmi_boost=7 # HDMIの信号強度を上げる
hdmi_group=2 # HDMIの規格を「DMT（PCモニター向け）」に設定する
hdmi_drive=2 # HDMIモードで出力する（1:音声無、2:音声有）
display_rotate=0 # 画面の回転設定（0: 通常、1: 90度、2: 180度、3: 270度）
hdmi_mode=87 # カスタム解像度設定
hdmi_cvt 1024 600 60 6 0 0 0 # カスタム解像度の詳細設定
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

# 2. 7inch HDMI Display

<img src="./docs/7inch HDMI Display.jpg" width="480">

SD カードのルート ディレクトリにある「config.txt」ファイルを開き、ファイルの末尾に次のコードを追加して保存し、終了します。

```
hdmi_force_edid_audio=1
max_usb_current=1
hdmi_force_hotplug=1
config_hdmi_boost=7
hdmi_group=2
hdmi_mode=87
hdmi_drive=1 # 音声無
display_rotate=0
hdmi_cvt 1024 600 60 6 0 0 0
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# 3. 7inch HDMI Display-H

<img src="./docs/7inch HDMI Display-H.jpg" width="480">

SD カードのルート ディレクトリにある「config.txt」ファイルを開き、ファイルの末尾に次のコードを追加して保存し、終了します。

```
hdmi_force_edid_audio=1
max_usb_current=1
hdmi_force_hotplug=1
config_hdmi_boost=7
hdmi_group=2
hdmi_mode=87
hdmi_drive=1 # ディスプレイのスピーカーがあれば2
display_rotate=0
hdmi_cvt 1024 600 60 6 0 0 0
```

- [7inch HDMI Display-H](https://www.lcdwiki.com/7inch_HDMI_Display-H)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
