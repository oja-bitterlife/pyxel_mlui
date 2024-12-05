import pyxel

# xmlui_pyxelの初期化
# *****************************************************************************
from xmlui_pyxel import xmlui_pyxel_init,select,text,win,input
from xmlui_core import XMLUI,XUState,XUEvent

# ライブラリのインスタンス化
xmlui = XMLUI()
xmlui.template_fromfile("assets/ui/common.xml", "common")

# 初期化セット
xmlui_pyxel_init(xmlui,
    inputlist_dict = input.INPUT_LIST,
    font_path = "assets/font/b12.bdf"
)

# (ライブラリ開発用)
xmlui.debug.level = xmlui.debug.DEBUG_LEVEL_LIB


# 共通で使える関数
# *****************************************************************************
# カーソル描画
def draw_menu_cursor(state:XUState, x:int, y:int):
    tri_size = 6
    left = state.area.x + x
    top = state.area.y+2 + y
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)

def draw_msg_cursor(state:XUState):
    tri_size = 6
    center_x = state.area.center_x(tri_size)
    bottom = state.area.bottom(tri_size) - 2
    pyxel.tri(center_x, bottom, center_x+tri_size, bottom, center_x+tri_size//2, bottom+tri_size//2, 7)


# 工事中表示用
# *****************************************************************************
# ポップアップウインドウ
# ---------------------------------------------------------
@win.rect(xmlui, "popup_win", 1000)  # アニメはしない
def popup_win_draw(win:win.Rect, event:XUEvent):
    clip = win.area.to_offset()
    clip.h = int(win.update_count*win.speed)
    win.draw_buf(pyxel.screen.data_ptr(), [0,7,13], 0, clip)

@text.msg(xmlui, "popup_text")
def popup_text(popup_text:text.Msg, event:XUEvent):
    popup_text.finish()  # 常に一気に表示

    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        popup_text.close()

    # テキスト描画
    area = popup_text.area  # areaは重いので必ずキャッシュ

    h = len(popup_text.page_text.split()) * text.default.size
    y = area.aligned_y(h, "center")
    for i,page in enumerate(popup_text.page_text.split()):
        x = area.aligned_x(text.default.font.text_width(page), "center")
        pyxel.text(x, y+i*text.default.size, page, 7, text.default.font)


# ゲーム内共通
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
@win.round(xmlui, "round_win")
def round_win_draw(round_win:win.Round, event:XUEvent):
    clip = round_win.area.to_offset()
    clip.h = int(round_win.update_count*round_win.speed)
    round_win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)
