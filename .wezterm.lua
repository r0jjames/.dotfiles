local wezterm = require "wezterm"
local mux = wezterm.mux
local act = wezterm.action
wezterm.on('gui-startup', function()
	local tab, pane, window = mux.spawn_window({})
	window:gui_window():maximize()
end)
function scheme_for_appearance(appearance)
	if appearance:find "Dark" then
		return "tokyonight-night"
	else
		return "Catppuccin Latte"
	end
end

return {
	-- ...your existing config
	color_scheme = scheme_for_appearance(wezterm.gui.get_appearance()),
	-- font = wezterm.font('JetBrains Mono', { weight = 'Bold', italic = true }),
	font_size = 14,
	line_height = 1.2,
	use_fancy_tab_bar = false,
	enable_scroll_bar = false,
	window_padding = {
		left = 0,
		right = 0,
		top = 0,
		bottom = 0,
	},
	tab_bar_at_bottom = true,
	freetype_load_target = "HorizontalLcd",
}
