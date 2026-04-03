--- roj-wezterm-setup - Modern Ubuntu Terminal style

local wezterm = require("wezterm")
require("events")  -- custom event handlers

local config = {}

if wezterm.config_builder then
    config = wezterm.config_builder()
end

-- ======================
-- Font & Appearance
-- ======================
config.font = wezterm.font_with_fallback({
    "Ubuntu Mono",        -- main font
    "Fira Code",          -- fallback for ligatures/emoji
})
config.font_size = 15
config.line_height = 1.15
config.bold_brightens_ansi_colors = true
config.freetype_load_flags = "NO_HINTING"  -- smoother fonts
config.window_background_opacity = 0.95
config.window_padding = {
    left = 6,
    right = 6,
    top = 4,
    bottom = 4,
}

-- ======================
-- Cursor
-- ======================
config.default_cursor_style = "BlinkingBlock"
config.cursor_blink_rate = 600
config.cursor_blink_ease_in = "Linear"
config.cursor_blink_ease_out = "Linear"
config.cursor_thickness = 2

-- ======================
-- Scrollback
-- ======================
config.scrollback_lines = 10000
config.enable_scroll_bar = true

-- ======================
-- Window
-- ======================
config.use_fancy_tab_bar = true
config.hide_tab_bar_if_only_one_tab = true
config.automatically_reload_config = true
config.window_close_confirmation = "NeverPrompt"
config.adjust_window_size_when_changing_font_size = false
config.window_decorations = "RESIZE"
config.tab_bar_at_bottom = false
config.check_for_updates = false

-- ======================
-- Color Scheme
-- ======================
config.color_scheme = "Yaru Dark"  -- modern Ubuntu dark theme
config.colors = {
    foreground = "#EEEEEE",
    background = "#2C001E",
    cursor_bg = "#FFFFFF",
    cursor_fg = "#000000",
    cursor_border = "#FFFFFF",
    selection_bg = "#6666FF",
    selection_fg = "#FFFFFF",
    split = "#444444",
    ansi = {"#000000","#CC0000","#4E9A06","#C4A000","#3465A4","#75507B","#06989A","#D3D7CF"},
    brights = {"#555753","#EF2929","#8AE234","#FCE94F","#729FCF","#AD7FA8","#34E2E2","#EEEEEC"},
}

-- ======================
-- Background
-- ======================
config.background = {
    {
        source = { Color = "#1B1B1B" },  -- subtle dark
        width = "100%",
        height = "100%",
    },
}

-- ======================
-- Keys
-- ======================
config.keys = {
    { key = "Enter", mods = "CMD|SHIFT", action = wezterm.action.ToggleFullScreen },
    { key = "t", mods = "CMD|SHIFT", action = wezterm.action { SpawnTab = "CurrentPaneDomain" } },
    { key = "w", mods = "CMD|SHIFT", action = wezterm.action { CloseCurrentTab = { confirm = true } } },
    { key = "LeftArrow", mods = "CMD|OPT", action = wezterm.action { ActivateTabRelative = -1 } },
    { key = "RightArrow", mods = "CMD|OPT", action = wezterm.action { ActivateTabRelative = 1 } },
    { key = "1", mods = "CMD", action = wezterm.action { ActivateTab = 0 } },
    { key = "2", mods = "CMD", action = wezterm.action { ActivateTab = 1 } },
    { key = "3", mods = "CMD", action = wezterm.action { ActivateTab = 2 } },
}

-- ======================
-- Hyperlink rules
-- ======================
config.hyperlink_rules = {
    { regex = "\\b(https?://\\S+)\\b", format = "$1", highlight = 6 },
    { regex = "\\bERROR\\b", format = "$0", highlight = 1 },
    { regex = "\\bWARN\\b", format = "$0", highlight = 3 },
}

-- ======================
-- Misc
-- ======================
config.enable_tab_bar = true
config.tab_max_width = 24
config.window_close_confirmation = "NeverPrompt"

return config