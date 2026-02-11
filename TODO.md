# TODO

- [ ] More maps
- [ ] Legacy character support
- [ ] Keybindings in editor
- [ ] Settings
  - [ ] Theme

# LOW PRIORITY

- [ ] ChromeDino/Scrollable type level
- [ ] Maps types in tabs (official, community)
- [ ] Allow resizing from the top-left corner
- [ ] Refactor colors of the objects
- [ ] Map registry
- [ ] Map browsing
- [ ] Map preview or data in map menu screen
- [ ] Effects stack for each object
- [ ] High Score / Save scores
  - [ ] Save points and time
- [x] Check fonts
  - [x] Basic font rendering
  - [ ] Tweaks
- [ ] Switch off visuals with flag
- [ ] Show the name of the map (in game and editor)
- [ ] Select elements in editor by dragin across screen
- [ ]

# NICE TO HAVE

- [ ] Background behind map

- UI for score
- Choose player color
- Add dynamic lights
- Background effects?
- Sounds?
- Pet the Tofu (by mouse clicking)

# Bugs

- [ ] When an object is selected, mouse movement outside the Display also moves it.
- [ ] You can input an incorrect size, which won't have an effect, but it's still possible to enter it.
- [ ] Spikes currently only work for even input sizes (but it's possible to change to odd sizes).
- [ ] We do not check collisions when the player is inside an object.
- [ ] Player might get stuck in corners (likely) or jump by first falling one block from the floor.
- [ ] Player can jump into the floor when jumping from a corner.
- [/] Starting near a corner might allow collecting more than one star (this could potentially be a feature).
  ```
    P
  **
  O*
  ```
  This is caused by the fact that we check vertical and horizontal collisions,
  and taking stars is done on the prediction where the user will be.

# To refactor

- Player and BaseObject should share common code for editable and playable aspects.
- Display can draw lines from non-Message Pump objects (which might offer a performance boost).-

# Items

- [x] Ending point
- [x] Floors
- [x] Spikes
- [x] Spikes Down
- [x] Lights

- Doors
- Bridges
- Turrets (lasers)
- Teleports
- Flames
- Vertical spikes
- Switch, action
- Sticky surface
- When touched - change floor color

## DONE

- [x] Main Menu
  - [x] Choose level
  - [x] Start game
- [x] Pause Menu
  - [x] Resume
  - [x] Discard Game
- [x] Support keys in menu
- [x] Fix Css
- [x] Lives
  - [x] Remove life
  - [x] Die screen
- [x] End game screen
  - [x] Restart
  - [x] Points and time
  - [x] Return
- [x] Heart display
  - [x] Clarify if max represents current value or total count.
- [x] Map config
- [x] Wait before lose screen
- [x] Add layers for stuff
- [x] Make generic controller Windows/Linux/Mac
- [x] Create map button
- [x] Create maps
- [x] Can go into the spike from the upper corner down
- [x] Verify size before resizing
- [x] Switch on/off killing boundary (or move to a bottom layer)
- [x] Ensure new maps appear in the user directory
- [x] Ensure paths/strings work properly
- [x] Validate map does not already exist
- [x] Allow downloading maps from the editor to the current directory
- [x] Refactor css
- [x] Refactor colors (from CSS to in-code definitions)
- [x] Text floating
- [x] Maps versioning
- [x] Ultra optimization
- [x] Chaining maps
- [x] Save chosen theme
- [x] About Author
  - [x] Fill in data
- [x] When reset, reset game
- [x] License
- [x] Input manager check before initial start
- [x] Select multiple objects in edit mode
- [x] Test packaging
- [x] Allow near-misses with spikes
- [x] README
- [x] troubleshooting in README
- [x] Choose themes / Default theme
