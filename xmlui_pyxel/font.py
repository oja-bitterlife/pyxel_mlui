import pyxel

data = None
size = 0

def set_font(font_path:str):
    global data,size

    # フォントデータ読み込み
    data = pyxel.Font(font_path)

    # フォントサイズ算出
    with open(font_path, "r") as f:
        for i, line in enumerate(f.readlines()):
            if i > 100:  # 100行も見りゃええじゃろ...
                raise Exception("font error")
            if line.startswith("PIXEL_SIZE"):
                size = int(line.split()[-1])
                break
