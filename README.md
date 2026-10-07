# Tart greeting animation

A five-second, 1280 x 720, 30 fps animation created in Unreal Engine 5.8 through the local Unreal MCP server at `http://127.0.0.1:8000/mcp`, using `tart-young.png` as the character reference.

The character is a procedural stylized interpretation of the reference: cream coloring, floppy ears, large eyes, an orange training vest, and a blue guide-dog badge. The shot includes a head tilt, blinks, tail wagging, a paw wave, and a gentle camera push.

## Deliverables

- `output/tart-greeting-5s.mp4`: final H.264 MP4.
- `output/tart_preview.png`: first rendered frame.
- `output/animation-contact-sheet.jpg`: representative frames.
- `output/frames/`: original Unreal PNG frames.
- `output/video_verification.json`: duration, frame count, resolution, and motion checks.

## Unreal assets

Project: `C:/Users/admina/Documents/Unreal Projects/dog20261007/dog20261007.uproject`

- Level: `/Game/TartAnimation/Tart_Studio`
- Editable Level Sequence: `/Game/TartAnimation/Tart_Greeting_5s`
- Materials: `/Game/TartAnimation/Materials/`

## Rebuild

Run this command in Unreal's console to register the task-specific MCP toolset:

```text
py "C:/Users/admina/Downloads/project/dog-test/bootstrap_tart_mcp.py"
```

The toolset's `run_step` method supports `probe`, `build`, `preview`, `render`, and `verify`. Rebuilding replaces this task's `Tart_` actors in its dedicated studio level. Rendering uses Unreal's built-in Sequencer image capture. The encoder uses a workspace-local FFmpeg package in `.tools`.

To encode the completed 150-frame render:

```powershell
& 'C:/Users/admina/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' encode_animation.py
```
