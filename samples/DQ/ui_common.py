import pyxel

# xmlui_pyxelの初期化
# *****************************************************************************
from xmlui.lib import select,text,win,input
from xmlui.pyxel_util.theme import Theme
from xmlui.pyxel_util.font import PyxelFont
from xmlui.core import XMLUI,XUState,XUEvent,XUWinFrameBase

ui_theme = Theme(PyxelFont("assets/font/b12.bdf"))

# ライブラリのインスタンス化
xmlui = XMLUI(pyxel.width, pyxel.height)
xmlui.template_fromfile("assets/ui/common.xml", "common")
xmlui.debug.level = ui_theme.debug.debug_level



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

def get_winclip_h(state:XUState):
    size = state.closing_count*ui_theme.win.close_speed
    if state.is_closing:
        return max(0, state.area.h - size)
    else:  # opening
        return min(state.area.h, size)


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
    input_def = ui_theme.input_def
    if input_def.BTN_A in event.trg or input_def.BTN_B in event.trg:
        popup_text.close()

    # テキスト描画
    area = popup_text.area  # areaは重いので必ずキャッシュ
    system_font = ui_theme.font.system
    h = len(popup_text.text.split()) * system_font.size
    y = area.aligned_y(h, "center")

    for i,page in enumerate(popup_text.text.split()):
        x = area.aligned_x(system_font.text_width(page), "center")
        pyxel.text(x, y+i*system_font.size, page, 7, system_font.font)


# ゲーム内共通
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
@common_win.round("round_win")
def round_win_draw(round_win:win.Round, event:XUEvent):
    area = round_win.area
    clip = round_win.area.to_offset()
    clip.h = int(round_win.update_count*ui_theme.win.open_speed)

    if round_win.is_closing:
        clip.h = get_winclip_h(round_win)
        # waitが終わるのをまたないでとっとと閉じる
        if clip.is_empty:
            round_win.finish_closing()
            return

    # 背景
    pyxel.rect(area.x, area.y, area.w, min(area.h, clip.h+2), ui_theme.win.bg_color)

    # フレーム
    round_win.draw_frame(pyxel.screen.data_ptr(), ui_theme.win.frame_pattern, area.inflate(-2, -2), clip)
