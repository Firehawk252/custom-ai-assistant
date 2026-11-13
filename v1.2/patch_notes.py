# ----------------------------------------------------------------------
# PATCH NOTES - Galaxy / Neon Orchid redesign
# ----------------------------------------------------------------------
# New dependency:
#   - numpy (pip install numpy) generates the gradient quickly
#
# Layout:
#   - The whole window is now one full-window tk.Canvas. The gradient,
#     title bar, input bar, buttons and chat are all drawn on it, so the
#     background shows through everywhere instead of only in the chat area.
#   - The settings sidebar now sits to the left of the chat, between the
#     title bar and input bar, inside a glass panel.
#   - Removed the CTkFrame title bar, CTkFrame input bar, CTkScrollbar and
#     the invisible resize-handle frames. Dragging, edge resizing, the
#     window buttons and the send/settings buttons are handled by mouse
#     events on the canvas (on_press, on_motion, on_drag, on_release).
#
# Background:
#   - Replaced the pixel-loop gradient with a NumPy galaxy gradient:
#     deep base gradient, muted nebula clouds, a faint haze band, three
#     deeper purple patches, soft sparkles and light dithering.
#   - The background is cached and only rebuilt when the window size changes.
#
# Window shape:
#   - Rounded corners (WINDOW_RADIUS = 28) use the Windows -transparentcolor
#     attribute with KEY = "#010101". On other platforms the window stays
#     square. Corners are removed when the window is maximized.
#
# Glass look:
#   - Title bar, input bar, sidebar and chat bubbles are translucent plum
#     panels with thin light borders, rendered with Pillow.
#   - Assistant bubbles have a small squared top-left corner and user bubbles
#     (purple gradient) have a squared bottom-right corner.
#   - Panel and bubble images are cached by size.
#
# Controls:
#   - Settings and send buttons are gradient circles that brighten on hover.
#     The send button dims while a reply is loading (set_sending).
#   - Minimize/maximize/close get hover highlights. Close hovers red.
#   - The text box is a CTkEntry placed on the canvas. Its color is matched
#     to the input bar underneath it each redraw.
#
# Chat:
#   - Messages scroll with the mouse wheel (manual scroll offset) and only
#     bubbles in view are drawn. A slim indicator shows the scroll position.
#   - Covers (crops of the background) hide messages that scroll under the
#     title bar and input bar.
#
# Palette:
#   - Text #EDE9FE, muted text #C4B5FD, sidebar #1E1336
#   - Panels rgba(40,26,64,.6) with border rgba(200,160,235,.3)
#   - User bubble gradient (122,45,140) to (91,60,176)
#
# Known limitations:
#   - The scroll indicator can't be dragged (mouse wheel only).
#   - No glow around bubbles or bars.
#   - Minimizing briefly restores the native title bar (overrideredirect).
#   - The Appearance "Light" option does little because colors are fixed.
# ----------------------------------------------------------------------