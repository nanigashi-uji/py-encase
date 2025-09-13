# py-encase

[![PyPI version](https://img.shields.io/pypi/v/py-encase?logo=pypi)](https://pypi.org/project/py-encase/)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-encase?logo=python)](https://pypi.org/project/py-encase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/py-encase)](https://pepy.tech/project/py-encase)

**py-encase** is a utility to set up a **portable Python script environment** quickly and consistently.  
It automates repetitive tasks often required in script development, such as creating directory structures, generating script templates, managing libraries, installing dependencies locally, and initializing Git repositories.

---

## Features

- Create portable script environments under a given prefix
- Generate script templates and reusable library modules
- Manage dependencies locally (no need for system-wide pip installs)
- Initialize Git repositories with remote setup support
- Keep documentation (`README.md`) updated automatically
- Support both **script-based tools** and **package/module development**

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

  - Python >= 3.9
  - pip3

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

The entity of this tool will be copied to `${prefix}/py_encase.py`
New script is created as `lib/python/newscript.py`. 

The symbolic link under `bin/` (=`bin/newscript`) is run
`lib/python/newscript.py` by dealing with environmental variable
`PYTHONPATH` to use python modules that are locally installed by pip
under `lib/python/site-packages`.

```
% ${prefix}/bin/newscript -d
Hello, World! It is "Wed Jul  2 16:26:06 2025."
Python : 3.13.4 ({somewhere}/bin/python3.13)
1  : ${prefix}/lib/python
2  : ${prefix}/lib/python/site-packages/3.13.4
3  : ....
```

Another symbolic link `bin/mng_encase` can be used to make another
python script and symbolic link for execution from template.

```
% ${prefix}/bin/mng_encase add another_script_can_be_run.py
```

another python script for library/module from template also can be created.

```
% ${prefix}bin/mng_encase addlib another_script_can_be_run.py
```

It is also possible to install module by `pip` locally under
'${prefix}/lib/python/site-packages'.

```
% ${prefix}bin/mng_encase install modulename1 modulename2 ....
```

The moduled installed locally by this tool can be deleted by
sub-commands `clean` or `distclean`

```
# Removing module installed locally by currently used python/pip version
% ${prefix}bin/mng_encase clean
# Removing all module installed locally by pip
% ${prefix}bin/mng_encase distclean
```

## Subcommands

### `init`
- Bootstraps a new execution environment under a given prefix.
- Includes directory structure, template script, `bin/` launcher, README, Git initialization.
- Options: `--readme`, `--title`, `--app-framework`, `--required-module`.

### `add`
- Adds a new script to an existing environment.
- Generates from template and symlinks into `bin/` for execution.

### `addlib`
- Adds a one-file library module.
- For factoring out utilities shared across scripts.

### `newmodule`
- Creates a package-structured Python module (source, tests, docs).
- Suitable for distributing reusable modules.

### `install`, `download`, `freeze`, `inspect`, `list`, `cache`, `piphelp`
- Wrappers for pip commands.
- Manage local installs, caches, dependency locking, inspection.

### `clean`, `distclean`
- `clean`: remove installed modules/caches for the current Python/pip version.
- `distclean`: more thorough cleanup.

### `selfupdate`
- Updates py-encase to the latest version from PyPI.

### `update_readme`
- Updates `README.md` with project structure and file listings.

### `init_git`
- Initializes a Git repository with `.gitignore`, `.gitkeep`, user/remote setup.

### `contents`
- Lists scripts, libraries, modules, installed packages in the environment.

### `info`
- Shows environment info: versions, paths, directory layout, symlinks.

---

## Author
    Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
    Nanigashi Uji (4423013-nanigashi_uji@users.noreply.gitlab.com)
