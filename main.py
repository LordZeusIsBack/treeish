import argparse
import os
import subprocess
import sys


DEFAULT_IGNORE = {
    "node_modules", ".git", ".hg", ".svn",
    ".venv", "venv", "env", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
    "dist", "build", ".next", ".nuxt", ".cache",
    ".idea", ".vscode", ".DS_Store",
    ".eggs", ".gradle", "target",
}


def find_git_root(path):
    """Return the repo root if `path` is inside a git work tree, else None."""
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def git_tracked_paths(root):
    """
    Return a set of absolute paths that git tracks under `root`.

    Both the tracked files themselves and every ancestor directory are
    included, so an interior directory that only contains tracked files
    is itself considered "tracked" and gets shown.
    """
    result = subprocess.run(
        ["git", "-C", root, "ls-files", "-z"],
        capture_output=True, text=True, check=False,
    )
    tracked = set()
    for rel in result.stdout.split("\0"):
        if not rel:
            continue
        abs_path = os.path.join(root, rel)
        tracked.add(abs_path)
        parent = os.path.dirname(abs_path)
        while True:
            tracked.add(parent)
            if os.path.normpath(parent) == os.path.normpath(root):
                break
            new_parent = os.path.dirname(parent)
            if new_parent == parent:
                break
            parent = new_parent
    return tracked


def build_tree(root, show_all, tracked):
    """
    Recursively build a nested-dict representation of `root`.

    Directories -> dict of contents (possibly {}). Files -> None.
    Symlinks are listed but never followed, so a symlink loop can't
    cause infinite recursion.

    `tracked` is either None (no git filtering) or a set of absolute
    paths that git tracks; entries not in the set are skipped.
    """
    node = {}
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                if not show_all and entry.name in DEFAULT_IGNORE:
                    continue
                if tracked is not None and entry.path not in tracked:
                    continue
                if entry.is_dir(follow_symlinks=False):
                    node[entry.name] = build_tree(entry.path, show_all, tracked)
                else:
                    node[entry.name] = None
    except OSError as e:
        print(f"warning: skipping {root!r}: {e.strerror}", file=sys.stderr)
    return node


def print_tree(node, prefix=""):
    """Recursively print a nested-dict tree using box-drawing characters."""
    items = sorted(node.items())
    for i, (name, child) in enumerate(items):
        last = i == len(items) - 1
        is_dir = isinstance(child, dict)
        connector = "└── " if last else "├── "
        print(prefix + connector + name + ("/" if is_dir else ""))
        if is_dir:
            print_tree(child, prefix + ("    " if last else "│   "))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Print a git-aware directory tree, similar to the Unix `tree` command."
    )
    parser.add_argument(
        "--path", "-p", default=".",
        help="Path of the folder whose tree is required (default: current directory)",
    )
    parser.add_argument(
        "--all", "-a", action="store_true",
        help="Show everything: disable the built-in ignore list and git filtering",
    )
    parser.add_argument(
        "--no-git", action="store_true",
        help="Don't consult git; only apply the built-in ignore list",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = os.path.abspath(os.path.expanduser(args.path))

    if not os.path.exists(root):
        print(f"Error: no such file or directory: {args.path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(root):
        print(f"Error: not a directory: {args.path}", file=sys.stderr)
        sys.exit(1)

    tracked = None
    if not args.all and not args.no_git:
        git_root = find_git_root(root)
        if git_root is not None:
            tracked = git_tracked_paths(git_root)

    label = os.path.basename(root) or root
    if not label.endswith("/"):
        label += "/"

    tree = build_tree(root, show_all=args.all, tracked=tracked)
    print(label)
    print_tree(tree)


if __name__ == "__main__":
    main()
