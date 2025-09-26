local wezterm = require("wezterm")
local mux = wezterm.mux

wezterm.on("gui-startup", function(cmd)
  -- spawn a window (tab, pane, window)
  local tab, pane, window = mux.spawn_window(cmd or {})

  -- desired terminal grid size (cols x rows) — adjust as needed
  local DESIRED_COLS = 250
  local DESIRED_ROWS = 100

  -- try to compute actual character cell size from the spawned pane
  local cell_w, cell_h
  if pane then
    local pd = pane:get_dimensions()
    if pd and pd.viewport_cols and pd.viewport_rows and pd.pixel_width and pd.pixel_height then
      cell_w = pd.pixel_width / pd.viewport_cols
      cell_h = pd.pixel_height / pd.viewport_rows
    end
  end

  -- sensible fallbacks if we couldn't measure
  cell_w = cell_w or 8  -- tweak if text looks too wide/too narrow
  cell_h = cell_h or 18 -- tweak if text looks too tall/too short

  local width_px = math.floor(DESIRED_COLS * cell_w)
  local height_px = math.floor(DESIRED_ROWS * cell_h)

  local gui_win = window:gui_window()

  -- set inner pixel size
  gui_win:set_inner_size(width_px, height_px)

  -- try to center on the main screen
  local screens = wezterm.gui.screens()
  -- screens() may return array-like; try index 1 first, then .main
  local screen = (screens and screens[1]) or screens and screens.main

  if screen and screen.width and screen.height then
    local x = math.floor((screen.width - width_px) / 2)
    local y = math.floor((screen.height - height_px) / 2)
    gui_win:set_position(x, y)
  else
    -- fallback: maximize if we can't get screen geometry
    gui_win:maximize()
  end
end)

-- wezterm.on("window-resized", function(window, pane)
-- 	readjust_font_size(window, pane)
-- end)

-- Readjust font size on window resize to get rid of the padding at the bottom
function readjust_font_size(window, pane)
  local window_dims = window:get_dimensions()
  local pane_dims = pane:get_dimensions()

  local config_overrides = {}
  local initial_font_size = 13 -- Set to your desired font size
  config_overrides.font_size = initial_font_size

  local max_iterations = 5
  local iteration_count = 0
  local tolerance = 3

  -- Calculate the initial difference between window and pane heights
  local current_diff = window_dims.pixel_height - pane_dims.pixel_height
  local min_diff = math.abs(current_diff)
  local best_font_size = initial_font_size

  -- Loop to adjust font size until the difference is within tolerance or max iterations reached
  while current_diff > tolerance and iteration_count < max_iterations do
    -- wezterm.log_info(window_dims, pane_dims, config_overrides.font_size)
    wezterm.log_info(
      string.format(
        "Win Height: %d, Pane Height: %d, Height Diff: %d, Curr Font Size: %.2f, Cells: %d, Cell Height: %.2f",
        window_dims.pixel_height,
        pane_dims.pixel_height,
        window_dims.pixel_height - pane_dims.pixel_height,
        config_overrides.font_size,
        pane_dims.viewport_rows,
        pane_dims.pixel_height / pane_dims.viewport_rows
      )
    )

    -- Increment the font size slightly
    config_overrides.font_size = config_overrides.font_size + 0.5
    window:set_config_overrides(config_overrides)

    -- Update dimensions after changing font size
    window_dims = window:get_dimensions()
    pane_dims = pane:get_dimensions()
    current_diff = window_dims.pixel_height - pane_dims.pixel_height

    -- Check if the current difference is the smallest seen so far
    local abs_diff = math.abs(current_diff)
    if abs_diff < min_diff then
      min_diff = abs_diff
      best_font_size = config_overrides.font_size
    end

    iteration_count = iteration_count + 1
  end

  -- If no acceptable difference was found, set the font size to the best one encountered
  if current_diff > tolerance then
    config_overrides.font_size = best_font_size
    window:set_config_overrides(config_overrides)
  end
end
