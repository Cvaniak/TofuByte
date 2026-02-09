<p>
    <img src="./animation.svg" hspace="10" >
    <img src="./logo.svg" hspace="10" >
</p>

Terminal game with sweet block of [tofu](https://fonts.google.com/knowledge/glossary/tofu) character!

## How to install

### Prerequisites

To properly display all characters:

- Use a modern terminal emulator.
- Install a Unicode-ready font (e.g., NerdFonts).
- Ensure your shell environment is configured to use UTF-8 encoding.

### Using pip/pipx

```bash
pip install tofubyte
# or
pipx install tofubyte
```

and run with

```bash
tofubyte
# or source venv first
source .venv/bin/activate
tofubyte
```

### Using uv/uvx

```bash
uv pip install tofubyte
# or
uvx install tofubyte
```

and run with

```bash
tofubyte
# or source venv first
source .venv/bin/activate
tofubyte
```

## Input system

The game uses `pynput` for handling keyboard input. As it is not a terminal-native input system, it might not work as expected in all terminal environments or operating systems.

I plan to implement an alternative input mode in the game that will not require any additional input system.

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

## Development

```
uv run textual run --dev tofu_byte.command_line:run --debug contact_dir,step,fps,footer
```

## License and Community

This is my little independent game, developed in my personal time.

As I have many plans for further changes and wish to maintain a clear mental model of the project, I am not currently planning to accept code contributions.

However, feedback is very welcome.
If you encounter bugs, issues, or have feature ideas, please open an issue on GitHub.

I also plan to implement features for uploading, browsing, and downloading maps directly from within the game.
