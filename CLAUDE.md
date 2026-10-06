# Elements 47: working rules

- Work on a new branch; Victor creates and merges the PRs. Never force-push or rewrite history.
- Commit author: "Victor Valdes" <valdesvj@users.noreply.github.com>.
- Never commit binaries (.p47 files made by rejig, f42run, the patched rejig).
- Edit the programs in programs_rem/ (commented source), then run python3 tools/build_elem47.py:
  it writes programs/, build/ and listings/. Never edit those three by hand.
- Text on the C47 screen: ATEXT in GRFNT 21 (GRFNT 10 for the tiny font), as in Almanac 47.
  Restore GRFNT 20 and GRMOD 0 before the program ends.
- Key waits: LBL n / PAUSE 50 / KEY? r / GTO n (not a bare KEY? loop; see Almanac 47 DEVELOPMENT_NOTES).
- Before changing a screen, check it in the simulator (python/elem47sim.py writes the pictures in docs/);
  then python3 tests/test_elem47.py.
- python/c47sim.py, stdfont.py, tinyfont.py come from Almanac 47: fix them there first, then copy.
- ~/opt/c43 (C47 firmware, git) and ~/opt/rpn (rejig, fossil): only read their files; never branch,
  build or write there.
- Ask before anything that can't be undone.
- Pull requests only for elements47.
