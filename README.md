# treeish

A git-aware directory tree printer. Like `tree`, but it quietly leaves out the noise — `node_modules`, `__pycache__`, build artifacts, and anything your repo doesn't actually track. Built for handing clean project structures to LLMs, and just as useful anywhere you'd reach for `tree`.

The name is a nod to git: a _treeish_ is anything git can resolve to a tree. This tool prints one.

```
myproject/
├── .gitignore
├── README.md
└── src/
    ├── main.py
    └── utils/
        └── helper.py
```

That's the same project a plain `tree` would have buried under a few hundred lines of `node_modules` and `.git` internals.

## Motivation

`treeish` started from a specific, recurring annoyance: **giving an LLM a clean picture of a codebase.**

When you're doing agentic engineering or vibe coding — asking a model to reason about, navigate, or modify a project — the file structure is one of the most valuable things you can hand it. It tells the model where things live, how the project is organized, and what to touch. But a raw directory listing is nearly useless for this: `node_modules`, `.venv`, `__pycache__`, `dist`, lockfiles, and build output can be _thousands_ of lines that carry no signal about your actual code. Pasting that into a prompt does real damage:

- It **burns context window** on paths the model doesn't need, leaving less room for the code that matters.
- It **buries the signal** — the ten files you care about are lost in a sea of dependency internals.
- It **misleads the model** into treating vendored or generated files as part of your source, sometimes trying to "fix" things it shouldn't touch.

The insight is that your repo _already knows_ what matters. Your `.gitignore` is a hand-curated list of exactly the stuff that isn't your code. `treeish` leans on that: it shows the model the files git tracks and nothing else, producing a compact, high-signal tree that drops cleanly into a prompt. What the model sees is what you'd actually want it to reason about.

So while `treeish` is a perfectly good general-purpose `tree` replacement, its reason for existing is that moment when you type "here's my project structure:" into a chat and want what follows to be _useful_.

## Why

Running `tree` on a real project is mostly noise: dependency folders, virtualenvs, caches, and build output drown out the files you care about. `treeish` filters that out two ways:

- A built-in ignore list drops the usual suspects (`node_modules`, `.venv`, `__pycache__`, `dist`, `build`, and friends) everywhere.
- Inside a git repo, it shows **only files git tracks** — so untracked scratch files, generated output, and everything matched by your `.gitignore` disappear automatically. It asks git itself (`git ls-files`) rather than re-implementing `.gitignore` matching, so nested `.gitignore` files, `.git/info/exclude`, and your global excludes are all honored correctly.

The result is a tree that's ready to paste into an LLM prompt (see [Motivation](#motivation)), drop into a README, share in an issue, or just read at a glance.

## Install

`treeish` is a single file with no dependencies beyond Python 3.7+ (and `git` on your PATH for the git-aware mode).

```sh
git clone https://github.com/YOUR_USERNAME/treeish.git
cd treeish
```

Run it directly:

```sh
python3 treeish.py --path .
```

Or drop it somewhere on your PATH to call it from anywhere:

```sh
chmod +x treeish.py
cp treeish.py ~/.local/bin/treeish     # make sure ~/.local/bin is on your PATH
treeish --path .
```

## Usage

```sh
treeish [--path PATH] [--all] [--no-git] [--json]
```

| Flag           | Description                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------ |
| `--path`, `-p` | Folder whose tree to print. Defaults to the current directory.                                                     |
| `--all`, `-a`  | Show everything: disable both the built-in ignore list and git filtering.                                          |
| `--no-git`     | Skip git entirely; apply only the built-in ignore list.                                                            |
| `--json`       | Output the tree as JSON instead of the pretty box-drawing format. Handy for feeding structure to a program or LLM. |

### Examples

Print the current directory, git-aware (the default):

```sh
treeish
```

Print a specific folder:

```sh
treeish --path ~/code/myproject
```

See untracked files too, while still hiding `node_modules` and other junk:

```sh
treeish --no-git
```

See absolutely everything, filters off:

```sh
treeish --all
```

Get the structure as JSON, ready for a script or LLM to parse:

```sh
treeish --json
```

```json
{
  "README.md": 47,
  "src": {
    "main.py": 156,
    "utils.py": 89
  }
}
```

File values show line count; directory values are objects containing their contents.

## Behavior notes

- **Git-aware means tracked-only.** Inside a repo, a brand-new file you haven't `git add`ed yet won't appear. That's intentional — use `--no-git` if you want to see untracked files.
- **Outside a repo**, only the built-in ignore list applies.
- **No git installed?** It degrades gracefully to the built-in list instead of erroring.
- **Symlinks** are listed but never followed, so a symlink loop can't send it into infinite recursion.
- **Unreadable folders** produce a warning on stderr and are shown empty, rather than crashing the run.

## Customizing the ignore list

The built-in list lives in a `DEFAULT_IGNORE` set at the top of `treeish.py`. Add or remove entries to taste:

```python
DEFAULT_IGNORE = {
    "node_modules", ".git", ".venv", "__pycache__",
    "dist", "build", ".mypy_cache", ".pytest_cache",
    # add your own here...
}
```

## Compatibility

The tree uses Unicode box-drawing characters (`├──`, `└──`, `│`). These render fine on Linux, macOS, and Windows Terminal, but may look garbled in the legacy Windows `cmd.exe`. On modern shells you're good.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
