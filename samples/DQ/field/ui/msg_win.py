from xmlui.core import XMLUI,XUEvent,XUWinInfo

import msg_dq
from msg_dq import MsgDQ

def ui_init(xmlui:XMLUI):
    field_dq = msg_dq.Decorator(xmlui)

    # フィールド画面のメッセージウインドウ
    # ---------------------------------------------------------
    @field_dq.msg_dq("msg_text")
    def msg_text(msg_text:MsgDQ, event:XUEvent):
        # メッセージ共通処理
        msg_text.draw(event, True)

        # 自分が閉じたらメニューごと閉じる
        if XUWinInfo.find_parent_win(msg_text).win_state == XUWinInfo.WIN_STATE.CLOSED:
            XUWinInfo(msg_text.xmlui.find_by_id("menu")).setter.start_close()

        # 入力アクション
        # ---------------------------------------------------------
        if event.check_trg(XUEvent.Key.BTN_A) or event.check_now(XUEvent.Key.BTN_B):
            if msg_text.is_all_finish:
                XUWinInfo.find_parent_win(msg_text).setter.start_close()  # 閉じる
                return

            if msg_text.is_next_wait:
                msg_text.page_no += 1  # 次ページへ
                return
