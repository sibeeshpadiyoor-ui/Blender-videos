# Blender videos

Scripted Blender animations rendered straight to MP4s that Instagram and
YouTube accept. One animation script renders to every format - the camera
re-frames itself for vertical or horizontal video.

## Setup

You need Python 3.13, [ffmpeg](https://ffmpeg.org/download.html), and Blender's
Python module:

```bash
pip install -r requirements.txt
```

Or skip the pip install and use a normal Blender (5.1+) install:

```bash
blender -b -P render.py -- wave_ring --format reels
```

## Render a video

```bash
python render.py wave_ring --format reels --quality preview
```

```bash
python render.py title_card --format youtube --text "SUBSCRIBE"
```

Videos land in `output/`.

| `--format` | Size      | Use for                                   |
|------------|-----------|-------------------------------------------|
| `reels`    | 1080x1920 | Instagram Reels / Stories, YouTube Shorts |
| `youtube`  | 1920x1080 | Regular YouTube videos                    |
| `feed`     | 1080x1350 | Instagram feed posts                      |
| `square`   | 1080x1080 | Square posts                              |

| `--quality` | Resolution | Use for                                  |
|-------------|------------|------------------------------------------|
| `draft`     | 25%        | Checking motion and timing, fast         |
| `preview`   | 50%        | Checking the look (default)              |
| `final`     | 100%       | Uploading - slow on a CPU, see below     |

Other options:

- `--still 40` renders only frame 40 as a PNG, the quickest way to check a look.
- `--loops 3` repeats the animation in the video (a 4 s loop becomes 12 s).
- `--audio music.mp3` adds a soundtrack, trimmed to the video length.
- `--text "LINE ONE\nLINE TWO"` sets the text for text animations.
- `--save-blend` also saves a `.blend` you can open and tweak in Blender.

## Animations

- `wave_ring` - a ring of balls bouncing in a wave. Loops seamlessly.
- `title_card` - 3D text popping in letter by letter, for intros and outros.

## Make your own

Copy a file in `animations/` and give it a new name; it becomes available to
`render.py` under that name. An animation needs two things:

```python
SECONDS = 4.0

def build(scene, fmt):   # add `text=None` to accept --text
    ...
```

`bvid/scene.py` has the helpers the examples use: `material`, `add_floor`,
`add_wall`, `add_area_light`, `key` (set and keyframe a property) and
`add_camera`, which places the camera so a given area stays in frame at any
aspect ratio.

## Render time

Rendering uses Cycles on the CPU, so it works on any machine, including ones
without a graphics card. Expect roughly 10 seconds per frame at `preview` and
a minute or more per frame at `final` on a 4-core machine; a 4-second video is
120 frames. To use a GPU, open the `--save-blend` file in Blender and render
from there, or set `scene.cycles.device = "GPU"` in `bvid/scene.py` after
enabling your GPU in Blender's preferences.
