# Intro 3D ASCII Words Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render `WELCOME / TO / MY / AI / WORLD` with the exact 3D ASCII material used by the final `KJ-AIML` wordmark while preserving the existing boot choreography.

**Architecture:** Refactor the current global-text renderer into a parameterized grid renderer, then emit precomputed intro grids through the existing SVG text-run machinery. The final mark stays on the current 91-column frame path; intro words use the approved 91/55-column mapping and are centered in the same art viewport.

**Tech Stack:** Python 3.14, NumPy 2.5.0, Pillow 12.3.0, SVG/SMIL, pytest.

## Global Constraints

- `WELCOME` and `WORLD` use 91 columns.
- `TO`, `MY`, and `AI` use centered 55-column grids without stretching cells.
- Intro words use uppercase labels and the exact final-mark font, extrusion, camera, 4-degree tilt, lighting, fog, density ramp, and shade buckets.
- Preserve boot order, `WORD_HOLD`, `WORD_BURST`, particle paths, loading bar, final `KJ-AIML` geometry, and rock loop.
- Add no fonts, raster images, JavaScript, CSS animation, or remote assets.
- Do not include the separate dirty `README.md` collaboration-line change in implementation commits.

---

### Task 1: Parameterize the 3D ASCII grid renderer

**Files:**
- Modify: `scripts/generate_wordmark.py`
- Test: `tests/test_wordmark_freshness.py`

**Interfaces:**
- Produces: `INTRO_WORD_COLS: dict[str, int]` with the approved width mapping.
- Produces: `render_text_grid(text: str, cols: int, yaw: float) -> np.ndarray`, a deterministic shaded grid using the existing material constants.
- Preserves: the existing final-frame list and `target_cells()` contract used by particles and final SVG emission.

- [ ] **Step 1: Add failing tests for the approved mapping and grid widths**

Add these focused assertions to `tests/test_wordmark_freshness.py`:

```python
def test_intro_word_widths_match_the_approved_system() -> None:
    wordmark = importlib.import_module("generate_wordmark")
    assert wordmark.INTRO_WORD_COLS == {
        "WELCOME": 91,
        "TO": 55,
        "MY": 55,
        "AI": 55,
        "WORLD": 91,
    }


@pytest.mark.parametrize("word, cols", [
    ("WELCOME", 91),
    ("TO", 55),
    ("MY", 55),
    ("AI", 55),
    ("WORLD", 91),
])
def test_intro_word_grid_uses_approved_width(word: str, cols: int) -> None:
    wordmark = importlib.import_module("generate_wordmark")
    grid = wordmark.render_text_grid(word, cols, wordmark.REST_YAW)
    assert grid.shape[1] == cols
    assert grid.any()
```

- [ ] **Step 2: Run the focused tests and confirm the expected failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_wordmark_freshness.py \
  -k 'intro_word_widths or intro_word_grid' -q
```

Expected: failure because `INTRO_WORD_COLS`, `REST_YAW`, and `render_text_grid` do not yet exist.

- [ ] **Step 3: Extract a parameterized render path**

In `scripts/generate_wordmark.py`:

1. Add the approved constant:

```python
INTRO_WORD_COLS = {
    "WELCOME": 91,
    "TO": 55,
    "MY": 55,
    "AI": 55,
    "WORLD": 91,
}
REST_YAW = math.radians(-13)
```

2. Change `build_shell()` to accept `text: str` and replace reads of global
   `TEXT` inside that function with the argument.
3. Change `fit()` and `rasterize()` to accept `cols: int` and return/consume a
   local row count rather than mutating global `ROWS`.
4. Add `render_text_grid(text, cols, yaw)` that calls `build_shell(text)`,
   `project(...)`, the parameterized fit, and the parameterized rasterizer.
5. Keep the existing animated final-frame generation byte-equivalent by passing
   `TEXT`, `COLS`, and the existing yaw values through the new functions.

- [ ] **Step 4: Run the focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_wordmark_freshness.py \
  -k 'intro_word_widths or intro_word_grid' -q
```

Expected: 6 passed.

- [ ] **Step 5: Prove the refactor does not change the current asset yet**

Run:

```bash
tmp_svg="$(mktemp -t kj-wordmark-refactor).svg"
WORDMARK_FONT='/System/Library/Fonts/Supplemental/Arial Bold.ttf' \
  .venv/bin/python scripts/generate_wordmark.py --out "$tmp_svg"
cmp assets/kj-wordmark.svg "$tmp_svg"
```

Expected: `cmp` exits 0. This isolates the renderer refactor from the visual
change and protects the final mark.

- [ ] **Step 6: Commit the renderer seam**

```bash
git add scripts/generate_wordmark.py tests/test_wordmark_freshness.py
git commit -m "refactor: parameterize 3d ascii word rendering"
```

---

### Task 2: Emit intro words as centered 3D ASCII cells

**Files:**
- Modify: `scripts/generate_wordmark.py`
- Modify: `tests/test_wordmark_freshness.py`
- Modify: `assets/kj-wordmark.svg`
- Modify: `docs/3d-ascii-wordmark.md`

**Interfaces:**
- Consumes: `INTRO_WORD_COLS` and `render_text_grid(text, cols, yaw)` from Task 1.
- Produces: `intro_word_grids() -> dict[str, np.ndarray]` and SVG groups marked with `data-intro-word="WORD"` for focused validation.
- Preserves: `word_cells()` and the existing particle station sequence; those particles still converge, hide during the readable form, and burst outward.

- [ ] **Step 1: Add failing SVG-emission tests**

Add to `tests/test_wordmark_freshness.py`:

```python
def test_intro_words_are_ascii_groups_not_solid_text(tmp_path: Path) -> None:
    fresh = tmp_path / "kj-wordmark.svg"
    subprocess.run(
        [sys.executable, "scripts/generate_wordmark.py", "--out", str(fresh)],
        check=True,
        capture_output=True,
    )
    svg = fresh.read_text(encoding="utf-8")
    for word in ("WELCOME", "TO", "MY", "AI", "WORLD"):
        assert f'data-intro-word="{word}"' in svg
    assert ">Welcome<" not in svg
    assert ">World<" not in svg


def test_short_intro_words_are_centered() -> None:
    wordmark = importlib.import_module("generate_wordmark")
    for word in ("TO", "MY", "AI"):
        grid = wordmark.intro_word_grids()[word]
        occupied = grid.nonzero()[1]
        left = int(occupied.min())
        right = grid.shape[1] - 1 - int(occupied.max())
        assert abs(left - right) <= 2
```

- [ ] **Step 2: Run the new tests and confirm the expected failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_wordmark_freshness.py \
  -k 'intro_words_are_ascii or short_intro_words_are_centered' -q
```

Expected: failure because `intro_word_grids()` and intro SVG groups do not exist.

- [ ] **Step 3: Reuse the existing text-run emitter for arbitrary grids**

Move the nested `frame_group()` logic out of `emit()` into:

```python
def grid_group(
    grid: np.ndarray,
    *,
    art_top: float,
    x_offset: float,
    extra: str = "",
) -> str:
    ...
```

Use the unchanged `CELL_W`, `CELL_H`, `RAMP`, `BUCKETS`, and `SHADES`. The final
frames call it with `x_offset=PAD`. Intro grids call it with:

```python
x_offset = PAD + (COLS - grid.shape[1]) * CELL_W / 2
```

This centers 55-column grids without scaling their cells.

- [ ] **Step 4: Replace solid intro labels with animated ASCII groups**

1. Change `WORDS` to uppercase strings while retaining the tuple shape used by
   particle choreography.
2. Add `intro_word_grids()` that renders each unique word at `REST_YAW` using
   its `INTRO_WORD_COLS` value.
3. In `boot_sequence()`, remove the `<text ...>{word}</text>` emission loop.
4. Emit one `grid_group(...)` per word with
   `data-intro-word="{word}"`, the same `values="0;1;1;0;0"` opacity animation,
   `WORD_CYCLE`, and existing begin offsets.
5. Leave `word_cells()`, debris opacity, particle transforms, bar sequence, and
   final-target logic unchanged.

- [ ] **Step 5: Update the renderer documentation**

In `docs/3d-ascii-wordmark.md`, replace the claim that intro words are “real
text” with the approved system:

- full-width 91-column `WELCOME` and `WORLD`;
- centered 55-column `TO`, `MY`, and `AI`;
- identical material and camera to the final mark;
- particles remain transition debris rather than spelling the words.

- [ ] **Step 6: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_wordmark_freshness.py \
  -k 'intro_word or short_intro' -q
```

Expected: all selected tests pass.

- [ ] **Step 7: Regenerate the committed SVG**

Run:

```bash
WORDMARK_FONT='/System/Library/Fonts/Supplemental/Arial Bold.ttf' \
  .venv/bin/python scripts/generate_wordmark.py
```

Expected: `assets/kj-wordmark.svg` is rewritten deterministically and remains
below the existing 500,000-byte safety limit.

- [ ] **Step 8: Run complete automated verification**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/validate_profile.py
git diff --check
```

Expected: all tests pass, profile validation prints `Profile validation passed.`,
and `git diff --check` exits 0.

- [ ] **Step 9: Perform visual verification at README width**

Open the regenerated `assets/kj-wordmark.svg` at 855 px and watch one complete
boot. Confirm:

- `WORLD` matches the approved preview's depth and readability;
- `WELCOME` remains legible at 91 columns;
- `TO`, `MY`, and `AI` are centered compact objects with unchanged cell size;
- transitions have no blank flash, clipping, or overlap;
- the loading bar and final `KJ-AIML` reveal are unchanged;
- the agent CLI begins only after the wordmark boot completes.

- [ ] **Step 10: Commit the visual change without the dirty README**

```bash
git add scripts/generate_wordmark.py tests/test_wordmark_freshness.py \
  assets/kj-wordmark.svg docs/3d-ascii-wordmark.md
git commit -m "feat: render intro words as 3d ascii"
```

After committing, run `git status --short --branch` and confirm the only
remaining worktree change is the pre-existing `README.md` collaboration line.
