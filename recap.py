import subprocess
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"

def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def fmt(text, *codes):
    if not supports_color():
        return text
    return "".join(codes) + text + RESET

def get_git_author():
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True
        )
        name = result.stdout.strip()
        return name if name else None
    except FileNotFoundError:
        return None

def find_git_repos(root):
    repos = []
    root = Path(root).expanduser().resolve()
    if (root / ".git").exists():
        return [root]
    for path in sorted(root.iterdir()):
        if path.is_dir() and (path / ".git").exists():
            repos.append(path)
    return repos

def get_commits(repo_path, author, since, until):
    cmd = [
        "git", "-C", str(repo_path),
        "log",
        "--oneline",
        "--no-merges",
        f"--author={author}",
        f"--since={since}",
        f"--until={until}",
        "--format=%h|||%s|||%cr|||%ae",
        "--all",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return []
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        commits = []
        for line in lines:
            parts = line.split("|||")
            if len(parts) == 4:
                commits.append({
                    "hash":    parts[0],
                    "message": parts[1],
                    "ago":     parts[2],
                    "email":   parts[3],
                })
        return commits
    except FileNotFoundError:
        print(fmt("  Error: git not found. Make sure git is installed.", RED))
        sys.exit(1)

def parse_since(value):
    value = value.strip().lower()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if value == "yesterday":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"), \
               today.strftime("%Y-%m-%d 00:00:00")
    if value == "today":
        return today.strftime("%Y-%m-%d 00:00:00"), \
               (today + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    if value.endswith("d") and value[:-1].isdigit():
        days = int(value[:-1])
        return (today - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00"), \
               (today + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    if value.endswith("w") and value[:-1].isdigit():
        weeks = int(value[:-1])
        return (today - timedelta(weeks=weeks)).strftime("%Y-%m-%d 00:00:00"), \
               (today + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    # fallback: pass raw to git
    return value, (today + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")

def print_repo_commits(repo_name, commits, verbose=False):
    print(fmt("  " + "-" * 44, DIM))
    print(f"  {fmt(repo_name, BOLD, CYAN)}  {fmt(f'{len(commits)} commit{'s' if len(commits) != 1 else ''}', DIM)}")
    print()
    for c in commits:
        hash_str  = fmt(c["hash"], YELLOW)
        msg       = c["message"]
        ago       = fmt(c["ago"], DIM)
        print(f"    {hash_str}  {msg}  {ago}")
        if verbose:
            print(fmt(f"           {c['email']}", DIM))
    print()

def main():
    parser = argparse.ArgumentParser(
        description="See what you committed across your repos — perfect for daily standups.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python recap.py                          yesterday's commits, all repos in current dir
  python recap.py --since today            today's commits
  python recap.py --since 7d              last 7 days
  python recap.py --since 2w              last 2 weeks
  python recap.py --repo ~/projects/myapp  single repo
  python recap.py --author "Jane Doe"      filter by author name
  python recap.py --verbose                show commit author email
        """
    )
    parser.add_argument("--since",   default="yesterday",
                        help="time range: yesterday, today, 7d, 2w (default: yesterday)")
    parser.add_argument("--repo",    default=".",
                        help="path to scan for git repos (default: current directory)")
    parser.add_argument("--author",  default=None,
                        help="author name to filter by (default: your git config user.name)")
    parser.add_argument("--verbose", action="store_true",
                        help="show commit author email")
    parser.add_argument("--all",     action="store_true",
                        help="include repos with no commits in the range")

    args = parser.parse_args()

    author = args.author or get_git_author()
    if not author:
        print(fmt("  Error: could not detect git author. Use --author \"Your Name\".", RED))
        sys.exit(1)

    since, until = parse_since(args.since)

    repos = find_git_repos(args.repo)
    if not repos:
        print(fmt(f"  No git repositories found in: {args.repo}", RED))
        sys.exit(1)

    print()
    print(fmt("  Commit Recap", BOLD) + fmt(f"  {author}  /  since {args.since}", DIM))
    print()

    total_commits = 0
    active_repos  = 0

    for repo in repos:
        commits = get_commits(repo, author, since, until)
        if not commits and not args.all:
            continue
        print_repo_commits(repo.name, commits, verbose=args.verbose)
        total_commits += len(commits)
        if commits:
            active_repos += 1

    print(fmt("  " + "-" * 44, DIM))
    if total_commits == 0:
        print(fmt(f"  No commits found since {args.since}. Either you rested or the range is off.", DIM))
    else:
        print(f"  {fmt(str(total_commits), BOLD)} commit{'s' if total_commits != 1 else ''} across "
              f"{fmt(str(active_repos), BOLD)} repo{'s' if active_repos != 1 else ''}")
    print()

if __name__ == "__main__":
    main()
