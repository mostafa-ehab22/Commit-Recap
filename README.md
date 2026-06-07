<div align="center">

# commit-recap

See everything you committed across all your repos since yesterday, in one command.

[![](https://skillicons.dev/icons?i=python,git)](https://skillicons.dev)

</div>

---

## The problem

Daily standups happen at 9am. You committed across three different repos yesterday and you can't remember what any of them were. You either open each repo manually and run `git log`, or you make something up.

This tool scans all git repositories in a directory, filters commits by your name, and prints a clean summary in one shot.

```
  Commit Recap  Mostafa Ehab  /  since yesterday

  --------------------------------------------
  flight-controller  2 commits

    1787b46  Implement PID loop for altitude hold  3 hours ago
    f2c06a8  Add flight controller base class  5 hours ago

  --------------------------------------------
  aws-iot-pipeline  1 commit

    d6c471d  Add IoT telemetry Lambda handler  yesterday

  --------------------------------------------
  3 commits across 2 repos
```

---

## Usage

```bash
python recap.py
```

Defaults to yesterday's commits across all repos in the current directory, filtered by your `git config user.name`.

```bash
# options
--since     yesterday | today | 7d | 2w   (default: yesterday)
--repo      path to scan for git repos     (default: current directory)
--author    filter by author name          (default: git config user.name)
--verbose   show commit author email
--all       include repos with no commits in the range
```

**Examples**

```bash
python recap.py                              # yesterday, all repos here
python recap.py --since today                # today so far
python recap.py --since 7d                   # last 7 days
python recap.py --since 2w                   # last 2 weeks
python recap.py --repo ~/projects            # scan a specific directory
python recap.py --repo ~/projects/myapp      # single repo
python recap.py --author "Jane Doe"          # someone else's commits
python recap.py --verbose                    # include author email per commit
python recap.py --all                        # show repos with zero commits too
```

---

## How it works

Scans the target directory for any folder containing a `.git` subdirectory. For each repo found, runs `git log` with your author name and the specified time range. Results are grouped by repo with commit hash, message, and relative timestamp.

Author name is auto-detected from `git config user.name`. Override anytime with `--author`.

---

## No dependencies

Standard library only. Requires git to be installed and accessible in your PATH.

```bash
git clone https://github.com/mostafa-ehab22/commit-recap
cd commit-recap
python recap.py
```

---

## License

MIT
