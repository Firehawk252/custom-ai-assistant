
# Custom AI Assistant - GI
# Create a separate graphical interface that opens in its own desktop window
# Notes:
#   'window' creates the main application window
#   'window.geometry' sets the initial dimensions
#   'CustomTkinter' widgets create and organize the interface
#   'pack()' controls how widgets are positioned and sized
#   'bind' and 'lambda' allow Enter to send messages
#   'threading' runs AI requests separately from the GUI
#   'queue' safely passes responses from the background thread to the GUI

import main as assistant
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.font as tkfont
import threading
import queue


def main():
    # Configure application appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    response_queue = queue.Queue()
    thinking_visible = False

    # Create the main application window
    window = ctk.CTk()
    window.title("Custom AI Assistant")
    window.geometry("1100x700")
    window.configure(fg_color = "#111318")
    window.minsize(900, 600)
    window.is_resizing = False

    # Configure application fonts
    FONT_FAMILY = "Plus Jakarta Sans"

    FONT_TITLE = ctk.CTkFont(
        family = FONT_FAMILY,
        size = 20,
        weight = "bold"
    )

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

    FONT_SMALL = ctk.CTkFont(
        family = FONT_FAMILY,
        size = 12,
        weight = "normal"
    )

    MESSAGE_FONT = tkfont.Font(
        family = FONT_FAMILY,
        size = 14
    )

    THINKING_FONT = tkfont.Font(
        family = FONT_FAMILY,
        size = 12
    )

    # Load title bar icons
    minimize_icon = ctk.CTkImage(
        light_image = Image.open("icons/minimize.png"),
        dark_image = Image.open("icons/minimize.png"),
        size = (16, 16)
    )

    maximize_icon = ctk.CTkImage(
        light_image = Image.open("icons/maximize.png"),
        dark_image = Image.open("icons/maximize.png"),
        size = (16, 16)
    )

    close_icon = ctk.CTkImage(
        light_image = Image.open("icons/close.png"),
        dark_image = Image.open("icons/close.png"),
        size = (16, 16)
    )

    settings_icon = ctk.CTkImage(
        light_image = Image.open("icons/settings.png"),
        dark_image = Image.open("icons/settings.png"),
        size = (20, 20)
    )

    send_icon = ctk.CTkImage(
        light_image = Image.open("icons/send.png"),
        dark_image = Image.open("icons/send.png"),
        size = (20, 20)
    )

    # Hide the default Windows title bar
    window.overrideredirect(True)

    # Custom application title bar
    title_bar = ctk.CTkFrame(
        window,
        height = 48,
        corner_radius = 14,
        fg_color = "#1D1E27",
        border_width = 1,
        border_color = "#292A35"
    )

    title_bar.pack(
        fill = "x",
        padx = 18,
        pady = (14, 0)
    )

    title_bar.pack_propagate(False)

    # Window dragging
    def start_drag(event):
        window.drag_start_x = event.x_root
        window.drag_start_y = event.y_root

        window.drag_window_x = window.winfo_x()
        window.drag_window_y = window.winfo_y()

    def drag_window(event):
        x = window.drag_window_x + (
            event.x_root - window.drag_start_x
        )

        y = window.drag_window_y + (
            event.y_root - window.drag_start_y
        )

        window.geometry(f"+{x}+{y}")

    title_bar.bind("<Button-1>", start_drag)
    title_bar.bind("<B1-Motion>", drag_window)

    title_label = ctk.CTkLabel(
        title_bar,
        text = "Custom AI Assistant",
        font = FONT_TITLE,
        text_color = "#FFFFFF"
    )

    title_label.pack(side = "left", padx = 15)

    title_label.bind("<Button-1>", start_drag)
    title_label.bind("<B1-Motion>", drag_window)

    # Window resizing
    RESIZE_BORDER = 8
    MIN_WIDTH = 900
    MIN_HEIGHT = 600

    def start_resize(event):
        window.is_resizing = True

        window.resize_start_x = event.x_root
        window.resize_start_y = event.y_root

        window.resize_start_width = window.winfo_width()
        window.resize_start_height = window.winfo_height()

        window.resize_start_window_x = window.winfo_x()
        window.resize_start_window_y = window.winfo_y()

        window.resize_direction = event.widget.resize_direction

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
            new_width = max(
                MIN_WIDTH,
                window.resize_start_width - dx
            )

            x += window.resize_start_width - new_width
            width = new_width

        if "n" in direction:
            new_height = max(
                MIN_HEIGHT,
                window.resize_start_height - dy
            )

            y += window.resize_start_height - new_height
            height = new_height

        window.geometry(f"{width}x{height}+{x}+{y}")

    # Windows controls
    close_button = ctk.CTkButton(
        title_bar,
        text = "",
        image = close_icon,
        width = 40,
        height = 30,
        corner_radius = 6,
        fg_color = "transparent",
        hover_color = "#C42B3B",
        command = window.destroy
    )

    close_button.pack(side = "right", padx = 5)

    # Maximize and restore window
    def toggle_maximize():
        if window.state() == "zoomed":
            window.state("normal")
        else:
            window.state("zoomed")

    maximize_button = ctk.CTkButton(
        title_bar,
        text = "",
        image = maximize_icon,
        width = 40,
        height = 30,
        corner_radius = 6,
        fg_color = "transparent",
        hover_color = "#353640",
        command = toggle_maximize
    )

    maximize_button.pack(side = "right")

    minimize_button = ctk.CTkButton(
        title_bar,
        text = "",
        image = minimize_icon,
        width = 40,
        height = 30,
        corner_radius = 6,
        fg_color = "transparent",
        hover_color = "#353640",
        command = lambda: window.overrideredirect(False) or window.iconify()
    )

    minimize_button.pack(side = "right")

    # Initialize conversation settings and memory
    memories = assistant.load_memory()

    messages = assistant.create_messages(
        "Professional",
        "Friendly",
        "Normal",
        "English",
        "Beginner",
        "Medium",
        "",
        memories
    )

    # Update personality when the selection changes
    def update_personality(selected_personality):
        new_messages = assistant.create_messages(
            selected_personality,
            "Friendly",
            "Normal",
            "English",
            "Beginner",
            "Medium",
            "",
            memories
        )

        messages[0] = new_messages[0]

    # Main chat layout
    content_frame = ctk.CTkFrame(
        window,
        fg_color = "transparent",
        corner_radius = 0,
        border_width = 0
    )

    content_frame.pack(
        fill = "both",
        expand = True,
        padx = 18,
        pady = (14, 18)
    )

    # Settings sidebar
    settings_sidebar = ctk.CTkFrame(
        content_frame,
        width = 250,
        fg_color = "#211D2B",
        corner_radius = 20,
        border_width = 1,
        border_color = "#393144"
    )

    settings_sidebar.pack_propagate(False)

    settings_title = ctk.CTkLabel(
        settings_sidebar,
        text = "Settings",
        font = FONT_HEADING,
        text_color = "#E6E6EF"
    )

    settings_title.pack(
        anchor = "w",
        padx = 20,
        pady = (25, 30)
    )

    # Appearance settings
    appearance_label = ctk.CTkLabel(
        settings_sidebar,
        text = "Appearance",
        font = FONT_LABEL,
        text_color = "#E6E6EF"
    )

    appearance_label.pack(
        anchor = "w",
        padx = 20,
        pady = (0, 5)
    )

    appearance_menu = ctk.CTkOptionMenu(
        settings_sidebar,
        values = ["Dark", "Light", "System"],
        command = ctk.set_appearance_mode,
        fg_color = "#514568",
        button_color = "#403149",
        button_hover_color = "#665078",
        text_color = "#FFFFFF",
        dropdown_fg_color = "#292033",
        dropdown_hover_color = "#514568",
        dropdown_text_color = "#FFFFFF",
        font = FONT_BODY,
        dropdown_font = FONT_BODY
    )

    appearance_menu.pack(fill = "x", padx = 20)

    # Personality setting
    personality_label = ctk.CTkLabel(
        settings_sidebar,
        text = "Personality",
        font = FONT_LABEL,
        text_color = "#E6E6EF"
    )

    personality_label.pack(
        anchor = "w",
        padx = 20,
        pady = (25, 5)
    )

    personality_menu = ctk.CTkOptionMenu(
        settings_sidebar,
        values = [
            "Professional",
            "Casual",
            "Teacher",
            "Concise",
            "Creative"
        ],
        command = update_personality,
        fg_color = "#514568",
        button_color = "#403149",
        button_hover_color = "#665078",
        text_color = "#FFFFFF",
        dropdown_fg_color = "#292033",
        dropdown_hover_color = "#514568",
        dropdown_text_color = "#FFFFFF",
        font = FONT_BODY,
        dropdown_font = FONT_BODY
    )

    personality_menu.pack(fill = "x", padx = 20)

    # Main chat area
    chat_frame = ctk.CTkFrame(
        content_frame,
        fg_color = "transparent",
        corner_radius = 0,
        border_width = 0
    )

    chat_frame.pack(
        side = "right",
        fill = "both",
        expand = True
    )

    # Configure the chat layout
    chat_frame.grid_rowconfigure(0, weight = 1)
    chat_frame.grid_columnconfigure(0, weight = 1)

    # Toggle settings sidebar
    def toggle_settings():
        if settings_sidebar.winfo_manager():
            settings_sidebar.pack_forget()
        else:
            settings_sidebar.pack(
                side = "left",
                fill = "y",
                padx = (0, 15),
                before = chat_frame
            )

    # Conversation history displayed on the canvas
    conversation = []
    chat_image_ref = None
    chat_resize_job = None

    # Create the conversation canvas
    chat_canvas = tk.Canvas(
        chat_frame,
        bg = "#111318",
        highlightthickness = 0,
        bd = 0
    )

    chat_scrollbar = ctk.CTkScrollbar(
        chat_frame,
        orientation = "vertical",
        command = chat_canvas.yview,
        button_color = "#493957",
        button_hover_color = "#665078"
    )

    chat_canvas.configure(
        yscrollcommand = chat_scrollbar.set
    )

    chat_canvas.grid(
        row = 0,
        column = 0,
        sticky = "nsew",
        padx = (10, 0),
        pady = 5
    )

    chat_scrollbar.grid(
        row = 0,
        column = 1,
        sticky = "ns",
        padx = (0, 10),
        pady = 5
    )

    # Wrap text according to its pixel width
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

    # Draw rounded message bubbles
    def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, color):
        canvas.create_polygon(
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            smooth = True,
            splinesteps = 20,
            fill = color,
            outline = color
        )

    # Draw the gradient and conversation messages
    def redraw_chat_canvas(scroll_to_bottom = False):
        nonlocal chat_image_ref

        width = chat_canvas.winfo_width()
        height = chat_canvas.winfo_height()

        if width < 2 or height < 2:
            return

        # Generate the gradient at a smaller resolution
        small_width = max(1, width // 4)
        small_height = max(1, height // 4)

        image = Image.new(
            "RGB",
            (small_width, small_height)
        )

        pixels = image.load()

        base = (17, 19, 24)
        purple = (55, 42, 72)
        indigo = (36, 42, 62)

        for x in range(small_width):
            for y in range(small_height):
                x_normalized = x / max(1, small_width - 1)
                y_normalized = y / max(1, small_height - 1)

                # Purple glow toward the bottom-right
                purple_distance = (
                    ((x_normalized - 0.78) / 0.72) ** 2 +
                    ((y_normalized - 0.82) / 0.65) ** 2
                ) ** 0.5

                purple_glow = (
                    max(0, 1 - purple_distance) ** 2 * 0.35
                )

                # Subtle indigo glow toward the upper-left
                indigo_distance = (
                    ((x_normalized - 0.18) / 0.85) ** 2 +
                    ((y_normalized - 0.15) / 0.75) ** 2
                ) ** 0.5

                indigo_glow = (
                    max(0, 1 - indigo_distance) ** 2 * 0.12
                )

                pixels[x, y] = tuple(
                    int(
                        (
                            base[i] * (1 - purple_glow) +
                            purple[i] * purple_glow
                        ) * (1 - indigo_glow) +
                        indigo[i] * indigo_glow
                    )
                    for i in range(3)
                )

        image = image.resize(
            (width, height),
            Image.Resampling.BILINEAR
        )

        chat_image_ref = ImageTk.PhotoImage(image)

        chat_canvas.delete("all")

        # Draw the gradient directly on the chat canvas
        chat_canvas.create_image(
            0,
            0,
            image = chat_image_ref,
            anchor = "nw",
            tags = "background"
        )

        chat_canvas.tag_lower("background")

        # Position and draw each conversation message
        current_y = 18

        bubble_padding_x = 13
        bubble_padding_y = 9

        left_margin = 20
        right_margin = 20

        max_bubble_width = max(
            180,
            int(width * 0.65)
        )

        max_text_width = max_bubble_width - (
            bubble_padding_x * 2
        )

        line_height = MESSAGE_FONT.metrics("linespace")

        for sender, content in conversation:
            wrapped_text = wrap_message(
                content,
                MESSAGE_FONT,
                max_text_width
            )

            lines = wrapped_text.split("\n")

            text_width = max(
                MESSAGE_FONT.measure(line)
                for line in lines
            )

            text_height = line_height * len(lines)

            bubble_width = min(
                max_bubble_width,
                text_width + bubble_padding_x * 2
            )

            bubble_height = (
                text_height + bubble_padding_y * 2
            )

            if sender == "You":
                bubble_color = "#514568"
                x2 = width - right_margin
                x1 = x2 - bubble_width
            else:
                bubble_color = "#30263A"
                x1 = left_margin
                x2 = x1 + bubble_width

            y1 = current_y
            y2 = current_y + bubble_height

            draw_rounded_rectangle(
                chat_canvas,
                x1,
                y1,
                x2,
                y2,
                15,
                bubble_color
            )

            chat_canvas.create_text(
                x1 + bubble_padding_x,
                y1 + bubble_padding_y,
                text = wrapped_text,
                font = MESSAGE_FONT,
                fill = "#FFFFFF",
                anchor = "nw",
                justify = "left"
            )

            current_y = y2 + 12

        # Display the thinking indicator
        if thinking_visible:
            chat_canvas.create_text(
                left_margin + 8,
                current_y,
                text = "Thinking...",
                font = THINKING_FONT,
                fill = "#91869B",
                anchor = "nw"
            )

            current_y += 30

        # Update the scrollable area
        chat_canvas.configure(
            scrollregion = (
                0,
                0,
                width,
                max(height, current_y + 20)
            )
        )

        if scroll_to_bottom:
            chat_canvas.yview_moveto(1.0)

    # Delay redraws while resizing
    def schedule_chat_redraw(event):
        nonlocal chat_resize_job

        if window.is_resizing:
            return

        if chat_resize_job is not None:
            window.after_cancel(chat_resize_job)

        chat_resize_job = window.after(
            120,
            redraw_after_resize
        )

    def redraw_after_resize():
        nonlocal chat_resize_job

        chat_resize_job = None
        redraw_chat_canvas()

    chat_canvas.bind(
        "<Configure>",
        schedule_chat_redraw
    )

    # Display a new message in the conversation
    def add_message(sender, content):
        conversation.append((sender, content))
        redraw_chat_canvas(scroll_to_bottom = True)

    # User input area
    input_frame = ctk.CTkFrame(
        chat_frame,
        fg_color = "#20232C",
        corner_radius = 18,
        border_width = 1,
        border_color = "#363442",
        height = 58
    )

    input_frame.grid(
        row = 1,
        column = 0,
        columnspan = 2,
        sticky = "ew",
        padx = 18,
        pady = (8, 18)
    )

    input_frame.pack_propagate(False)

    # Settings button
    settings_button = ctk.CTkButton(
        input_frame,
        text = "",
        image = settings_icon,
        width = 36,
        height = 36,
        corner_radius = 18,
        fg_color = "#514568",
        hover_color = "#665078",
        command = toggle_settings
    )

    settings_button.pack(
        side = "left",
        padx = (8, 8),
        pady = 0
    )

    # Message input field
    user_input = ctk.CTkEntry(
        input_frame,
        placeholder_text = "Type here...",
        height = 44,
        corner_radius = 12,
        fg_color = "transparent",
        border_width = 0,
        text_color = "#E6E0EB",
        placeholder_text_color = "#91869B",
        font = FONT_BODY
    )

    user_input.pack(
        side = "left",
        fill = "x",
        expand = True,
        padx = (0, 8),
        pady = 0
    )

    # Queue for collecting AI response tokens
    response_parts = []

    # Check for the AI response
    def check_response():
        nonlocal thinking_visible

        try:
            response = response_queue.get_nowait()

            if response is not None:
                response_parts.append(response)

                window.after(
                    50,
                    check_response
                )

            else:
                thinking_visible = False
                redraw_chat_canvas()

                if response_parts:
                    full_response = "".join(response_parts)
                    add_message("Assistant", full_response)
                else:
                    add_message(
                        "Assistant",
                        "Unable to generate a response"
                    )

                send_button.configure(state = "normal")

        except queue.Empty:
            window.after(
                100,
                check_response
            )

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

            send_button.configure(state = "disabled")

            thinking_visible = True
            redraw_chat_canvas(scroll_to_bottom = True)

            # Run the AI request in a background thread
            def get_response():
                try:
                    for token in assistant.ask_ai_stream(message):
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

    # Send button
    send_button = ctk.CTkButton(
        input_frame,
        text = "",
        image = send_icon,
        width = 36,
        height = 36,
        corner_radius = 18,
        fg_color = "#514568",
        hover_color = "#665078",
        command = send_message
    )

    send_button.pack(
        side = "right",
        padx = 8,
        pady = 0
    )

    # Create invisible window resize areas
    resize_handles = [
        # Left and right edges
        ("w", {
            "x": 0,
            "y": 8,
            "width": 8,
            "relheight": 1,
            "height": -16
        }),

        ("e", {
            "relx": 1,
            "x": -8,
            "y": 8,
            "width": 8,
            "relheight": 1,
            "height": -16
        }),

        # Top and bottom edges
        ("n", {
            "x": 8,
            "y": 0,
            "relwidth": 1,
            "width": -16,
            "height": 8
        }),

        ("s", {
            "x": 8,
            "rely": 1,
            "y": -8,
            "relwidth": 1,
            "width": -16,
            "height": 8
        }),

        # Corners
        ("nw", {
            "x": 0,
            "y": 0,
            "width": 8,
            "height": 8
        }),

        ("ne", {
            "relx": 1,
            "x": -8,
            "y": 0,
            "width": 8,
            "height": 8
        }),

        ("sw", {
            "x": 0,
            "rely": 1,
            "y": -8,
            "width": 8,
            "height": 8
        }),

        ("se", {
            "relx": 1,
            "x": -8,
            "rely": 1,
            "y": -8,
            "width": 8,
            "height": 8
        })
    ]

    # Enable resizing from edges and corners
    def enable_resize(widget, direction):
        widget.resize_direction = direction

        widget.bind(
            "<Button-1>",
            start_resize
        )

        widget.bind(
            "<B1-Motion>",
            resize_window
        )

        widget.bind(
            "<ButtonRelease-1>",
            finish_resize
        )

    def finish_resize(event):
        window.is_resizing = False

        window.after(
            100,
            redraw_chat_canvas
        )

    for direction, position in resize_handles:
        resize_area = tk.Frame(
            window,
            bg = "#111318",
            cursor = (
                "size_nw_se" if direction in ("nw", "se") else
                "size_ne_sw" if direction in ("ne", "sw") else
                "size_we" if direction in ("w", "e") else
                "size_ns"
            )
        )

        resize_area.place(**position)

        enable_resize(
            resize_area,
            direction
        )

    # Keep application running
    window.mainloop()


if __name__ == "__main__":
    main()
