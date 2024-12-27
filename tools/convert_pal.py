# フルカラー画像を256パレットpngに変換するツール
# PyxelのAlt+Shift+0でのパレット出力がなぜがフルカラー画像だった

# 使い方
# pip install pillow
# python3 convert_pal.py [inputファイル]
# 出力は[inputファイル(拡張子除く).pal.png

import argparse, os.path

parser = argparse.ArgumentParser(description="フルカラー画像を256パレットpngに変換するツール")
parser.add_argument("input_file", help="変換元画像ファイル名") 
parser.add_argument("--out", metavar="output_file", help="出力ファイル名。未指定時はinput_fileの拡張子を.pal.pngとして出力") 
args = parser.parse_args()

# 出力ファイル名決定
output_file = args.out
if output_file is None:
    output_file = os.path.splitext(os.path.basename(args.input_file))[0] + ".pal.png"

# 画像変換
import sys
from PIL import Image

img = Image.open(args.input_file)
w, h = img.size

# pxelの出力形式変更に備えておく
if not img.mode.startswith("RGB") or h != 16 or not isinstance(img.getpixel((0, 0)), tuple):
    print("未対応の画像形式です")
    sys.exit(1)

# 元の並びを取得する
pal_img = Image.new("P", (w//16, 1))
for x in range(w//16):
    rgb = img.getpixel((x*16, 0))
    if isinstance(rgb, tuple):
        pal_img.putpixel((x, 0), rgb)

pal_img.save(output_file)
