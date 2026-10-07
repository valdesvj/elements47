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
  data labels reached with XEQ IND stay numeric. build/ELEM47.txt keeps the names;
  build/ELEM47_num.txt is the numeric fallback (listings/ELEM47_labels.txt).
- Key waits: LBL n / PAUSE 50 / KEY? r / GTO n (not a bare KEY? loop; see Almanac 47 DEVELOPMENT_NOTES).
- Before changing a screen, check it in the simulator (python/elem47sim.py writes the pictures in docs/);
  then python3 tests/test_elem47.py.
- python/c47sim.py, stdfont.py, tinyfont.py come from Almanac 47: a fix is made there first (in a session
  working on Almanac 47), then copied here.
- Work in one repository at a time (this one); the others are for reference only: ~/opt/almanac47,
  ~/opt/c43 (C47 firmware, git), ~/opt/rpn and ~/opt/rejig (rejig). Read their files and run their tests;
  never edit, branch, commit, build or write there. A change they need: tell Victor.
- Ask before anything that can't be undone.
- Pull requests only for elements47.
