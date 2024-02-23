--- __      __      _
--- \ \    / /__ __| |_ ___ _ _ _ __
---  \ \/\/ / -_)_ /  _/ -_) '_| '  \
---   \_/\_/\___/__|\__\___|_| |_|_|_|
---
--- Roj's Wezterm config file
--
local wezterm = require("wezterm")
local act = wezterm.action
local mux = wezterm.mux
wezterm.on('gui-startup', function()
	local tab, pane, window = mux.spawn_window({})
	window:gui_window():maximize()
end)

local zsh_path = "zsh"
local config = {}
-- Use config builder object if possible
if wezterm.config_builder then config = wezterm.config_builder() end

-- Settings
config.default_prog = { zsh_path, "-l" }

-- config.color_scheme = "Tokyo Night"
config.color_scheme = "Catppuccin Mocha"
-- config.font = wezterm.font('JetBrains Mono')
config.font = wezterm.font_with_fallback({
	-- { family = "iosevka nerd font",       scale = 1.24, weight = "medium", },
	-- { family = "caskaydiacove nerd font", scale = 1.2 },
	{ family = "JetBrains Mono", scale = 1.1 },
})
config.window_background_opacity = 0.9
config.window_decorations = "RESIZE"
config.window_close_confirmation = "AlwaysPrompt"
config.scrollback_lines = 3000
config.default_workspace = "main"
config.font_size = 15
-- config.line_height = 1.2
config.use_fancy_tab_bar = false
config.enable_scroll_bar = false
config.window_padding = {
	left = 0,
	right = 0,
	top = 0,
	bottom = 0,
}
config.freetype_load_target = "HorizontalLcd"
-- Dim inactive panes
config.inactive_pane_hsb = {
	saturation = 2.24,
	brightness = 0.5
}

-- Keys
config.leader = { key = "a", mods = "CMD", timeout_milliseconds = 1000 }
config.keys = {
	{
		key = 'f',
		mods = 'CTRL',
		action = wezterm.action.ToggleFullScreen,
	},
	-- Send C-a when pressing C-a twice
	{ key = "a",          mods = "LEADER|CMD", action = act.SendKey { key = "a", mods = "CMD" } },
	{ key = "c",          mods = "LEADER",     action = act.ActivateCopyMode },
	{ key = "phys:Space", mods = "LEADER",     action = act.ActivateCommandPalette },

	-- Pane keybindings
	{ key = "s",          mods = "LEADER",     action = act.SplitVertical { domain = "CurrentPaneDomain" } },
	{ key = "v",          mods = "LEADER",     action = act.SplitHorizontal { domain = "CurrentPaneDomain" } },
	{ key = "h",          mods = "LEADER",     action = act.ActivatePaneDirection("Left") },
	{ key = "j",          mods = "LEADER",     action = act.ActivatePaneDirection("Down") },
	{ key = "k",          mods = "LEADER",     action = act.ActivatePaneDirection("Up") },
	{ key = "l",          mods = "LEADER",     action = act.ActivatePaneDirection("Right") },
	{ key = "q",          mods = "LEADER",     action = act.CloseCurrentPane { confirm = true } },
	{ key = "z",          mods = "LEADER",     action = act.TogglePaneZoomState },
	{ key = "o",          mods = "LEADER",     action = act.RotatePanes "Clockwise" },
	-- We can make separate keybindings for resizing panes
	-- But Wezterm offers custom "mode" in the name of "KeyTable"
	{ key = "r",          mods = "LEADER",     action = act.ActivateKeyTable { name = "resize_pane", one_shot = false } },

	-- Tab keybindings
	{ key = "t",          mods = "LEADER",     action = act.SpawnTab("CurrentPaneDomain") },
	{ key = "[",          mods = "LEADER",     action = act.ActivateTabRelative(-1) },
	{ key = "]",          mods = "LEADER",     action = act.ActivateTabRelative(1) },
	{ key = "n",          mods = "LEADER",     action = act.ShowTabNavigator },
	{
		key = "e",
		mods = "LEADER",
		action = act.PromptInputLine {
			description = wezterm.format {
				{ Attribute = { Intensity = "Bold" } },
				{ Foreground = { AnsiColor = "Fuchsia" } },
				{ Text = "Renaming Tab Title...:" },
			},
			action = wezterm.action_callback(function(window, pane, line)
				if line then
					window:active_tab():set_title(line)
				end
			end)
		}
	},
	-- Key table for moving tabs around
	{ key = "m", mods = "LEADER",       action = act.ActivateKeyTable { name = "move_tab", one_shot = false } },
	-- Or shortcuts to move tab w/o move_tab table. SHIFT is for when caps lock is on
	{ key = "{", mods = "LEADER|SHIFT", action = act.MoveTabRelative(-1) },
	{ key = "}", mods = "LEADER|SHIFT", action = act.MoveTabRelative(1) },

	-- Lastly, workspace
	{ key = "w", mods = "LEADER",       action = act.ShowLauncherArgs { flags = "FUZZY|WORKSPACES" } },

}
-- I can use the tab navigator (LDR t), but I also want to quickly navigate tabs with index
for i = 1, 9 do
	table.insert(config.keys, {
		key = tostring(i),
		mods = "LEADER",
		action = act.ActivateTab(i - 1)
	})
end

config.key_tables = {
	resize_pane = {
		{ key = "h",      action = act.AdjustPaneSize { "Left", 1 } },
		{ key = "j",      action = act.AdjustPaneSize { "Down", 1 } },
		{ key = "k",      action = act.AdjustPaneSize { "Up", 1 } },
		{ key = "l",      action = act.AdjustPaneSize { "Right", 1 } },
		{ key = "Escape", action = "PopKeyTable" },
		{ key = "Enter",  action = "PopKeyTable" },
	},
	move_tab = {
		{ key = "h",      action = act.MoveTabRelative(-1) },
		{ key = "j",      action = act.MoveTabRelative(-1) },
		{ key = "k",      action = act.MoveTabRelative(1) },
		{ key = "l",      action = act.MoveTabRelative(1) },
		{ key = "Escape", action = "PopKeyTable" },
		{ key = "Enter",  action = "PopKeyTable" },
	}
}

-- Tab bar
config.status_update_interval = 1000
config.tab_bar_at_bottom = true
wezterm.on("update-status", function(window, pane)
	-- Workspace name
	local stat = window:active_workspace()
	local stat_color = "#f7768e"
	-- It's a little silly to have workspace name all the time
	-- Utilize this to display LDR or current key table name
	if window:active_key_table() then
		stat = window:active_key_table()
		stat_color = "#7dcfff"
	end
	if window:leader_is_active() then
		stat = "LDR"
		stat_color = "#bb9af7"
	end

	-- Current working directory
	local basename = function(s)
		-- Nothing a little regex can't fix
		return string.gsub(s, "(.*[/\\])(.*)", "%2")
	end
	-- CWD and CMD could be nil (e.g. viewing log using Ctrl-Alt-l). Not a big deal, but check in case
	local cwd = pane:get_current_working_dir()
	cwd = cwd and basename(cwd) or ""
	-- Current command
	local cmd = pane:get_foreground_process_name()
	cmd = cmd and basename(cmd) or ""

	-- Time
	local time = wezterm.strftime("%H:%M")

	-- Left status (left of the tab line)
	window:set_left_status(wezterm.format({
		{ Foreground = { Color = stat_color } },
		{ Text = "  " },
		{ Text = wezterm.nerdfonts.oct_table .. "  " .. stat },
		{ Text = " |" },
	}))

	-- Right status
	window:set_right_status(wezterm.format({
		-- Wezterm has a built-in nerd fonts
		-- https://wezfurlong.org/wezterm/config/lua/wezterm/nerdfonts.html
		{ Text = wezterm.nerdfonts.md_folder .. "  " .. cwd },
		{ Text = " | " },
		{ Foreground = { Color = "#e0af68" } },
		{ Text = wezterm.nerdfonts.fa_code .. "  " .. cmd },
		"ResetAttributes",
		{ Text = " | " },
		{ Text = wezterm.nerdfonts.md_clock .. "  " .. time },
		{ Text = "  " },
	}))
end)

--[[ Appearance setting for when I need to take pretty screenshots
config.enable_tab_bar = false
config.window_padding = {
  left = '0.5cell',
  right = '0.5cell',
  top = '0.5cell',
  bottom = '0cell',

}
--]]

return config
