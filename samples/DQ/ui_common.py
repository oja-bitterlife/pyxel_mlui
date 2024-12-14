import pyxel

# xmlui_pyxelの初期化
# *****************************************************************************
from xmlui.lib import text,win
from xmlui.pyxel_util.theme import Theme
from xmlui.pyxel_util.font import PyxelFont
from xmlui.core import XMLUI,XUState,XUEvent,XUWinBase,XURect,XUTextBase
from params import param_db

ui_theme = Theme(PyxelFont("assets/font/b12.bdf"))

# ライブラリのインスタンス化
xmlui = XMLUI(pyxel.width, pyxel.height)
common_template = xmlui.load_template("assets/ui/common.xml")
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

common_win = win.Decorator(common_template)
common_text = text.Decorator(common_template)

# 工事中表示用
# *****************************************************************************
# ポップアップウインドウ
# ---------------------------------------------------------
@common_win.rect_frame("popup_win")  # アニメはしない
def popup_win(win:win.RectFrame, event:XUEvent):
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

@common_win.round_frame("round_win")
def round_win(round_win:win.RoundFrame, event:XUEvent):
    area = round_win.area
    clip = get_world_clip(round_win).to_offset()  # クリップエリアの設定

    # 表示領域が無ければ完了なので閉じる
    if round_win.is_closing and clip.is_empty:
        round_win.close()  # 即座にclose
    
    # 背景
    pyxel.rect(area.x, area.y, area.w, min(area.h, clip.h+2), ui_theme.win.bg_color)

    # フレーム
    round_win.draw_frame(pyxel.screen.data_ptr(), ui_theme.win.frame_pattern, area.inflate(-2, -2), clip)

# メッセージウインドウ
# ---------------------------------------------------------
@common_text.msg_dq("msg_text")
def msg_text(msg_text:text.MsgDQ, event:XUEvent):
    area = msg_text.area  # areaは重いので必ずキャッシュ

    # テーマ情報取得
    system_font = ui_theme.font.system  # フォント
    input_def = ui_theme.input_def  # 入力イベント情報

    # テキスト表示
    # ---------------------------------------------------------
    msg_text.anim.draw_count += 0.5

    # talkの時は各ページ先頭にマーク
    if msg_text.is_talk:
        for i,page in enumerate(msg_text.pages):
            msg_text.pages[i][0] = text.MsgDQ.TALK_MARK + page[0]

    # Scroll
    scroll_size = msg_text.page_line_num+2
    scroll_buf = msg_text.scroll_buf(scroll_size)
    if msg_text.page_text.startswith("＊「"):
        scroll_indents = msg_text.scroll_indents(scroll_size)
    else:
        scroll_indents = [False for _ in range(scroll_size)]

    # アニメーション用表示位置ずらし。スクロール時半文字ずれる
    shift_y = -3 if not msg_text.anim.is_finish and len(scroll_buf) >= scroll_size else 5

    # テキスト描画
    line_height = system_font.size + 3  # 行間設定
    for i,page in enumerate(scroll_buf):
        x = area.x + (system_font.size*2 if scroll_indents[i] else 0)
        y = shift_y + area.y + i*line_height
        pyxel.text(x, y, page, 7, system_font.font)

    # カーソル表示
    # ---------------------------------------------------------
    if msg_text.is_next_wait:
        cursor_count = msg_text.anim.draw_count-msg_text.anim.length
        if cursor_count//7 % 2 == 0:
            draw_msg_cursor(msg_text, 0, len(scroll_buf)*line_height + shift_y-3)

    # 入力アクション
    # ---------------------------------------------------------
    if input_def.BTN_A in event.trg or input_def.BTN_B in event.now:
        if msg_text.is_finish:
            XUWinBase.find_win(msg_text).start_close()
        elif msg_text.is_next_wait:
            msg_text.page_no += 1  # 次ページへ

    # 表示途中のアクション
    if not msg_text.is_next_wait:
        if input_def.BTN_A in event.now or input_def.BTN_B in event.now:
            msg_text.anim.draw_count += 2  # 素早く表示

    # 自分が閉じたらメニューごと閉じる
    if XUWinBase.find_win(msg_text).win_state == XUWinBase.STATE_CLOSED:
        XUWinBase(msg_text.xmlui.find_by_id("menu")).start_close()


# ステータスウインドウ( ｰ`дｰ´)ｷﾘｯ
# ---------------------------------------------------------
# ステータス各種アイテム
@common_text.label("status_item")
def status_item(status_item:text.Label, event:XUEvent):
    system_font = ui_theme.font.system

    # 値の取得
    text = XUTextBase.dict_new(status_item.text, param_db)

    # テキストは右寄せ
    area = status_item.area
    x, y = XURect.align_offset(area.w, area.h, system_font.text_width(text) + 5, 0, status_item.align, status_item.valign)
    if area.y+y < get_world_clip(XUWinBase.find_win(status_item)).bottom():
        pyxel.text(area.x + x, area.y + y, text, 7, system_font.font)

# ステータスタイトル(名前)
@common_text.label("status_title", "align", "valign")
def status_title(status_title:text.Label, event:XUEvent):
    clip = get_world_clip(XUWinBase.find_win(status_title)).intersect(status_title.area)
    pyxel.rect(status_title.area.x, status_title.area.y, status_title.area.w, clip.h, 0)  # タイトルの下地

    # テキストは左寄せ
    if status_title.area.y < clip.bottom():  # world座標で比較
        x, y = status_title.aligned_pos(ui_theme.font.system)
        pyxel.text(x+1, y-1, param_db["name"], 7, ui_theme.font.system.font)
