#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_py_encase.py: Python wrapper for py-encase
py-encase 用 Python ラッパースクリプト
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ======================================================================
# Configurable variables (edit this section)
# 設定セクション（ここを書き換えてカスタマイズしてください）
# ======================================================================

# Specify python & pip if necessary (full path or command name)
# 必要なら Python / pip のパスを明示指定（未指定なら自動検出）
PYTHON: Optional[str] = None
PIP: Optional[str] = None

# PY_MOD_VER: "py-encase" version to be used.
#   - Set a string to pin a specific version (e.g. "0.0.30")
#   - None / "" -> detect latest version via `pip index versions py-encase`
# PY_MOD_VER: 使用する py-encase のバージョン
#   - 文字列を設定するとそのバージョンを固定使用（例: "0.0.30"）
#   - None / "" -> `pip index versions py-encase` で最新版を自動検出
PY_MOD_VER: Optional[str] = None

# WORKTOP: Top directory of user working directory
# (Default: $WORKTOP or ~/Documents/workspace)
# WORKTOP: ユーザーワークトップディレクトリ
# （デフォルト: 環境変数 WORKTOP または ~/Documents/workspace）
WORKTOP: Optional[str] = None

# DEPOT: Location where "py-encase" directory will be created.
# (Default: $DEPOT or ${WORKTOP}/opr/depot)
# DEPOT: py-encase をインストールするベースディレクトリ
# （デフォルト: 環境変数 DEPOT または ${WORKTOP}/opr/depot）
DEPOT: Optional[str] = None

# PY_MOD_DEST:
#   - If set, use this directory as install location regardless of version.
#   - If not set, use ${DEPOT}/py-encase-${PY_MOD_VER or ""}.
# PY_MOD_DEST:
#   - 指定されていれば、バージョンに関係なくこのディレクトリを使用
#   - 未指定なら ${DEPOT}/py-encase-${PY_MOD_VER or ""} を使用
PY_MOD_DEST: Optional[str] = None

# Default repository type
# デフォルトのリポジトリ種別
REPO_TYPE_DEFAULT: str = "local"

# ----------------------------------------------------------------------
# Repository type definitions
# リポジトリ種別定義
#
# ここを編集すると、利用可能な repo_type とその挙動を
# データ駆動的にカスタマイズできます。
#
# Key: repo_type string used by -t option
# キー: -t オプションで指定する repo_type 名
#
# Known fields (典型的なキー):
#   description       : Shown in help text / ヘルプ表示用説明文
#   prefix_template   : Project root directory template
#                       利用可能プレースホルダ:
#                         {worktop}, {repo_type}, {user}, {proj},
#                         {account}, {git_remote_host}
#   use_gh_api        : If True, use `gh api user` to detect account
#                       True なら `gh api user` で GitHub アカウントを自動取得
#   use_glab_api      : If True, use `glab api user` to detect account
#                       True なら `glab api user` で GitLab アカウントを自動取得
#   Other keys        : copied into self.cfg[...] (readme, setup_git, etc.)
#                       その他のキーは self.cfg[...] にそのまま流し込まれる
# ----------------------------------------------------------------------
REPO_TYPES: Dict[str, Dict[str, object]] = {
    "local": {
        "description": (
            "Local git repo under {worktop}/git_workdirs/local/{user}/{proj}"
        ),
        "prefix_template": "{worktop}/git_workdirs/local/{user}/{proj}",
        "readme": True,
        "setup_git": True,
    },
    "selfhosted": {
        "description": (
            "Self-hosted git repo under "
            "{worktop}/git_workdirs/{git_remote_host}/{user}/{proj}"
        ),
        # git_remote_host is taken from cfg or from this spec.
        # git_remote_host は cfg かこの定義の値を利用（なければ repo_type 名）
        "prefix_template": "{worktop}/git_workdirs/{git_remote_host}/{user}/{proj}",
        "git_remote_host": "selfhosted",
        "readme": True,
        "setup_git": True,
    },
    "github": {
        "description": (
            "GitHub-hosted repo; account is taken from `gh api user`"
        ),
        "prefix_template": "{worktop}/git_workdirs/github/{account}/{proj}",
        "use_gh_api": True,           # gh でアカウント情報を取得
        "readme": True,
        "setup_git": True,
        "git_set_upstream": True,
        "git_remote_setup": True,
        "git_hosting": "github",
        "github_userinfo": True,
    },
    "gitlab": {
        "description": (
            "GitLab-hosted repo; account is taken from `glab api user`"
        ),
        "prefix_template": "{worktop}/git_workdirs/gitlab/{account}/{proj}",
        "use_glab_api": True,         # glab でアカウント情報を取得
        "readme": True,
        "setup_git": True,
        "git_set_upstream": True,
        "git_remote_setup": True,
        "git_hosting": "gitlab",
        "gitlab_userinfo": True,
    },
    # Example: custom Gitea server / 独自 Gitea サーバー用の例
    # "gitea": {
    #     "description": "My self-hosted Gitea / 自前の Gitea",
    #     "prefix_template": "{worktop}/git_workdirs/gitea/{user}/{proj}",
    #     "git_hosting": "gitea",
    #     "readme": True,
    #     "setup_git": True,
    #     "git_set_upstream": True,
    #     "git_remote_setup": True,
    # },
}

# ----------------------------------------------------------------------
# py-encase option defaults
# py-encase オプションのデフォルト値
#
# Boolean: False -> not passed, True -> "--option" is passed
#  真偽値: False -> オプション付与なし, True -> "--option" を付与
# String:  None/"" -> not passed, else "--option VALUE"
#  文字列: None/"" -> オプション付与なし, その他 -> "--option 値"
# ----------------------------------------------------------------------

# Common project / repository options
# 共通プロジェクト／リポジトリ関連オプション
prefix: Optional[str] = None          # init, add, addlib, addkv, newmodule
title: Optional[str] = None           # init, newmodule, update_readme
template: Optional[str] = None        # init, add, addlib, addkv, newmodule, update_readme, init_git, dump_template
app_framework: bool = False           # init, add
bare_script: bool = False             # init, add
gui_kvfile: Optional[str] = None      # init, add
readme: bool = False                  # init, add, addlib
required_module: bool = False         # init, add, addlib
script_lib: Optional[str] = None      # init, add
std_script_lib: bool = False          # init, add, addlib
setup_git: bool = False               # init
git_set_upstream: bool = False        # init, newmodule, init_git
git_remote_setup: bool = False        # init, newmodule, init_git
git_user_name: Optional[str] = None   # init, newmodule, init_git
git_user_email: Optional[str] = None  # init, newmodule, init_git

# Repo / module naming etc.
# リポジトリ／モジュール名など
module: Optional[str] = None          # init, add, newmodule
required_module_name: Optional[str] = None  # kept for compatibility / 互換性保持用

# Repository / remote configuration
# リポジトリ／リモート設定
git_repository_name: Optional[str] = None
git_hosting: Optional[str] = None
git_protocol: Optional[str] = None
git_remote_url: Optional[str] = None
git_remote_account: Optional[str] = None
git_remote_host: Optional[str] = None
git_remote_port: Optional[str] = None
git_remote_path: Optional[str] = None
git_remote_sshopts: Optional[str] = None
git_remote_cmd: Optional[str] = None
git_remote_share: Optional[str] = None
git_remote_name: Optional[str] = None
ssh_command: Optional[str] = None
gh_command: Optional[str] = None
glab_command: Optional[str] = None

# CLI tools for py-encase itself
# py-encase 本体の実行オプション
move: Optional[str] = None            # init
python_opt: Optional[str] = None      # init, add, addlib, newmodule (called "python" in the shell script)
pip_opt: bool = False                 # if True pass "--pip <pip_cmd>" / True なら "--pip <pip_cmd>" を付与
git_command: Optional[str] = None     # init, add, addlib, newmodule, init_git
verbose_flag: bool = False            # info, contents, init, add, addlib, addkv, newmodule, ...

# New-module specific options
# newmodule 用オプション
description: Optional[str] = None
module_website: Optional[str] = None
class_name: Optional[str] = None
keywords: Optional[str] = None
classifiers: Optional[str] = None
author_name: Optional[str] = None
author_email: Optional[str] = None
maintainer_name: Optional[str] = None
maintainer_email: Optional[str] = None
create_year: Optional[str] = None
no_readme: bool = False
no_git_file: bool = False
set_shebang: bool = False

# init_git
# init_git 用オプション
module_src: Optional[str] = None

# update_readme
# update_readme 用オプション
backup: bool = False

# dump_template
# dump_template 用オプション
output: Optional[str] = None

# info
# info 用オプション
long: bool = False
short: bool = False
version: bool = False
pip_module_name: bool = False
manage_script_name: bool = False
manage_option: bool = False

# contents
# contents 用オプション
all: bool = False   # noqa: A001  # shadowing built-in / 組み込み all との衝突を許容
bin_script: bool = False
lib_script: bool = False
modules_src: bool = False

# git host specific userinfo flags
# Git ホスティングサービス固有のユーザー情報フラグ
github_userinfo: bool = False
gitlab_userinfo: bool = False


# ======================================================================
# Implementation / 実装
# ======================================================================


class RunPyEncase:
    """
    Wrapper for py-encase with user defaults.
    ユーザーのデフォルト設定付きで py-encase を呼び出すラッパークラス。
    """

    def __init__(self) -> None:
        self.this = Path(__file__).resolve()
        self.py_module = "py-encase"
        self.py_mod_fn = self.py_module.replace("-", "_")

        # Environment / command resolution
        # 環境変数や自動検出によるコマンド決定
        self.pip_cmd = PIP or os.environ.get("PIP3") or os.environ.get("PIP") or "pip3"
        self.python_cmd = (
            PYTHON
            or os.environ.get("PYTHON3")
            or os.environ.get("PYTHON")
            or sys.executable
        )

        # Keep raw config value first (env has priority over file-level constant)
        # まずは「指定された値」をそのまま保持（環境変数がファイル先頭の設定より優先）
        self.py_mod_version_config: str = (
            os.environ.get("PY_MOD_VER") or (PY_MOD_VER or "") or ""
        )

        # Actual version will be decided by detect_py_mod_version()
        # 実際に使うバージョンは detect_py_mod_version() で決定する
        self.py_mod_version: Optional[str] = None

        # Working directories
        # 作業ディレクトリ関連
        self.worktop = (
            WORKTOP
            or os.environ.get("WORKTOP")
            or str(Path.home() / "Documents" / "workspace")
        )
        self.depot = (
            DEPOT
            or os.environ.get("DEPOT")
            or os.path.join(self.worktop, "opr", "depot")
        )

        # Will be set by detect_py_mod_version()
        # detect_py_mod_version() により設定される
        self.dest_py_mod: Optional[str] = None
        self.py_encase_runner: Optional[str] = None

        # script options (wrapper-level)
        # ラッパースクリプト自身のオプション
        self.repo_type_default = REPO_TYPE_DEFAULT
        self.s_dry_run: bool = False
        self.s_verbose: bool = False

        # runtime option values (start from configurable defaults)
        # 実行時オプション値（上の設定セクションをコピーして保持）
        self.cfg: Dict[str, object] = {
            # project / repository options / プロジェクト・リポジトリ関連
            "prefix": prefix,
            "title": title,
            "template": template,
            "app_framework": app_framework,
            "bare_script": bare_script,
            "gui_kvfile": gui_kvfile,
            "readme": readme,
            "required_module": required_module,
            "script_lib": script_lib,
            "std_script_lib": std_script_lib,
            "setup_git": setup_git,
            "git_set_upstream": git_set_upstream,
            "git_remote_setup": git_remote_setup,
            "git_user_name": git_user_name,
            "git_user_email": git_user_email,
            "module": module,
            "git_repository_name": git_repository_name,
            "git_hosting": git_hosting,
            "git_protocol": git_protocol,
            "git_remote_url": git_remote_url,
            "git_remote_account": git_remote_account,
            "git_remote_host": git_remote_host,
            "git_remote_port": git_remote_port,
            "git_remote_path": git_remote_path,
            "git_remote_sshopts": git_remote_sshopts,
            "git_remote_cmd": git_remote_cmd,
            "git_remote_share": git_remote_share,
            "git_remote_name": git_remote_name,
            "ssh_command": ssh_command,
            "gh_command": gh_command,
            "glab_command": glab_command,
            "move": move,
            "python_opt": python_opt,
            "pip_opt": pip_opt,
            "git_command": git_command,
            "verbose_flag": verbose_flag,
            "description": description,
            "module_website": module_website,
            "class_name": class_name,
            "keywords": keywords,
            "classifiers": classifiers,
            "author_name": author_name,
            "author_email": author_email,
            "maintainer_name": maintainer_name,
            "maintainer_email": maintainer_email,
            "create_year": create_year,
            "no_readme": no_readme,
            "no_git_file": no_git_file,
            "set_shebang": set_shebang,
            "module_src": module_src,
            "backup": backup,
            "output": output,
            "long": long,
            "short": short,
            "version": version,
            "pip_module_name": pip_module_name,
            "manage_script_name": manage_script_name,
            "manage_option": manage_option,
            "all": all,
            "bin_script": bin_script,
            "lib_script": lib_script,
            "modules_src": modules_src,
            "github_userinfo": github_userinfo,
            "gitlab_userinfo": gitlab_userinfo,
        }

    # ------------------------------------------------------------------
    # Utility helpers / ユーティリティ
    # ------------------------------------------------------------------
    def _debug(self, msg: str) -> None:
        """Print debug message when verbose is enabled.
        verbose 指定時のみデバッグメッセージを標準エラーに出力。
        """
        if self.s_verbose:
            print(f"[run_py_encase] {msg}", file=sys.stderr)

    @staticmethod
    def available_repo_types() -> List[str]:
        """Return list of available repo_type keys.
        利用可能な repo_type の一覧を返す。
        """
        return list(REPO_TYPES.keys())

    # ------------------------------------------------------------------
    # Repo type handling (data-driven via REPO_TYPES)
    # リポジトリ種別の処理（REPO_TYPES によるデータ駆動）
    # ------------------------------------------------------------------
    def repo_type_select(self, repo_type: str, projname: str) -> Tuple[str, int]:
        """
        Update self.cfg according to repo_type, based on REPO_TYPES.

        REPO_TYPES に基づき、指定された repo_type 用の設定を self.cfg に反映し、
        prefix などを生成する。

        Returns (normalized_repo_type, status) where status != 0 on error.
        戻り値: (正規化された repo_type, status)、status != 0 ならエラー。
        """
        status = 0

        spec = REPO_TYPES.get(repo_type)
        if spec is None:
            return "unknown", 1

        user = os.environ.get("USER") or ""
        account = user

        # Determine git_remote_host (from cfg, spec or repo_type)
        # git_remote_host の決定（cfg → spec → repo_type の順で採用）
        git_remote_host = (
            self.cfg.get("git_remote_host")
            or spec.get("git_remote_host")
            or repo_type
        )

        use_gh = bool(spec.get("use_gh_api"))
        use_glab = bool(spec.get("use_glab_api"))

        # Fetch GitHub or GitLab account if requested
        # GitHub / GitLab アカウント情報を必要に応じて取得
        if use_gh:
            env = os.environ.copy()
            env.setdefault("NO_COLOR", "1")
            env.setdefault("TERM", "dumb")
            gh_bin = os.environ.get("GH") or "gh"
            try:
                out = subprocess.check_output(
                    [gh_bin, "api", "user"],
                    env=env,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                data = json.loads(out)
                account = str(data.get("login") or "")
                github_id = str(data.get("id") or "")
                github_user_email = (
                    f"{github_id}+{account}@users.noreply.github.com"
                )
                # store into cfg (user can still override later)
                # cfg に格納（ユーザーが後から上書きしてもよい）
                self.cfg["git_user_name"] = account
                self.cfg["git_user_email"] = github_user_email
                self.cfg["git_remote_account"] = account
                self.cfg["author_email"] = github_user_email
                self.cfg["maintainer_name"] = account
                self.cfg["maintainer_email"] = github_user_email
            except Exception as exc:  # noqa: BLE001
                print(f"GH error: {exc}", file=sys.stderr)
                return "unknown", 1

        if use_glab:
            env = os.environ.copy()
            env.setdefault("NO_COLOR", "1")
            env.setdefault("TERM", "dumb")
            glab_bin = os.environ.get("GLAB") or "glab"
            try:
                out = subprocess.check_output(
                    [glab_bin, "api", "user"],
                    env=env,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                data = json.loads(out)
                account = str(data.get("username") or data.get("name") or "")
                gitlab_id = str(data.get("id") or "")
                glab_user_email = (
                    f"{gitlab_id}-{account}@users.noreply.gitlab.com"
                )
                self.cfg["git_user_name"] = account
                self.cfg["git_user_email"] = glab_user_email
                self.cfg["git_remote_account"] = account
                self.cfg["author_email"] = glab_user_email
                self.cfg["maintainer_name"] = account
                self.cfg["maintainer_email"] = glab_user_email
            except Exception as exc:  # noqa: BLE001
                print(f"GLab error: {exc}", file=sys.stderr)
                return "unknown", 1

        # Build prefix from template
        # テンプレートから prefix（プロジェクトルート）を生成
        tmpl = spec.get("prefix_template")
        if not tmpl:
            print(
                f"Error: REPO_TYPES[{repo_type!r}] has no prefix_template",
                file=sys.stderr,
            )
            return "unknown", 1

        prefix = str(
            tmpl.format(
                worktop=self.worktop,
                repo_type=repo_type,
                user=user,
                proj=projname,
                account=account,
                git_remote_host=git_remote_host,
            )
        )
        self.cfg["prefix"] = prefix

        # Copy remaining keys into cfg (except special keys)
        # 残りのキーを（特別扱いのものを除いて）cfg にコピー
        for key, value in spec.items():
            if key in {"description", "prefix_template", "use_gh_api", "use_glab_api"}:
                continue
            self.cfg[key] = value

        return repo_type, status

    # ------------------------------------------------------------------
    # Argument parsing / 引数解析
    # ------------------------------------------------------------------
    def parse_args(self, argv: List[str]) -> Tuple[argparse.Namespace, List[str]]:
        """
        Parse wrapper options and remaining args (for py-encase).
        ラッパー用オプションと、py-encase に渡す残りの引数を解析する。
        """
        parser = argparse.ArgumentParser(
            prog=self.this.name,
            add_help=False,
            description=(
                "Wrapper script to run py-encase with personal default "
                "configuration."
            ),
        )
        parser.add_argument(
            "-P",
            dest="proj_name",
            metavar="PROJECT",
            help="Repository / project name / プロジェクト名",
        )
        parser.add_argument(
            "-t",
            dest="repo_type",
            metavar="TYPE",
            default=self.repo_type_default,
            help=(
                "Repository type (default: {default}) / "
                "リポジトリ種別 (デフォルト: {default})"
            ).format(default=self.repo_type_default),
        )
        parser.add_argument(
            "-n",
            dest="dry_run",
            action="store_true",
            help="Dry-run mode for this script / このラッパーのみドライラン",
        )
        parser.add_argument(
            "-v",
            dest="verbose",
            action="store_true",
            help="Verbose message from this script / ラッパーの詳細ログ",
        )
        parser.add_argument(
            "-V",
            dest="verbose_py",
            action="store_true",
            help="Verbose message for py-encase / py-encase の --verbose を有効化",
        )
        parser.add_argument(
            "-H",
            dest="help_flag",
            action="store_true",
            help="Show help message / ヘルプメッセージを表示",
        )

        args, rest = parser.parse_known_args(argv)

        if args.help_flag:
            self.print_usage()
            sys.exit(0)

        if not rest:
            self.print_usage()
            sys.exit(1)

        # Reflect wrapper flags
        # ラッパー用フラグを反映
        self.s_dry_run = bool(args.dry_run)
        self.s_verbose = bool(args.verbose or args.verbose_py)
        if args.verbose_py:
            self.cfg["verbose_flag"] = True

        return args, rest

    def print_usage(self) -> None:
        """Print short usage including repo_type list.
        簡単な使い方と repo_type 一覧を表示。
        """
        print(
            f"[Usage] {self.this.name} [-t repo_type ] [-H] "
            "project_name       [py-encase options ... ]"
        )
        print(
            f"[Usage] {self.this.name} [-t repo_type ] [-P project_name ] "
            "[-H] [py-encase options ... ]"
        )
        print("[Options / オプション]")
        print("         -P proj_name : Repository name / プロジェクト名")
        print(
            f"         -t repo_type : Repository type (Default: {self.repo_type_default})"
        )
        print("         -n           : Dry-run mode for this script / ドライラン")
        print("         -v           : Verbose message from this script / ラッパー詳細ログ")
        print(
            "         -V           : Verbose message for py-encase / "
            "py-encase を verbose 実行"
        )
        print("         -H           : Show help message / このヘルプを表示")
        print("[Available Repository Type options / 使用可能なリポジトリ種別]")
        for name, spec in REPO_TYPES.items():
            desc = str(spec.get("description") or "")
            print(f"        {name:10s} : {desc}")

    # ------------------------------------------------------------------
    # py-encase version detection (PY_MOD_VER)
    # PY_MOD_VER の検出
    # ------------------------------------------------------------------
    def detect_py_mod_version(self) -> None:
        """
        Decide self.py_mod_version and set dest_py_mod / py_encase_runner.

        self.py_mod_version を決定し、それに基づいて
        self.dest_py_mod, self.py_encase_runner を設定する。

        Priority / 優先順位:
            1. Environment variable PY_MOD_VER
            2. File-level constant PY_MOD_VER
            3. Detect latest via `pip index versions py-encase`
            4. On failure, use empty version (no suffix directory name)
               失敗した場合はバージョンなし（ディレクトリ名にサフィックスなし）
        """
        if self.py_mod_version is not None:
            # Already decided / 既に決定済み
            return

        cfg = (self.py_mod_version_config or "").strip()
        if cfg:
            self.py_mod_version = cfg
        else:
            # Auto-detect latest version via pip index
            # pip index で最新版を自動検出
            try:
                out = subprocess.check_output(
                    [self.pip_cmd, "index", "versions", self.py_module],
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                first_line = ""
                for line in out.splitlines():
                    if line.strip():
                        first_line = line.strip()
                        break

                # Typical format: "py-encase (0.0.30)"
                # 典型フォーマット: "py-encase (0.0.30)"
                m = re.match(r"^[^\s]+\s*\(([\d\.]+)\)", first_line)
                if m:
                    self.py_mod_version = m.group(1)
                else:
                    # If parsing fails, fall back to no explicit version
                    # 解析失敗時はバージョン指定なし扱い
                    self.py_mod_version = ""
            except Exception as exc:  # noqa: BLE001
                self._debug(f"Failed to detect version via pip index: {exc}")
                self.py_mod_version = ""

        # Decide install destination directory
        # インストール先ディレクトリの決定
        env_dest = os.environ.get("PY_MOD_DEST")
        if PY_MOD_DEST or env_dest:
            self.dest_py_mod = PY_MOD_DEST or env_dest
        else:
            py_mod_spath = self.py_module + (
                f"-{self.py_mod_version}" if self.py_mod_version else ""
            )
            self.dest_py_mod = os.path.join(self.depot, py_mod_spath)

        self.py_encase_runner = os.path.join(self.dest_py_mod, "bin", self.py_mod_fn)
        self._debug(
            f"py-encase version={self.py_mod_version!r}, "
            f"dest_py_mod={self.dest_py_mod}"
        )

    # ------------------------------------------------------------------
    # py-encase installation / py-encase のインストール
    # ------------------------------------------------------------------
    def ensure_py_encase_installed(self) -> None:
        """
        Ensure that py-encase is installed into self.dest_py_mod.

        self.dest_py_mod に py-encase がインストールされていることを保証する。
        """
        if not self.dest_py_mod or not self.py_encase_runner:
            raise RuntimeError(
                "detect_py_mod_version() must be called before "
                "ensure_py_encase_installed()."
            )

        dest = Path(self.dest_py_mod)
        runner = Path(self.py_encase_runner)

        if dest.is_dir():
            self._debug(f"Using existing py-encase at {dest}")
            return

        if not self.py_mod_version and runner.exists():
            # When version is empty and runner already exists, respect it.
            # バージョン指定なし & runner が既に存在する場合は再インストールしない
            self._debug(f"Existing runner found at {runner}, not reinstalling.")
            return

        self._debug(f"Installing {self.py_module} into {dest} using {self.pip_cmd}")
        if self.s_dry_run:
            # Dry-run: only show message, no install.
            # ドライラン時はメッセージのみでインストールしない
            return

        dest.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.pip_cmd,
            "install",
            "--upgrade",
            "--target",
            str(dest),
        ]
        if self.py_mod_version:
            cmd.append(f"{self.py_module}=={self.py_mod_version}")
        else:
            cmd.append(self.py_module)

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            print(f"Can not install : {self.py_module}", file=sys.stderr)
            sys.exit(1)

    # ------------------------------------------------------------------
    # runner selection / 実行ファイルの選択
    # ------------------------------------------------------------------
    def select_runner(
        self, py_sbcmd: str, prefix: Optional[str]
    ) -> Tuple[str, List[str], bool]:
        """
        Decide which executable to use and whether to set PYTHONPATH.

        どの実行ファイルを使うか、PYTHONPATH を設定するかを決定する。

        Returns (runner_path, manage_opts_list, flg_no_env)
        戻り値 (runner_path, manage_opts_list, flg_no_env)
        """
        runner = self.py_encase_runner or ""
        manage_opts: List[str] = []
        flg_no_env = False

        prefix_path = Path(prefix) if prefix else None

        if py_sbcmd == "init":
            # For "init" always use the module in dest_py_mod with --manage
            # init のときは常にインストール先の manage 実行を使う
            manage_opts = ["--manage"]
            flg_no_env = False
        elif prefix_path and (prefix_path / "bin" / "mng_encase").is_file():
            # If project already has mng_encase, use it without PYTHONPATH
            # プロジェクトに mng_encase があれば、それを PYTHONPATH なしで起動
            runner = str(prefix_path / "bin" / "mng_encase")
            manage_opts = []
            flg_no_env = True
        elif prefix_path and (prefix_path / "bin" / f"{self.py_mod_fn}.py").is_file():
            # If project has py_encase.py, use it with --manage, no PYTHONPATH
            # プロジェクトに py_encase.py があれば、それを --manage 付きで使用
            runner = str(prefix_path / "bin" / f"{self.py_mod_fn}.py")
            manage_opts = ["--manage"]
            flg_no_env = True

        return runner, manage_opts, flg_no_env

    # ------------------------------------------------------------------
    # def_opts construction / デフォルトオプションの構築
    # ------------------------------------------------------------------
    def _add_flag(self, args: List[str], cfg_key: str, flag: str) -> None:
        """Append flag if cfg[cfg_key] is truthy.
        cfg[cfg_key] が真ならフラグを追加。
        """
        if self.cfg.get(cfg_key):
            args.append(flag)

    def _add_value(
        self,
        args: List[str],
        cfg_key: str,
        flag: str,
        value_override: Optional[str] = None,
    ) -> None:
        """Append flag + value if value is non-empty.
        値が空でなければ、フラグと共に追加。
        """
        val = value_override if value_override is not None else self.cfg.get(cfg_key)
        if val not in (None, "", False):
            args.extend([flag, str(val)])

    def build_def_opts(self, py_sbcmd: str) -> List[str]:
        """
        Build default option list for a given py-encase subcommand.

        サブコマンド py_sbcmd に応じたデフォルトオプションリストを生成。
        """
        args: List[str] = []

        if py_sbcmd == "info":
            self._add_flag(args, "verbose_flag", "--verbose")
            self._add_flag(args, "long", "--long")
            self._add_flag(args, "short", "--short")
            self._add_flag(args, "version", "--version")
            self._add_flag(args, "pip_module_name", "--pip-module-name")
            self._add_flag(args, "manage_script_name", "--manage-script-name")
            self._add_flag(args, "manage_option", "--manage-option")
        elif py_sbcmd == "contents":
            self._add_flag(args, "verbose_flag", "--verbose")
            self._add_flag(args, "all", "--all")
            self._add_flag(args, "bin_script", "--bin-script")
            self._add_flag(args, "lib_script", "--lib-script")
            self._add_flag(args, "modules_src", "--modules-src")
        elif py_sbcmd == "init":
            self._add_value(args, "prefix", "--prefix")
            self._add_value(args, "title", "--title")
            self._add_value(args, "template", "--template")
            self._add_flag(args, "app_framework", "--app-framework")
            self._add_flag(args, "bare_script", "--bare-script")
            self._add_value(args, "gui_kvfile", "--gui-kvfile")
            self._add_flag(args, "readme", "--readme")
            self._add_value(args, "module", "--module")
            self._add_flag(args, "required_module", "--required-module")
            self._add_value(args, "script_lib", "--script-lib")
            self._add_flag(args, "std_script_lib", "--std-script-lib")
            self._add_flag(args, "setup_git", "--setup-git")
            self._add_flag(args, "git_set_upstream", "--git-set-upstream")
            self._add_flag(args, "git_remote_setup", "--git-remote-setup")
            self._add_value(args, "git_user_name", "--git-user-name")
            self._add_value(args, "git_user_email", "--git-user-email")
            self._add_flag(args, "github_userinfo", "--github-userinfo")
            self._add_flag(args, "gitlab_userinfo", "--gitlab_userinfo")
            self._add_value(args, "git_repository_name", "--git-repository-name")
            self._add_value(args, "git_hosting", "--git-hosting")
            self._add_value(args, "git_protocol", "--git-protocol")
            self._add_value(args, "git_remote_url", "--git-remote-url")
            self._add_value(args, "git_remote_account", "--git-remote-account")
            self._add_value(args, "git_remote_host", "--git-remote-host")
            self._add_value(args, "git_remote_port", "--git-remote-port")
            self._add_value(args, "git_remote_path", "--git-remote-path")
            self._add_value(args, "git_remote_sshopts", "--git-remote-sshopts")
            self._add_value(args, "git_remote_cmd", "--git-remote-cmd")
            self._add_value(args, "git_remote_share", "--git-remote-share")
            self._add_value(args, "git_remote_name", "--git-remote-name")
            self._add_value(args, "ssh_command", "--ssh-command")
            self._add_value(args, "gh_command", "--gh-command")
            self._add_value(args, "glab_command", "--glab-command")
            self._add_flag(args, "set_shebang", "--set-shebang")
            # In the shell script these are "python" / "pip" variables.
            # シェル版の "python" / "pip" 変数に相当
            if self.cfg.get("python_opt"):
                args.extend(["--python", str(self.cfg["python_opt"])])
            if self.cfg.get("pip_opt"):
                args.extend(["--pip", self.pip_cmd])
            self._add_value(args, "git_command", "--git-command")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "add":
            self._add_value(args, "prefix", "--prefix")
            self._add_value(args, "module", "--module")
            self._add_value(args, "title", "--title")
            self._add_value(args, "template", "--template")
            self._add_flag(args, "app_framework", "--app-framework")
            self._add_flag(args, "bare_script", "--bare-script")
            self._add_value(args, "gui_kvfile", "--gui-kvfile")
            self._add_flag(args, "readme", "--readme")
            self._add_flag(args, "required_module", "--required-module")
            self._add_value(args, "script_lib", "--script-lib")
            self._add_flag(args, "std_script_lib", "--std-script-lib")
            if self.cfg.get("python_opt"):
                args.extend(["--python", str(self.cfg["python_opt"])])
            if self.cfg.get("pip_opt"):
                args.extend(["--pip", self.pip_cmd])
            self._add_value(args, "git_command", "--git-command")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "addlib":
            self._add_value(args, "prefix", "--prefix")
            self._add_value(args, "module", "--module")
            self._add_value(args, "template", "--template")
            self._add_flag(args, "readme", "--readme")
            self._add_flag(args, "required_module", "--required-module")
            self._add_flag(args, "std_script_lib", "--std-script-lib")
            if self.cfg.get("python_opt"):
                args.extend(["--python", str(self.cfg["python_opt"])])
            if self.cfg.get("pip_opt"):
                args.extend(["--pip", self.pip_cmd])
            self._add_value(args, "git_command", "--git-command")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "addkv":
            self._add_value(args, "prefix", "--prefix")
            self._add_value(args, "template", "--template")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "newmodule":
            self._add_value(args, "prefix", "--prefix")
            self._add_value(args, "title", "--title")
            self._add_value(args, "description", "--description")
            self._add_value(args, "template", "--template")
            self._add_value(args, "module_website", "--module-website")
            self._add_value(args, "class_name", "--class-name")
            self._add_value(args, "module", "--module")
            self._add_value(args, "keywords", "--keywords")
            self._add_value(args, "classifiers", "--classifiers")
            self._add_value(args, "author_name", "--author-name")
            self._add_value(args, "author_email", "--author-email")
            self._add_value(args, "maintainer_name", "--maintainer-name")
            self._add_value(args, "maintainer_email", "--maintainer-email")
            self._add_value(args, "create_year", "--create-year")
            self._add_flag(args, "no_readme", "--no-readme")
            self._add_flag(args, "no_git_file", "--no-git-file")
            self._add_flag(args, "set_shebang", "--set-shebang")
            self._add_flag(args, "github_userinfo", "--github-userinfo")
            self._add_flag(args, "gitlab_userinfo", "--gitlab-userinfo")
            self._add_flag(args, "git_set_upstream", "--git-set-upstream")
            self._add_flag(args, "git_remote_setup", "--git-remote-setup")
            self._add_value(args, "git_user_name", "--git-user-name")
            self._add_value(args, "git_user_email", "--git-user-email")
            self._add_value(args, "git_repository_name", "--git-repository-name")
            self._add_value(args, "git_hosting", "--git-hosting")
            self._add_value(args, "git_protocol", "--git-protocol")
            self._add_value(args, "git_remote_url", "--git-remote-url")
            self._add_value(args, "git_remote_account", "--git-remote-account")
            self._add_value(args, "git_remote_host", "--git-remote-host")
            self._add_value(args, "git_remote_port", "--git-remote-port")
            self._add_value(args, "git_remote_path", "--git-remote-path")
            self._add_value(args, "git_remote_sshopts", "--git-remote-sshopts")
            self._add_value(args, "git_remote_cmd", "--git-remote-cmd")
            self._add_value(args, "git_remote_share", "--git-remote-share")
            self._add_value(args, "git_remote_name", "--git-remote-name")
            self._add_value(args, "ssh_command", "--ssh-command")
            self._add_value(args, "gh_command", "--gh-command")
            self._add_value(args, "glab_command", "--glab-command")
            self._add_flag(args, "set_shebang", "--set-shebang")
            if self.cfg.get("python_opt"):
                args.extend(["--python", str(self.cfg["python_opt"])])
            if self.cfg.get("pip_opt"):
                args.extend(["--pip", self.pip_cmd])
            self._add_value(args, "git_command", "--git-command")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "update_readme":
            self._add_value(args, "title", "--title")
            self._add_value(args, "template", "--template")
            self._add_flag(args, "backup", "--backup")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "init_git":
            self._add_value(args, "module_src", "--module-src")
            self._add_flag(args, "git_set_upstream", "--git-set-upstream")
            self._add_flag(args, "git_remote_setup", "--git-remote-setup")
            self._add_value(args, "git_user_name", "--git-user-name")
            self._add_value(args, "git_user_email", "--git-user-email")
            self._add_flag(args, "github_userinfo", "--github-userinfo")
            self._add_flag(args, "gitlab_userinfo", "--gitlab-userinfo")
            self._add_value(args, "git_repository_name", "--git-repository-name")
            self._add_value(args, "git_hosting", "--git-hosting")
            self._add_value(args, "git_protocol", "--git-protocol")
            self._add_value(args, "git_remote_url", "--git-remote-url")
            self._add_value(args, "git_remote_account", "--git-remote-account")
            self._add_value(args, "git_remote_host", "--git-remote-host")
            self._add_value(args, "git_remote_port", "--git-remote-port")
            self._add_value(args, "git_remote_path", "--git-remote-path")
            self._add_value(args, "git_remote_sshopts", "--git-remote-sshopts")
            self._add_value(args, "git_remote_cmd", "--git-remote-cmd")
            self._add_value(args, "git_remote_share", "--git-remote-share")
            self._add_value(args, "git_remote_name", "--git-remote-name")
            self._add_value(args, "ssh_command", "--ssh-command")
            self._add_value(args, "gh_command", "--gh-command")
            self._add_value(args, "glab_command", "--glab-command")
            self._add_value(args, "git_command", "--git-command")
            self._add_value(args, "template", "--template")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd == "dump_template":
            self._add_value(args, "output", "--output")
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd in ("clean", "distclean", "selfupdate"):
            self._add_flag(args, "verbose_flag", "--verbose")
        elif py_sbcmd in (
            "install",
            "download",
            "freeze",
            "inspect",
            "list",
            "cache",
            "piphelp",
        ):
            # No default options for these subcommands
            # これらのサブコマンドにはデフォルトオプションなし
            pass

        return args

    # ------------------------------------------------------------------
    # Main entry / エントリポイント
    # ------------------------------------------------------------------
    def main(self, argv: Optional[List[str]] = None) -> None:
        """
        Main entry point. Equivalent to the shell wrapper behavior.

        シェル版ラッパーと同等の振る舞いをするメインエントリポイント。
        """
        if argv is None:
            argv = sys.argv[1:]

        args, rest = self.parse_args(argv)

        # Determine project name and py-encase subcommand.
        # プロジェクト名と py-encase サブコマンドを決定
        proj_name = args.proj_name
        py_sbcmd = ""
        extra_for_py_encase: List[str] = []

        known_sbcmds = {
            "info",
            "contents",
            "init",
            "add",
            "addlib",
            "addkv",
            "newmodule",
            "update_readme",
            "init_git",
            "dump_template",
            "clean",
            "distclean",
            "selfupdate",
            "install",
            "download",
            "freeze",
            "inspect",
            "list",
            "cache",
            "piphelp",
        }

        first = rest[0]
        remain = rest[1:]

        if first in known_sbcmds:
            # Pattern: run_py_encase.py [-P proj] subcmd [args...]
            # 形式: run_py_encase.py [-P proj] subcmd [args...]
            if not proj_name:
                self.print_usage()
                print("Error : Project name is not specified", file=sys.stderr)
                sys.exit(1)
            py_sbcmd = first
            extra_for_py_encase = remain
        else:
            # Pattern A: proj_name given by -P, then first is subcmd
            # パターンA: -P で proj_name 指定済み、first が subcmd
            # Pattern B: first is proj_name, remain[0] is subcmd
            # パターンB: first が proj_name, remain[0] が subcmd
            if not proj_name:
                proj_name = first
                if remain:
                    py_sbcmd = remain[0]
                    extra_for_py_encase = remain[1:]
            else:
                py_sbcmd = first
                extra_for_py_encase = remain

        if not py_sbcmd and self.s_verbose:
            print(
                "No known sub-command of py-encase is specified.",
                "py-encase の既知サブコマンドが指定されていません。",
                file=sys.stderr,
            )

        if proj_name is None:
            self.print_usage()
            print("Error : Project name is not specified", file=sys.stderr)
            sys.exit(1)

        # Adjust configuration by repo_type
        # repo_type に応じて設定を反映
        repo_type = args.repo_type or self.repo_type_default
        repo_type, status = self.repo_type_select(repo_type, proj_name)
        if status != 0:
            print(
                f"Error: unknown or unsupported repo_type '{repo_type}'",
                file=sys.stderr,
            )
            sys.exit(status)

        prefix_val = self.cfg.get("prefix")
        self._debug(f"repo_type={repo_type}, prefix={prefix_val}")

        # Decide py-encase version and install destination
        # py-encase のバージョンとインストール先を決定
        self.detect_py_mod_version()

        # Ensure py-encase installation
        # py-encase のインストール確認
        self.ensure_py_encase_installed()

        # Choose runner and manage option
        # 実行ファイルと manage オプションの選択
        runner, manage_opts, flg_no_env = self.select_runner(
            py_sbcmd, str(prefix_val) if prefix_val else None
        )

        # Build default options according to subcommand
        # サブコマンドに応じてデフォルトオプションを構築
        def_opts = self.build_def_opts(py_sbcmd)

        # Compose full command
        # 実際に実行するコマンド列を生成
        cmd: List[str] = [runner]
        cmd.extend(manage_opts)
        if py_sbcmd:
            cmd.append(py_sbcmd)
        cmd.extend(def_opts)
        cmd.extend(extra_for_py_encase)

        env = os.environ.copy()
        if not flg_no_env:
            old_ppath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = str(self.dest_py_mod) + (
                os.pathsep + old_ppath if old_ppath else ""
            )

        # Dry-run / verbose echo
        # ドライラン／詳細表示時にコマンドを表示
        if self.s_dry_run or self.s_verbose:
            if not flg_no_env:
                print(
                    "env",
                    f'PYTHONPATH="{self.dest_py_mod}{os.pathsep}$PYTHONPATH"',
                    *cmd,
                )
            else:
                print(*cmd)

        # Actual execution
        # 実際のコマンド実行
        if not self.s_dry_run:
            try:
                subprocess.check_call(cmd, env=env)
            except FileNotFoundError:
                print(f"Can not execute : {runner}", file=sys.stderr)
                sys.exit(1)
            except subprocess.CalledProcessError as exc:
                sys.exit(exc.returncode)


if __name__ == "__main__":
    RunPyEncase().main()
