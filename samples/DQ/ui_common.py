import pyxel

# xmlui_pyxelの初期化
# *****************************************************************************
from xmlui.lib import text,win
from xmlui.pyxel_util.theme import Theme
from xmlui.pyxel_util.font import PyxelFont
from xmlui.core import XMLUI,XUState,XUEvent,XUWinBase,XURect

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

def get_world_clip(win:XUWinBase) -> XURect:
    area = win.area
    if win.is_opening:
        clip_size = min(int(win.opening_count * ui_theme.win.open_speed), area.h)
        area.h = clip_size
    else:
        clip_size = max(int(win.closing_count * ui_theme.win.close_speed), 0)
        area.h -= clip_size
    return area

common_win = win.Decorator(xmlui)
common_text = text.Decorator(xmlui)

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

    for i,page in enumerate(popup_text.text.split()):
        area = popup_text.area
        x, y = area.aligned_pos(system_font.text_width(page), h, XURect.ALIGN_CENTER, XURect.ALIGN_CENTER)
        pyxel.text(x, y + i*system_font.size, page, 7, system_font.font)


# ゲーム内共通
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
# openで値をセットをした後closeされる、closingなのに値はopningになっちゃうので別々に保存する
CLOSING_CLIP_SIZE="_xmlui_closing_clip_size"
OPENING_CLIP_SIZE="_xmlui_opening_clip_size"

@common_win.round_anim("round_win")
def round_win(round_win:win.RoundAnim, event:XUEvent):
    area = round_win.area
    clip = get_world_clip(round_win).to_offset()  # クリップエリアの設定

    # 表示領域が無ければ完了なので閉じる
    if round_win.is_closing and clip.is_empty:
        round_win.close()  # 即座にclose
    
    # 背景
    pyxel.rect(area.x, area.y, area.w, min(area.h, clip.h+2), ui_theme.win.bg_color)

    # フレーム
    round_win.draw_frame(pyxel.screen.data_ptr(), ui_theme.win.frame_pattern, area.inflate(-2, -2), clip)
