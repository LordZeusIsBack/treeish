# Contributing to treeish

Thanks for your interest in improving `treeish`. It's a small, single-file tool, and the goal is to keep it that way: simple, dependency-free, and easy to read. Contributions of all sizes are welcome — bug reports, doc fixes, and features alike.

## Ground rules

- **No runtime dependencies.** `treeish` runs on a stock Python 3.7+ install with nothing to `pip install`. Please keep it that way; the standard library covers everything this tool needs.
- **Stay single-file.** The whole tool lives in `treeish.py`. Unless there's a strong reason, keep it that way — it's part of what makes the project easy to drop into a PATH or vendor into another repo.
- **Cross-platform.** Code should work on Linux, macOS, and Windows. Prefer `os.path` / `pathlib` over hardcoded separators, and don't assume a particular shell.

## Getting set up

```sh
git clone https://github.com/YOUR_USERNAME/treeish.git
cd treeish
python3 treeish.py --path .
```

That's the whole setup. No build step, no environment to create.

## Reporting bugs

Open an issue and include:

- What you ran (the exact command).
- What you expected to see.
- What you actually saw (paste the output).
- Your OS, Python version (`python3 --version`), and git version (`git --version`) if the git-aware mode is involved.

A minimal directory layout that reproduces the problem is the single most helpful thing you can provide.

## Proposing features

Open an issue to discuss before writing a large change, so we can agree on scope and approach. A few things to keep in mind about direction:

- `treeish` prints a filtered tree. Features that serve that job (better filtering, output formats, sorting options) are in scope.
- Features that turn it into a different tool (file editing, network calls, heavy config systems) are probably out of scope. When in doubt, ask.

## Submitting a pull request

1. Fork the repo and create a branch off `main` (e.g. `fix-symlink-loop` or `add-json-output`).
2. Make your change. Keep the diff focused — one logical change per PR.
3. **Test it manually against a real directory.** Because git behavior is central, please verify your change against a folder that is (a) a git repo with tracked, untracked, and `.gitignore`'d files, and (b) a plain non-git folder. A quick way to build a test repo:

   ```sh
   mkdir /tmp/tt && cd /tmp/tt && git init -q
   mkdir -p src node_modules
   echo "print(1)" > src/main.py
   echo "junk"      > node_modules/x.js
   echo "*.log"     > .gitignore
   echo "log"       > debug.log      # gitignored
   echo "scratch"   > scratch.py     # untracked
   git add src .gitignore && git commit -qm init
   python3 /path/to/treeish.py --path .
   ```

   Confirm the default output shows only tracked files, `--no-git` shows untracked files but still hides `node_modules`, and `--all` shows everything.
4. Update `README.md` if you added or changed a flag or a user-facing behavior.
5. Open the PR with a clear description of what changed and why, and mention how you tested it.

## Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python style. If you have them installed, `black treeish.py` and `ruff check treeish.py` are a nice sanity check, but they're not required to contribute.
- Keep functions small and give them docstrings, matching the existing code.
- Prefer clear names over cleverness. This tool is meant to be readable at a glance.

## Code of conduct

Be kind and constructive. Assume good faith, keep discussion focused on the work, and help newcomers where you can.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers the project.
