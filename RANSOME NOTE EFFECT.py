# colorful_transformer_ultrahd.py
import tkinter as tk
from tkinter import font, messagebox, filedialog
import random
from PIL import Image, ImageDraw, ImageFont

# pip install pillow

# Expanded font list (system-dependent)
FONTS = [
    "Arial", "Verdana", "Tahoma", "Times New Roman", "Courier New",
    "Georgia", "Trebuchet MS", "Impact", "Comic Sans MS", "DejaVuSans",
    "Liberation Serif", "Liberation Sans", "Ubuntu", "Helvetica", "Courier",
    "Palatino Linotype", "Lucida Console", "Lucida Sans", "Garamond"
]

def rand_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def rand_size(min_size=12, max_size=48):
    return random.randint(min_size, max_size)

def rand_font():
    return random.choice(FONTS)

class ColorfulTransformer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Colorful Transformer — Ultra HD Random Fonts")
        self.geometry("980x640")
        self.chars = []  # list of per-character metadata for export
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Enter text or numbers:").pack(side="left")

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(top, textvariable=self.input_var)
        self.entry.pack(side="left", fill="x", expand=True, padx=8)
        self.entry.bind("<Return>", lambda e: self.generate())

        self.generate_btn = tk.Button(top, text="Generate", command=self.generate)
        self.generate_btn.pack(side="left", padx=8)

        opts = tk.Frame(self)
        opts.pack(fill="x", padx=10)
        tk.Label(opts, text="Min size:").pack(side="left")
        self.min_size_var = tk.IntVar(value=16)
        tk.Spinbox(opts, from_=8, to=120, textvariable=self.min_size_var, width=5).pack(side="left", padx=(6, 12))

        tk.Label(opts, text="Max size:").pack(side="left")
        self.max_size_var = tk.IntVar(value=40)
        tk.Spinbox(opts, from_=8, to=200, textvariable=self.max_size_var, width=5).pack(side="left", padx=(6, 12))

        out_frame = tk.Frame(self)
        out_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output = tk.Text(out_frame, wrap="word")
        self.output.pack(side="left", fill="both", expand=True)
        self.output.configure(state="disabled")

        scrollbar = tk.Scrollbar(out_frame, command=self.output.yview)
        scrollbar.pack(side="right", fill="y")
        self.output.config(yscrollcommand=scrollbar.set)

        bottom = tk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=10)

        tk.Button(bottom, text="Copy Text", command=self.copy_plain).pack(side="left", padx=5)
        tk.Button(bottom, text="Copy Styled HTML", command=self.copy_styled).pack(side="left", padx=5)
        tk.Button(bottom, text="Export as Image (PNG)", command=self.export_image).pack(side="left", padx=5)
        tk.Button(bottom, text="Clear", command=self.clear_output).pack(side="right", padx=5)

    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.configure(state="disabled")
        self.chars = []

    def generate(self):
        text = self.input_var.get()
        if not text:
            return

        min_size = max(1, self.min_size_var.get())
        max_size = max(min_size, self.max_size_var.get())

        self.chars = []
        for ch in text:
            size = rand_size(min_size, max_size)
            color = rand_color()
            font_family = rand_font()
            self.chars.append({
                "ch": ch,
                "family": font_family,
                "size": size,
                "color": color
            })

        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        for i, meta in enumerate(self.chars):
            tag = f"char_{i}"
            f = font.Font(family=meta["family"], size=meta["size"])
            self.output.tag_configure(tag, font=f, foreground=meta["color"])
            self.output.insert(tk.END, meta["ch"], tag)
        self.output.configure(state="disabled")

    def copy_plain(self):
        text = self.output.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Plain text copied to clipboard ✅")

    def copy_styled(self):
        html = self.generate_html_from_chars()
        self.clipboard_clear()
        self.clipboard_append(html)
        messagebox.showinfo("Copied", "Styled HTML copied to clipboard ✅")

    def generate_html_from_chars(self):
        html = ""
        for meta in self.chars:
            ch = meta["ch"]
            esc = (ch.replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;")
                      .replace('"', "&quot;"))
            style = f'color:{meta["color"]}; font-size:{meta["size"]}px; font-family:{meta["family"]};'
            html += f'<span style="{style}">{esc}</span>'
        return html

    def export_image(self):
        if not self.chars:
            messagebox.showwarning("Nothing to export", "Generate text first.")
            return

        SCALE = 5       # Ultra HD scale
        DPI = 600       # Ultra HD DPI
        lines = []
        current_line = []
        for meta in self.chars:
            if meta["ch"] == "\n":
                lines.append(current_line)
                current_line = []
            else:
                current_line.append(meta)
        lines.append(current_line)

        def get_pil_font(family, size):
            candidates = [
                f"{family}.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            ]
            for c in candidates:
                try:
                    return ImageFont.truetype(c, size=int(size * SCALE))
                except Exception:
                    continue
            return ImageFont.load_default()

        # Compute per-line height using baseline alignment
        padding = 50 * SCALE
        max_width = 0
        total_height = padding
        line_metrics = []

        for line in lines:
            x = 0
            max_ascent = 0
            max_descent = 0
            letter_widths = []

            # Find tallest ascent and descent in the line
            for meta in line:
                f = get_pil_font(meta["family"], meta["size"])
                ascent, descent = f.getmetrics()
                if ascent > max_ascent:
                    max_ascent = ascent
                if descent > max_descent:
                    max_descent = descent
                try:
                    w, _ = f.getsize(meta["ch"])
                except Exception:
                    w = f.getbbox(meta["ch"])[2]
                letter_widths.append(w)
                x += w

            max_width = max(max_width, x)
            line_height = max_ascent + max_descent
            line_metrics.append((max_ascent, max_descent, letter_widths, line))
            total_height += line_height

        total_width = max_width + padding
        total_height += padding

        # Transparent background
        image = Image.new("RGBA", (int(total_width), int(total_height)), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        y = padding // 2
        for ascent, descent, widths, line in line_metrics:
            x = padding // 2
            for meta, w in zip(line, widths):
                f = get_pil_font(meta["family"], meta["size"])
                letter_ascent, _ = f.getmetrics()
                y_offset = ascent - letter_ascent  # align baseline
                draw.text((x, y + y_offset), meta["ch"], font=f, fill=meta["color"])
                x += w
            y += ascent + descent

        fpath = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG Image", "*.png")],
                                             title="Save image as...")
        if not fpath:
            return

        try:
            image.save(fpath, format="PNG", dpi=(DPI, DPI), optimize=True)
            messagebox.showinfo("Exported", f"✅ Ultra HD image saved with transparent background!\n{fpath}")
        except Exception as e:
            messagebox.showerror("Save failed ❌", str(e))


if __name__ == "__main__":
    app = ColorfulTransformer()
    app.mainloop()

