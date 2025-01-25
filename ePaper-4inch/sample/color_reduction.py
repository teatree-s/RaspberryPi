import os
from datetime import datetime
from PIL import Image

# 現在のスクリプトのフォルダパスを取得
folder_path = os.path.dirname(os.path.abspath(__file__))

# 処理対象のBMPファイル名（このフォルダ内にある）
input_file_name = "Georges_Seurat.bmp"

# 減色するパレットを定義
custom_palette = [
    (0, 0, 0),  # 黒
    (255, 255, 255),  # 白
    (0, 255, 0),  # 緑
    (0, 0, 255),  # 青
    (255, 0, 0),  # 赤
    (255, 255, 0),  # 黄色
]


def reduce_colors_with_palette(input_path, output_path, palette_colors):
    # パレットの色を定義（最大256色まで指定可能）
    # 各色は(R, G, B)のタプル
    palette = []
    for color in palette_colors:
        palette.extend(color)  # RGBを展開して追加

    # パレットを256色分埋める（足りない場合は0で埋める）
    while len(palette) < 256 * 3:
        palette.extend((0, 0, 0))

    # 入力画像を開く
    image = Image.open(input_path).convert("RGB")

    # 新しい画像を作成し、指定したパレットを設定
    paletted_image = Image.new("P", image.size)
    paletted_image.putpalette(palette)

    # 入力画像をパレット画像に変換
    paletted_image.paste(image.convert("RGB").quantize(palette=paletted_image))

    # BMP形式で保存
    paletted_image.save(output_path, format="BMP")


# 入力画像と出力画像のパスを定義
input_file_path = os.path.join(folder_path, input_file_name)
current_datetime = datetime.now().strftime("%y%m%d_%H%M%S%f")[:-3]
output_file_name = f"{current_datetime}_{input_file_name}"
output_file_path = os.path.join(folder_path, output_file_name)

# 指定パレットで減色
reduce_colors_with_palette(input_file_path, output_file_path, custom_palette)
print("指定パレットによる減色処理が完了しました！")
