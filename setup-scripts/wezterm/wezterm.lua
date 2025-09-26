--- __      __      _
--- \ \    / /__ __| |_ ___ _ _ _ __
---  \ \/\/ / -_)_ /  _/ -_) '_| '  \
---   \_/\_/\___/__|\__\___|_| |_|_|_|
---
--- Roj's IDE-style WezTerm launcher

local wezterm = require("wezterm")
require("events")
local config = {}

if wezterm.config_builder then
    config = wezterm.config_builder()
end

-- ======================
-- Font & Appearance
-- ======================
config.font = wezterm.font("JetBrains Mono", { weight = "Bold" })
config.font_size = 12.5

-- config.line_height = 1.1
config.window_padding = {
    left = 3,
    right = 3,
    top = 0,
    bottom = 0,
}

-- ======================
-- Cursor
-- ======================
config.default_cursor_style = "BlinkingBar"
-- config.cursor_blink_rate = 600


-- ======================
-- Window
-- ======================
-- Window size
-- config.initial_cols = 168
-- config.initial_rows = 55

config.automatically_reload_config = true
config.window_close_confirmation = "NeverPrompt"
config.adjust_window_size_when_changing_font_size = false
config.window_decorations = "RESIZE"
config.check_for_updates = false
config.enable_tab_bar = false
config.tab_bar_at_bottom = false

-- ======================
-- Color scheme
-- ======================
config.color_scheme = "Nord (Gogh)"


-- ======================
-- Background
-- ======================
config.background = {
    {
        source = {
            File = "/Users/roj/Pictures/Wallpapers/Landscape/circus.jpg",
        },
        hsb = {
            hue = 1.0,
            saturation = 1.02,
            brightness = 0.25,
        },
        width = "100%",
        height = "100%",
    },
    {
        source = {
            Color = "#282c35",
        },
        width = "100%",
        height = "100%",
        opacity = 0.55,
    },
}


-- ======================
-- Keys
-- ======================
config.keys = {
    { key = "Enter", mods = "CMD|SHIFT", action = wezterm.action.ToggleFullScreen },
    { key = "Enter", mods = "CTRL",      action = wezterm.action({ SendString = "\x1b[13;5u" }) },
    { key = "Enter", mods = "SHIFT",     action = wezterm.action({ SendString = "\x1b[13;2u" }) },
}

-- ======================
-- Hyperlink rules (optional, colorful)
-- ======================
config.hyperlink_rules = {
    {
        regex = "\\b(https?://\\S+)\\b",
        format = "$1",
        highlight = 6,
    },
    {
        regex = "\\bERROR\\b",
        format = "$0",
        highlight = 1,
    },
    {
        regex = "\\bWARN\\b",
        format = "$0",
        highlight = 3,
    },
}

return config
