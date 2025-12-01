from tkinter import Tk, ttk, Text, Frame, filedialog, END
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
    root.title("GML Beautify EX")
    root.geometry("1200x700")

    BG = "#1e1e1e"
    FG = "#e5e5e5"
    LINE_BG = "#2d2d2d"
    KEYWORD = "#569cd6"
    STRING = "#ce9178"
    NUMBER = "#b5cea8"
    COMMENT = "#6a9955"

    root.configure(bg=BG)

    # Create a grid layout with 2 columns
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    # Left Panel
    left_frame = Frame(root, bg=BG)
    left_frame.grid(row=0, column=0, sticky="nsew")
    left_frame.rowconfigure(0, weight=1)
    left_frame.columnconfigure(1, weight=1)

    input_lines = Text(left_frame, width=4, bg=LINE_BG, fg=FG, state="disabled")
    input_lines.grid(row=0, column=0, sticky="ns")

    input_text = Text(left_frame, wrap="none", bg=BG, fg=FG, insertbackground=FG)
    input_text.grid(row=0, column=1, sticky="nsew")

    # Right Panel
    right_frame = Frame(root, bg=BG)
    right_frame.grid(row=0, column=1, sticky="nsew")
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
    button_frame.grid(row=1, column=0, columnspan=2, pady=10)

    ttk.Button(button_frame, text="Beautify", command=beautify_gml).grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Load", command=load_file).grid(row=0, column=1, padx=10)
    ttk.Button(button_frame, text="Save", command=save_file).grid(row=0, column=2, padx=10)
    ttk.Button(button_frame, text="Copy", command=copy_output).grid(row=0, column=3, padx=10)

    input_text.bind("<KeyRelease>", lambda e: on_text_change(e, input_text, input_lines))
    output_text.bind("<KeyRelease>", lambda e: on_text_change(e, output_text, output_lines))

    root.mainloop()