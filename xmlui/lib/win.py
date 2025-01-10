from xmlui.core import *

# コレは外だし
class _XUWinFrameBase(XUWinBase):
    # ウインドウ(ピクセル)描画
    # 0 1 2
    # 3 4 5
    # 6 7 8
    # -----------------------------------------------------
    # 枠外は-1を返す
    def _get_pattern_index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        raise NotImplementedError("no implements")
    

    # 1,3,5,7,4のエリア(カド以外)は特に計算が必要ない
    def _get13574index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        return [-1, y, -1, x, size-1, w-1-x, -1, h-1-y][self.get_area(size, x, y, w, h)]

    # どのエリアに所属するかを返す
    def get_area(self, size:int, x:int, y:int, w:int, h:int) -> int:
        if x < size:
            if y < size:
                return 0
            return 3 if y < h-size else 6
        elif x < w-size:
            if y < size:
                return 1
            return 4 if y < h-size else 7
        else:
            if y < size:
                return 2
            return 5 if y < h-size else 8

    # フレームだけバッファに書き込む。中央部分塗りつぶしは呼び出し側で行う
    def draw_frame(self, screen_buf:bytearray, pattern:list[int], screen_area:XURect, clip:XURect|None=None):
        screen_buf_w = self.xmlui.screen_w  # バッファサイズは画面幅で確定(繰り返し使うのでキャッシュ)

        # 画面外に描画しない
        screen_area = screen_area.intersect(XURect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h))

        # オフセットなので0,0～w,h
        area = screen_area.to_offset()
        clip = clip.intersect(area) if clip else area
        if clip.is_empty:
            return

        size = len(pattern)
        pat_bytes = bytes(pattern)
        rev_butes = bytes(reversed(pat_bytes))

        # 角の描画
        # ---------------------------------------------------------------------
        def _draw_shoulder(self, off_x:int, off_y:int, pattern:bytes):
           # クリップチェック
            if clip.contains(off_x, off_y):
                index = self._get_pattern_index(size, off_x, off_y, area.w, area.h)
                if index >= 0:  # 枠外チェック
                    screen_buf[(screen_area.y + off_y)*screen_buf_w + (screen_area.x + off_x)] = pattern[index]

        for y_ in range(size):
            for x_ in range(size):
                _draw_shoulder(self, x_, y_, pat_bytes)  # 左上
                _draw_shoulder(self, area.w-1-x_, y_, pat_bytes)  # 右上
                _draw_shoulder(self, x_, area.h-1-y_, rev_butes)  # 左下
                _draw_shoulder(self, area.w-1-x_, area.h-1-y_, rev_butes)  # 右下

        # bytearrayによる角以外の高速描画(patternキャッシュを作ればもっと速くなるかも)
        # ---------------------------------------------------------------------
        # 上下のライン
        line_clip = clip.inflate(-size, 0)
        if not line_clip.is_empty:
            for y_ in range(size):
                # 上
                if line_clip.contains_y(y_):
                    offset = (screen_area.y + y_)*screen_buf_w + screen_area.x
                    screen_buf[offset+line_clip.x: offset+line_clip.right] = pat_bytes[y_:y_+1] * line_clip.w
                # 下
                if line_clip.contains_y(area.h-1-y_):
                    offset = (screen_area.bottom-1-y_)*screen_buf_w + screen_area.x
                    screen_buf[offset+line_clip.x: offset+line_clip.right] = rev_butes[y_:y_+1] * line_clip.w

        # 左
        left_clip = clip.intersect(XURect(0, 0, size, area.h).inflate(0, -size))
        if not left_clip.is_empty:
            for y_ in range(area.h):
                if left_clip.contains_y(y_):
                    offset = (screen_area.y + y_)*screen_buf_w + screen_area.x
                    screen_buf[offset:offset+left_clip.w] = pat_bytes[:left_clip.w]

        # 右
        right_clip = clip.intersect(XURect(area.w-size, 0, size, area.h).inflate(0, -size))
        if not right_clip.is_empty:
            for y_ in range(area.h):
                if right_clip.contains_y(y_):
                    offset = (screen_area.y + y_)*screen_buf_w + screen_area.x + area.w-size
                    screen_buf[offset:offset+right_clip.w] = rev_butes[:right_clip.w]

class XURoundFrame(_XUWinFrameBase):
    def _get_veclen(self, x:int, y:int, org_x:int, org_y:int) -> int:
        return math.ceil(math.sqrt((x-org_x)**2 + (y-org_y)**2))

    # override
    def _get_pattern_index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        match self.get_area(size, x, y, w, h):
            case 0:
                l = size-1-self._get_veclen(x, y, size-1, size-1)
                return l if l < size else -1
            case 2:
                l = size-1-self._get_veclen(x, y, w-size, size-1)
                return l if l < size else -1
            case 6:
                l = size-1-self._get_veclen(x, y, size-1, h-size)
                return l if l < size else -1
            case 8:
                l = size-1-self._get_veclen(x, y, w-size, h-size)
                return l if l < size else -1
        return self._get13574index(size, x, y, w, h)

class XURectFrame(_XUWinFrameBase):
    # override
    def _get_pattern_index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        match self.get_area(size, x, y, w, h):
            case 0:
                return y if x > y else x
            case 2:
                return y if w-1-x > y else w-1-x
            case 6:
                y = h-1-y
                return y if x > y else size-1-x
            case 8:
                x = w-1-x
                y = h-1-y
                return y if x > y else size-1-x
        return self._get13574index(size, x, y, w, h)


# デコレータを用意
# *****************************************************************************
class Decorator(XMLUI.HasRef):
    def round_frame(self, tag_name:str):
        def wrapper(bind_func:Callable[[XURoundFrame,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                frame = XURoundFrame(elem)
                frame.update()
                return bind_func(frame, event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper

    def rect_frame(self, tag_name:str):
        def wrapper(bind_func:Callable[[XURectFrame,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                frame = XURectFrame(elem)
                frame.update()
                return bind_func(frame, event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper
