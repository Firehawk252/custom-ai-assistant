# ----------------------------------------------------------------------
# PATCH NOTES - Settings Sidebar Layout Fix
# ----------------------------------------------------------------------
#
# Settings sidebar:
#   - Fixed a CustomTkinter placement error when opening the settings sidebar.
#   - Moved the sidebar width and height configuration from .place() to
#     .configure(), since CTkScrollableFrame does not accept width and
#     height through .place().
#   - Kept the sidebar positioned inside the glass panel with consistent
#     spacing around its edges.
#   - Ensured the settings sidebar is raised above the main canvas.
#
# Scrolling:
#   - Set the sidebar's internal canvas scroll increment to 30 for
#     larger scrolling steps.
#
# ----------------------------------------------------------------------