import ctypes
import tkinter as tk
from tkinter import messagebox, ttk

from pythonosc.udp_client import SimpleUDPClient

# 键位定义：显示字符 -> Tk 绑定键 -> Windows 虚拟键码 -> 参数名
KEYS = (
    {"label": "1", "bind": "1", "vk": 0x31, "param": "Emote1"},
    {"label": "2", "bind": "2", "vk": 0x32, "param": "Emote2"},
    {"label": "3", "bind": "3", "vk": 0x33, "param": "Emote3"},
    {"label": "4", "bind": "4", "vk": 0x34, "param": "Emote4"},
    {"label": "5", "bind": "5", "vk": 0x35, "param": "Emote5"},
    {"label": "6", "bind": "6", "vk": 0x36, "param": "Emote6"},
    {"label": "7", "bind": "7", "vk": 0x37, "param": "Emote7"},
    {"label": "8", "bind": "8", "vk": 0x38, "param": "Emote8"},
    {"label": "9", "bind": "9", "vk": 0x39, "param": "Emote9"},
    {"label": "0", "bind": "0", "vk": 0x30, "param": "Emote10"},
    {"label": "-", "bind": "minus", "vk": 0xBD, "param": "Emote11"},  # VK_OEM_MINUS
    {"label": "+", "bind": "plus", "vk": 0xBB, "param": "Emote12"},   # VK_OEM_PLUS
)


class OSCToggleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VRC OSC 快捷键面板")
        self.root.geometry("820x520")
        self.root.resizable(False, False)

        # 配色
        self.colors = {
            "bg": "#f5f6f7",
            "card": "#ffffff",
            "primary": "#0052d9",
            "text": "#1f2430",
            "muted": "#7a8499",
            "tile_off_bg": "#f2f3f5",
            "tile_on_bg": "#e0eaff",
        }

        self.ip_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.IntVar(value=9000)
        self.prefix_var = tk.StringVar(value="/avatar/parameters/")
        self.mode_toggle = tk.BooleanVar(value=False)  # False=按住开关，True=单击切换
        self.allow_stack = tk.BooleanVar(value=True)   # True=允许叠加
        self.allow_background = tk.BooleanVar(value=True)  # True=后台也捕捉
        self.user32 = getattr(ctypes, "windll", None).user32 if hasattr(ctypes, "windll") else None

        self.pressed = {key["label"]: False for key in KEYS}
        self.physical_state = {key["label"]: False for key in KEYS}
        self.key_map = {key["label"]: key for key in KEYS}

        self._configure_styles()
        self.root.configure(bg=self.colors["bg"])
        self._build_ui()
        self._bind_keys()
        self.client = SimpleUDPClient(self.ip_var.get(), self.port_var.get())
        self._start_poll()

    @staticmethod
    def _round_rect_points(x1: int, y1: int, x2: int, y2: int, r: int):
        return [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]

    def _round_rect(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, r: int, **kwargs):
        pts = self._round_rect_points(x1, y1, x2, y2, r)
        return canvas.create_polygon(pts, smooth=True, **kwargs)

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

    def _rounded_entry(self, parent, textvariable, width_px: int = 180):
        height = 40
        radius = 12
        canvas = tk.Canvas(
            parent,
            width=width_px,
            height=height,
            bg=self.colors["card"],
            highlightthickness=0,
            bd=0,
        )
        self._round_rect(
            canvas,
            1,
            1,
            width_px - 1,
            height - 1,
            radius,
            fill=self.colors["tile_off_bg"],
            outline=self.colors["tile_off_bg"],
        )
        entry = tk.Entry(
            canvas,
            textvariable=textvariable,
            relief="flat",
            bd=0,
            bg=self.colors["tile_off_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
        )
        canvas.create_window(width_px // 2, height // 2, window=entry, width=width_px - 20)
        # 点击外部可取消焦点：在容器层绑定 focus_set 到根
        def unfocus(event):  # noqa: ANN001
            if event.widget not in (entry, canvas):
                self.root.focus_set()

        self.root.bind("<Button-1>", unfocus, add="+")
        return canvas

    def _rounded_button(self, parent, text: str, command, width_px: int = 180, active: bool = True):
        height = 44
        radius = 14
        fill = self.colors["primary"] if active else self.colors["tile_off_bg"]
        text_color = "#ffffff" if active else self.colors["text"]
        canvas = tk.Canvas(
            parent,
            width=width_px,
            height=height,
            bg=self.colors["card"],
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        rect = self._round_rect(
            canvas,
            1,
            1,
            width_px - 1,
            height - 1,
            radius,
            fill=fill,
            outline=fill,
        )
        label = canvas.create_text(
            width_px // 2,
            height // 2,
            text=text,
            fill=text_color,
            font=("Segoe UI", 10, "bold"),
        )

        def on_enter(_e):
            hover = "#1a61e6" if canvas.active else "#d6d9e0"
            canvas.itemconfig(rect, fill=hover, outline=hover)

        def on_leave(_e):
            base = self.colors["primary"] if canvas.active else self.colors["tile_off_bg"]
            canvas.itemconfig(rect, fill=base, outline=base)

        def on_click(_e):
            if command:
                command()

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<ButtonRelease-1>", lambda _e: on_leave(None))
        canvas.label = label  # keep reference
        canvas.rect_id = rect
        canvas.active = active
        return canvas

    def _set_button_active(self, canvas: tk.Canvas, active: bool):
        fill = self.colors["primary"] if active else self.colors["tile_off_bg"]
        text_color = "#ffffff" if active else self.colors["text"]
        canvas.itemconfig(canvas.rect_id, fill=fill, outline=fill)
        canvas.itemconfig(canvas.label, fill=text_color)
        canvas.active = active

    def _build_ui(self):
        wrapper = tk.Frame(self.root, bg=self.colors["bg"])
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(wrapper, bg=self.colors["card"], bd=0, relief="flat", highlightthickness=0)
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg=self.colors["card"])
        header.pack(fill="x", padx=16, pady=(16, 10))
        tk.Label(
            header,
            text="OSC 快捷键控制",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"],
        ).pack(anchor="w")
        tk.Label(
            header,
            text="简洁客户端 · 方形按键指示 · 前后台均可响应",
            font=("Segoe UI", 10),
            fg=self.colors["muted"],
            bg=self.colors["card"],
        ).pack(anchor="w", pady=(4, 0))

        form = tk.Frame(card, bg=self.colors["card"])
        form.pack(fill="x", padx=16, pady=(4, 8))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)

        tk.Label(form, text="OSC IP", fg=self.colors["text"], bg=self.colors["card"]).grid(
            row=0, column=0, sticky="w", pady=6
        )
        ip_entry = self._rounded_entry(form, self.ip_var, width_px=190)
        ip_entry.grid(row=0, column=1, sticky="w", pady=6, padx=(8, 4))

        tk.Label(form, text="端口", fg=self.colors["text"], bg=self.colors["card"]).grid(
            row=0, column=2, sticky="w", padx=(12, 4), pady=6
        )
        port_entry = self._rounded_entry(form, self.port_var, width_px=100)
        port_entry.grid(row=0, column=3, sticky="w", pady=6)

        tk.Label(form, text="地址前缀", fg=self.colors["text"], bg=self.colors["card"]).grid(
            row=1, column=0, sticky="w", pady=6
        )
        prefix_entry = self._rounded_entry(form, self.prefix_var, width_px=240)
        prefix_entry.grid(row=1, column=1, columnspan=2, sticky="we", pady=6, padx=(8, 4))

        self.update_btn = self._rounded_button(form, "更新 OSC 目标", self._update_client, width_px=130, active=True)
        self.update_btn.grid(row=1, column=3, sticky="e", pady=6)

        controls = tk.Frame(card, bg=self.colors["card"])
        controls.pack(fill="x", padx=16, pady=(0, 12))

        self.mode_btn = self._rounded_button(controls, "", self._toggle_mode, width_px=210, active=self.mode_toggle.get())
        self.mode_btn.pack(side="left", pady=(0, 8))
        self._update_mode_button_text()

        self.stack_btn = self._rounded_button(
            controls,
            "",
            self._toggle_stack,
            width_px=190,
            active=self.allow_stack.get(),
        )
        self.stack_btn.pack(side="left", padx=(12, 0), pady=(0, 8))
        self._update_stack_button_text()

        self.bg_btn = self._rounded_button(
            controls,
            "",
            self._toggle_background,
            width_px=230,
            active=self.allow_background.get(),
        )
        self.bg_btn.pack(side="left", padx=(12, 0), pady=(0, 8))
        self._update_background_button_text()

        grid_card = tk.Frame(card, bg=self.colors["card"])
        grid_card.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        grid = tk.Frame(grid_card, bg=self.colors["card"])
        grid.pack(fill="x")

        self.tiles = {}
        for idx, key in enumerate(KEYS):
            row, col = divmod(idx, 6)
            tile_w, tile_h, radius = 110, 90, 14
            tile_canvas = tk.Canvas(
                grid,
                width=tile_w,
                height=tile_h,
                bg=self.colors["card"],
                highlightthickness=0,
                bd=0,
            )
            rect = self._round_rect(
                tile_canvas,
                2,
                2,
                tile_w - 2,
                tile_h - 2,
                radius,
                fill=self.colors["tile_off_bg"],
                outline=self.colors["tile_off_bg"],
            )
            text = tile_canvas.create_text(
                tile_w // 2,
                tile_h // 2,
                text=f"{key['label']} · {key['param']}\nOFF",
                fill=self.colors["muted"],
                font=("Segoe UI", 12, "bold"),
                justify="center",
            )
            tile_canvas.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.tiles[key["label"]] = {"canvas": tile_canvas, "rect": rect, "text": text}

        for i in range(6):
            grid.columnconfigure(i, weight=1)

        self.log_var = tk.StringVar(value="等待按键...")
        tk.Label(
            grid_card,
            textvariable=self.log_var,
            fg=self.colors["muted"],
            bg=self.colors["card"],
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(4, 6))

        help_text = (
            "提示：数字键 1-9、0、-、+ 对应 Emote1-Emote12，前后台均可触发。\n"
            "模式按钮：按住=发送 True/松开 False；点按=切换开关。\n"
            "表情叠加：开启则允许多个同时开启，关闭则新按键会先关闭其它已开。\n"
            "OSC 地址示例：/avatar/parameters/Emote1"
        )
        tk.Label(
            card,
            text=help_text,
            fg=self.colors["muted"],
            bg=self.colors["card"],
            font=("Segoe UI", 10),
            justify="left",
        ).pack(fill="x", padx=16, pady=(0, 16))

    def _bind_keys(self):
        for key in KEYS:
            self.root.bind(
                f"<KeyPress-{key['bind']}>",
                lambda e, k=key["label"]: self._process_physical_state(k, True),
            )
            self.root.bind(
                f"<KeyRelease-{key['bind']}>",
                lambda e, k=key["label"]: self._process_physical_state(k, False),
            )

    def _start_poll(self):
        if not self.user32:
            self.log_var.set("当前环境不支持全局按键轮询")
            return

        if not self.allow_background.get():
            self.root.after(20, self._start_poll)
            return

        for key in KEYS:
            state = self.user32.GetAsyncKeyState(key["vk"])
            is_down = bool(state & 0x8000)
            self._process_physical_state(key["label"], is_down)

        self.root.after(20, self._start_poll)  # 约 50fps

    def _update_client(self):
        try:
            self.client = SimpleUDPClient(self.ip_var.get(), int(self.port_var.get()))
            self.log_var.set(f"已更新 OSC 目标: {self.ip_var.get()}:{self.port_var.get()}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("错误", f"无法更新 OSC 目标: {exc}")

    def _process_physical_state(self, key: str, is_down: bool):
        # 仅在物理状态变化时才处理，避免重复触发
        if self.physical_state[key] == is_down:
            return
        self.physical_state[key] = is_down
        self._handle_key(key, is_down)

    def _handle_key(self, key: str, is_down: bool):
        if self.mode_toggle.get():
            # 点一下切换：仅在按下时翻转状态
            if not is_down:
                return
            new_state = not self.pressed[key]
            self._apply_state(key, new_state)
        else:
            # 按住生效，松开关闭
            self._apply_state(key, is_down)

    def _apply_state(self, key: str, state: bool):
        if state and not self.allow_stack.get():
            for other in list(self.pressed.keys()):
                if other != key and self.pressed[other]:
                    self.pressed[other] = False
                    self._send_parameter(self.key_map[other]["param"], False)
                    self._set_label(other, False)

        if self.pressed[key] == state:
            return

        self.pressed[key] = state
        self._send_parameter(self.key_map[key]["param"], state)
        self._set_label(key, state)

    def _send_parameter(self, name: str, value: bool):
        addr = f"{self.prefix_var.get().rstrip('/')}/{name}"
        try:
            self.client.send_message(addr, value)
            self.log_var.set(f"发送 {addr} = {value}")
        except Exception as exc:  # noqa: BLE001
            self.log_var.set(f"发送失败: {exc}")

    def _set_label(self, key: str, on: bool):
        tile = self.tiles[key]
        canvas = tile["canvas"]
        if on:
            canvas.itemconfig(tile["rect"], fill=self.colors["tile_on_bg"], outline=self.colors["tile_on_bg"])
            canvas.itemconfig(
                tile["text"],
                text=f"{key} · {self.key_map[key]['param']}\nON",
                fill=self.colors["primary"],
            )
        else:
            canvas.itemconfig(tile["rect"], fill=self.colors["tile_off_bg"], outline=self.colors["tile_off_bg"])
            canvas.itemconfig(
                tile["text"],
                text=f"{key} · {self.key_map[key]['param']}\nOFF",
                fill=self.colors["muted"],
            )

    def _toggle_mode(self):
        self.mode_toggle.set(not self.mode_toggle.get())
        self._update_mode_button_text()
        self.log_var.set("已切换为点按切换模式" if self.mode_toggle.get() else "已切换为按住开启模式")
        # 如果切回长按模式，立即同步：物理已松开的按键应被关闭
        if not self.mode_toggle.get():
            for key in list(self.pressed.keys()):
                if self.pressed[key] and not self.physical_state.get(key, False):
                    self._apply_state(key, False)

    def _update_mode_button_text(self):
        on = self.mode_toggle.get()
        text = "模式：切换模式" if on else "模式：长按模式"
        if hasattr(self, "mode_btn") and hasattr(self.mode_btn, "label"):
            self.mode_btn.itemconfig(self.mode_btn.label, text=text)
            self._set_button_active(self.mode_btn, on)

    def _toggle_stack(self):
        self.allow_stack.set(not self.allow_stack.get())
        self._update_stack_button_text()
        self.log_var.set("已开启表情叠加" if self.allow_stack.get() else "已关闭表情叠加")

    def _update_stack_button_text(self):
        on = self.allow_stack.get()
        text = "表情叠加：开启" if on else "表情叠加：关闭"
        if hasattr(self, "stack_btn") and hasattr(self.stack_btn, "label"):
            self.stack_btn.itemconfig(self.stack_btn.label, text=text)
            self._set_button_active(self.stack_btn, on)

    def _toggle_background(self):
        self.allow_background.set(not self.allow_background.get())
        self._update_background_button_text()
        self.log_var.set("允许后台捕捉按键" if self.allow_background.get() else "后台捕捉已关闭，仅前台响应")

    def _update_background_button_text(self):
        on = self.allow_background.get()
        text = "后台捕捉：开启" if on else "后台捕捉：关闭"
        if hasattr(self, "bg_btn") and hasattr(self.bg_btn, "label"):
            self.bg_btn.itemconfig(self.bg_btn.label, text=text)
            self._set_button_active(self.bg_btn, on)


def main():
    root = tk.Tk()
    app = OSCToggleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
