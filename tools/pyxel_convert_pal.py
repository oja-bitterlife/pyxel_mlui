# フルカラー画像を256パレットpngに変換するツール
# PyxelのAlt+Shift+0でのパレット出力がなぜがフルカラー画像だった

# 使い方
# pip install pillow
# python3 convert_pal.py [inputファイル]
# 出力は[inputファイル(拡張子除く).pal.png

import argparse, os.path

parser = argparse.ArgumentParser(description="pyxelで出力されたパレット画像(フルカラー)をパレットpngに変換するツール")
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
    print("あれ？Pyxelのパレット出力画像じゃないような")
    sys.exit(1)

# 元の並びを元にパレットを取得する
pal_img = Image.new("P", (w//16, 1))
palettes = []
for x in range(w//16):
    rgb = img.getpixel((x*16, 0))
    if isinstance(rgb, tuple):
        palettes.append(list(rgb))

# 出力ファイルにパレットの設定
pal_img.putpalette(sum([pal for pal in palettes], []))

# 出力ファイルにピクセル打ち(パレット順)
for x in range(w//16):
    pal_img.putpixel((x, 0), x)


pal_img.save(output_file)
