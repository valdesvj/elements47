# Elements 47: working rules

- Work on a new branch; Victor creates and merges the PRs. Never force-push or rewrite history.
- Commit author: "Victor Valdes" <valdesvj@users.noreply.github.com>.
- Never commit binaries (.p47 files made by rejig, f42run, the patched rejig).
- Edit the programs in programs_rem/ (commented source), then run python3 tools/build_elem47.py:
  it writes programs/, build/ and listings/. Never edit those three by hand.
- Text on the C47 screen: ATEXT in GRFNT 21 (GRFNT 10 for the tiny font), as in Almanac 47.
  Restore GRFNT 20 and GRMOD 0 before the program ends.
- GRMOD and GRFNT take X: write `3 GRMOD`, not `3 STO r GRMOD r` (rejig writes "GRMOD r" as GRMOD and r).
- ELEM47 keeps the user's registers (LocR copy at the start, back at the end): a new register goes in
  that block (tools/build_elem47.py, the save list in programs_rem/ELEM47.txt).
- Optimizations must keep the screens: python3 tests/test_opt.py (pixel for pixel against branch optimize).
- One global label, LBL "ELEM47". Code labels by name in programs_rem (LBL :NAME:, 1-7 letters or digits);
  data labels reached with XEQ IND stay numeric. The build numbers the names (listings/ELEM47_labels.txt).
- Key waits: LBL n / PAUSE 50 / KEY? r / GTO n (not a bare KEY? loop; see Almanac 47 DEVELOPMENT_NOTES).
- Before changing a screen, check it in the simulator (python/elem47sim.py writes the pictures in docs/);
  then python3 tests/test_elem47.py.
- python/c47sim.py, stdfont.py, tinyfont.py come from Almanac 47: fix them there first, then copy.
- ~/opt/c43 (C47 firmware, git) and ~/opt/rpn (rejig, fossil): only read their files; never branch,
  build or write there.
- Ask before anything that can't be undone.
- Pull requests only for elements47.
