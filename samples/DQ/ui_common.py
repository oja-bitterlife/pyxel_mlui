import pyxel

# xmlui_pyxelの初期化
# *****************************************************************************
from xmlui.core import XMLUI,XUElem,XUEvent,XUWinInfo,XURect,XUTextUtil
from xmlui.lib import text,win

from db import user_data
from system_dq import system_font


# 共通定義
# *****************************************************************************
WIN_OPEN_SPEED   = 16
WIN_CLOSE_SPEED   = 32
KOJICHU_COL = 15


# 共通で使える関数
# *****************************************************************************
# カーソル描画
def draw_menu_cursor(elem:XUElem, x:int, y:int):
    col = get_text_color()

    tri_size = 6
    left = elem.area.x + x
    top = elem.area.y+2 + y
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, col)

def draw_msg_cursor(elem:XUElem, x:int, y:int):
    col = get_text_color()

    tri_size = 6
    center_x = 127-tri_size//2+x  # Xはど真ん中固定で
    y = elem.area.y + tri_size - 3 + y
    pyxel.tri(center_x, y, center_x+tri_size, y, center_x+tri_size//2, y+tri_size//2, col)

def get_world_clip(win:XUWinInfo) -> XURect:
    area = win.area
    if win.is_opening:
        clip_size = min(int(win.opening_count * WIN_OPEN_SPEED), area.h)
        area.h = clip_size
    else:
        clip_size = max(int(win.closing_count * WIN_CLOSE_SPEED), 0)
        area.h -= clip_size
    return area

# テキストカラー
def get_text_color() -> int:
    return 8 if user_data.hp <= 1 else 7

# テキストカラー
def get_shadow_color() -> int:
    return 2 if user_data.hp <= 1 else 13


# 共通UI
# *****************************************************************************
def ui_init(xmlui:XMLUI):
    common_win = win.Decorator(xmlui)
    common_text = text.Decorator(xmlui)

    # 工事中表示用
    # *****************************************************************************
    # ポップアップウインドウ
    # ---------------------------------------------------------
    @common_win.rect_frame("popup_win")  # アニメはしない
    def popup_win(win:win.XURectFrame, event:XUEvent):
        pyxel.rect(win.area.x, win.area.y, win.area.w, win.area.h, 0)
        win.draw_frame(pyxel.screen.data_ptr(), [0,7,13], win.area.inflate(-2, -2))

    @common_text.msg("popup_text")
    def popup_text(popup_text:text.XUMsg, event:XUEvent):
        if event.check(XUEvent.Key.BTN_A, XUEvent.Key.BTN_B):
            XUWinInfo.find_parent_win(popup_text).close()

        # テキスト描画
        area = popup_text.area  # areaは重いので必ずキャッシュ
        h = len(popup_text.text.split()) * system_font.size

        for i,page in enumerate(popup_text.text.split()):
            area = popup_text.area
            x, y = area.aligned_pos(system_font.text_width(page), h, XURect.Align.CENTER, XURect.Align.CENTER)
            pyxel.text(x, y + i*system_font.size, page, 7, system_font.font)


    # ゲーム内共通
    # *****************************************************************************
    # 角丸ウインドウ
    # ---------------------------------------------------------
    @common_win.round_frame("round_win")
    def round_win(round_win:win.XURoundFrame, event:XUEvent):
        area = round_win.area
        clip = get_world_clip(round_win).to_offset()  # クリップエリアの設定

        # 表示領域が無ければ完了なので閉じる
        if round_win.is_closing and clip.is_empty:
            round_win.close()  # 即座にclose
            round_win.xmlui.on(f"close_win:{round_win.id}")  # ウインドウ閉じたイベント発行
            return
        
        # 背景
        pyxel.rect(area.x, area.y, area.w, min(area.h, clip.h+2), 0)

        col = get_text_color()
        shadow_col = get_shadow_color()

        # フレーム
        round_win.draw_frame(pyxel.screen.data_ptr(), [col, shadow_col], area.inflate(-2, -2), clip)

    # ステータスウインドウ( ｰ`дｰ´)ｷﾘｯ
    # ---------------------------------------------------------
    # ステータス各種アイテム
    @common_text.label("status_item")
    def status_item(status_item:text.XULabel, event:XUEvent):
        # 値の取得
        text = XUTextUtil.format_zenkaku(XUTextUtil.format_dict(status_item.text, user_data.data))

        col = get_text_color()

        # テキストは右寄せ
        area = status_item.area
        x, y = XURect.align_offset(area.w, area.h, system_font.text_width(text) + 5, 0, status_item.align, status_item.valign)
        if area.y+y < get_world_clip(XUWinInfo.find_parent_win(status_item)).bottom:
            pyxel.text(area.x + x, area.y + y, text, col, system_font.font)

    # ステータスタイトル(名前)
    @common_text.label("status_title")
    def status_title(status_title:text.XULabel, event:XUEvent):
        clip = get_world_clip(XUWinInfo.find_parent_win(status_title)).intersect(status_title.area)
        pyxel.rect(status_title.area.x, status_title.area.y, status_title.area.w, clip.h, 0)  # タイトルの下地

        col = get_text_color()

        # テキストは左寄せ
        if status_title.area.y < clip.bottom:  # world座標で比較
            x, y = status_title.aligned_pos(system_font)
            pyxel.text(x+1, y-1, user_data.data["name"], col, system_font.font)
