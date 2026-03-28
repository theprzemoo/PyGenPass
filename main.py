import customtkinter as ctk
import random
import string
import pyperclip
import math
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#080808"
CARD    = "#111014"
CARD2   = "#1a1520"
ACCENT  = "#6c1ca6"
ACCENT2 = "#b06ee0"
SUCCESS = "#22d3a5"
WARN    = "#f59e0b"
DANGER  = "#ef4444"
TEXT    = "#ede8f5"
MUTED   = "#6b5f7a"
BORDER  = "#2d1f40"

# Character-type colours for the coloured preview
COL_UPPER   = "#facc15"   # yellow
COL_LOWER   = "#f87171"   # red
COL_DIGIT   = "#22d3a5"   # teal
COL_SPECIAL = "#f472b6"   # pink

STRENGTH_COLORS = ["#ef4444", "#f97316", "#f59e0b", "#22d3a5", "#6c1ca6"]
STRENGTH_LABELS = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]

SLOT_CHARS = string.ascii_letters + string.digits + "!@#$%^&*"
SLOT_STEPS = 12          # frames of animation
SLOT_DELAY = 22          # ms between frames


def char_color(c: str) -> str:
    if c.isupper():              return COL_UPPER
    if c.islower():              return COL_LOWER
    if c.isdigit():              return COL_DIGIT
    return COL_SPECIAL


def password_strength(pwd: str) -> int:
    if not pwd: return 0
    score = 0
    if len(pwd) >= 8:  score += 1
    if len(pwd) >= 14: score += 1
    if any(c.isupper()              for c in pwd): score += 1
    if any(c.islower()              for c in pwd): score += 1
    if any(c.isdigit()             for c in pwd): score += 1
    if any(c in string.punctuation for c in pwd): score += 1
    return min(4, score - 1) if score > 0 else 0


def calc_entropy(pwd: str,
                 upper: bool, lower: bool,
                 digits: bool, special: bool) -> float:
    pool = 0
    if upper:   pool += 26
    if lower:   pool += 26
    if digits:  pool += 10
    if special: pool += 32
    if pool == 0 or not pwd: return 0.0
    return len(pwd) * math.log2(pool)


# ── Toggle switch ─────────────────────────────────────────────────────────────
class ToggleSwitch(ctk.CTkFrame):
    W, H, K = 48, 26, 20

    def __init__(self, master, text="", variable: ctk.BooleanVar = None,
                 on_change=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._var       = variable or ctk.BooleanVar(value=False)
        self._on_change = on_change
        self._canvas    = ctk.CTkCanvas(
            self, width=self.W, height=self.H,
            bg=CARD, highlightthickness=0, cursor="hand2")
        self._canvas.pack(side="left", padx=(0, 8))
        self._lbl = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT, cursor="hand2")
        self._lbl.pack(side="left")
        self._canvas.bind("<Button-1>", self._toggle)
        self._lbl.bind("<Button-1>",    self._toggle)
        self._render_switch()

    def _render_switch(self):
        c, on = self._canvas, self._var.get()
        c.delete("all")
        fill = ACCENT if on else "#1e1228"
        r = self.H // 2
        c.create_oval(0, 0, self.H, self.H,                     fill=fill, outline="")
        c.create_oval(self.W - self.H, 0, self.W, self.H,       fill=fill, outline="")
        c.create_rectangle(r, 0, self.W - r, self.H,            fill=fill, outline="")
        pad = (self.H - self.K) // 2
        x   = self.W - pad - self.K if on else pad
        c.create_oval(x, pad, x + self.K, pad + self.K, fill="white", outline="")
        self._lbl.configure(text_color=ACCENT2 if on else MUTED)

    def _toggle(self, _=None):
        self._var.set(not self._var.get())
        self._render_switch()
        if self._on_change:
            self._on_change()

    def get(self): return self._var.get()


# ── Strength bar ──────────────────────────────────────────────────────────────
class StrengthBar(ctk.CTkFrame):
    SEG = 5

    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._bars = []
        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(side="left", fill="x", expand=True)
        for _ in range(self.SEG):
            b = ctk.CTkFrame(bf, height=6, corner_radius=3, fg_color=BORDER)
            b.pack(side="left", fill="x", expand=True, padx=2)
            self._bars.append(b)
        self._lbl = ctk.CTkLabel(
            self, text="", width=80, anchor="e",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=MUTED)
        self._lbl.pack(side="right", padx=(8, 0))

    def update(self, score: int):
        col = STRENGTH_COLORS[score]
        for i, b in enumerate(self._bars):
            b.configure(fg_color=col if i <= score else BORDER)
        self._lbl.configure(text=STRENGTH_LABELS[score], text_color=col)

    def reset(self):
        for b in self._bars: b.configure(fg_color=BORDER)
        self._lbl.configure(text="")


# ── Coloured password preview (Canvas) ───────────────────────────────────────
class ColourPreview(ctk.CTkFrame):
    PAD_X = 14
    PAD_Y = 10

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=CARD2, corner_radius=10, **kw)
        self._canvas = ctk.CTkCanvas(
            self, bg=CARD2, highlightthickness=0, height=36)
        self._canvas.pack(fill="x", padx=self.PAD_X, pady=self.PAD_Y)

    def render(self, pwd: str):
        c = self._canvas
        c.delete("all")
        if not pwd: return
        font = ("Consolas", 15)
        # measure one char width (approximate)
        char_w = 10
        x = 0
        for ch in pwd:
            col = char_color(ch)
            c.create_text(x, 18, text=ch, fill=col, font=font, anchor="w")
            x += char_w
        c.configure(scrollregion=(0, 0, x, 36))

    def clear(self):
        self._canvas.delete("all")


# ── Main app ──────────────────────────────────────────────────────────────────
class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyGenPass")
        self.geometry("580x980")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        # Icon – icon.ico must be in the same folder as the script
        import os
        _icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        self.after(200, lambda: self.iconbitmap(_icon))

        self._history:    list[dict] = []
        self._animating:  bool       = False
        self._final_pwd:  str        = ""

        self._build_ui()
        self._bind_keys()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="🔐", font=ctk.CTkFont(size=30)).pack(side="left", padx=(0, 10))
        col = ctk.CTkFrame(hdr, fg_color="transparent")
        col.pack(side="left")
        ctk.CTkLabel(col, text="PyGenPass",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(col, text="Ctrl+G  generate  ·  Ctrl+C  copy  ·  Ctrl+H  clear history",
                     font=ctk.CTkFont(family="Segoe UI", size=10),
                     text_color=MUTED).pack(anchor="w")

        # ── Password card ─────────────────────────────────────────────────
        pcard = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18,
                             border_width=1, border_color=BORDER)
        pcard.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(pcard, text="Generated Password",
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=MUTED).pack(anchor="w", padx=20, pady=(16, 4))

        self.password_var = ctk.StringVar(value="")
        self.password_entry = ctk.CTkEntry(
            pcard, textvariable=self.password_var,
            font=ctk.CTkFont(family="Consolas", size=16),
            height=48, corner_radius=12,
            border_width=2, border_color=BORDER,
            fg_color=CARD2, text_color=ACCENT2, state="readonly")
        self.password_entry.pack(fill="x", padx=20)

        # Strength bar
        self._sbar = StrengthBar(pcard)
        self._sbar.pack(fill="x", padx=20, pady=(8, 2))

        # Entropy label
        self._entropy_var = ctk.StringVar(value="")
        ctk.CTkLabel(pcard, textvariable=self._entropy_var,
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=MUTED).pack(anchor="e", padx=22, pady=(0, 4))

        # Coloured preview
        ctk.CTkLabel(pcard, text="👁  Character preview",
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color=MUTED).pack(anchor="w", padx=20)

        self._preview = ColourPreview(pcard)
        self._preview.pack(fill="x", padx=20, pady=(4, 4))

        # Legend
        leg = ctk.CTkFrame(pcard, fg_color="transparent")
        leg.pack(anchor="w", padx=22, pady=(0, 10))
        for label, col in [("Uppercase", COL_UPPER), ("Lowercase", COL_LOWER),
                            ("Digit", COL_DIGIT), ("Special", COL_SPECIAL)]:
            ctk.CTkLabel(leg, text=f"■ {label}",
                         font=ctk.CTkFont(size=10), text_color=col).pack(side="left", padx=(0, 12))

        # Buttons
        brow = ctk.CTkFrame(pcard, fg_color="transparent")
        brow.pack(fill="x", padx=20, pady=(4, 18))
        brow.columnconfigure(0, weight=1)
        brow.columnconfigure(1, weight=1)

        ctk.CTkButton(brow, text="⚡  Generate  (Ctrl+G)",
                      command=self._generate,
                      height=42, corner_radius=12,
                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                      fg_color=ACCENT, hover_color="#5a52d5",
                      text_color="white").grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(brow, text="📋  Copy  (Ctrl+C)",
                      command=self._copy,
                      height=42, corner_radius=12,
                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                      fg_color=CARD2, hover_color=BORDER, text_color=ACCENT2,
                      border_width=1, border_color=BORDER).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # ── Length card ───────────────────────────────────────────────────
        lcard = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18,
                             border_width=1, border_color=BORDER)
        lcard.pack(fill="x", padx=20, pady=(0, 10))

        trow = ctk.CTkFrame(lcard, fg_color="transparent")
        trow.pack(fill="x", padx=20, pady=(14, 4))
        ctk.CTkLabel(trow, text="Password Length",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color=TEXT).pack(side="left")
        self.length_var = ctk.IntVar(value=16)
        self._len_lbl = ctk.CTkLabel(trow, text="16",
                                     font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
                                     text_color=ACCENT2, width=36)
        self._len_lbl.pack(side="right")

        self.slider = ctk.CTkSlider(
            lcard, from_=3, to=30, number_of_steps=27,
            variable=self.length_var, command=self._on_slider,
            button_color=ACCENT, button_hover_color=ACCENT2,
            progress_color=ACCENT, fg_color=BORDER)
        self.slider.pack(fill="x", padx=20, pady=(0, 16))

        # ── Toggles card ──────────────────────────────────────────────────
        tcard = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18,
                             border_width=1, border_color=BORDER)
        tcard.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(tcard, text="Character Types",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=20, pady=(14, 8))

        self.use_uppercase = ctk.BooleanVar(value=True)
        self.use_lowercase = ctk.BooleanVar(value=True)
        self.use_digits    = ctk.BooleanVar(value=True)
        self.use_special   = ctk.BooleanVar(value=False)

        grid = ctk.CTkFrame(tcard, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 14))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        toggles = [
            ("🔠  Uppercase (A–Z)", self.use_uppercase),
            ("🔢  Digits (0–9)",    self.use_digits),
            ("🔡  Lowercase (a–z)", self.use_lowercase),
            ("✳️  Special chars",   self.use_special),
        ]
        for i, (lbl, var) in enumerate(toggles):
            r, c = divmod(i, 2)
            ToggleSwitch(grid, text=lbl, variable=var,
                         on_change=self._auto_generate).grid(
                row=r, column=c, sticky="w", pady=5)

        # ── Status ────────────────────────────────────────────────────────
        self.status_var = ctk.StringVar(value="Press ⚡ Generate or Ctrl+G to start.")
        ctk.CTkLabel(self, textvariable=self.status_var,
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=MUTED).pack(pady=(0, 4))

        # ── History card ──────────────────────────────────────────────────
        hcard = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18,
                             border_width=1, border_color=BORDER)
        hcard.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        hhdr = ctk.CTkFrame(hcard, fg_color="transparent")
        hhdr.pack(fill="x", padx=20, pady=(14, 6))
        ctk.CTkLabel(hhdr, text="🕐  History",
                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                     text_color=TEXT).pack(side="left")
        ctk.CTkButton(hhdr, text="🗑  Clear  (Ctrl+H)",
                      command=self._clear_history,
                      width=130, height=32, corner_radius=10,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      fg_color="#2a1535", hover_color="#4a1a6a",
                      text_color="#b06ee0").pack(side="right")

        self._hist_scroll = ctk.CTkScrollableFrame(
            hcard, fg_color="transparent", corner_radius=0)
        self._hist_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._refresh_history()

    # ── Key bindings ──────────────────────────────────────────────────────────
    def _bind_keys(self):
        self.bind("<Control-g>", lambda _: self._generate())
        self.bind("<Control-G>", lambda _: self._generate())
        self.bind("<Control-c>", lambda _: self._copy())
        self.bind("<Return>",    lambda _: self._generate())
        self.bind("<Control-h>", lambda _: self._clear_history())
        self.bind("<Control-H>", lambda _: self._clear_history())

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _build_charset(self) -> str:
        cs = ""
        if self.use_uppercase.get(): cs += string.ascii_uppercase
        if self.use_lowercase.get(): cs += string.ascii_lowercase
        if self.use_digits.get():    cs += string.digits
        if self.use_special.get():   cs += string.punctuation
        return cs

    def _make_password(self, charset: str, length: int) -> str:
        return "".join(random.choice(charset) for _ in range(length))

    # ── Slot-machine animation ────────────────────────────────────────────────
    def _generate(self):
        if self._animating:
            return
        charset = self._build_charset()
        if not charset:
            self.status_var.set("⚠  Select at least one character type.")
            self._sbar.reset()
            return
        length = self.length_var.get()
        self._final_pwd  = self._make_password(charset, length)
        self._animating  = True
        self._slot_step(charset, length, 0)

    def _slot_step(self, charset: str, length: int, step: int):
        if step < SLOT_STEPS:
            fake = self._make_password(SLOT_CHARS, length)
            self.password_var.set(fake)
            self._preview.render(fake)
            self.after(SLOT_DELAY, lambda: self._slot_step(charset, length, step + 1))
        else:
            pwd = self._final_pwd
            self.password_var.set(pwd)
            self._preview.render(pwd)
            self._animating = False
            score  = password_strength(pwd)
            entr   = calc_entropy(pwd,
                                  self.use_uppercase.get(), self.use_lowercase.get(),
                                  self.use_digits.get(),    self.use_special.get())
            self._sbar.update(score)
            self._entropy_var.set(f"Entropy: {entr:.1f} bits")
            self.status_var.set(f"✅  Generated  ·  {length} chars  ·  {entr:.0f} bits entropy")
            self._add_to_history(pwd, score, entr)

    def _auto_generate(self):
        """Called when a toggle changes – silently regenerate if a password exists."""
        if self.password_var.get():
            self._generate()

    def _on_slider(self, val):
        self._len_lbl.configure(text=str(int(float(val))))
        if self.password_var.get():
            self._generate()

    # ── Copy ──────────────────────────────────────────────────────────────────
    def _copy(self):
        pwd = self.password_var.get()
        if not pwd:
            self.status_var.set("⚠  Generate a password first.")
            return
        try:
            pyperclip.copy(pwd)
            self.status_var.set("📋  Copied to clipboard!")
        except Exception:
            self.status_var.set("⚠  Copy failed.")

    def _copy_str(self, s: str):
        try:
            pyperclip.copy(s)
            self.status_var.set("📋  Copied from history!")
        except Exception:
            self.status_var.set("⚠  Copy failed.")

    # ── History ───────────────────────────────────────────────────────────────
    def _add_to_history(self, pwd: str, score: int, entropy: float):
        self._history.insert(0, {
            "pwd": pwd, "score": score, "entropy": entropy,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        self._history = self._history[:10]
        self._refresh_history()

    def _refresh_history(self):
        for w in self._hist_scroll.winfo_children():
            w.destroy()
        if not self._history:
            ctk.CTkLabel(self._hist_scroll,
                         text="No passwords generated yet.",
                         font=ctk.CTkFont(family="Segoe UI", size=13),
                         text_color=MUTED).pack(pady=16)
            return
        for item in self._history:
            row = ctk.CTkFrame(self._hist_scroll, fg_color=CARD2, corner_radius=12,
                               border_width=1, border_color=BORDER)
            row.pack(fill="x", pady=4, padx=4)
            row.columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=item["pwd"],
                         font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                         text_color=TEXT, anchor="w").grid(
                row=0, column=0, sticky="w", padx=14, pady=(10, 3))

            meta = ctk.CTkFrame(row, fg_color="transparent")
            meta.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

            col = STRENGTH_COLORS[item["score"]]
            ctk.CTkLabel(meta,
                         text=f"● {STRENGTH_LABELS[item['score']]}",
                         font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                         text_color=col).pack(side="left")
            ctk.CTkLabel(meta,
                         text=f"   {item['entropy']:.0f} bits   ·   {item['time']}",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=MUTED).pack(side="left")

            ctk.CTkButton(row, text="📋 Copy",
                          command=lambda p=item["pwd"]: self._copy_str(p),
                          width=80, height=36, corner_radius=10,
                          font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                          fg_color=ACCENT, hover_color="#8a2fd4",
                          text_color="white").grid(row=0, column=1, rowspan=2, padx=12)

    def _clear_history(self):
        self._history.clear()
        self._refresh_history()
        self.status_var.set("🗑  History cleared.")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
    
