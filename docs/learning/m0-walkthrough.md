# M0 walkthrough: set up, run the tests, make your first change

Goal of M0: the repo is on GitHub, the tests pass on your machine and in CI,
and you've added one small, tested feature through a pull request.

## 1. Install the tools (once)

1. **VS Code** with the **Python** and **Ruff** extensions.
2. **GitHub Desktop** (you have it; it includes git).
3. **uv**, which manages Python versions, virtual environments and packages.
   In PowerShell:

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   Close and reopen the terminal, then check: `uv --version`.
   You don't need to install Python separately; uv fetches one if needed.

## 2. Put the repo on GitHub

1. Unzip `kitlist` somewhere permanent (not Downloads).
2. GitHub Desktop: **File > Add local repository**, pick the folder. It will say it
   isn't a git repository yet; click **create a repository**, keep the name, leave
   README/license unticked (we already have them), **Create**.
3. **Publish repository**. Untick *Keep this code private* when you're ready for it
   to be public (you can also start private and flip it later in GitHub settings).
4. On github.com: **Settings > Rules > Rulesets > New branch ruleset** for `main`:
   require a pull request and require the `CI / check` status to pass. From now on,
   nothing reaches `main` without passing tests, including from me.

## 3. Run it

Open the folder in VS Code, then in its terminal (**Ctrl+`**):

```bash
uv sync          # makes .venv, installs pytest + ruff at the versions in uv.lock
uv run pytest    # should end with "11 passed"
uv run ruff check .
```

When VS Code asks which interpreter to use, pick the one in `.venv`.

## 4. Read the code (15 minutes)

Open `src/kitlist/sizing.py` and `tests/test_sizing.py` side by side. Things to notice:

- **Type hints** (`required: float`) say what goes in and out. Python doesn't enforce
  them, but VS Code uses them to catch mistakes as you type.
- **The docstring** explains the function for a reader who never saw this chat.
  The `>>>` example inside it is a *doctest*: pytest runs it, so the docs can't go stale.
- **Validate inputs first, then do the work.** Errors say what was wrong and what value
  caused it. A good error message saves the next person an hour.
- **`REL_TOL`** exists because `0.1 + 0.2 != 0.3` in floating point. There's a test that
  proves the tolerance is needed: delete the tolerance and watch it fail.
- **`@pytest.mark.parametrize`** runs one test over a table of cases. Adding a design case
  is one line.
- **Test names read like design checks**: `test_load_above_largest_size_is_an_error`.
- **`src/` layout**: tests import the *installed* package, not loose files, which catches
  packaging mistakes early.
- **`uv.lock`** pins exact versions, so CI and your laptop run identical tools.

Try it: break something on purpose. In `sizing.py`, change `sorted(sizes)` to `list(sizes)`,
run `uv run pytest`, read which test fails and why, then undo with **Ctrl+Z**.

## 5. The everyday loop

1. GitHub Desktop: **Current branch > New branch**, named for the change,
   e.g. `feat/generator-checks`.
2. Write the test first. Run it. Watch it **fail** (proves the test can catch something).
3. Write the code. Run tests until they **pass**.
4. `uv run ruff format .` then `uv run ruff check .`
5. Commit with a message saying *why*, e.g. `Add prime <= standby check for generators`.
6. **Publish branch**, then **Create Pull Request**. CI runs. Green = mergeable.
7. Add a line under `[Unreleased]` in `CHANGELOG.md`.

## 6. Your turn: generator rating check

The prime/standby mistake on the sample schedule (prime 165 > standby 150) becomes the
tool's first design check. Create `src/kitlist/checks.py` with:

```python
def check_generator_ratings(standby_kw: float, prime_kw: float) -> list[str]:
    """Return a list of problems with a generator's ratings (empty list = OK)."""
```

Returning a list of messages (rather than True/False) lets the workbook show *what's*
wrong, and lets one function report several problems at once.

Write `tests/test_checks.py` **first**, with at least these cases:

- 150 standby, 135 prime: no problems.
- 150 standby, 165 prime: exactly one problem, and its text mentions "prime".
- prime equal to standby: your call. Decide, then write a test that pins your decision
  and a comment saying why. (This is an engineering decision, not a coding one.)
- negative or zero ratings: raise `ValueError`.

Stretch: add a demand check. Demand on the sample sheet is in kVA but generator ratings
are in kW, so you'll need a power factor input. Think about what default is defensible
and where it should be stated.

When CI is green, send me the PR link or paste the diff, and I'll review it like a
colleague would.
