# Custom AI Assistant - GUI
# Create a separate graphical interface that opens in its own desktop window
# Notes:
#   'window' creates the main application window
#   'window.geometry' sets the initial dimensions
#   One full-window 'tk.Canvas' draws the galaxy gradient, glass panels, buttons and chat
#   'CustomTkinter' widgets are used for the text box and the settings sidebar
#   'numpy' generates the gradient quickly, 'Pillow' renders the glass shapes
#   '-transparentcolor' (Windows) cuts the rounded window corners
#   'bind' and 'lambda' allow Enter to send messages
#   'threading' runs AI requests separately from the GUI
#   'queue' safely passes responses from the background thread to the GUI

import main as assistant
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageChops
import tkinter as tk
import tkinter.font as tkfont
import threading
import queue
import sys


def main():
    # Configure application appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    response_queue = queue.Queue()
    thinking_visible = False

    # ------------------------------------------------------------------
    # Design constants
    # ------------------------------------------------------------------
    KEY = "#010101"                 # transparent key color (rounded corners)
    ROUNDED = sys.platform == "win32"
    WINDOW_RADIUS = 28

    PAD = 16                        # space around the window content
    TITLE_H = 48
    INPUT_H = 54
    SIDEBAR_W = 280
    RESIZE_BORDER = 8
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    SS = 3                          # supersampling for smooth shapes

    BUBBLE_PAD_X = 14
    BUBBLE_PAD_Y = 9
    BUBBLE_RADIUS = 22
    BUBBLE_TAIL = 6

    TEXT = "#EDE9FE"
    MUTED = "#C4B5FD"
    SIDEBAR_HEX = "#1e1336"

    GLASS_FILL = (40, 26, 64, 153)          # rgba(40,26,64,.6)
    GLASS_BORDER = (200, 160, 235, 77)      # rgba(200,160,235,.3)
    BAR_FILL = (18, 10, 34, 225)            # darker, mostly opaque
    BAR_BORDER = (200, 160, 235, 55)
    SIDEBAR_FILL = (30, 19, 54, 255)
    SIDEBAR_BORDER = (200, 160, 235, 60)

    USER_GRADIENT = ((122, 45, 140), (91, 60, 176))
    USER_BORDER = (255, 255, 255, 38)

    # Galaxy background: base colors along a 145 degree gradient
    BASE_STOPS = [0.0, 0.40, 0.62, 0.82, 1.0]
    BASE_COLORS = [
        (13, 7, 32),
        (28, 16, 54),
        (40, 23, 66),
        (21, 11, 42),
        (10, 5, 22)
    ]

    # (x, y, size in px, strength) -- muted warm-white sparkles
    STARS = [
        (0.08, 0.14, 1.6, 0.50),
        (0.22, 0.62, 1.2, 0.35),
        (0.37, 0.09, 1.8, 0.45),
        (0.51, 0.44, 1.2, 0.30),
        (0.64, 0.88, 1.6, 0.45),
        (0.78, 0.21, 1.2, 0.40),
        (0.91, 0.57, 1.8, 0.50),
        (0.94, 0.92, 1.2, 0.35),
        (0.15, 0.90, 1.2, 0.35)
    ]
    STAR_COLOR = (235, 228, 250)

    # Create the main application window
    window = ctk.CTk()
    window.title("Custom AI Assistant")
    window.geometry("1200x780")
    window.configure(fg_color = KEY)
    window.minsize(1000, 650)
    window.is_resizing = False

    # Hide the default Windows title bar
    window.overrideredirect(True)

    # Make the key color transparent so the window corners are rounded
    if ROUNDED:
        try:
            window.attributes("-transparentcolor", KEY)
        except tk.TclError:
            ROUNDED = False

    # Configure application fonts
    FONT_FAMILY = "Lato"

    FONT_HEADING = ctk.CTkFont(
        family = FONT_FAMILY,
        size = 16,
        weight = "bold"
    )

    FONT_BODY = ctk.CTkFont(
        family = FONT_FAMILY,
        size = 14,
        weight = "normal"
    )

    FONT_LABEL = ctk.CTkFont(
        family = FONT_FAMILY,
        size = 13,
        weight = "bold"
    )

    TITLE_FONT = tkfont.Font(
        family = FONT_FAMILY,
        size = -20,
        weight = "bold"
    )

    MESSAGE_FONT = tkfont.Font(
        family = FONT_FAMILY,
        size = 12,
        weight = "normal"
    )

    THINKING_FONT = tkfont.Font(
        family = FONT_FAMILY,
        size = 12
    )

    # ------------------------------------------------------------------
    # Conversation settings and memory
    # ------------------------------------------------------------------
    memories = assistant.load_memory()

    settings = {
        "personality": "Professional",
        "tone": "Friendly",
        "response_length": "Normal",
        "language": "English",
        "technical_level": "Beginner",
        "creativity": "Medium",
        "custom_instructions": ""
    }

    def update_messages():
        new_messages = assistant.create_messages(
            settings["personality"],
            settings["tone"],
            settings["response_length"],
            settings["language"],
            settings["technical_level"],
            settings["creativity"],
            settings["custom_instructions"],
            memories
        )

        messages[0] = new_messages[0]

    messages = assistant.create_messages(
        settings["personality"],
        settings["tone"],
        settings["response_length"],
        settings["language"],
        settings["technical_level"],
        settings["creativity"],
        settings["custom_instructions"],
        memories
    )

    def update_setting(setting, value):
        settings[setting] = value
        update_messages()

    def update_custom_instructions():
        settings["custom_instructions"] = custom_instructions_box.get("1.0", "end-1c")
        update_messages()

    # ------------------------------------------------------------------
    # Shared state
    # ------------------------------------------------------------------
    conversation = []
    chat_resize_job = None

    S = {
        "g": None,              # current geometry
        "scroll": 0,            # chat scroll offset in pixels
        "layout": None,         # cached message layout
        "layout_key": None,
        "items": {},            # canvas item ids for buttons
        "regions": {},          # clickable rectangles
        "hover": None,
        "mode": None,           # "drag" or "resize"
        "sidebar_open": False,
        "sending": False,
        "minimized": False,
        "bg_key": None,
        "bg_img": None
    }

    ui_refs = []                # images that must stay alive
    panel_cache = {}
    bubble_cache = {}

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------
    def load_icon(name, size):
        return Image.open(f"icons/{name}.png").convert("RGBA").resize(
            (size, size),
            Image.Resampling.LANCZOS
        )

    def gradient_image(w, h, c1, c2):
        # Diagonal (135 degree) gradient from c1 to c2
        xs = np.arange(w, dtype = np.float32)[None, :]
        ys = np.arange(h, dtype = np.float32)[:, None]
        t = ((xs + ys) / max(1, w + h))[..., None]

        arr = (
            np.array(c1, np.float32) * (1 - t) +
            np.array(c2, np.float32) * t
        )

        return Image.fromarray(arr.astype(np.uint8))

    def shape_image(mask_hi, w, h, fill, border, gradient = None):
        # Turn a hi-res mask into a smooth RGBA image with fill and border
        mask = mask_hi.resize((w, h), Image.Resampling.LANCZOS)

        if gradient:
            base = gradient_image(w, h, gradient[0], gradient[1])
            base = base.convert("RGBA")
            fill_alpha = 255
        else:
            base = Image.new("RGBA", (w, h), tuple(fill[:3]) + (255,))
            fill_alpha = fill[3]

        base.putalpha(mask.point(lambda p: p * fill_alpha // 255))

        if border:
            ring_hi = ImageChops.subtract(
                mask_hi,
                mask_hi.filter(ImageFilter.MinFilter(2 * SS + 1))
            )

            ring = ring_hi.resize((w, h), Image.Resampling.LANCZOS)
            border_alpha = border[3]

            edge = Image.new("RGBA", (w, h), tuple(border[:3]) + (255,))
            edge.putalpha(ring.point(lambda p: p * border_alpha // 255))

            base = Image.alpha_composite(base, edge)

        return base

    def get_panel(w, h, radius, fill, border):
        # Rounded translucent panel (title bar, input bar, sidebar, ...)
        key = (w, h, radius, fill, border)

        if key not in panel_cache:
            radius = min(radius, h // 2, w // 2)

            mask_hi = Image.new("L", (w * SS, h * SS), 0)

            ImageDraw.Draw(mask_hi).rounded_rectangle(
                (0, 0, w * SS - 1, h * SS - 1),
                radius * SS,
                fill = 255
            )

            panel_cache[key] = ImageTk.PhotoImage(
                shape_image(mask_hi, w, h, fill, border)
            )

        return panel_cache[key]

    def get_bubble(w, h, sender):
        # Chat bubble with a small "tail" corner
        key = (w, h, sender)

        if key not in bubble_cache:
            r = min(BUBBLE_RADIUS, h // 2)

            mask_hi = Image.new("L", (w * SS, h * SS), 0)
            draw = ImageDraw.Draw(mask_hi)

            draw.rounded_rectangle(
                (0, 0, w * SS - 1, h * SS - 1),
                r * SS,
                fill = 255
            )

            if sender == "You":
                draw.rounded_rectangle(
                    ((w - r) * SS, (h - r) * SS, w * SS - 1, h * SS - 1),
                    BUBBLE_TAIL * SS,
                    fill = 255,
                    corners = (False, False, True, False)
                )

                image = shape_image(
                    mask_hi, w, h,
                    None,
                    USER_BORDER,
                    gradient = USER_GRADIENT
                )
            else:
                draw.rounded_rectangle(
                    (0, 0, r * SS - 1, r * SS - 1),
                    BUBBLE_TAIL * SS,
                    fill = 255,
                    corners = (True, False, False, False)
                )

                image = shape_image(
                    mask_hi, w, h,
                    GLASS_FILL,
                    GLASS_BORDER
                )

            bubble_cache[key] = ImageTk.PhotoImage(image)

        return bubble_cache[key]

    def make_circle_button(c1, c2, icon, icon_opacity = 1.0):
        d, ss = 36, 4

        mask = Image.new("L", (d * ss, d * ss), 0)

        ImageDraw.Draw(mask).ellipse(
            (0, 0, d * ss - 1, d * ss - 1),
            fill = 255
        )

        mask = mask.resize((d, d), Image.Resampling.LANCZOS)

        image = gradient_image(d, d, c1, c2).convert("RGBA")
        image.putalpha(mask)

        glyph = icon.copy()

        if icon_opacity < 1:
            alpha = glyph.getchannel("A").point(
                lambda p: int(p * icon_opacity)
            )
            glyph.putalpha(alpha)

        image.alpha_composite(
            glyph,
            ((d - glyph.width) // 2, (d - glyph.height) // 2)
        )

        return ImageTk.PhotoImage(image)

    # ------------------------------------------------------------------
    # Galaxy background
    # ------------------------------------------------------------------
    def build_background(width, height, radius):
        # Build the soft gradient small, then upscale
        sw = max(2, width // 3)
        sh = max(2, height // 3)

        xs = np.linspace(0, 1, sw, dtype = np.float32)[None, :]
        ys = np.linspace(0, 1, sh, dtype = np.float32)[:, None]

        def linear_t(angle):
            # CSS-style linear gradient position (0 to 1)
            a = np.radians(angle)
            dx, dy = np.sin(a), -np.cos(a)
            length = abs(width * dx) + abs(height * dy)

            return (
                (xs * width - width / 2) * dx +
                (ys * height - height / 2) * dy
            ) / length + 0.5

        def blob(img, cx, cy, rx, ry, color, strength, fade):
            dist = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2)
            alpha = (np.clip(1 - dist / fade, 0, 1) * strength)[..., None]

            return (
                img * (1 - alpha) +
                np.array(color, np.float32) * alpha
            )

        # Deep base gradient
        t = linear_t(145)

        img = np.stack(
            [
                np.interp(t, BASE_STOPS, [c[i] for c in BASE_COLORS])
                for i in range(3)
            ],
            axis = -1
        ).astype(np.float32)

        # Wide, muted nebula clouds
        img = blob(img, 0.85, 0.82, 1.20, 0.90, (140, 80, 145), 0.18, 0.78)
        img = blob(img, 0.15, 0.25, 1.40, 0.90, (92, 68, 150), 0.26, 0.75)

        # Faint diagonal haze band
        t = linear_t(118)
        stops = [0.24, 0.48, 0.56, 0.78]

        haze_alpha = np.interp(t, stops, [0, 0.09, 0.06, 0])[..., None]

        haze_color = np.stack(
            [
                np.interp(t, stops, [150, 150, 180, 180]),
                np.interp(t, stops, [125, 125, 140, 140]),
                np.interp(t, stops, [190, 190, 185, 185])
            ],
            axis = -1
        )

        img = img * (1 - haze_alpha) + haze_color * haze_alpha

        # A few deeper purple patches
        img = blob(img, 0.58, 0.90, 0.30, 0.26, (40, 10, 82), 0.50, 1.0)
        img = blob(img, 0.72, 0.28, 0.28, 0.34, (34, 8, 70), 0.55, 1.0)
        img = blob(img, 0.32, 0.58, 0.34, 0.30, (38, 10, 78), 0.60, 1.0)

        image = Image.fromarray(
            np.clip(img, 0, 255).astype(np.uint8)
        ).resize(
            (width, height),
            Image.Resampling.BICUBIC
        )

        # Sparkles and light dithering at full resolution
        full = np.array(image, dtype = np.float32)

        for sx, sy, size, strength in STARS:
            cx, cy = sx * width, sy * height

            x0 = int(max(0, cx - size - 1))
            x1 = int(min(width, cx + size + 2))
            y0 = int(max(0, cy - size - 1))
            y1 = int(min(height, cy + size + 2))

            yy, xx = np.mgrid[y0:y1, x0:x1]
            dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            alpha = (np.clip(1 - dist / size, 0, 1) * strength)[..., None]

            full[y0:y1, x0:x1] = (
                full[y0:y1, x0:x1] * (1 - alpha) +
                np.array(STAR_COLOR, np.float32) * alpha
            )

        rng = np.random.default_rng(7)
        full += rng.normal(0, 0.7, (height, width, 1)).astype(np.float32)

        image = Image.fromarray(np.clip(full, 0, 255).astype(np.uint8))

        # Rounded window corners (the key color becomes see-through)
        if radius:
            ImageDraw.Draw(image).rounded_rectangle(
                (0, 0, width - 1, height - 1),
                radius,
                outline = (78, 60, 118),
                width = 1
            )

            ss = 2
            mask = Image.new("L", (width * ss, height * ss), 0)

            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, width * ss - 1, height * ss - 1),
                radius * ss,
                fill = 255
            )

            mask = mask.resize((width, height), Image.Resampling.LANCZOS)

            image = Image.composite(
                image,
                Image.new("RGB", (width, height), (1, 1, 1)),
                mask
            )

        return image

    # ------------------------------------------------------------------
    # Main canvas
    # ------------------------------------------------------------------
    canvas = tk.Canvas(
        window,
        bg = KEY,
        highlightthickness = 0,
        bd = 0
    )

    canvas.pack(fill = "both", expand = True)

    # Static images (created once)
    icon_photos = {
        "min": ImageTk.PhotoImage(load_icon("minimize", 16)),
        "max": ImageTk.PhotoImage(load_icon("maximize", 16)),
        "close": ImageTk.PhotoImage(load_icon("close", 16)),
        "sparkle": ImageTk.PhotoImage(load_icon("logo_1_sparkle", 28)),
    }

    control_hover = {
        "normal": get_panel(40, 30, 8, (59, 42, 102, 255), None),
        "close": get_panel(40, 30, 8, (196, 43, 59, 255), None)
    }

    settings_glyph = load_icon("settings", 20)
    send_glyph = load_icon("send", 20)

    button_images = {
        "settings": {
            "normal": make_circle_button((138, 58, 158), (91, 60, 176), settings_glyph),
            "hover": make_circle_button((158, 74, 178), (110, 78, 198), settings_glyph)
        },
        "send": {
            "normal": make_circle_button((138, 58, 158), (91, 60, 176), send_glyph),
            "hover": make_circle_button((158, 74, 178), (110, 78, 198), send_glyph),
            "disabled": make_circle_button((70, 56, 92), (58, 48, 84), send_glyph, 0.45)
        }
    }


    # ------------------------------------------------------------------
    # Settings sidebar
    # ------------------------------------------------------------------
    settings_sidebar = ctk.CTkScrollableFrame(
        window,
        fg_color = SIDEBAR_HEX,
        corner_radius = 0,
        border_width = 0,
        scrollbar_button_color = "#5B3CB0",
        scrollbar_button_hover_color = "#7656C9"
    )

    settings_title = ctk.CTkLabel(
        settings_sidebar,
        text = "Settings",
        font = FONT_HEADING,
        text_color = TEXT
    )

    settings_title.pack(
        anchor = "w",
        padx = 10,
        pady = (10, 20)
    )

    def add_setting_label(title):
        label = ctk.CTkLabel(
            settings_sidebar,
            text = title,
            font = FONT_LABEL,
            text_color = TEXT
        )

        label.pack(
            anchor = "w",
            padx = 10,
            pady = (14, 5)
        )

    def add_setting_menu(title, setting, options):
        add_setting_label(title)

        menu = ctk.CTkOptionMenu(
            settings_sidebar,
            values = options,
            command = lambda value: update_setting(setting, value),
            fg_color = "#3B2A66",
            button_color = "#5B3CB0",
            button_hover_color = "#6B4BC4",
            text_color = "#FFFFFF",
            dropdown_fg_color = SIDEBAR_HEX,
            dropdown_hover_color = "#3B2A66",
            dropdown_text_color = "#FFFFFF",
            font = FONT_BODY,
            dropdown_font = FONT_BODY
        )

        menu.set(settings[setting])
        menu.pack(fill = "x", padx = 10, pady = 2)
        menu.configure(height = 36)

        return menu

    # Appearance
    add_setting_label("Appearance")

    appearance_menu = ctk.CTkOptionMenu(
        settings_sidebar,
        values = ["Dark", "Light", "System"],
        command = ctk.set_appearance_mode,
        fg_color = "#3B2A66",
        button_color = "#5B3CB0",
        button_hover_color = "#6B4BC4",
        text_color = "#FFFFFF",
        dropdown_fg_color = SIDEBAR_HEX,
        dropdown_hover_color = "#3B2A66",
        dropdown_text_color = "#FFFFFF",
        font = FONT_BODY,
        dropdown_font = FONT_BODY
    )

    appearance_menu.set("Dark")
    appearance_menu.pack(fill = "x", padx = 10, pady = 2)
    appearance_menu.configure(height = 36)

    # Assistant personality
    add_setting_menu(
        "Personality",
        "personality",
        ["Professional", "Casual", "Teacher", "Concise", "Creative"]
    )

    # Communication tone
    add_setting_menu(
        "Tone",
        "tone",
        ["Formal", "Friendly", "Direct", "Humorous"]
    )

    # Response length
    add_setting_menu(
        "Response Length",
        "response_length",
        ["Short", "Normal", "Detailed"]
    )

    # Response language
    add_setting_menu(
        "Language",
        "language",
        ["English", "French", "Spanish", "German"]
    )

    # Technical knowledge level
    add_setting_menu(
        "Technical Level",
        "technical_level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    # Creativity
    add_setting_menu(
        "Creativity",
        "creativity",
        ["Low", "Medium", "High"]
    )

    # Custom instructions
    add_setting_label("Custom Instructions")

    custom_instructions_box = ctk.CTkTextbox(
        settings_sidebar,
        height = 100,
        corner_radius = 10,
        fg_color = "#291D40",
        border_width = 1,
        border_color = "#51416F",
        text_color = TEXT,
        font = FONT_BODY
    )

    custom_instructions_box.pack(
        fill = "x",
        padx = 10,
        pady = (0, 5)
    )

    custom_instructions_box.insert(
        "1.0",
        settings["custom_instructions"]
    )

    save_instructions_button = ctk.CTkButton(
        settings_sidebar,
        text = "Apply Instructions",
        command = update_custom_instructions,
        fg_color = "#5B3CB0",
        hover_color = "#7656C9",
        text_color = "#FFFFFF",
        font = FONT_BODY,
        corner_radius = 10,
        height = 34
    )

    save_instructions_button.pack(
        fill = "x",
        padx = 10,
        pady = (5, 20)
    )

    # ------------------------------------------------------------------
    # Message input (a CustomTkinter entry placed on the canvas)
    # ------------------------------------------------------------------
    user_input = ctk.CTkEntry(
        canvas,
        placeholder_text = "Type here...",
        height = 36,
        corner_radius = 0,
        fg_color = "#1e1336",
        bg_color = "#1e1336",
        border_width = 0,
        text_color = TEXT,
        placeholder_text_color = MUTED,
        font = FONT_BODY
    )

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def wrap_message(text, font, max_width):
        wrapped_lines = []

        for paragraph in text.split("\n"):
            words = paragraph.split()

            if not words:
                wrapped_lines.append("")
                continue

            current_line = words[0]

            for word in words[1:]:
                test_line = current_line + " " + word

                if font.measure(test_line) <= max_width:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word

            wrapped_lines.append(current_line)

        return "\n".join(wrapped_lines)

    def compute_geometry(width, height):
        g = {"W": width, "H": height}

        g["title"] = (PAD, PAD, width - PAD, PAD + TITLE_H)
        g["input"] = (PAD, height - PAD - INPUT_H, width - PAD, height - PAD)
        g["chat_top"] = PAD + TITLE_H + 12
        g["chat_bottom"] = height - PAD - INPUT_H - 12

        chat_left = PAD
        g["sidebar"] = None

        if S["sidebar_open"]:
            g["sidebar"] = (
                PAD,
                g["chat_top"],
                PAD + SIDEBAR_W,
                g["chat_bottom"]
            )

            chat_left = PAD + SIDEBAR_W + 14

        g["chat_left"] = chat_left
        g["chat_right"] = width - PAD

        return g

    def get_layout(chat_width):
        key = (chat_width, len(conversation), thinking_visible)

        if S["layout_key"] == key:
            return S["layout"]

        max_bubble_width = max(160, int(chat_width * 0.58))
        max_text_width = max_bubble_width - BUBBLE_PAD_X * 2
        line_height = MESSAGE_FONT.metrics("linespace")

        items = []
        y = 8

        for sender, content in conversation:
            wrapped = wrap_message(content, MESSAGE_FONT, max_text_width)
            lines = wrapped.split("\n")

            text_width = max(MESSAGE_FONT.measure(line) for line in lines)

            width = min(max_bubble_width, text_width + BUBBLE_PAD_X * 2)
            height = line_height * len(lines) + BUBBLE_PAD_Y * 2

            items.append((sender, wrapped, y, width, height))

            y += height + 14

        thinking_y = y

        if thinking_visible:
            y += 30

        S["layout"] = {
            "items": items,
            "height": y + 8,
            "thinking_y": thinking_y
        }

        S["layout_key"] = key

        return S["layout"]

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def render_messages(scroll_to_bottom = False):
        g = S["g"]

        if not g:
            return

        canvas.delete("msgs")

        if len(bubble_cache) > 200:
            bubble_cache.clear()

        top = g["chat_top"]
        bottom = g["chat_bottom"]
        chat_left = g["chat_left"]
        chat_right = g["chat_right"]

        view_height = bottom - top
        layout = get_layout(chat_right - chat_left)

        max_scroll = max(0, layout["height"] - view_height)

        if scroll_to_bottom:
            S["scroll"] = max_scroll

        S["scroll"] = max(0, min(S["scroll"], max_scroll))

        for sender, wrapped, rel_y, width, height in layout["items"]:
            y1 = top + rel_y - S["scroll"]
            y2 = y1 + height

            # Skip bubbles that are scrolled out of view
            if y2 < top - 4 or y1 > bottom + 4:
                continue

            if sender == "You":
                x1 = chat_right - 22 - width
            else:
                x1 = chat_left + 10

            bubble = get_bubble(int(width), int(height), sender)

            canvas.create_image(
                int(x1),
                int(y1),
                image = bubble,
                anchor = "nw",
                tags = "msgs"
            )

            canvas.create_text(
                x1 + BUBBLE_PAD_X,
                y1 + BUBBLE_PAD_Y,
                text = wrapped,
                font = MESSAGE_FONT,
                fill = "#FFFFFF" if sender == "You" else TEXT,
                anchor = "nw",
                justify = "left",
                tags = "msgs"
            )

        if thinking_visible:
            canvas.create_text(
                chat_left + 18,
                top + layout["thinking_y"] - S["scroll"],
                text = "Thinking...",
                font = THINKING_FONT,
                fill = MUTED,
                anchor = "nw",
                tags = "msgs"
            )

        # Slim scroll indicator
        if max_scroll > 0:
            thumb_height = max(30, view_height * view_height / layout["height"])

            thumb_y = top + (
                S["scroll"] / max_scroll
            ) * (view_height - thumb_height)

            canvas.create_line(
                chat_right - 6,
                thumb_y,
                chat_right - 6,
                thumb_y + thumb_height,
                width = 5,
                capstyle = "round",
                fill = "#4A3A78",
                tags = "msgs"
            )

        # Keep the covers and the interface above the messages
        canvas.tag_raise("cover")
        canvas.tag_raise("ui")

    def render_all():
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 2 or height < 2:
            return

        zoomed = window.state() == "zoomed"
        radius = WINDOW_RADIUS if (ROUNDED and not zoomed) else 0

        g = compute_geometry(width, height)
        S["g"] = g

        canvas.delete("all")

        ui_refs.clear()

        if len(panel_cache) > 30:
            panel_cache.clear()

        S["items"] = {}
        S["regions"] = {}
        S["hover"] = None

        # Background (cached until the size changes)
        bg_key = (width, height, radius)

        if S["bg_key"] != bg_key:
            S["bg_img"] = build_background(width, height, radius)
            S["bg_key"] = bg_key

        bg_img = S["bg_img"]

        bg_photo = ImageTk.PhotoImage(bg_img)
        ui_refs.append(bg_photo)

        canvas.create_image(
            0,
            0,
            image = bg_photo,
            anchor = "nw",
            tags = "bg"
        )

        # Messages
        render_messages()

        # Covers hide messages that scroll under the title and input bars
        top_cover = ImageTk.PhotoImage(
            bg_img.crop((0, 0, width, g["chat_top"]))
        )

        bottom_cover = ImageTk.PhotoImage(
            bg_img.crop((0, g["chat_bottom"], width, height))
        )

        ui_refs.extend([top_cover, bottom_cover])

        canvas.create_image(0, 0, image = top_cover, anchor = "nw", tags = "cover")

        canvas.create_image(
            0,
            g["chat_bottom"],
            image = bottom_cover,
            anchor = "nw",
            tags = "cover"
        )

        # Title bar
        tx1, ty1, tx2, ty2 = g["title"]

        canvas.create_image(
            tx1,
            ty1,
            image = get_panel(tx2 - tx1, ty2 - ty1, 20, BAR_FILL, BAR_BORDER),
            anchor = "nw",
            tags = "ui"
        )

        title_center = (ty1 + ty2) // 2

        # Sparkle logo
        canvas.create_image(
            tx1 + 18,
            title_center,
            image=icon_photos["sparkle"],
            anchor="w",
            tags="ui"
        )

        # Application title
        canvas.create_text(
            tx1 + 18 + 28 + 10,
            title_center,
            text="Custom AI Assistant",
            font=TITLE_FONT,
            fill="#FFFFFF",
            anchor="w",
            tags="ui"
        )

        # Window controls
        close_box = (tx2 - 8 - 40, title_center - 15, tx2 - 8, title_center + 15)
        max_box = (close_box[0] - 44, close_box[1], close_box[2] - 44, close_box[3])
        min_box = (max_box[0] - 44, max_box[1], max_box[2] - 44, max_box[3])

        for name, box in (("close", close_box), ("max", max_box), ("min", min_box)):
            hover_image = control_hover["close" if name == "close" else "normal"]

            S["items"][name + "_hover"] = canvas.create_image(
                box[0],
                box[1],
                image = hover_image,
                anchor = "nw",
                state = "hidden",
                tags = "ui"
            )

            canvas.create_image(
                (box[0] + box[2]) // 2,
                (box[1] + box[3]) // 2,
                image = icon_photos[name],
                anchor = "center",
                tags = "ui"
            )

            S["regions"][name] = box

        # Input bar
        ix1, iy1, ix2, iy2 = g["input"]

        canvas.create_image(
            ix1,
            iy1,
            image = get_panel(ix2 - ix1, iy2 - iy1, 27, BAR_FILL, BAR_BORDER),
            anchor = "nw",
            tags = "ui"
        )

        input_center = (iy1 + iy2) // 2

        settings_x = ix1 + 9
        send_x = ix2 - 9 - 36
        button_y = input_center - 18

        S["items"]["settings"] = canvas.create_image(
            settings_x,
            button_y,
            image = button_images["settings"]["normal"],
            anchor = "nw",
            tags = "ui"
        )

        S["regions"]["settings"] = (
            settings_x, button_y, settings_x + 36, button_y + 36
        )

        S["items"]["send"] = canvas.create_image(
            send_x,
            button_y,
            image = button_images["send"][
                "disabled" if S["sending"] else "normal"
            ],
            anchor = "nw",
            tags = "ui"
        )

        S["regions"]["send"] = (send_x, button_y, send_x + 36, button_y + 36)

        # The whole title bar can be dragged (buttons are checked first)
        S["regions"]["title"] = (tx1, ty1, tx2, ty2)

        # Text box between the two buttons
        entry_x1 = settings_x + 36 + 10
        entry_x2 = send_x - 10

        # Match the text box color to the bar underneath it
        pixel = bg_img.getpixel(((entry_x1 + entry_x2) // 2, input_center))

        alpha = BAR_FILL[3] / 255

        blended = tuple(
            int(pixel[i] * (1 - alpha) + BAR_FILL[i] * alpha)
            for i in range(3)
        )

        entry_color = "#%02x%02x%02x" % blended

        user_input.configure(
            fg_color = entry_color,
            bg_color = entry_color,
            width = entry_x2 - entry_x1,
            height = 36
        )

        canvas.create_window(
            entry_x1,
            input_center,
            window = user_input,
            anchor = "w",
            width = entry_x2 - entry_x1,
            height = 36,
            tags = "entry"
        )

        # Settings sidebar
        if g["sidebar"]:
            sx1, sy1, sx2, sy2 = g["sidebar"]

            canvas.create_image(
                sx1,
                sy1,
                image=get_panel(
                    sx2 - sx1,
                    sy2 - sy1,
                    22,
                    SIDEBAR_FILL,
                    SIDEBAR_BORDER
                ),
                anchor="nw",
                tags="ui"
            )

            settings_sidebar.configure(
                width=sx2 - sx1 - 32,
                height=sy2 - sy1 - 32
            )

            settings_sidebar.place(
                x=sx1 + 16,
                y=sy1 + 16
            )

            settings_sidebar.lift()

            settings_sidebar._parent_canvas.configure(
                yscrollincrement=30
            )

        else:
            settings_sidebar.place_forget()

    # ------------------------------------------------------------------
    # Redraw scheduling
    # ------------------------------------------------------------------
    def redraw_after_resize():
        nonlocal chat_resize_job

        chat_resize_job = None
        render_all()

    def schedule_redraw(event = None):
        nonlocal chat_resize_job

        if window.is_resizing:
            return

        if chat_resize_job is not None:
            window.after_cancel(chat_resize_job)

        chat_resize_job = window.after(120, redraw_after_resize)

    canvas.bind("<Configure>", schedule_redraw)

    # ------------------------------------------------------------------
    # Window actions
    # ------------------------------------------------------------------
    def toggle_maximize():
        if window.state() == "zoomed":
            window.state("normal")
        else:
            window.state("zoomed")

    def minimize_window():
        S["minimized"] = True
        window.overrideredirect(False)
        window.iconify()

    def on_map(event):
        # Restore the custom title bar after the window is un-minimized
        if event.widget is window and S["minimized"]:
            S["minimized"] = False
            window.after(10, lambda: window.overrideredirect(True))

    window.bind("<Map>", on_map)

    def toggle_settings():
        S["sidebar_open"] = not S["sidebar_open"]
        S["layout_key"] = None
        render_all()

    def start_drag(event):
        if window.state() == "zoomed":
            return

        S["mode"] = "drag"

        window.drag_start_x = event.x_root
        window.drag_start_y = event.y_root

        window.drag_window_x = window.winfo_x()
        window.drag_window_y = window.winfo_y()

    def drag_window(event):
        x = window.drag_window_x + (event.x_root - window.drag_start_x)
        y = window.drag_window_y + (event.y_root - window.drag_start_y)

        window.geometry(f"+{x}+{y}")

    def start_resize(event, direction):
        S["mode"] = "resize"
        window.is_resizing = True

        window.resize_start_x = event.x_root
        window.resize_start_y = event.y_root

        window.resize_start_width = window.winfo_width()
        window.resize_start_height = window.winfo_height()

        window.resize_start_window_x = window.winfo_x()
        window.resize_start_window_y = window.winfo_y()

        window.resize_direction = direction

    def resize_window(event):
        dx = event.x_root - window.resize_start_x
        dy = event.y_root - window.resize_start_y

        width = window.resize_start_width
        height = window.resize_start_height

        x = window.resize_start_window_x
        y = window.resize_start_window_y

        direction = window.resize_direction

        if "e" in direction:
            width = max(MIN_WIDTH, width + dx)

        if "s" in direction:
            height = max(MIN_HEIGHT, height + dy)

        if "w" in direction:
            new_width = max(MIN_WIDTH, window.resize_start_width - dx)
            x += window.resize_start_width - new_width
            width = new_width

        if "n" in direction:
            new_height = max(MIN_HEIGHT, window.resize_start_height - dy)
            y += window.resize_start_height - new_height
            height = new_height

        window.geometry(f"{width}x{height}+{x}+{y}")

    def finish_resize():
        window.is_resizing = False
        window.after(100, render_all)

    # ------------------------------------------------------------------
    # Mouse handling (everything is drawn on one canvas)
    # ------------------------------------------------------------------
    BUTTONS = ("close", "max", "min", "settings", "send")

    CURSORS = {
        "n": "size_ns",
        "s": "size_ns",
        "w": "size_we",
        "e": "size_we",
        "nw": "size_nw_se",
        "se": "size_nw_se",
        "ne": "size_ne_sw",
        "sw": "size_ne_sw"
    }

    def edge_direction(x, y):
        if window.state() == "zoomed":
            return ""

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        direction = ""

        if y <= RESIZE_BORDER:
            direction += "n"
        elif y >= height - RESIZE_BORDER:
            direction += "s"

        if x <= RESIZE_BORDER:
            direction += "w"
        elif x >= width - RESIZE_BORDER:
            direction += "e"

        return direction

    def hit_test(x, y):
        for name, (x1, y1, x2, y2) in S["regions"].items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return name

        return None

    def apply_hover(name, on):
        if not name:
            return

        if name in ("close", "max", "min"):
            canvas.itemconfigure(
                S["items"][name + "_hover"],
                state = "normal" if on else "hidden"
            )

        elif name == "settings":
            canvas.itemconfigure(
                S["items"]["settings"],
                image = button_images["settings"]["hover" if on else "normal"]
            )

        elif name == "send" and not S["sending"]:
            canvas.itemconfigure(
                S["items"]["send"],
                image = button_images["send"]["hover" if on else "normal"]
            )

    def set_hover(name):
        old = S["hover"]

        if old == name:
            return

        S["hover"] = name

        apply_hover(old, False)
        apply_hover(name, True)

    def set_sending(sending):
        S["sending"] = sending

        item = S["items"].get("send")

        if item:
            canvas.itemconfigure(
                item,
                image = button_images["send"][
                    "disabled" if sending else "normal"
                ]
            )

    def on_motion(event):
        if S["mode"]:
            return

        direction = edge_direction(event.x, event.y)

        if direction:
            canvas.configure(cursor = CURSORS[direction])
            set_hover(None)
            return

        name = hit_test(event.x, event.y)

        if name in BUTTONS:
            canvas.configure(cursor = "hand2")
            set_hover(name)
        else:
            canvas.configure(cursor = "")
            set_hover(None)

    def on_press(event):
        direction = edge_direction(event.x, event.y)

        if direction:
            start_resize(event, direction)
            return

        name = hit_test(event.x, event.y)

        if name == "close":
            window.destroy()
        elif name == "max":
            toggle_maximize()
        elif name == "min":
            minimize_window()
        elif name == "settings":
            toggle_settings()
        elif name == "send":
            if not S["sending"]:
                send_message()
        elif name == "title":
            start_drag(event)

    def on_drag(event):
        if S["mode"] == "drag":
            drag_window(event)
        elif S["mode"] == "resize":
            resize_window(event)

    def on_release(event):
        if S["mode"] == "resize":
            finish_resize()

        S["mode"] = None

    def on_wheel(event):
        if event.num == 4:
            step = -60
        elif event.num == 5:
            step = 60
        else:
            step = -int(event.delta / 120 * 60)

        S["scroll"] += step
        render_messages()

    canvas.bind("<Motion>", on_motion)
    canvas.bind("<Button-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<MouseWheel>", on_wheel)
    canvas.bind("<Button-4>", on_wheel)
    canvas.bind("<Button-5>", on_wheel)
    canvas.bind("<Leave>", lambda event: set_hover(None))

    # ------------------------------------------------------------------
    # Chat logic
    # ------------------------------------------------------------------
    def add_message(sender, content):
        conversation.append((sender, content))
        render_messages(scroll_to_bottom = True)

    # Queue for collecting AI response tokens
    response_parts = []

    # Check for the AI response
    def check_response():
        nonlocal thinking_visible

        try:
            response = response_queue.get_nowait()

            if response is not None:
                response_parts.append(response)

                window.after(50, check_response)

            else:
                thinking_visible = False
                render_messages()

                if response_parts:
                    full_response = "".join(response_parts)
                    add_message("Assistant", full_response)
                else:
                    add_message(
                        "Assistant",
                        "Unable to generate a response"
                    )

                set_sending(False)

        except queue.Empty:
            window.after(100, check_response)

    # Send a message to the AI
    def send_message():
        nonlocal thinking_visible

        message = user_input.get()

        if message:
            add_message("You", message)

            user_input.delete(0, "end")

            messages.append({
                "role": "user",
                "content": message
            })

            response_parts.clear()

            set_sending(True)

            thinking_visible = True
            render_messages(scroll_to_bottom = True)

            # Run the AI request in a background thread
            def get_response():
                try:
                    for token in assistant.ask_ai_stream(messages):
                        response_queue.put(token)

                except Exception as error:
                    response_queue.put(
                        f"Unable to generate a response: {error}"
                    )

                response_queue.put(None)

            threading.Thread(
                target = get_response,
                daemon = True
            ).start()

            check_response()

    user_input.bind(
        "<Return>",
        lambda event: send_message()
    )

    # Draw the first frame once the window is ready
    window.after(150, render_all)
    window.after(400, user_input.focus_set)

    # Keep application running
    window.mainloop()


if __name__ == "__main__":
    main()