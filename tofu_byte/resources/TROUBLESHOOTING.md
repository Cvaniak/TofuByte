# Input problem

The game uses [`pynput`](https://pynput.readthedocs.io/en/latest/) for handling keyboard input. As it is not a terminal-native input system, it might not work as expected in all terminal environments or operating systems.

I plan to implement scroll mode in the game that will not require any additional input system.

## Troubleshooting

### Input issues (Pynput)

If keyboard input is not working, the game should inform you with an in-game message. This is likely due to `pynput` compatibility issues with your terminal or operating system. It might also be affected by whether you are running X11 or Wayland.

Currently, you can try the following:

- Run the game with `sudo tofubyte`
- Run the terminal emulator with `sudo`
- Run the game with `PYNPUT_BACKEND_KEYBOARD=uinput tofubyte` (This forces `pynput` to use the `uinput` backend, which might be more compatible on some Linux systems.)
- Try running the game in a different terminal emulator:
  - Guake (should work without `sudo`)
  - Wezterm (should work without `sudo`)
  - Kitty (requires `sudo`)
  - Ghostty (requires `sudo`)
  - Terminator (requires `sudo`)
- On macOS, you can try running with `sudo` or refer to [this StackOverflow comment](https://stackoverflow.com/a/54659886) for alternative solutions.

Further reading and potential solutions can be found in the [Pynput Documentation](https://pynput.readthedocs.io/en/latest/limitations.html#mac-osx).

If you are concerned about how `Pynput` is used, feel free to review the available source code.

Also if you found solution for your problem, share this in the issue so it can help others.
