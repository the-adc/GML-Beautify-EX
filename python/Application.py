from tkinter import Tk, Button, Text, Frame, filedialog, END, Label
from gmlbeautifier import beautify, default_options

GML_KEYWORDS = [
    "var", "if", "else", "while", "for", "switch", "case", "break",
    "return", "function", "enum", "struct", "repeat", "with",
    "do", "until", "continue", "exit"
]

def beautify_gml():
    src = input_text.get("1.0", END)
    opts = default_options()
    opts.indent_with_tabs = True
    opts.indent_size = 1
    opts.brace_style = "expand"

    pretty_code = beautify(src, opts)

    output_text.delete("1.0", END)
    output_text.insert(END, pretty_code)

    lambda e: on_text_change(e, output_text, output_lines)

def save_file():
    file_path = filedialog.asksaveasfilename(
        title="Save GML Script",
        defaultextension=".gml",
        filetypes=[("GML Script", "*.gml;*.txt"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    content = output_text.get("1.0", END)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def load_file():
    file_path = filedialog.askopenfilename(
        title="Open GML Script",
        filetypes=[("GML Script", "*.gml;*.txt"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    input_text.delete("1.0", END)
    input_text.insert(END, content)

def copy_output():
    pretty_code = output_text.get("1.0", END)
    root.clipboard_clear()
    root.clipboard_append(pretty_code)

def update_line_numbers(text_widget, line_widget):
    line_widget.config(state="normal")
    line_widget.delete("1.0", END)

    total_lines = int(text_widget.index("end-1c").split(".")[0])
    line_numbers = "\n".join(str(i) for i in range(1, total_lines + 1))

    line_widget.insert("1.0", line_numbers)
    line_widget.config(state="disabled")

def on_text_change(event, text_widget, line_widget):
    update_line_numbers(text_widget, line_widget)
    highlight_syntax(text_widget)

def highlight_syntax(text_widget):
    text_widget.tag_remove("keyword", "1.0", END)
    text_widget.tag_remove("number", "1.0", END)
    text_widget.tag_remove("string", "1.0", END)
    text_widget.tag_remove("comment", "1.0", END)

    content = text_widget.get("1.0", END)

    for kw in GML_KEYWORDS:
        start = "1.0"
        while True:
            pos = text_widget.search(r"\m" + kw + r"\M", start, stopindex=END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(kw)}c"
            text_widget.tag_add("keyword", pos, end)
            start = end

    # Strings
    start = "1.0"
    while True:
        pos = text_widget.search(r"\".*?\"", start, stopindex=END, regexp=True)
        if not pos:
            break
        end = text_widget.index(pos + " lineend")
        text_widget.tag_add("string", pos, end)
        start = end

    # Numbers
    start = "1.0"
    while True:
        pos = text_widget.search(r"\m[0-9]+\M", start, stopindex=END, regexp=True)
        if not pos:
            break
        end = f"{pos}+1c"
        while text_widget.get(end) and text_widget.get(end).isdigit():
            end = text_widget.index(f"{end}+1c")
        text_widget.tag_add("number", pos, end)
        start = end

    # Comments
    start = "1.0"
    while True:
        pos = text_widget.search("//", start, stopindex=END)
        if not pos:
            break
        end = text_widget.index(pos + " lineend")
        text_widget.tag_add("comment", pos, end)
        start = end

if __name__ == "__main__":
    root = Tk()
    root.title("GML Beautify EX - Unstable Prototype v0.1")
    root.geometry("1200x700")

    # Use a custom title bar (remove OS title bar)
    root.overrideredirect(True)

    # Allow programmatic resizing (useful even with overrideredirect)
    root.resizable(True, True)

    # Colors
    TITLE_BG = "#0E1621"
    TITLE_FG = "#E6EEF3"
    TITLE_BTN_BG = "#0E1621"
    TITLE_BTN_HOVER = "#173E52"

    BG = "#0E1621"
    FG = "#e5e5e5"
    LINE_BG = "#313C49"
    KEYWORD = "#569cd6"
    STRING = "#ce9178"
    NUMBER = "#b5cea8"
    COMMENT = "#6a9955"

    root.configure(bg=BG)

    # Custom title bar
    title_bar = Frame(root, bg=TITLE_BG, relief="flat", bd=0)
    title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

    title_label = Label(title_bar, text="GML Beautify EX - Unstable Prototype v0.1", bg=TITLE_BG, fg=TITLE_FG)
    title_label.pack(side="left", padx=10, pady=6)

    is_maximized = False
    prev_geometry = None

    def on_close():
        root.destroy()

    def on_minimize():
        root.update_idletasks()
        root.overrideredirect(False)
        root.iconify()

    def on_restore(event=None):
        # Called when window is deiconified: reapply overrideredirect
        root.overrideredirect(True)

    def toggle_maximize():
        global is_maximized, prev_geometry
        if not is_maximized:
            # store previous geometry and maximize to screen size (simulate maximize with overrideredirect)
            prev_geometry = root.geometry()
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            # leave a small gap for taskbar safety on some systems
            root.geometry(f"{sw}x{sh}+0+0")
            is_maximized = True
            btn_max.config(text="❐")  # restore icon
        else:
            if prev_geometry:
                root.geometry(prev_geometry)
            is_maximized = False
            btn_max.config(text="▢")
        # update resize handles visibility
        _update_resize_handles_visibility()

    def make_btn(text, command):
        btn = Button(title_bar, text=text, bg=TITLE_BTN_BG, fg=TITLE_FG, bd=0, padx=8, pady=3, command=command)
        def on_enter(e):
            btn.config(bg=TITLE_BTN_HOVER)
        def on_leave(e):
            btn.config(bg=TITLE_BTN_BG)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    btn_close = make_btn("✕", on_close)
    btn_close.pack(side="right", padx=(0,6), pady=4)

    btn_max = make_btn("▢", toggle_maximize)
    btn_max.pack(side="right", padx=(0,4), pady=4)

    btn_min = make_btn("—", on_minimize)
    btn_min.pack(side="right", padx=(0,4), pady=4)

    # Allow dragging the window by the title bar and label
    def start_move(event):
        # ignore drag when maximized
        if is_maximized:
            return
        root._drag_start_x = event.x_root
        root._drag_start_y = event.y_root
        root._win_x = root.winfo_x()
        root._win_y = root.winfo_y()

    def on_move(event):
        if is_maximized:
            return
        dx = event.x_root - root._drag_start_x
        dy = event.y_root - root._drag_start_y
        new_x = root._win_x + dx
        new_y = root._win_y + dy
        root.geometry(f"+{new_x}+{new_y}")

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<B1-Motion>", on_move)
    title_label.bind("<ButtonPress-1>", start_move)
    title_label.bind("<B1-Motion>", on_move)

    # Reapply overrideredirect after restoring from minimized state
    root.bind("<Map>", on_restore)

    # Create a grid layout with 2 columns
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)  # main content is now row 1

    # Left Panel
    left_frame = Frame(root, bg=BG)
    left_frame.grid(row=1, column=0, sticky="nsew")
    left_frame.rowconfigure(0, weight=1)
    left_frame.columnconfigure(1, weight=1)

    input_lines = Text(left_frame, width=4, bg=LINE_BG, fg=FG, state="disabled")
    input_lines.grid(row=0, column=0, sticky="ns")

    input_text = Text(left_frame, wrap="none", bg=BG, fg=FG, insertbackground=FG)
    input_text.grid(row=0, column=1, sticky="nsew")

    # Right Panel
    right_frame = Frame(root, bg=BG)
    right_frame.grid(row=1, column=1, sticky="nsew")
    right_frame.rowconfigure(0, weight=1)
    right_frame.columnconfigure(1, weight=1)

    output_lines = Text(right_frame, width=4, bg=LINE_BG, fg=FG, state="disabled")
    output_lines.grid(row=0, column=0, sticky="ns")

    output_text = Text(right_frame, wrap="none", bg=BG, fg=FG, insertbackground=FG)
    output_text.grid(row=0, column=1, sticky="nsew")

    # Syntax Highlight Tag Config
    for widget in (input_text, output_text):
        widget.tag_config("keyword", foreground=KEYWORD)
        widget.tag_config("string", foreground=STRING)
        widget.tag_config("number", foreground=NUMBER)
        widget.tag_config("comment", foreground=COMMENT)

    # Buttons
    button_frame = Frame(root, bg=BG)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)  # moved down to row 2

    Button(button_frame, text="Beautify", bg=BG, fg=FG, command=beautify_gml).grid(row=0, column=0, padx=10)
    Button(button_frame, text="Load", bg=BG, fg=FG, command=load_file).grid(row=0, column=1, padx=10)
    Button(button_frame, text="Save", bg=BG, fg=FG, command=save_file).grid(row=0, column=2, padx=10)
    Button(button_frame, text="Copy", bg=BG, fg=FG, command=copy_output).grid(row=0, column=3, padx=10)

    input_text.bind("<KeyRelease>", lambda e: on_text_change(e, input_text, input_lines))
    output_text.bind("<KeyRelease>", lambda e: on_text_change(e, output_text, output_lines))

    # --- Resizing handles (right, bottom, bottom-right corner) ---
    RESIZE_BORDER = 6
    min_width = 400
    min_height = 200

    right_handle = Frame(root, cursor="size_we", bg=BG)
    bottom_handle = Frame(root, cursor="size_ns", bg=BG)
    corner_handle = Frame(root, cursor="size_nw_se", bg=BG)

    # place handles with relative sizes so they follow window resizing
    right_handle.place(relx=1.0, rely=0.0, anchor="ne", relheight=1.0, width=RESIZE_BORDER)
    bottom_handle.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0, height=RESIZE_BORDER)
    corner_handle.place(relx=1.0, rely=1.0, anchor="se", width=RESIZE_BORDER, height=RESIZE_BORDER)

    _resize_data = {}

    def _start_resize(event, mode):
        if is_maximized:
            return
        _resize_data["mode"] = mode
        _resize_data["start_x"] = event.x_root
        _resize_data["start_y"] = event.y_root
        geom = root.geometry().split("+")[0]
        w, h = geom.split("x")
        _resize_data["start_w"] = int(w)
        _resize_data["start_h"] = int(h)
        _resize_data["start_win_x"] = root.winfo_x()
        _resize_data["start_win_y"] = root.winfo_y()

    def _do_resize(event):
        if not _resize_data:
            return
        dx = event.x_root - _resize_data["start_x"]
        dy = event.y_root - _resize_data["start_y"]
        mode = _resize_data["mode"]

        new_w = _resize_data["start_w"]
        new_h = _resize_data["start_h"]
        new_x = _resize_data["start_win_x"]
        new_y = _resize_data["start_win_y"]

        if mode in ("right", "corner"):
            new_w = max(min_width, _resize_data["start_w"] + dx)
        if mode in ("bottom", "corner"):
            new_h = max(min_height, _resize_data["start_h"] + dy)

        root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")

    # Bindings
    right_handle.bind("<ButtonPress-1>", lambda e: _start_resize(e, "right"))
    right_handle.bind("<B1-Motion>", _do_resize)
    bottom_handle.bind("<ButtonPress-1>", lambda e: _start_resize(e, "bottom"))
    bottom_handle.bind("<B1-Motion>", _do_resize)
    corner_handle.bind("<ButtonPress-1>", lambda e: _start_resize(e, "corner"))
    corner_handle.bind("<B1-Motion>", _do_resize)

    def _update_resize_handles_visibility():
        if is_maximized:
            right_handle.place_forget()
            bottom_handle.place_forget()
            corner_handle.place_forget()
        else:
            right_handle.place(relx=1.0, rely=0.0, anchor="ne", relheight=1.0, width=RESIZE_BORDER)
            bottom_handle.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0, height=RESIZE_BORDER)
            corner_handle.place(relx=1.0, rely=1.0, anchor="se", width=RESIZE_BORDER, height=RESIZE_BORDER)

    # Ensure handles are positioned correctly whenever window config changes
    def _on_configure(event):
        # keep handles updated (place uses rel sizes so it follows automatically, but ensure visibility)
        _update_resize_handles_visibility()

    root.bind("<Configure>", _on_configure)

    _update_resize_handles_visibility()
    # --- end resizing handles ---

    root.mainloop()