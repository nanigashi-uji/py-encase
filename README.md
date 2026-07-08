# py-encase

[![PyPI version](https://img.shields.io/pypi/v/py-encase?logo=pypi)](https://pypi.org/project/py-encase/)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-encase?logo=python)](https://pypi.org/project/py-encase/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/py-encase)](https://pepy.tech/project/py-encase)

**py-encase** is a utility to set up a **portable Python script environment** quickly and consistently.
It automates repetitive tasks often required in script development, such as creating directory structures, generating script templates, managing libraries, installing dependencies locally, and initializing Git repositories.

The entire tool is a single self-contained script (`py_encase.py`). Once it is copied into a working tree, it plays two roles at the same time:

- **Runner** — a symlink named after your script (e.g. `bin/my_tool`) transparently sets `PYTHONPATH` and executes the corresponding library file under `lib/python/`.
- **Manager** (`bin/mng_encase`) — the very same file, invoked through a differently named symlink (or with the `--manage` flag), exposes a set of subcommands (`init`, `add`, `install`, `clean`, ...) used to scaffold and maintain the environment.

---

## Features

- Create portable script environments under a given prefix
- Generate script templates and reusable library modules
- Manage dependencies locally (no need for system-wide pip installs)
- Detect external imports in your scripts and translate them into pip package names automatically
- Initialize Git repositories with remote setup support (GitHub / GitLab / generic SSH host)
- Keep documentation (`README.md`) updated automatically
- Support both **script-based tools** and **package/module development**
- Read default options from a config file (TOML / JSON / INI)

---

## Installation

```bash
pip install py-encase
```

or install into a local sandbox directory:

```bash
pip install --target ./py_sandbox py-encase
```

---

## Requirement

- Python >= 3.9 (Python >= 3.11 is required to use TOML configuration files)
- pip3
- `git` (only required for the `init_git` / `--setup-git` related features)

---

## Usage Examples

### Create a new toolset

```bash
pip3 install --target "${workdir}/py_sandbox" py-encase

env PYTHONPATH="${workdir}/py_sandbox:" \
  "${workdir}/py_sandbox/bin/py_encase" --manage init --verbose \
  --prefix "${workdir}/my-new-tools" \
  --readme --title "Tools for my work ..." \
  --app-framework \
  --module dateutils \
  --required-module \
  --script-lib 'my_utils.py' \
  --setup-git \
  --git-user-name 'my_git_account' \
  --git-user-email 'my_git_account@my_git_host.domain' \
  --git-set-upstream \
  --git-remote-setup \
  --git-remote-account remote_account \
  --git-remote-host remotehost.remotedomain \
  --git-remote-path '~/git_repositories/' \
  --git-remote-share group \
  --git-protocol ssh \
  my_new_work_tool
```

### Running Scripts in the Encased Environment

One of the most important features of py-encase is that you do not need to manually set environment variables (such as `PYTHONPATH`) when running your scripts.

When you create a new script using py-encase, a symlink with the script's basename is placed under the `bin/` directory.
For example, after creating a script named `my_new_work_tool.py`, you will have:

```
my-new-tools/
├── bin/
│   ├── mng_encase
│   └── my_new_work_tool   -> symlink to py_encase.py
├── lib/
│   └── python/
│       └── my_new_work_tool.py
```

You can run your script simply by calling:

```bash
./bin/my_new_work_tool
```

The symlink automatically points to `py_encase.py`, which sets up the correct environment variables internally before executing the script.
This ensures the script runs inside the encased environment without requiring you to export variables manually.

This mechanism makes py-encase environments self-contained, portable, and easy to run.

---

### Add scripts and libraries

```bash
"${workdir}/my-new-tools/bin/mng_encase" add -v another_tool
"${workdir}/my-new-tools/bin/mng_encase" addlib -v util_helpers
```

### Start module development

```bash
"${workdir}/my_module_dev/bin/mng_encase" newmodule --verbose \
  --title "My New Work Utils" \
  --description "Utility classes for ...." \
  --module dateutils \
  --git-user-name 'my_git_account' \
  --git-user-email 'my_git_account@my_git_host.domain' \
  --git-set-upstream \
  --git-remote-setup \
  --git-remote-account remote_account \
  --git-remote-host remotehost.remotedomain \
  --git-remote-path '~/git_repositories' \
  my_new_work_utils
```

---

### Configuration via Environment Variables

| Variable | Purpose |
|----------|---------|
| `GIT_REMOTE_USER` | Remote git account user name |
| `GIT_REMOTE_HOST` | Remote git host name |
| `GIT_REMOTE_PATH` | Path of the remote git repository |
| `GIT` | Overrides the `git` command/path used when no `-G/--git-command` is given |
| `PY_ENCASE_TEMPLATE` | Overrides the template file used by subcommands that accept `-D/--template` |
| `XDG_CONFIG_HOME` | Base directory used to look up the default config file (`~/.config` if unset) |

### Configuration File

In manage mode, py-encase looks for a default configuration file before parsing subcommand options:

```
${XDG_CONFIG_HOME:-~/.config}/py-encase/py-encase_config.{toml,json,ini}
```

TOML is tried first (Python ≥ 3.11 only), then JSON, then INI. Keys under the `DEFAULT` section/table are always applied; an additional named section selected with `--config-type <name>` is applied on top of it. This lets you keep several named presets (e.g. `[github]` / `[gitlab]`) in a single file and select one per invocation.

| Option | Purpose |
|--------|---------|
| `--config-file <path>` | Load an additional config file on top of the default one |
| `--config-type <name>` | Select a named section/table of the config file to apply |
| `--no-config-read` | Skip reading the default config file entirely |
| `--config-help` | Show help about the configuration file mechanism |

---

## Step-by-step Usage

1. Initialization of working environment under certain directory
   ("${prefix}") with creating new python script 'newscript.py' from
   template and installing specified python modules specified in CLI.

```
# Create environment
% py_encase --manage init -r -g -v --prefix=${prefix} -m pytz -m tzlocal newscript.py
.....
# Check file produced
% ( cd ${prefix} ls -ltrd {bin,lib/python,lib/python/site-packages/*}/* )
.... bin/py_encase.py
.... bin/mng_encase -> py_encase.py
.... bin/newscript -> py_encase.py
.... lib/python/site-packages
.... lib/python/newscript.py
.... lib/python/site-packages/3.13.4/pytz
.... lib/python/site-packages/3.13.4/pytz-2025.2.dist-info
.... lib/python/site-packages/3.13.4/tzlocal
.... lib/python/site-packages/3.13.4/tzlocal-5.3.1.dist-info
```

The entity of this tool will be copied to `${prefix}/py_encase.py`.
A new script is created as `lib/python/newscript.py`.

The symbolic link under `bin/` (=`bin/newscript`) runs
`lib/python/newscript.py`, taking care of the environment variable
`PYTHONPATH` so that python modules locally installed by pip
under `lib/python/site-packages` are found.

```
% ${prefix}/bin/newscript -d
Hello, World! It is "Wed Jul  2 16:26:06 2025."
Python : 3.13.4 ({somewhere}/bin/python3.13)
1  : ${prefix}/lib/python
2  : ${prefix}/lib/python/site-packages/3.13.4
3  : ....
```

Another symbolic link `bin/mng_encase` can be used to create another
python script and its symbolic link for execution, from the template.

```
% ${prefix}/bin/mng_encase add another_script_can_be_run.py
```

Another python script for a library/module can also be created from
the template.

```
% ${prefix}bin/mng_encase addlib another_script_can_be_run.py
```

It is also possible to install a module by `pip` locally under
`${prefix}/lib/python/site-packages`.

```
% ${prefix}bin/mng_encase install modulename1 modulename2 ....
```

Modules installed locally by this tool can be deleted with the
subcommands `clean` or `distclean`.

```
# Removing modules installed locally for the currently used python/pip version
% ${prefix}bin/mng_encase clean
# Removing all modules installed locally by pip (all python versions)
% ${prefix}bin/mng_encase distclean
```

---

## Two Invocation Modes

`py_encase.py` behaves differently depending on how it is invoked:

- **Script (runner) mode** — when invoked through a symlink whose name is *not* `mng_encase` (e.g. `bin/newscript`), or without `--manage`, py-encase sets `PYTHONPATH` to include the encased `lib/python` and `lib/python/site-packages/<pyver>` directories, then `exec`s the target script (`lib/python/<name>.py`) with any remaining CLI arguments passed straight through.
- **Manage mode** — when invoked as `mng_encase` (or with `--manage` when the entity file `py_encase.py` is called directly), the argument list is parsed as one of the subcommands documented below.

```bash
# Script mode: runs lib/python/newscript.py
./bin/newscript --some-script-option

# Manage mode: administers the environment itself
./bin/mng_encase <subcommand> [options]
# equivalent, if you call the entity file directly:
./bin/py_encase.py --manage <subcommand> [options]
```

---

## Manage-mode Global Options

These options are parsed **before** the subcommand name and apply to manage mode as a whole:

| Option | Description |
|--------|-------------|
| `-p, --prefix PATH` | Prefix of the directory tree to operate on. Default: the grandparent directory of the invoked script if its parent directory is named `bin`, otherwise the current working directory |
| `-P, --python PATH` | Python interpreter path/command to use |
| `-I, --pip PATH` | pip command/path to use |
| `-G, --git-command PATH` | git command/path to use |
| `-v, --verbose` | Verbose output |
| `-n, --dry-run` | Dry-run mode (no filesystem/network changes) |
| `--manage-help` | Show help for manage-mode options |
| `-h, --help` | Show help (equivalent to `help` subcommand with no argument) |
| `--config-file PATH` | Additional configuration file to load |
| `--config-type NAME` | Named section of the configuration file to apply |
| `--no-config-read` | Do not read the default configuration file |
| `--config-help` | Show help about the configuration-file mechanism |

Most of the per-subcommand options below (`-p/--prefix`, `-P/--python`, `-I/--pip`, `-G/--git-command`, `-v/--verbose`, `-n/--dry-run`) simply repeat these global options at the subcommand level so they can also be given *after* the subcommand name.

---

## Subcommands

### `info`
Show information about the py-encase installation and the current environment.

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Show all path information (same as `--long`) |
| `-l, --long` | Show a long/detailed description |
| `-s, --short` | Show minimum description (values only, no labels) |
| `-V, --version` | Show version information |
| `-m, --pip-module-name` | Show the PyPI module name (`py-encase`) |
| `-M, --manage-script-name` | Show the manage script name (`mng_encase`) |
| `-O, --manage-option` | Show the CLI option used to enter manage mode (`--manage`) |

```bash
mng_encase info                 # short one-line description
mng_encase info --version       # e.g. "PIP module version: 0.0.34"
mng_encase info --long          # full dump: paths, python/pip commands, directories...
mng_encase info -s -V           # bare version string, no label
```

### `contents`
List the files that make up the environment: scripts, libraries and module sources.

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Print a section header before each category |
| `-a, --all` | Show all categories (default when no category flag is given) |
| `-b, --bin-script` | Show `bin/` scripts |
| `-l, --lib-script` | Show `lib/python` library scripts |
| `-m, --module-src` | Show module source directories |

```bash
mng_encase contents                 # everything
mng_encase contents -b -v           # only bin/ scripts, with section header
```

### `init`
Bootstrap a brand-new execution environment under a given prefix: directory structure, template script(s), `bin/` launcher symlinks, `README.md`, dependency installation, and Git initialization.

| Option | Description |
|--------|-------------|
| `-p, --prefix PATH` | Prefix of the directory tree (see global option) |
| `-t, --title TEXT` | Project title, used in the generated `README.md` |
| `-D, --template PATH` | Template file to use (default: `py_encase.py` itself) |
| `-x, --script-template-style STYLE` | Select a built-in script template style. Currently supported: `simple`, `app-framework`. The default is `simple`. |
| `-y, --scrlib-template-style STYLE` | Select a built-in script-library template style. Currently supported: `simple`. |
| `-F, --app-framework` | Use the template variant that includes the application framework (GUI/argparse-extd helpers) |
| `-B, --simple-script`, `--bare-script` | Use the simple built-in script template without the application framework. `--bare-script` is kept as a backward-compatible alias for `--simple-script`. |
| `-K, --gui-kvfile [NAME]` | Also create a sample Kivy `.kv` file for a GUI application |
| `-r, --readme` | Create/update `README.md` |
| `-m, --module NAME` | Install an extra module via pip (repeatable) |
| `-i, --install-dependency` | Install modules required by the generated script, detected automatically |
| `-O, --required-module` | Install modules/script-libraries that are referenced by the template itself |
| `-s, --script-lib NAME` | Copy a library script from the template's collection into `lib/python` (repeatable) |
| `-S, --std-script-lib` | Install all standard bundled library scripts (equivalent to giving `-s` for each of them) |
| `-g, --setup-git` | Initialize Git for the new environment (see [Git-remote options](#git-remote-options)) |
| `-M, --move` | Move (instead of copy) this script's own body into the new environment |
| `-P, --python PATH` | Python path/command |
| `-I, --pip PATH` | pip path/command |
| `-G, --git-command PATH` | git path/command |
| `--conv-table PATH` | Table file mapping import names → pip package names (see [`show_deps`](#show_deps)) |
| `--dependency-file PATH` | Explicit module requirement file |
| `-v, --verbose` | Verbose output |
| `-n, --dry-run` | Dry-run mode |
| `scriptnames...` | Script file name(s) to create (positional, zero or more) |

```bash
# Minimal environment with a single script
mng_encase init --prefix ./my-tool my_tool.py

# Full-featured environment: README, framework template, auto-installed deps, Git
mng_encase init -v -r -g -F -O \
  --prefix ./my-new-tools --title "My tools" \
  -m requests -m pyyaml \
  my_new_work_tool
```

### `add`
Add one or more new script files to an existing environment (creates the `lib/python/<name>.py` file plus its `bin/<name>` launcher symlink).

| Option | Description |
|--------|-------------|
| `-p, --prefix PATH` | Prefix of the directory tree |
| `-r, --readme` | Update `README.md` after adding the script(s) |
| `-D, --template PATH` | Template file to use |
| `-x, --script-template-style STYLE` | Select a built-in script template style. Currently supported: `simple`, `app-framework`. The default is `simple`. |
| `-F, --app-framework` | Use the application-framework template variant |
| `-B, --simple-script`, `--bare-script` | Use the simple built-in script template. `--bare-script` is a backward-compatible alias. |
| `-K, --gui-kvfile [NAME]` | Also create a sample Kivy `.kv` file |
| `-m, --module NAME` | Install an extra module via pip (repeatable) |
| `-i, --install-dependency` | Auto-detect and install modules required by the new script |
| `-O, --required-module` | Install modules/script-libraries referenced by the template |
| `-s, --script-lib NAME` | Copy a library script from the template (repeatable) |
| `-S, --std-script-lib` | Install all standard bundled library scripts |
| `-P, --python PATH` / `-I, --pip PATH` / `-G, --git-command PATH` | Command paths |
| `-T, --conv-table PATH` | Import-name → pip-name conversion table |
| `-R, --dependency-file PATH` | Explicit module requirement file |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |
| `scriptnames...` | Script file name(s) to create (positional, one or more, required) |

```bash
mng_encase add -v another_tool
mng_encase add -r -i second_tool third_tool   # two scripts at once, auto-install deps, update README
```

### Built-in script template styles

The `init` and `add` subcommands can choose a built-in script template style.

| Option | Equivalent style | Description |
|--------|------------------|-------------|
| `--script-template-style simple` | `simple` | The default simple script template. |
| `--script-template-style app-framework` | `app-framework` | The application-framework template. |
| `-B, --simple-script` | `simple` | Shortcut for the simple script template. |
| `--bare-script` | `simple` | Backward-compatible alias for `--simple-script`. |
| `-F, --app-framework` | `app-framework` | Shortcut for the application-framework template. |

Examples:

```bash
mng_encase init --script-template-style simple --prefix ./my-tool my_tool.py
mng_encase add --simple-script helper_tool.py
mng_encase add --bare-script legacy_name.py      # alias of --simple-script
mng_encase add --app-framework gui_tool.py
```

### `addlib`
Add one or more one-file library modules, for factoring out utilities shared across scripts. Library files are created under `lib/python` without a `bin/` launcher.

| Option | Description |
|--------|-------------|
| `-p, --prefix PATH` | Prefix of the directory tree |
| `-r, --readme` | Update `README.md` |
| `-D, --template PATH` | Template file to use |
| `-m, --module NAME` | Install an extra module via pip (repeatable) |
| `-i, --install-dependency` | Auto-detect and install required (external) modules |
| `-O, --required-module` | Install modules/script-libraries referenced by the template |
| `-S, --std-script-lib` | Install all standard bundled library scripts |
| `-P, --python PATH` / `-I, --pip PATH` / `-G, --git-command PATH` | Command paths |
| `-T, --conv-table PATH` / `-R, --dependency-file PATH` | Dependency-resolution overrides |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |
| `script_lib...` | Library-script file name(s) to create (positional, one or more, required) |

```bash
mng_encase addlib -v util_helpers
mng_encase addlib date_helpers string_helpers
```

### `addkv`
Add one or more Kivy (`.kv`) UI-definition files, for GUI applications built with the app-framework template.

| Option | Description |
|--------|-------------|
| `-p, --prefix PATH` | Prefix of the directory tree |
| `-D, --template PATH` | Template file to use |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |
| `kvfiles...` | KV-file name(s) to create (positional, one or more, required) |

```bash
mng_encase addkv main_window
```

### `newmodule`
Create a package-structured Python module (source layout, tests, docs, `pyproject.toml`, `LICENSE`) suitable for distribution, instead of a single script.

| Option | Description |
|--------|-------------|
| `-p, --prefix PATH` | Prefix of the directory tree |
| `-t, --title TEXT` | Project title |
| `-d, --description TEXT` | Project description |
| `-D, --template PATH` | Template file to use |
| `-W, --module-website URL` | Homepage/website URL for the new module (repeatable) |
| `-C, --class-name NAME` | Class name to generate inside the module (repeatable) |
| `-m, --module NAME` | External module required by the new module, added as a dependency (repeatable) |
| `-k, --keywords WORD` | Keyword(s) for `pyproject.toml` metadata (repeatable) |
| `-c, --classifiers TEXT` | PyPI trove classifier(s) (repeatable) |
| `-A, --author-name NAME` | Author name(s) (repeatable) |
| `-E, --author-email EMAIL` | Author email(s) (repeatable) |
| `-M, --maintainer-name NAME` | Maintainer name(s) (repeatable) |
| `-N, --maintainer-email EMAIL` | Maintainer email(s) (repeatable) |
| `-Y, --create-year YEAR` | Copyright year to put in `LICENSE` (repeatable) |
| `-Q, --no-readme` | Do not create `README.md` |
| `-b, --no-git-file` | Do not create Git-related files |
| `-S, --set-shebang` | Set the shebang line based on the local environment |
| `-P, --python PATH` / `-I, --pip PATH` / `-G, --git-command PATH` | Command paths |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |
| *(see [Git-remote options](#git-remote-options))* | Git repository setup, shared with `init`/`init_git` |
| `module_name...` | New module name(s) to create (positional, one or more, required) |

```bash
mng_encase newmodule --verbose \
  --title "My New Work Utils" \
  --description "Utility classes for ..." \
  --module dateutils \
  --author-name "My Name" --author-email me@example.com \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-remote-account remote_account --git-remote-host remotehost.remotedomain \
  --git-remote-path '~/git_repositories' \
  my_new_work_utils
```

### `update_readme`
Regenerate/refresh `README.md` from the template, filling in the current list of bin scripts, library scripts, and `.gitkeep` directories.

| Option | Description |
|--------|-------------|
| `-t, --title TEXT` | Title text to use in the README |
| `-D, --template PATH` | Template file to use |
| `-b, --backup` | Keep a timestamped backup of the previous `README.md` |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |

```bash
mng_encase update_readme -t "My Toolset" -b
```

### `init_git`
Initialize (or reconfigure) a Git repository for the working environment, or for a specific module source directory, including optional remote repository creation on GitHub/GitLab/a generic SSH host.

| Option | Description |
|--------|-------------|
| `-m, --module-src PATH` | Set up git for the specified module source directory instead of the top-level working environment |
| `-G, --git-command PATH` | git path/command |
| `-D, --template PATH` | Template file to use |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |
| *(see [Git-remote options](#git-remote-options))* | Full set of remote-repository options |

```bash
mng_encase init_git -v \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-hosting github --git-remote-account my_git_account --git-protocol ssh
```

### `dump_template`
Dump the embedded template portion of `py_encase.py` (used internally to generate scripts, libraries, `README.md`, etc.) to a file or to standard output. Useful for inspecting or customizing the template.

| Option | Description |
|--------|-------------|
| `-o, --output PATH` | Write to a file instead of stdout |
| `-D, --template PATH` | Template file to use as source |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |

```bash
mng_encase dump_template -o my_custom_template.py
```

### `clean`
Remove modules and caches installed locally by pip **for the currently selected Python/pip version only**.

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Verbose output |
| `-n, --dry-run` | Dry-run mode |

```bash
mng_encase clean -v
```

### `distclean`
Like `clean`, but removes **all** locally installed modules/caches for every Python version found under the environment (a more thorough cleanup).

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Verbose output |
| `-n, --dry-run` | Dry-run mode |

```bash
mng_encase distclean -v
```

### `selfupdate`
Update `py-encase` itself: installs the latest version from PyPI into the local sandbox, compares version numbers, and — if a newer version is available (or `--force-install` is given) — replaces the currently running `py_encase.py` entity file with the new one (keeping a timestamped backup of the old file).

| Option | Description |
|--------|-------------|
| `-f, --force-install` | Replace the entity file even if the installed version is not newer |
| `-v, --verbose` / `-n, --dry-run` | Verbose / dry-run |

```bash
mng_encase selfupdate -v
mng_encase selfupdate --force-install
```

### pip wrapper subcommands: `install`, `download`, `freeze`, `inspect`, `list`, `cache`, `help`
These subcommands pass their arguments straight through to `pip`, but automatically point pip at the environment's local sandbox (`--target`/`--path`/`--cache-dir`/`--log`, etc. under the encased `lib/python/site-packages`) so that nothing is ever installed system-wide.

| Subcommand | Underlying pip command | Notes |
|------------|------------------------|-------|
| `install` | `pip install --target <sandbox> ...` | Installs a package into the local sandbox |
| `download` | `pip download --dest <sandbox> ...` | Downloads a package's distribution files |
| `freeze` | `pip freeze --path <sandbox> ...` | Lists installed packages in requirements format |
| `inspect` | `pip inspect --path <sandbox> ...` | Shows machine-readable details of the local environment |
| `list` | `pip list --path <sandbox> ...` | Lists installed packages |
| `cache` | `pip cache ...` | Manages pip's cache |
| `help` | `pip help ...` | Shows pip's own help (mapped internally from the `piphelp` subcommand) |

Every one of these accepts any number of extra positional arguments (`pip_subcommand_args`), which are forwarded verbatim to `pip`.

```bash
mng_encase install requests pyyaml
mng_encase list
mng_encase freeze
mng_encase cache list
```

### `show_deps`
Statically scan the environment's scripts, libraries and/or module sources for `import`/`from ... import` statements, filter out standard-library and locally-defined names, and translate the remaining external import names into pip package names (using a built-in table plus any custom conversion table / requirement file). By default the resulting package list is printed to stdout.

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Show, for each detected import, which file(s) it came from and its resolved pip name |
| `-a, --all` | Scan all categories (default when no category flag is given) |
| `-b, --bin-script` | Scan `bin/` scripts |
| `-l, --lib-script` | Scan `lib/python` library scripts |
| `-m, --module-src` | Scan module source directories |
| `-D, --no-dump` | Suppress the stdout package list (still returns the list internally) |
| `-T, --conv-table PATH` | Table file mapping import names → pip package names (JSON/TOML/INI/plain text; overrides the auto-discovered `MODULE_NAME.*` file) |
| `-R, --dependency-file PATH` | Extra/forced requirements file (JSON/TOML/INI/plain text; overrides the auto-discovered `Requirements.*` file), merged into the conversion table |

```bash
mng_encase show_deps -v
mng_encase show_deps -b --conv-table my_import_map.json
```

### `install_deps`
Run `show_deps` internally to discover the required external packages, then `pip install` all of them into the local sandbox in one step.

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Verbose output |
| `-n, --dry-run` | Dry-run mode (show what would be installed) |
| `-a, --all` / `-b, --bin-script` / `-l, --lib-script` / `-m, --module-src` | Same scanning-scope flags as `show_deps` |
| `-D, --dump` | Also print the discovered package list to stdout |
| `-T, --conv-table PATH` | Import-name → pip-name conversion table |
| `-R, --dependency-file PATH` | Extra/forced requirements file |
| `pip_subcommand_args...` | Extra arguments forwarded to the underlying `pip install` call |

```bash
mng_encase install_deps -v
mng_encase install_deps -D -- --upgrade
```

### `help`
Show the top-level manage-mode help, or the detailed help for a single subcommand.

| Option | Description |
|--------|-------------|
| `command` | (optional, positional) name of a subcommand to show help for |

```bash
mng_encase help              # same as: mng_encase --help
mng_encase help init         # detailed help for the "init" subcommand
```

---

## Git-remote Options

`init`, `newmodule`, and `init_git` all share the same set of Git/remote-repository options:

| Option | Description |
|--------|-------------|
| `-y, --git-set-upstream` | Set the created local branch's upstream to the remote |
| `-R, --git-remote-setup` | Also create/initialize the remote bare repository |
| `-u, --git-user-name NAME` | Git user name to configure |
| `-e, --git-user-email EMAIL` | Git user email to configure |
| `--github-userinfo INFO` | GitHub account information (used together with `--git-hosting github`) |
| `--gitlab-userinfo INFO` | GitLab account information (used together with `--git-hosting gitlab`) |
| `-T, --git-repository-name NAME` | Remote repository name (default: derived from the project/module name) |
| `-H, --git-hosting {github,gitlab}` | Git hosting service to use for remote creation |
| `-z, --git-protocol {http,https,ssh}` | Protocol used to reach the remote |
| `-U, --git-remote-url URL` | Explicit remote URL (overrides host/account/path based construction) |
| `-l, --git-remote-account NAME` | Account name on the GitHub/GitLab/remote host |
| `-L, --git-remote-host HOST` | Remote git host name |
| `--git-remote-port PORT` | Port used to reach the remote host |
| `-w, --git-remote-path PATH` | Path of the repositories directory on the remote host |
| `-X, --git-remote-sshopts OPT` | Extra ssh option(s) for connecting to the remote (repeatable; escape a leading `-` as `\-`) |
| `-Z, --git-remote-cmd CMD` | git command to use on the remote host |
| `--git-remote-share MODE` | Value passed to `git init --shared=<MODE>` on the remote host |
| `--git-remote-name NAME` | Name of the git remote to register (default: `origin`) |
| `--ssh-command CMD` | ssh command to use |
| `--gh-command CMD` | `gh` (GitHub CLI) command to use |
| `--glab-command CMD` | `glab` (GitLab CLI) command to use |

```bash
# Create a local repo and push it to a new GitHub repository over SSH
mng_encase init_git \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-hosting github --git-remote-account my_git_account --git-protocol ssh

# Create a local repo and push it to a bare repository on a plain SSH host
mng_encase init_git \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-remote-account remote_account --git-remote-host remotehost.remotedomain \
  --git-remote-path '~/git_repositories/' --git-remote-share group --git-protocol ssh
```

---

## Author
    Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
    Nanigashi Uji (4423013-nanigashi_uji@users.noreply.gitlab.com)

    GitHub: https://github.com/nanigashi-uji/py-encase
    GitLab: https://gitlab.com/nanigashi_uji/py-encase
    PyPI:   https://pypi.org/project/py-encase/
