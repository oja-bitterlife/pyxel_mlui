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
    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        popup_text.close()

    # テキスト描画
    area = popup_text.area  # areaは重いので必ずキャッシュ

    h = len(popup_text.text.split()) * text.default.size
    y = area.aligned_y(h, "center")
    for i,page in enumerate(popup_text.text.split()):
        x = area.aligned_x(text.default.font.text_width(page), "center")
        pyxel.text(x, y+i*text.default.size, page, 7, text.default.font)


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
    pyxel.rect(area.x, area.y, area.w, min(area.h, clip.h+2), 0)

    # フレーム
    round_win.draw_frame(pyxel.screen.data_ptr(), [7,13], area.inflate(-2, -2), clip)
