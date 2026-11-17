# The hello hero

`scripts/generate_hello.py` writes the profile's hero in two forms:
[the animation](../assets/kj-hello.svg) and [its final frame](../assets/kj-hello-still.svg).
Both are 855 by 450 and well under the 500 KB asset limit. Generation is offline
and takes a few seconds.

The hand artwork and the pacing come from the owner's
[pi-ter](https://github.com/KJ-AIML/pi-ter) project; the vendored data and its
revision are described in [scripts/data](../scripts/data/README.md).

## How the hands are built

1. **Dither once.** Each hand's alpha and luminance field is sampled on a dot
   lattice and thresholded with a 4 by 4 Bayer matrix. Every lit dot keeps its
   own tone and size, so shading is per dot, not per cell.
2. **Bind to bones.** Every dot is assigned to one bone: forearm, wrist, index
   finger, the index finger's middle joint, or the other fingers. The joint
   positions were read off the source images and are listed in `RIGS`.
3. **Bend in strips.** A joint is a stack of thin strips, each turning an equal
   share of the angle about the same pivot. Dots near a knuckle spread across
   the bend instead of opening a crack. In SVG this is a chain of nested groups,
   each with one rotation.
4. **Carry, don't redraw.** The dots are drawn once and moved by those groups.
   Nothing is re-dithered while the hands move, so the texture does not shimmer.

Past each image's edge the forearm continues as a sheared mirror of itself, so
the arm stays attached to the frame while it moves and its top edge stays straight.

## How they move

`pose(i, t, ...)` returns the arm offset and every joint angle for a hand at a
time. All joints are zero in the drawn pose, which is the pose at the touch.

| Time | What happens |
| --- | --- |
| 0 to 1.5 s | The hands enter. The left wrist hangs limp; the right hand is a loose fist. `Hello World` fades in |
| 1.2 to 2.3 s | The arms swing in on an arc about off-canvas elbows. The wrists lift a beat later, and the index fingers extend late in the reach. The pointing hand leads slightly |
| 2.3 to 2.7 s | The last inch: slower, and the fingertips close the gap that exists in the drawn pose |
| 2.74 s | The touch. A spark bursts between the fingertips and both fingers recoil and settle |
| 3.0 to 4.5 s | The fingers relax first, then the wrists go limp as the arms withdraw. The spark's particles fly into the handle, which lights from the centre outward |
| 4.6 to 5.3 s | `Hello KJ` decodes under the handle |
| 5.0 to 6.1 s | One pale-green glint crosses the handle. The hands dim |
| 6.4 s | Everything holds |

Poses are eased with a minimum-jerk curve, the profile a relaxed limb follows
between two positions. The motion is sampled about 24 times a second and
interpolated by the viewer.

Each strip of the handle lights only after both hands have left it, and the
hands retreat until the handle has clear air around it. Both are computed from
where the dots actually are, not from fixed numbers, so changing the name or
the timing keeps them true.

## The handle

The name goes through the point shell in `scripts/generate_wordmark.py`: the
bundled font is rasterized, extruded, and lit, and the nearest surface point
wins each dot. The projection is repeated in the hero's generator with explicit
double-precision sums. A single-precision matrix product can round differently
between machines, and one dot that moves would change the committed file.

## Without animation

The animated file's base state is its final frame, in the group
`static-fallback`. The animation hides that frame at time zero and plays the
scene, which lives in `animated-scene` and is hidden in the base state. A viewer
that ignores SVG animation shows the handle and caption immediately.

## With reduced motion

Two things serve a visitor who asks for reduced motion, because the first alone
is not reliable.

1. The README's picture element offers the still for `prefers-reduced-motion`.
   GitHub wraps README images in links, and an image that is not a direct child
   of its picture element ignores the picture's sources.
2. The animated file carries the rule itself. Under `prefers-reduced-motion` its
   stylesheet hides the scene, forces the finished frame visible with
   `!important`, which outranks SVG animation, and paints the handle in flat
   colours so the glint cannot cross it.

The second was checked in a Chromium browser started with its reduced-motion
switch, with the file loaded as an image: the finished frame shows from the
first moment. A link under the hero also opens the still directly. The still
has the same composition, with the hands drawn where they come to rest.

## The window frame

There is no clip path. The window frame is protected by a test that follows
every dot through the whole timeline and fails if one reaches the titlebar or
leaves a rounded corner.

## Changing it

- `NAME` and `CAPTION` set the handle and the line under it.
- `RIGS` holds the joints. If a finger tears or bends in the wrong place, move
  its pivot or polygon and look at the result enlarged.
- `pose` holds the timing and the angles. Keep every joint at zero at `TOUCH`.
- `DOT_SIZE` and the two shade lists set the look of the dots.

Then rebuild, run the tests, and watch it play in a browser:

```bash
python scripts/generate_all.py
python -m pytest -q
```

To try a variation without touching the committed files:

```bash
python scripts/generate_hello.py --mode intro --out /tmp/hello.svg
```
