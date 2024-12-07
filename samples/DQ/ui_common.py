import pyxel

# xmlui_pyxelの初期化
# *****************************************************************************
from xmlui.lib import select,text,win,input
from xmlui.pyxel_util.theme import Theme
from xmlui.pyxel_util.theme import PyxelFont
from xmlui.xmlui_core import XMLUI,XUState,XUEvent

# ライブラリのインスタンス化
xmlui = XMLUI(pyxel.width, pyxel.height)
xmlui.template_fromfile("assets/ui/common.xml", "common")

# 初期化セット
ui_theme = Theme(xmlui, PyxelFont("assets/font/b12.bdf"))


# 共通で使える関数
# *****************************************************************************
# カーソル描画
def draw_menu_cursor(state:XUState, x:int, y:int):
    tri_size = 6
    left = state.area.x + x
    top = state.area.y+2 + y
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)

def draw_msg_cursor(state:XUState, x:int, y:int):
    tri_size = 6
    center_x = 127-tri_size//2+x  # Xはど真ん中固定で
    y = state.area.y + tri_size - 3 + y
    pyxel.tri(center_x, y, center_x+tri_size, y, center_x+tri_size//2, y+tri_size//2, 7)


common_win = win.Decorators(xmlui, "common")
common_text = text.Decorators(xmlui, "common")

# 工事中表示用
# *****************************************************************************
# ポップアップウインドウ
# ---------------------------------------------------------
@common_win.rect("popup_win")  # アニメはしない
def popup_win_draw(win:win.Rect, event:XUEvent):
    pyxel.rect(win.area.x, win.area.y, win.area.w, win.area.h, 0)
    win.draw_frame(pyxel.screen.data_ptr(), [0,7,13], win.area.inflate(-2, -2))

@common_text.msg("popup_text")
def popup_text(popup_text:text.Msg, event:XUEvent):
    if ui_theme.input.BTN_A in event.trg or ui_theme.input.BTN_B in event.trg:
        popup_text.close()

    # テキスト描画
    area = popup_text.area  # areaは重いので必ずキャッシュ

    h = len(popup_text.text.split()) * ui_theme.font.system.size
    y = area.aligned_y(h, "center")
    for i,page in enumerate(popup_text.text.split()):
        x = area.aligned_x(ui_theme.font.system.text_width(page), "center")
        pyxel.text(x, y+i*ui_theme.font.system.size, page, 7, ui_theme.font.system.font)


# ゲーム内共通
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
@common_win.round("round_win")
def round_win_draw(round_win:win.Round, event:XUEvent):
    area = round_win.area
    clip = round_win.area.to_offset()
    clip.h = int(round_win.update_count*32)

    # 背景
    pyxel.rect(area.x, area.y, area.w, min(area.h, clip.h+2), ui_theme.win.bg_color)

    # フレーム
    round_win.draw_frame(pyxel.screen.data_ptr(), ui_theme.win.frame_pattern, area.inflate(-2, -2), clip)
