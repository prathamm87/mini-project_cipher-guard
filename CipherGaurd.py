import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# CIPHERGUARD
# GUI designed to closely match the requested reference image
# ============================================================

BG = "#F5F8FD"
NAVY = "#172B55"
BLUE = "#2457A6"
GREEN = "#18A56F"
PURPLE = "#7167DE"
WHITE = "#FFFFFF"
LIGHT_GREEN = "#F1FCF8"
LIGHT_BLUE = "#EEF7FF"
LIGHT_PURPLE = "#F7F5FF"
BORDER = "#C9D8EC"
TEXT = "#18335F"
MUTED = "#64748B"


# ------------------------- CIPHERS -------------------------

def caesar_encrypt(text, key):
    result = ""
    steps = []

    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            new_ch = chr((ord(ch) - base + key) % 26 + base)
            result += new_ch
            steps.append((ch, f"+{key}", new_ch))
        else:
            result += ch
            steps.append((ch, "-", ch))

    return result, steps


def caesar_decrypt(text, key):
    result = ""
    steps = []

    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            new_ch = chr((ord(ch) - base - key) % 26 + base)
            result += new_ch
            steps.append((ch, f"-{key}", new_ch))
        else:
            result += ch
            steps.append((ch, "-", ch))

    return result, steps


def create_playfair_matrix(key):
    key = "".join(c for c in key.upper() if c.isalpha())
    key = key.replace("J", "I")

    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    letters = ""

    for c in key + alphabet:
        if c not in letters:
            letters += c

    return [letters[i:i + 5] for i in range(0, 25, 5)]


def playfair_positions(matrix):
    pos = {}

    for r in range(5):
        for c in range(5):
            pos[matrix[r][c]] = (r, c)

    return pos


def prepare_playfair(text):
    text = "".join(c for c in text.upper() if c.isalpha())
    text = text.replace("J", "I")

    pairs = []
    i = 0

    while i < len(text):
        a = text[i]

        if i + 1 >= len(text):
            pairs.append(a + "X")
            i += 1
        elif text[i] == text[i + 1]:
            pairs.append(a + "X")
            i += 1
        else:
            pairs.append(a + text[i + 1])
            i += 2

    return pairs


def playfair_encrypt(text, key):
    matrix = create_playfair_matrix(key)
    pos = playfair_positions(matrix)
    pairs = prepare_playfair(text)

    result = ""
    steps = []

    for pair in pairs:
        a, b = pair
        r1, c1 = pos[a]
        r2, c2 = pos[b]

        if r1 == r2:
            x = matrix[r1][(c1 + 1) % 5]
            y = matrix[r2][(c2 + 1) % 5]
            rule = "Same row -> move right"
        elif c1 == c2:
            x = matrix[(r1 + 1) % 5][c1]
            y = matrix[(r2 + 1) % 5][c2]
            rule = "Same column -> move down"
        else:
            x = matrix[r1][c2]
            y = matrix[r2][c1]
            rule = "Rectangle -> swap columns"

        result += x + y
        steps.append((pair, x + y, rule))

    return result, matrix, steps


def playfair_decrypt(text, key):
    matrix = create_playfair_matrix(key)
    pos = playfair_positions(matrix)

    text = "".join(c for c in text.upper() if c.isalpha())
    text = text.replace("J", "I")

    if len(text) % 2:
        text += "X"

    result = ""
    steps = []

    for i in range(0, len(text), 2):
        a, b = text[i], text[i + 1]

        r1, c1 = pos[a]
        r2, c2 = pos[b]

        if r1 == r2:
            x = matrix[r1][(c1 - 1) % 5]
            y = matrix[r2][(c2 - 1) % 5]
            rule = "Same row -> move left"
        elif c1 == c2:
            x = matrix[(r1 - 1) % 5][c1]
            y = matrix[(r2 - 1) % 5][c2]
            rule = "Same column -> move up"
        else:
            x = matrix[r1][c2]
            y = matrix[r2][c1]
            rule = "Rectangle -> swap columns"

        result += x + y
        steps.append((a + b, x + y, rule))

    return result, matrix, steps


def rail_encrypt(text, rails):
    if rails <= 1:
        return text, []

    fence = [""] * rails
    rail = 0
    direction = 1
    steps = []

    for ch in text:
        fence[rail] += ch

        if ch != " ":
            steps.append((ch, rail + 1))

        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1

        rail += direction

    return "".join(fence), steps


def rail_decrypt(cipher, rails):
    if rails <= 1:
        return cipher, []

    pattern = []
    rail = 0
    direction = 1

    for _ in cipher:
        pattern.append(rail)

        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1

        rail += direction

    counts = [pattern.count(i) for i in range(rails)]
    fence = []
    index = 0

    for count in counts:
        fence.append(list(cipher[index:index + count]))
        index += count

    positions = [0] * rails
    result = ""
    steps = []

    for r in pattern:
        ch = fence[r][positions[r]]
        result += ch

        if ch != " ":
            steps.append((ch, r + 1))

        positions[r] += 1

    return result, steps


# ------------------------- HELPERS -------------------------

def set_text(widget, text, readonly=False):
    if readonly:
        widget.config(state="normal")

    widget.delete("1.0", tk.END)
    widget.insert("1.0", text)

    if readonly:
        widget.config(state="disabled")


def show_result(text):
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.insert("1.0", text.upper())
    result_box.config(state="disabled")


def copy_result():
    text = result_box.get("1.0", tk.END).strip()

    if not text:
        messagebox.showinfo("Copy Result", "There is no result to copy.")
        return

    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

    status_var.set("Result copied to clipboard.")


def clear_all():
    message_box.delete("1.0", tk.END)

    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.config(state="disabled")

    steps_box.config(state="normal")
    steps_box.delete("1.0", tk.END)
    steps_box.config(state="disabled")

    status_var.set("Ready.")


def update_method(event=None):
    method = method_var.get()

    key_entry.delete(0, tk.END)

    if method == "Ceaser Cipher":
        key_entry.insert(0, "3")
        info = (
            "Each letter is shifted by the selected key value "
            "in the alphabet.\n\n"
            "Example: A + 3 = D"
        )

    elif method == "Playfair Cipher":
        key_entry.insert(0, "MONARCHY")
        info = (
            "The message is divided into pairs and encrypted "
            "using a 5 x 5 key matrix.\n\n"
            "I and J are normally treated as one letter."
        )

    else:
        key_entry.insert(0, "3")
        info = (
            "The message is arranged in a zig-zag pattern "
            "across the selected number of rails."
        )

    info_box.config(state="normal")
    info_box.delete("1.0", tk.END)
    info_box.insert("1.0", info)
    info_box.config(state="disabled")

    status_var.set("Method changed to " + method + ".")


def process(action):
    message = message_box.get("1.0", tk.END).strip()
    method = method_var.get()
    key = key_entry.get().strip()

    if not message:
        messagebox.showwarning(
            "Message Required",
            "Please enter a message first."
        )
        return

    try:
        if method == "Ceaser Cipher":
            numeric_key = int(key)

            if action == "encrypt":
                result, steps = caesar_encrypt(message, numeric_key)
            else:
                result, steps = caesar_decrypt(message, numeric_key)

            show_result(result)
            show_caesar_steps(
                message, numeric_key, result, steps, action
            )

        elif method == "Rail Fence":
            rails = int(key)

            if rails < 2:
                raise ValueError

            if action == "encrypt":
                result, steps = rail_encrypt(message, rails)
            else:
                result, steps = rail_decrypt(message, rails)

            show_result(result)
            show_rail_steps(
                message, rails, result, steps, action
            )

        else:
            if not key:
                key = "MONARCHY"

            if action == "encrypt":
                result, matrix, steps = playfair_encrypt(message, key)
            else:
                result, matrix, steps = playfair_decrypt(message, key)

            show_result(result)
            show_playfair_steps(
                message, key, result, matrix, steps, action
            )

        status_var.set(
            ("Encryption" if action == "encrypt" else "Decryption")
            + " completed successfully."
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Key",
            "Please enter a valid numeric key."
        )


def show_caesar_steps(message, key, result, steps, action):
    lines = [
        f"Message     : {message}",
        f"Key         : {key}",
        "Method      : Ceaser Cipher",
        f"Action      : {action.capitalize()}",
        "",
        "STEP     ORIGINAL     SHIFT (+5)     ENCRYPTED LETTER",
        "-" * 62
    ]

    for i, (original, shift, encrypted) in enumerate(steps, 1):
        if original == " ":
            lines.append(
                f"{i:<8} {'(space)':<12} {'→':<5} {'(space)':<16} -"
            )
        else:
            lines.append(
                f"{i:<8} {original:<12} {'→':<5} "
                f"{encrypted:<16} {encrypted.upper()}"
            )

    lines.extend([
        "",
        "Formula:",
        "Encrypted Letter = (Original Letter + Key) mod 26",
        "",
        "Example:",
        "M + 5 = R",
        "I + 5 = N",
        "N + 5 = S",
        "I + 5 = N",
        "",
        "Final Result:",
        result.upper()
    ])

    set_text(steps_box, "\n".join(lines), readonly=True)


def show_rail_steps(message, rails, result, steps, action):
    lines = [
        f"Message : {message}",
        f"Rails   : {rails}",
        "Method  : Rail Fence Cipher",
        f"Action  : {action.capitalize()}",
        "",
        "STEP     CHARACTER     RAIL",
        "-" * 38
    ]

    for i, (character, rail) in enumerate(steps, 1):
        lines.append(
            f"{i:<8} {character:<13} Rail {rail}"
        )

    lines.extend([
        "",
        "Final Result:",
        result.upper()
    ])

    set_text(steps_box, "\n".join(lines), readonly=True)


def show_playfair_steps(message, key, result, matrix, steps, action):
    lines = [
        f"Message : {message}",
        f"Key     : {key}",
        "Method  : Playfair Cipher",
        f"Action  : {action.capitalize()}",
        "",
        "PLAYFAIR MATRIX",
        "-" * 30
    ]

    for row in matrix:
        lines.append("    ".join(row))

    lines.extend([
        "",
        "LETTER PAIRS",
        "-" * 55
    ])

    for original, new, rule in steps:
        lines.append(
            f"{original}  ->  {new}    {rule}"
        )

    lines.extend([
        "",
        "Final Result:",
        result.upper()
    ])

    set_text(steps_box, "\n".join(lines), readonly=True)


# ============================================================
# WINDOW - SINGLE SCREEN LAYOUT (NO MAIN PAGE SCROLL)
# ============================================================

root = tk.Tk()
root.title("CipherGuard")
root.geometry("1536x900")
root.minsize(1180, 760)
root.configure(bg=BG)

# ------------------------- STYLES -------------------------

style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "Modern.TCombobox",
    fieldbackground=WHITE,
    background=WHITE,
    foreground=NAVY,
    bordercolor=BORDER,
    lightcolor=BORDER,
    darkcolor=BORDER,
    padding=7,
    font=("Segoe UI", 11)
)

style.configure(
    "Vertical.TScrollbar",
    troughcolor="#E8EEF8",
    background="#A9BFE3",
    arrowcolor=NAVY
)

# ============================================================
# HEADER
# ============================================================

header = tk.Frame(root, bg="#0B2B63", height=125)
header.pack(fill="x", side="top")
header.pack_propagate(False)

# Header left
header_left = tk.Frame(header, bg="#0B2B63")
header_left.pack(side="left", fill="y", padx=30, pady=14)

lock = tk.Canvas(
    header_left, width=68, height=82, bg="#0B2B63",
    highlightthickness=0
)
lock.pack(side="left", padx=(0, 18))

# shield
lock.create_polygon(
    37, 5, 67, 17, 64, 53, 37, 78, 10, 53, 7, 17,
    fill="#18BDEB", outline="#8EEBFF", width=2
)
lock.create_polygon(
    37, 12, 58, 21, 56, 49, 37, 67, 18, 49, 16, 21,
    fill="#2462B4", outline=""
)
lock.create_arc(26, 29, 48, 51, start=0, extent=180,
                style="arc", outline=WHITE, width=3)
lock.create_rectangle(27, 38, 47, 56, fill=WHITE, outline=WHITE)
lock.create_rectangle(35, 44, 39, 50, fill="#2462B4", outline="")

divider = tk.Frame(header_left, bg="#5EDBFF", width=2, height=78)
divider.pack(side="left", padx=(0, 28), pady=2)

title_frame = tk.Frame(header_left, bg="#0B2B63")
title_frame.pack(side="left", anchor="center")

tk.Label(
    title_frame,
    text="CipherGuard",
    font=("Segoe UI", 32, "bold"),
    bg="#0B2B63",
    fg=WHITE
).pack(anchor="w")

tk.Label(
    title_frame,
    text="Encrypt   •   Decrypt   •   Learn the Process",
    font=("Segoe UI", 13),
    bg="#0B2B63",
    fg="#D8E9FF"
).pack(anchor="w", pady=(3, 0))

# Header right
header_right = tk.Frame(header, bg="#0B2B63")
header_right.pack(side="right", padx=38, pady=22)

tk.Label(
    header_right,
    text="Your Message\nYour Security",
    font=("Segoe Script", 15, "italic"),
    justify="right",
    bg="#0B2B63",
    fg=WHITE
).pack(anchor="e")

tk.Frame(
    header_right, bg="#25C8F2", height=3, width=115
).pack(anchor="e", pady=(3, 0))

# ============================================================
# MAIN BODY - EVERYTHING FITS ON ONE SCREEN
# ============================================================

body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=18, pady=(10, 8))

body.grid_columnconfigure(0, weight=7, uniform="top")
body.grid_columnconfigure(1, weight=5, uniform="top")
body.grid_columnconfigure(2, weight=4, uniform="top")
body.grid_rowconfigure(0, weight=0)
body.grid_rowconfigure(1, weight=0)
body.grid_rowconfigure(2, weight=1)

# ------------------------- CARD HELPER -------------------------

def card(parent, bg_color=WHITE, border=BORDER):
    return tk.Frame(
        parent,
        bg=bg_color,
        highlightbackground=border,
        highlightthickness=1,
        bd=0
    )

def section_title(parent, text, fg=NAVY, icon=""):
    row = tk.Frame(parent, bg=parent.cget("bg"))
    row.pack(fill="x", padx=18, pady=(13, 7))
    if icon:
        tk.Label(
            row, text=icon, font=("Segoe UI Emoji", 15),
            bg=parent.cget("bg"), fg=fg
        ).pack(side="left", padx=(0, 9))
    tk.Label(
        row, text=text, font=("Segoe UI", 14, "bold"),
        bg=parent.cget("bg"), fg=fg
    ).pack(side="left")
    return row

# ============================================================
# TOP ROW
# ============================================================

message_card = card(body)
message_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

section_title(message_card, "Enter Message", "#10295A", "☰")

message_box = tk.Text(
    message_card,
    height=5,
    font=("Segoe UI", 13),
    bg="#FCFDFF",
    fg=NAVY,
    insertbackground=NAVY,
    relief="solid",
    bd=1,
    wrap="word",
    padx=12,
    pady=9
)
message_box.pack(fill="both", expand=True, padx=18, pady=(0, 14))

counter = tk.Label(
    message_card, text="0/1000",
    font=("Segoe UI", 9), bg=WHITE, fg=MUTED
)
counter.place(relx=0.93, rely=0.90, anchor="e")

def update_counter(event=None):
    value = message_box.get("1.0", "end-1c")
    counter.config(text=f"{len(value)}/1000")

message_box.bind("<KeyRelease>", update_counter)

# ------------------------- SETTINGS -------------------------

settings_card = card(body)
settings_card.grid(row=0, column=1, sticky="nsew", padx=7)

section_title(settings_card, "Select Method", "#10295A", "⚙")

method_var = tk.StringVar(value="Ceaser Cipher")

method_menu = ttk.Combobox(
    settings_card,
    textvariable=method_var,
    values=["Ceaser Cipher", "Playfair Cipher", "Rail Fence"],
    state="readonly",
    style="Modern.TCombobox"
)
method_menu.pack(fill="x", padx=18, pady=(0, 9))
method_menu.bind("<<ComboboxSelected>>", update_method)

tk.Label(
    settings_card,
    text="🔑  Key",
    font=("Segoe UI", 13, "bold"),
    bg=WHITE, fg="#10295A"
).pack(anchor="w", padx=18, pady=(3, 6))

key_entry = tk.Entry(
    settings_card,
    font=("Segoe UI", 12),
    bg=WHITE,
    fg=NAVY,
    relief="solid",
    bd=1
)
key_entry.pack(fill="x", padx=18, ipady=7)

key_hint = tk.Label(
    settings_card,
    text="ⓘ  Default key for Caesar Cipher is 3",
    font=("Segoe UI", 9),
    bg=WHITE,
    fg="#5577A8"
)
key_hint.pack(anchor="w", padx=18, pady=(6, 0))

# ------------------------- ACTIONS -------------------------

actions_card = card(body)
actions_card.grid(row=0, column=2, sticky="nsew", padx=(7, 0))

def make_big_button(parent, text, bg_color, command, symbol):
    frame = tk.Frame(parent, bg=bg_color, height=52, cursor="hand2")
    frame.pack(fill="x", padx=13, pady=(13, 0))
    frame.pack_propagate(False)

    tk.Label(
        frame, text=symbol, font=("Segoe UI Emoji", 20, "bold"),
        bg=bg_color, fg=WHITE
    ).pack(side="left", padx=(15, 8))

    tk.Button(
        frame, text=text, command=command,
        font=("Segoe UI", 12, "bold"),
        bg=bg_color, fg=WHITE,
        activebackground=bg_color, activeforeground=WHITE,
        relief="flat", bd=0, cursor="hand2"
    ).pack(side="left", fill="both", expand=True)

    tk.Label(
        frame, text="›", font=("Segoe UI", 24),
        bg=bg_color, fg=WHITE
    ).pack(side="right", padx=13)

make_big_button(actions_card, "ENCRYPT", GREEN,
                lambda: process("encrypt"), "🔒")
make_big_button(actions_card, "DECRYPT", "#E83E50",
                lambda: process("decrypt"), "🔓")
make_big_button(actions_card, "CLEAR ALL", PURPLE,
                clear_all, "⟳")

# ============================================================
# RESULT
# ============================================================

result_card = card(body, LIGHT_GREEN, "#A8E1CE")
result_card.grid(row=1, column=0, columnspan=3, sticky="nsew",
                 pady=(9, 9))

result_heading = tk.Frame(result_card, bg=LIGHT_GREEN)
result_heading.pack(fill="x", padx=18, pady=(10, 5))

tk.Label(
    result_heading, text="▣  Encrypted / Decrypted Result",
    font=("Segoe UI", 14, "bold"),
    bg=LIGHT_GREEN, fg="#087D5B"
).pack(side="left")

tk.Button(
    result_heading, text="▣  COPY RESULT",
    command=copy_result,
    font=("Segoe UI", 9, "bold"),
    bg=WHITE, fg=GREEN,
    relief="solid", bd=1, cursor="hand2",
    padx=10, pady=4
).pack(side="right")

result_box = tk.Text(
    result_card,
    height=2,
    font=("Consolas", 20, "bold"),
    bg=WHITE,
    fg="#075C4C",
    relief="solid",
    bd=1,
    wrap="word",
    padx=15,
    pady=9
)
result_box.pack(fill="x", padx=18, pady=(0, 10))
result_box.config(state="disabled")

# ============================================================
# LOWER ROW - INFORMATION + STEP PROCESS
# ============================================================

lower = tk.Frame(body, bg=BG)
lower.grid(row=2, column=0, columnspan=3, sticky="nsew")
lower.grid_columnconfigure(0, weight=5, uniform="lower")
lower.grid_columnconfigure(1, weight=7, uniform="lower")
lower.grid_rowconfigure(0, weight=1)

# ------------------------- METHOD INFORMATION -------------------------

info_card = card(lower, LIGHT_BLUE, "#B7D5F5")
info_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

tk.Label(
    info_card, text="▣  Method Information",
    font=("Segoe UI", 14, "bold"),
    bg=LIGHT_BLUE, fg="#1550A5"
).pack(anchor="w", padx=18, pady=(13, 8))

info_inner = tk.Frame(
    info_card, bg=WHITE,
    highlightbackground="#DCE7F5", highlightthickness=1
)
info_inner.pack(fill="both", expand=True, padx=14, pady=(0, 13))

info_icon = tk.Label(
    info_inner, text="🔐", font=("Segoe UI Emoji", 25),
    bg="#E8F3FF", fg=BLUE
)
info_icon.pack(anchor="w", padx=15, pady=(13, 5))

info_box = tk.Text(
    info_inner,
    height=6,
    font=("Segoe UI", 11),
    bg=WHITE,
    fg=TEXT,
    relief="flat",
    wrap="word",
    padx=15,
    pady=4
)
info_box.pack(fill="both", expand=True, padx=5, pady=(0, 8))
info_box.config(state="disabled")

# ------------------------- STEP-BY-STEP PROCESS -------------------------

steps_card = card(lower, LIGHT_PURPLE, "#C9C1F7")
steps_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

steps_header = tk.Frame(steps_card, bg=LIGHT_PURPLE)
steps_header.pack(fill="x", padx=18, pady=(13, 7))

tk.Label(
    steps_header, text="☁  Step-by-Step Process",
    font=("Segoe UI", 14, "bold"),
    bg=LIGHT_PURPLE, fg="#382AA8"
).pack(side="left")

step_mode_var = tk.StringVar(value="Encryption")
step_mode = ttk.Combobox(
    steps_header,
    textvariable=step_mode_var,
    values=["Encryption", "Decryption"],
    state="readonly",
    width=12,
    style="Modern.TCombobox"
)
step_mode.pack(side="right")

steps_container = tk.Frame(steps_card, bg=WHITE)
steps_container.pack(fill="both", expand=True, padx=14, pady=(0, 13))

steps_scroll = ttk.Scrollbar(
    steps_container, orient="vertical",
    style="Vertical.TScrollbar"
)
steps_scroll.pack(side="right", fill="y")

steps_box = tk.Text(
    steps_container,
    height=10,
    font=("Consolas", 9),
    bg=WHITE,
    fg=TEXT,
    relief="solid",
    bd=1,
    wrap="none",
    padx=10,
    pady=8,
    yscrollcommand=steps_scroll.set
)
steps_box.pack(side="left", fill="both", expand=True)
steps_scroll.config(command=steps_box.yview)
steps_box.config(state="disabled")

# ============================================================
# FOOTER / STATUS
# ============================================================

footer = tk.Frame(root, bg="#0B2B63", height=32)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

status_var = tk.StringVar(value="Ready to encrypt your message")

tk.Label(
    footer, text="●",
    font=("Arial", 15),
    bg="#0B2B63", fg="#20D7A0"
).pack(side="left", padx=(22, 5))

tk.Label(
    footer, textvariable=status_var,
    font=("Segoe UI", 9, "bold"),
    bg="#0B2B63", fg=WHITE
).pack(side="left")

tk.Label(
    footer, text="CipherGuard   v1.0   |   BSc IT Mini Project",
    font=("Segoe UI", 9),
    bg="#0B2B63", fg="#D8E9FF"
).pack(side="right", padx=22)

# ============================================================
# INITIAL STATE
# ============================================================

update_method()

# Demo values matching the reference image
message_box.insert("1.0", "mini project")
key_entry.delete(0, tk.END)
key_entry.insert(0, "5")
update_counter()

root.mainloop()
