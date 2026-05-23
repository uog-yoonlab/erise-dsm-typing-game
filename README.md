# ERISE_DSM Typing Game (Web)

A single-file browser game where students practice typing real Python code and key concept sentences from the ERISE_DSM curriculum.

**Live game:** https://jcslayer-code.github.io/erise-dsm-typing-game/typing_game.html *(populated after the first push)*

**Status:** v0 — written as a starting tool for the Spring 2027 MA581 course. A redesigned-from-scratch v1 by a summer 2026 collaborator is planned in a separate repo for portfolio-credit reasons; this v0 stays here as the immediate-use version.

## How to play

Open `typing_game.html` in any browser. Double-click the file, or:

```bash
xdg-open typing_game.html      # Linux
open typing_game.html          # macOS
```

No install, no server, no internet needed. Works offline.

### A round

1. Pick a mode: **Mixed** (code + prose), **Code only**, or **Prose only**
2. Pick how many snippets (default 8)
3. Optionally enter your name (saved with the round result)
4. Click **Start round**

For each snippet:

- **Code snippets** (single line or multi-line block): type the highlighted line, press <kbd>Enter</kbd>. If correct, the line turns green and the next line becomes active. If wrong, you'll see a colored diff and can retry.
- **Prose snippets** (key sentences from the lesson): type the sentence as shown, press <kbd>Enter</kbd>.

### Controls

- <kbd>Enter</kbd> — submit the current line
- <kbd>Esc</kbd> — skip the current snippet (counts as skipped, doesn't affect WPM)
- <kbd>Ctrl</kbd>+<kbd>Q</kbd> — quit round (no score saved)

### Scoring

- **WPM** — standard 5-char-per-word convention, calculated per line
- **Accuracy** — character-level match between expected and typed
- **Paste detection** — anything typed faster than 0.05s with >10 characters is flagged as pasted; accuracy still counts but WPM is not recorded
- Round results are saved to browser **localStorage** under the key `erise_dsm_typing_results`. Inspect via DevTools console: `JSON.parse(localStorage.getItem("erise_dsm_typing_results"))`

## Content

Pick the lesson from the **Lesson** dropdown at the top of the setup panel. Each lesson has three content types: single-line code idioms, multi-line code blocks (typed one line at a time), and prose sentences pulled from the lesson text.

| Lesson | Code snippets | Prose | Total |
|---|---|---|---|
| Lesson 1: Data Loading & EDA | 24 | 17 | 41 |
| Lesson 2: Feature Engineering | 30 | 18 | 48 |
| Lesson 3: Data Wrangling & QC | 31 | 17 | 48 |
| Lesson 4: Linear Regression | 33 | 22 | 55 |
| Lesson 5: Logistic Regression & Classification | 28 | 17 | 45 |
| Lesson 6: Imbalanced Data | 24 | 15 | 39 |
| Lesson 7: Decision Trees & Random Forest | 29 | 14 | 43 |
| Lesson 8: Model Selection & Pipelines | 23 | 12 | 35 |
| Lesson 9: Clustering & Unsupervised Learning | 32 | 18 | 50 |
| Lesson 10: Geospatial Data Analysis | 27 | 15 | 42 |
| Lesson 11: Intro to Neural Networks | 30 | 19 | 49 |
| Lesson 12: Image Basics with OpenCV | 32 | 17 | 49 |
| Lesson 13: CNN Image Classification | 32 | 16 | 48 |
| Lesson 14: Image Segmentation with UNet | 20 | 17 | 37 |
| Lesson 15: Model Interpretation & Explainability | 20 | 15 | 35 |
| Lesson 16: End-to-End ML Pipeline (Capstone) | 26 | 16 | 42 |

Code snippets prefixed `asg_l*` are pulled from the assignment-complete notebooks (`*_complete.ipynb`) and preserve their teaching comments. The 10 lessons with complete-answer notebooks each gained 2–3 new multi-line snippets covering the core tasks of the assignment.

## Linter (`lint_typing_game.py`)

A small Python checker keeps the snippet bank keyboard-typeable. It scans every `lines: [...]` array for non-ASCII characters (Greek letters, subscripts, em dashes, etc.) that a student cannot enter on a normal keyboard.

```bash
python3 lint_typing_game.py            # report only — exits 1 if issues found
python3 lint_typing_game.py --fix      # apply the standard ASCII replacements
python3 lint_typing_game.py --js-check # also run `node --check` on the embedded JS
```

The standard replacement map (`β → b`, `₀ → 0`, `× → *`, `² → **2`, `— → -`, `… → ...`, etc.) is applied only inside snippet content — topic labels and UI ornaments (the `→`, `↻`, `✓`, `📝` icons, em dashes in topic strings) are left alone since students never type them.

**When to run it:** after pulling new code from any `*_complete.ipynb` notebook, or anytime you paste content from outside sources into a snippet body. Run with `--fix` to auto-clean, then `--js-check` to confirm the JS still parses.

Prose includes single-sentence idiom-statements and multi-sentence **concept blocks** (typed one sentence at a time). Key ideas — "Garbage in, garbage out", the three missing-data mechanisms, the bias-variance tradeoff, precision/recall/F1, etc. — are 3–4 sentence concept blocks so the typing reinforces a full argument, not just a single line.

All content is taken directly from `semester_course/0N_lesson.md` and the corresponding notebook.

## Adding more lessons

The content lives in JavaScript objects near the top of `typing_game.html` (`const LESSON_1`, `const LESSON_2`). To add Lesson 3:

1. Open `typing_game.html` in any text editor
2. After `const LESSON_2 = { ... };`, add `const LESSON_3 = { title: "...", description: "...", snippets: [ ... ] };`
3. Find the line `const LESSONS = { "1": LESSON_1, "2": LESSON_2 };` and extend it: `const LESSONS = { "1": LESSON_1, "2": LESSON_2, "3": LESSON_3 };`
4. Reload the page — the new lesson appears in the Lesson dropdown automatically.

Each snippet has this shape:

```js
{
  id: "unique_id",
  type: "code" | "prose",
  topic: "Short description shown to the student",
  lines: ["one or more strings — each is one line to type"]
}
```

For multi-line code blocks, list each line in `lines` separately — the game shows the whole block but advances line by line. For prose, usually one entry in `lines`.

### Content selection guidelines

**Code snippets:**
- Use real lines from the lesson, exactly as students will type them in Colab
- Mix lengths — short ones build muscle memory, long ones build endurance
- For multi-line blocks, each line should be valid in isolation (no broken parentheses across lines)

**Prose snippets:**
- Pick the principle-stating sentences, not narrative or descriptive prose
- Keep each prose entry under ~120 characters where possible — long sentences become tedious to type
- Pull verbatim from the lesson so the typing reinforces exact phrasing

## Distributing to students

Just send them the HTML file. They can save it anywhere and open it in any modern browser (Chrome, Firefox, Safari, Edge, Brave). Each student's results live in their own browser's localStorage — no central server, no privacy concerns, no setup.

For a classroom session, you can have students compare WPM/accuracy informally; for a more formal exercise, ask them to copy a round result from `localStorage` and paste into a Moodle text-response question.
