
# standard is 10 cells wide and 20 cells high, plus two hidden rows
num_rows = 20
num_cols = 10

block_width = 30  # in pixels
hidden_row_fraction = 0.3  # fraction of first hidden row to show

# speed settings
auto_repeat_initial_delay = 10  # frames to wait after an initial left/right move before triggering autorepeat
auto_repeat_delay = 4  # frames to wait before each left/right step on autorepeat (3 frames == 20 Hz at 60fps)
soft_drop_delay = 3  # frames to wait before each down step on soft drop (3 frames == 1/3 G at 60fps)
lock_delay = 30  # frames to wait before locking a piece after downward collision
