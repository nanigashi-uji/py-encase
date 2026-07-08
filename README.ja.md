# py-encase

[![PyPI version](https://img.shields.io/pypi/v/py-encase?logo=pypi)](https://pypi.org/project/py-encase/)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-encase?logo=python)](https://pypi.org/project/py-encase/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/py-encase)](https://pepy.tech/project/py-encase)

**py-encase** は、**可搬性のあるPythonスクリプト実行環境**を素早く一貫した手順で構築するためのユーティリティです。
ディレクトリ構造の作成、スクリプトテンプレートの生成、ライブラリの管理、依存パッケージのローカルインストール、Gitリポジトリの初期化など、スクリプト開発でありがちな定型作業を自動化します。

このツール全体は単一の自己完結スクリプト(`py_encase.py`)で構成されています。作業ツリーにコピーされると、このファイル1つが同時に2つの役割を担います。

- **ランナー(実行役)** — スクリプト名にちなんだシンボリックリンク(例: `bin/my_tool`)経由で呼び出されると、`PYTHONPATH` を透過的に設定した上で `lib/python/` 以下の対応するライブラリファイルを実行します。
- **マネージャ(管理役)**(`bin/mng_encase`) — 同じファイルが別名のシンボリックリンク経由(または `--manage` フラグ付き)で呼び出されると、環境を構築・保守するための一連のサブコマンド(`init`, `add`, `install`, `clean` など)を提供します。

---

## 特徴

- 指定したプレフィックス配下に可搬性のあるスクリプト実行環境を作成
- スクリプトテンプレートや再利用可能なライブラリモジュールを生成
- 依存パッケージをローカルに管理(システム全体へのpipインストール不要)
- スクリプト内の外部importを自動検出し、pipパッケージ名に変換
- Gitリポジトリを初期化し、リモート設定(GitHub / GitLab / 汎用SSHホスト)にも対応
- `README.md` を自動的に最新化
- スクリプト単体の開発とパッケージ/モジュール開発の両方をサポート
- 設定ファイル(TOML / JSON / INI)からデフォルトオプションを読み込み可能

---

## インストール

```bash
pip install py-encase
```

あるいは、ローカルのサンドボックスディレクトリにインストール:

```bash
pip install --target ./py_sandbox py-encase
```

---

## 動作要件

- Python >= 3.9(TOML形式の設定ファイルを使う場合はPython >= 3.11が必要)
- pip3
- `git`(`init_git` サブコマンドや `--setup-git` 関連機能を使う場合のみ必要)

---

## 使用例

### 新しいツールセットを作成する

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

### エンケース環境内でスクリプトを実行する

py-encase の最も重要な特徴の一つは、スクリプトを実行する際に `PYTHONPATH` などの環境変数を手動で設定する必要がないことです。

py-encase で新しいスクリプトを作成すると、そのスクリプトのベース名と同じ名前のシンボリックリンクが `bin/` ディレクトリ以下に作成されます。
例えば `my_new_work_tool.py` という名前のスクリプトを作成すると、次のような構成になります。

```
my-new-tools/
├── bin/
│   ├── mng_encase
│   └── my_new_work_tool   -> py_encase.py へのシンボリックリンク
├── lib/
│   └── python/
│       └── my_new_work_tool.py
```

スクリプトの実行は、単に次のように呼び出すだけです。

```bash
./bin/my_new_work_tool
```

このシンボリックリンクは自動的に `py_encase.py` を指しており、`py_encase.py` が実行前に内部で適切な環境変数を設定します。
これにより、手動で環境変数をエクスポートしなくても、エンケースされた環境内でスクリプトが実行されることが保証されます。

この仕組みによって、py-encase環境は自己完結的かつ可搬性が高く、実行が容易なものになっています。

---

### スクリプトやライブラリを追加する

```bash
"${workdir}/my-new-tools/bin/mng_encase" add -v another_tool
"${workdir}/my-new-tools/bin/mng_encase" addlib -v util_helpers
```

### モジュール開発を開始する

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

### 環境変数による設定

| 変数 | 用途 |
|------|------|
| `GIT_REMOTE_USER` | リモートgitアカウントのユーザー名 |
| `GIT_REMOTE_HOST` | リモートgitホスト名 |
| `GIT_REMOTE_PATH` | リモートgitリポジトリのパス |
| `GIT` | `-G/--git-command` が指定されなかった場合に使用される `git` コマンド/パス |
| `PY_ENCASE_TEMPLATE` | `-D/--template` を受け付けるサブコマンドで使用されるテンプレートファイルを上書き |
| `XDG_CONFIG_HOME` | デフォルト設定ファイルの検索先ディレクトリ(未設定時は `~/.config`) |

### 設定ファイル

マネージモードでは、サブコマンドのオプションを解析する前に、以下のデフォルト設定ファイルを探索します。

```
${XDG_CONFIG_HOME:-~/.config}/py-encase/py-encase_config.{toml,json,ini}
```

まずTOML(Python 3.11以上のみ)、次にJSON、次にINIの順で試されます。`DEFAULT` セクション(またはテーブル)のキーは常に適用され、さらに `--config-type <name>` で選択した名前付きセクションがその上に重ねて適用されます。これにより、1つの設定ファイルの中に複数のプリセット(例: `[github]` / `[gitlab]`)を保持し、実行時に選択して使うことができます。

| オプション | 用途 |
|-----------|------|
| `--config-file <path>` | デフォルトの設定ファイルに加えて、追加の設定ファイルを読み込む |
| `--config-type <name>` | 設定ファイル中の名前付きセクション/テーブルを選択して適用する |
| `--no-config-read` | デフォルトの設定ファイルを一切読み込まない |
| `--config-help` | 設定ファイルの仕組みに関するヘルプを表示する |

---

## ステップバイステップの使い方

1. 指定したディレクトリ("${prefix}")以下に作業環境を初期化し、テンプレートから新しいPythonスクリプト 'newscript.py' を作成しつつ、CLIで指定したPythonモジュールをインストールする。

```
# 環境を作成
% py_encase --manage init -r -g -v --prefix=${prefix} -m pytz -m tzlocal newscript.py
.....
# 生成されたファイルを確認
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

このツール自体の実体は `${prefix}/py_encase.py` にコピーされます。
新しいスクリプトは `lib/python/newscript.py` として作成されます。

`bin/` 以下のシンボリックリンク(=`bin/newscript`)は、環境変数 `PYTHONPATH` を適切に扱いながら `lib/python/newscript.py` を実行し、`lib/python/site-packages` 以下にローカルインストールされたPythonモジュールを利用できるようにします。

```
% ${prefix}/bin/newscript -d
Hello, World! It is "Wed Jul  2 16:26:06 2025."
Python : 3.13.4 ({somewhere}/bin/python3.13)
1  : ${prefix}/lib/python
2  : ${prefix}/lib/python/site-packages/3.13.4
3  : ....
```

`bin/mng_encase` という別のシンボリックリンクを使うと、テンプレートから別のPythonスクリプトとその実行用シンボリックリンクを作成できます。

```
% ${prefix}/bin/mng_encase add another_script_can_be_run.py
```

同様に、テンプレートからライブラリ/モジュール用のPythonスクリプトを作成することもできます。

```
% ${prefix}bin/mng_encase addlib another_script_can_be_run.py
```

`pip` を使ってモジュールを `${prefix}/lib/python/site-packages` 以下にローカルインストールすることも可能です。

```
% ${prefix}bin/mng_encase install modulename1 modulename2 ....
```

このツールによってローカルにインストールされたモジュールは、サブコマンド `clean` または `distclean` で削除できます。

```
# 現在使用中のpython/pipバージョン用にローカルインストールされたモジュールを削除
% ${prefix}bin/mng_encase clean
# pipによってローカルインストールされた全モジュールを削除(全pythonバージョン分)
% ${prefix}bin/mng_encase distclean
```

---

## 2つの起動モード

`py_encase.py` は、どのように呼び出されるかによって動作が異なります。

- **スクリプト(ランナー)モード** — `mng_encase` 以外の名前のシンボリックリンク経由(例: `bin/newscript`)、または `--manage` を付けずに呼び出された場合、py-encase は `PYTHONPATH` にエンケースされた `lib/python` と `lib/python/site-packages/<pyver>` を追加した上で、対象スクリプト(`lib/python/<name>.py`)を残りのCLI引数をそのまま渡して `exec` します。
- **マネージモード** — `mng_encase` として呼び出された場合(または実体ファイル `py_encase.py` を直接呼び出す際に `--manage` を付けた場合)、引数リストは以下で説明するいずれかのサブコマンドとして解析されます。

```bash
# スクリプトモード: lib/python/newscript.py を実行する
./bin/newscript --some-script-option

# マネージモード: 環境自体を管理する
./bin/mng_encase <subcommand> [options]
# 実体ファイルを直接呼び出す場合の等価な書き方:
./bin/py_encase.py --manage <subcommand> [options]
```

---

## マネージモード共通オプション

以下のオプションはサブコマンド名より前に解析され、マネージモード全体に対して適用されます。

| オプション | 説明 |
|-----------|------|
| `-p, --prefix PATH` | 操作対象とするディレクトリツリーのプレフィックス。デフォルト: 起動されたスクリプトの親ディレクトリ名が `bin` であればその祖父母ディレクトリ、そうでなければカレントディレクトリ |
| `-P, --python PATH` | 使用するPythonインタプリタのパス/コマンド |
| `-I, --pip PATH` | 使用するpipコマンド/パス |
| `-G, --git-command PATH` | 使用するgitコマンド/パス |
| `-v, --verbose` | 詳細出力 |
| `-n, --dry-run` | ドライランモード(ファイルシステム/ネットワークへの変更を行わない) |
| `--manage-help` | マネージモードのオプションに関するヘルプを表示 |
| `-h, --help` | ヘルプを表示(引数なしの `help` サブコマンドと等価) |
| `--config-file PATH` | 追加で読み込む設定ファイル |
| `--config-type NAME` | 設定ファイル中で適用する名前付きセクション |
| `--no-config-read` | デフォルトの設定ファイルを読み込まない |
| `--config-help` | 設定ファイルの仕組みに関するヘルプを表示 |

以下の各サブコマンドのオプションの多く(`-p/--prefix`, `-P/--python`, `-I/--pip`, `-G/--git-command`, `-v/--verbose`, `-n/--dry-run`)は、この共通オプションをサブコマンドレベルでも受け付けられるように繰り返し定義したものです。サブコマンド名の**後**に指定することもできます。

---

## サブコマンド一覧

### `info`
py-encaseのインストール状況および現在の環境に関する情報を表示します。

| オプション | 説明 |
|-----------|------|
| `-v, --verbose` | すべてのパス情報を表示(`--long` と同等) |
| `-l, --long` | 詳細な説明を表示 |
| `-s, --short` | 最小限の説明を表示(ラベルなしの値のみ) |
| `-V, --version` | バージョン情報を表示 |
| `-m, --pip-module-name` | PyPIモジュール名(`py-encase`)を表示 |
| `-M, --manage-script-name` | マネージスクリプト名(`mng_encase`)を表示 |
| `-O, --manage-option` | マネージモードに入るためのCLIオプション(`--manage`)を表示 |

```bash
mng_encase info                 # 短い一行の説明
mng_encase info --version       # 例: "PIP module version: 0.0.34"
mng_encase info --long          # パス・python/pipコマンド・各ディレクトリなどの完全な情報
mng_encase info -s -V           # ラベルなしのバージョン文字列のみ
```

### `contents`
環境を構成するファイル(スクリプト、ライブラリ、モジュールソース)の一覧を表示します。

| オプション | 説明 |
|-----------|------|
| `-v, --verbose` | 各カテゴリの前に見出しを表示 |
| `-a, --all` | すべてのカテゴリを表示(カテゴリ指定なしの場合のデフォルト) |
| `-b, --bin-script` | `bin/` スクリプトを表示 |
| `-l, --lib-script` | `lib/python` ライブラリスクリプトを表示 |
| `-m, --module-src` | モジュールソースディレクトリを表示 |

```bash
mng_encase contents                 # すべて表示
mng_encase contents -b -v           # bin/ スクリプトのみ、見出し付きで表示
```

### `init`
指定したプレフィックス配下に、まったく新しい実行環境を構築します。ディレクトリ構造、テンプレートスクリプト、`bin/` 起動用シンボリックリンク、`README.md`、依存パッケージのインストール、Git初期化までを一括で行います。

| オプション | 説明 |
|-----------|------|
| `-p, --prefix PATH` | ディレクトリツリーのプレフィックス(共通オプション参照) |
| `-t, --title TEXT` | プロジェクトタイトル。生成される `README.md` で使用 |
| `-D, --template PATH` | 使用するテンプレートファイル(デフォルト: `py_encase.py` 自身) |
| `-x, --script-template-style STYLE` | 使用する組み込みスクリプトテンプレートの種類を選択。現在は `simple`, `app-framework` をサポート。デフォルトは `simple` |
| `-y, --scrlib-template-style STYLE` | 使用する組み込みライブラリスクリプトテンプレートの種類を選択。現在は `simple` をサポート |
| `-F, --app-framework` | アプリケーションフレームワーク(GUI/argparse-extdヘルパー)を含むテンプレート版を使用 |
| `-B, --simple-script`, `--bare-script` | アプリケーションフレームワークを含まないシンプルな組み込みスクリプトテンプレートを使用。`--bare-script` は `--simple-script` の後方互換用エイリアスです。 |
| `-K, --gui-kvfile [NAME]` | GUIアプリケーション用のサンプルKivy `.kv` ファイルも作成する |
| `-r, --readme` | `README.md` を作成/更新する |
| `-m, --module NAME` | pipで追加モジュールをインストール(繰り返し指定可) |
| `-i, --install-dependency` | 生成されたスクリプトが必要とするモジュールを自動検出してインストール |
| `-O, --required-module` | テンプレート自体が参照しているモジュール/スクリプトライブラリをインストール |
| `-s, --script-lib NAME` | テンプレートに含まれるライブラリスクリプトを `lib/python` にコピー(繰り返し指定可) |
| `-S, --std-script-lib` | 標準添付のライブラリスクリプトをすべてインストール(各スクリプトに対して `-s` を指定するのと同等) |
| `-g, --setup-git` | 新しい環境に対してGitを初期化する([Git remoteオプション](#git-remoteオプション)参照) |
| `-M, --move` | このスクリプト自身の実体を、コピーではなく移動して新環境に配置する |
| `-P, --python PATH` | Pythonパス/コマンド |
| `-I, --pip PATH` | pipパス/コマンド |
| `-G, --git-command PATH` | gitパス/コマンド |
| `--conv-table PATH` | import名 → pipパッケージ名の変換テーブルファイル([`show_deps`](#show_deps)参照) |
| `--dependency-file PATH` | 明示的なモジュール要件ファイル |
| `-v, --verbose` | 詳細出力 |
| `-n, --dry-run` | ドライランモード |
| `scriptnames...` | 作成するスクリプトファイル名(位置引数、0個以上) |

```bash
# 単一スクリプトのみの最小構成環境
mng_encase init --prefix ./my-tool my_tool.py

# フル機能環境: README、フレームワークテンプレート、依存関係自動インストール、Git初期化
mng_encase init -v -r -g -F -O \
  --prefix ./my-new-tools --title "My tools" \
  -m requests -m pyyaml \
  my_new_work_tool
```

### `add`
既存の環境に新しいスクリプトファイルを1つ以上追加します(`lib/python/<name>.py` ファイルと、その起動用シンボリックリンク `bin/<name>` を作成)。

| オプション | 説明 |
|-----------|------|
| `-p, --prefix PATH` | ディレクトリツリーのプレフィックス |
| `-r, --readme` | スクリプト追加後に `README.md` を更新する |
| `-D, --template PATH` | 使用するテンプレートファイル |
| `-x, --script-template-style STYLE` | 使用する組み込みスクリプトテンプレートの種類を選択。現在は `simple`, `app-framework` をサポート。デフォルトは `simple` |
| `-F, --app-framework` | アプリケーションフレームワークを含むテンプレート版を使用 |
| `-B, --simple-script`, `--bare-script` | シンプルな組み込みスクリプトテンプレートを使用。`--bare-script` は後方互換用エイリアスです。 |
| `-K, --gui-kvfile [NAME]` | サンプルKivy `.kv` ファイルも作成する |
| `-m, --module NAME` | pipで追加モジュールをインストール(繰り返し指定可) |
| `-i, --install-dependency` | 新規スクリプトが必要とするモジュールを自動検出してインストール |
| `-O, --required-module` | テンプレートが参照しているモジュール/スクリプトライブラリをインストール |
| `-s, --script-lib NAME` | テンプレートからライブラリスクリプトをコピー(繰り返し指定可) |
| `-S, --std-script-lib` | 標準添付のライブラリスクリプトをすべてインストール |
| `-P, --python PATH` / `-I, --pip PATH` / `-G, --git-command PATH` | 各種コマンドパス |
| `-T, --conv-table PATH` | import名 → pip名の変換テーブル |
| `-R, --dependency-file PATH` | 明示的なモジュール要件ファイル |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |
| `scriptnames...` | 作成するスクリプトファイル名(位置引数、1個以上、必須) |

```bash
mng_encase add -v another_tool
mng_encase add -r -i second_tool third_tool   # 2つのスクリプトを同時に作成、依存関係自動インストール、READMEも更新
```

### 組み込みスクリプトテンプレートスタイル

`init` と `add` サブコマンドでは、組み込みスクリプトテンプレートの種類を選択できます。

| オプション | 対応するスタイル | 説明 |
|-----------|------------------|------|
| `--script-template-style simple` | `simple` | デフォルトのシンプルなスクリプトテンプレート |
| `--script-template-style app-framework` | `app-framework` | アプリケーションフレームワーク付きテンプレート |
| `-B, --simple-script` | `simple` | シンプルなスクリプトテンプレートを選ぶショートカット |
| `--bare-script` | `simple` | `--simple-script` の後方互換用エイリアス |
| `-F, --app-framework` | `app-framework` | アプリケーションフレームワーク付きテンプレートを選ぶショートカット |

例:

```bash
mng_encase init --script-template-style simple --prefix ./my-tool my_tool.py
mng_encase add --simple-script helper_tool.py
mng_encase add --bare-script legacy_name.py      # --simple-script の別名
mng_encase add --app-framework gui_tool.py
```

### `addlib`
複数のスクリプト間で共有するユーティリティを切り出すための、単一ファイルのライブラリモジュールを1つ以上追加します。ライブラリファイルは `lib/python` 以下に作成され、`bin/` の起動用リンクは作成されません。

| オプション | 説明 |
|-----------|------|
| `-p, --prefix PATH` | ディレクトリツリーのプレフィックス |
| `-r, --readme` | `README.md` を更新する |
| `-D, --template PATH` | 使用するテンプレートファイル |
| `-m, --module NAME` | pipで追加モジュールをインストール(繰り返し指定可) |
| `-i, --install-dependency` | 必要な外部モジュールを自動検出してインストール |
| `-O, --required-module` | テンプレートが参照しているモジュール/スクリプトライブラリをインストール |
| `-S, --std-script-lib` | 標準添付のライブラリスクリプトをすべてインストール |
| `-P, --python PATH` / `-I, --pip PATH` / `-G, --git-command PATH` | 各種コマンドパス |
| `-T, --conv-table PATH` / `-R, --dependency-file PATH` | 依存関係解決の上書き設定 |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |
| `script_lib...` | 作成するライブラリスクリプトファイル名(位置引数、1個以上、必須) |

```bash
mng_encase addlib -v util_helpers
mng_encase addlib date_helpers string_helpers
```

### `addkv`
GUIアプリケーション(アプリケーションフレームワークテンプレート使用時)向けのKivy(`.kv`)UI定義ファイルを1つ以上追加します。

| オプション | 説明 |
|-----------|------|
| `-p, --prefix PATH` | ディレクトリツリーのプレフィックス |
| `-D, --template PATH` | 使用するテンプレートファイル |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |
| `kvfiles...` | 作成するKVファイル名(位置引数、1個以上、必須) |

```bash
mng_encase addkv main_window
```

### `newmodule`
単一スクリプトではなく、配布可能なパッケージ構造のPythonモジュール(ソースレイアウト、テスト、ドキュメント、`pyproject.toml`、`LICENSE`)を作成します。

| オプション | 説明 |
|-----------|------|
| `-p, --prefix PATH` | ディレクトリツリーのプレフィックス |
| `-t, --title TEXT` | プロジェクトタイトル |
| `-d, --description TEXT` | プロジェクトの説明 |
| `-D, --template PATH` | 使用するテンプレートファイル |
| `-W, --module-website URL` | 新モジュールのホームページ/WebサイトURL(繰り返し指定可) |
| `-C, --class-name NAME` | モジュール内に生成するクラス名(繰り返し指定可) |
| `-m, --module NAME` | 新モジュールが必要とする外部モジュール。依存関係として追加(繰り返し指定可) |
| `-k, --keywords WORD` | `pyproject.toml` メタデータ用のキーワード(繰り返し指定可) |
| `-c, --classifiers TEXT` | PyPI trove classifier(繰り返し指定可) |
| `-A, --author-name NAME` | 著者名(繰り返し指定可) |
| `-E, --author-email EMAIL` | 著者メールアドレス(繰り返し指定可) |
| `-M, --maintainer-name NAME` | メンテナ名(繰り返し指定可) |
| `-N, --maintainer-email EMAIL` | メンテナメールアドレス(繰り返し指定可) |
| `-Y, --create-year YEAR` | `LICENSE` に記載する著作権年(繰り返し指定可) |
| `-Q, --no-readme` | `README.md` を作成しない |
| `-b, --no-git-file` | Git関連ファイルを作成しない |
| `-S, --set-shebang` | ローカル環境に基づいてshebang行を設定する |
| `-P, --python PATH` / `-I, --pip PATH` / `-G, --git-command PATH` | 各種コマンドパス |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |
| *([Git remoteオプション](#git-remoteオプション)参照)* | `init`/`init_git` と共通のGitリポジトリ設定 |
| `module_name...` | 作成する新モジュール名(位置引数、1個以上、必須) |

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
テンプレートから `README.md` を再生成/更新し、現在のbinスクリプト、ライブラリスクリプト、`.gitkeep` ディレクトリの一覧を反映します。

| オプション | 説明 |
|-----------|------|
| `-t, --title TEXT` | READMEで使用するタイトルテキスト |
| `-D, --template PATH` | 使用するテンプレートファイル |
| `-b, --backup` | 更新前の `README.md` のタイムスタンプ付きバックアップを保持する |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |

```bash
mng_encase update_readme -t "My Toolset" -b
```

### `init_git`
作業環境全体、または指定したモジュールソースディレクトリに対して、Gitリポジトリを初期化(または再設定)します。GitHub/GitLab/汎用SSHホスト上でのリモートリポジトリ作成にも対応します。

| オプション | 説明 |
|-----------|------|
| `-m, --module-src PATH` | トップレベルの作業環境ではなく、指定したモジュールソースディレクトリに対してgitを設定する |
| `-G, --git-command PATH` | gitパス/コマンド |
| `-D, --template PATH` | 使用するテンプレートファイル |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |
| *([Git remoteオプション](#git-remoteオプション)参照)* | リモートリポジトリ関連オプション一式 |

```bash
mng_encase init_git -v \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-hosting github --git-remote-account my_git_account --git-protocol ssh
```

### `dump_template`
`py_encase.py` に埋め込まれたテンプレート部分(スクリプト、ライブラリ、`README.md` などの生成に内部的に使用される)を、ファイルまたは標準出力にダンプします。テンプレートの確認やカスタマイズに便利です。

| オプション | 説明 |
|-----------|------|
| `-o, --output PATH` | 標準出力ではなくファイルに書き出す |
| `-D, --template PATH` | ダンプ元として使用するテンプレートファイル |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |

```bash
mng_encase dump_template -o my_custom_template.py
```

### `clean`
**現在選択されているPython/pipバージョンについてのみ**、pipによってローカルにインストールされたモジュールとキャッシュを削除します。

| オプション | 説明 |
|-----------|------|
| `-v, --verbose` | 詳細出力 |
| `-n, --dry-run` | ドライランモード |

```bash
mng_encase clean -v
```

### `distclean`
`clean` と同様ですが、環境下で見つかったすべてのPythonバージョンについて、ローカルインストール済みのモジュール/キャッシュを削除します(より徹底したクリーンアップ)。

| オプション | 説明 |
|-----------|------|
| `-v, --verbose` | 詳細出力 |
| `-n, --dry-run` | ドライランモード |

```bash
mng_encase distclean -v
```

### `selfupdate`
`py-encase` 自体を更新します。PyPIから最新版をローカルサンドボックスにインストールし、バージョン番号を比較した上で、より新しいバージョンが利用可能な場合(または `--force-install` 指定時)に、現在実行中の `py_encase.py` 実体ファイルを新しいものに置き換えます(旧ファイルはタイムスタンプ付きでバックアップされます)。

| オプション | 説明 |
|-----------|------|
| `-f, --force-install` | インストール済みバージョンが新しくなくても実体ファイルを置き換える |
| `-v, --verbose` / `-n, --dry-run` | 詳細出力 / ドライラン |

```bash
mng_encase selfupdate -v
mng_encase selfupdate --force-install
```

### pipラッパー系サブコマンド: `install`, `download`, `freeze`, `inspect`, `list`, `cache`, `help`
これらのサブコマンドは引数をそのまま `pip` に渡しますが、自動的にエンケースされた `lib/python/site-packages` 以下のローカルサンドボックスをpipの対象(`--target`/`--path`/`--cache-dir`/`--log` など)に指定するため、システム全体に何かがインストールされることはありません。

| サブコマンド | 対応するpipコマンド | 備考 |
|-------------|---------------------|------|
| `install` | `pip install --target <sandbox> ...` | パッケージをローカルサンドボックスにインストール |
| `download` | `pip download --dest <sandbox> ...` | パッケージの配布物をダウンロード |
| `freeze` | `pip freeze --path <sandbox> ...` | requirements形式でインストール済みパッケージを一覧表示 |
| `inspect` | `pip inspect --path <sandbox> ...` | ローカル環境の詳細情報を機械可読形式で表示 |
| `list` | `pip list --path <sandbox> ...` | インストール済みパッケージを一覧表示 |
| `cache` | `pip cache ...` | pipのキャッシュを管理 |
| `help` | `pip help ...` | pip自体のヘルプを表示(内部的には `piphelp` サブコマンドにマッピング) |

これらはいずれも任意の数の追加位置引数(`pip_subcommand_args`)を受け付け、そのまま `pip` に渡します。

```bash
mng_encase install requests pyyaml
mng_encase list
mng_encase freeze
mng_encase cache list
```

### `show_deps`
環境内のスクリプト・ライブラリ・モジュールソースを静的に走査して `import`/`from ... import` 文を検出し、標準ライブラリやローカル定義の名前を除外した上で、残った外部importの名前を(組み込みテーブルに加え、任意のカスタム変換テーブル/要件ファイルを使って)pipパッケージ名に変換します。デフォルトでは、結果のパッケージ一覧が標準出力に表示されます。

| オプション | 説明 |
|-----------|------|
| `-v, --verbose` | 検出した各importについて、どのファイル由来か、および解決されたpip名を表示 |
| `-a, --all` | すべてのカテゴリを走査(カテゴリ指定なしの場合のデフォルト) |
| `-b, --bin-script` | `bin/` スクリプトを走査 |
| `-l, --lib-script` | `lib/python` ライブラリスクリプトを走査 |
| `-m, --module-src` | モジュールソースディレクトリを走査 |
| `-D, --no-dump` | 標準出力へのパッケージ一覧表示を抑制する(内部的には結果を返す) |
| `-T, --conv-table PATH` | import名 → pipパッケージ名の変換テーブルファイル(JSON/TOML/INI/プレーンテキスト。自動検出される `MODULE_NAME.*` ファイルより優先) |
| `-R, --dependency-file PATH` | 追加/強制の要件ファイル(JSON/TOML/INI/プレーンテキスト。自動検出される `Requirements.*` ファイルより優先)。変換テーブルにマージされる |

```bash
mng_encase show_deps -v
mng_encase show_deps -b --conv-table my_import_map.json
```

### `install_deps`
内部で `show_deps` を実行して必要な外部パッケージを検出し、それらをすべて一度にローカルサンドボックスへ `pip install` します。

| オプション | 説明 |
|-----------|------|
| `-v, --verbose` | 詳細出力 |
| `-n, --dry-run` | ドライランモード(インストール予定内容のみ表示) |
| `-a, --all` / `-b, --bin-script` / `-l, --lib-script` / `-m, --module-src` | `show_deps` と同じ走査範囲指定フラグ |
| `-D, --dump` | 検出したパッケージ一覧も標準出力に表示する |
| `-T, --conv-table PATH` | import名 → pip名の変換テーブル |
| `-R, --dependency-file PATH` | 追加/強制の要件ファイル |
| `pip_subcommand_args...` | 実際の `pip install` 呼び出しに渡す追加引数 |

```bash
mng_encase install_deps -v
mng_encase install_deps -D -- --upgrade
```

### `help`
マネージモードのトップレベルヘルプ、または指定した単一サブコマンドの詳細ヘルプを表示します。

| オプション | 説明 |
|-----------|------|
| `command` | (省略可、位置引数)ヘルプを表示するサブコマンド名 |

```bash
mng_encase help              # mng_encase --help と同じ
mng_encase help init         # "init" サブコマンドの詳細ヘルプ
```

---

## Git remoteオプション

`init`、`newmodule`、`init_git` はいずれも、同じGit/リモートリポジトリ関連オプション群を共有しています。

| オプション | 説明 |
|-----------|------|
| `-y, --git-set-upstream` | 作成したローカルブランチのアップストリームをリモートに設定する |
| `-R, --git-remote-setup` | リモートのベアリポジトリも作成/初期化する |
| `-u, --git-user-name NAME` | 設定するgitユーザー名 |
| `-e, --git-user-email EMAIL` | 設定するgitユーザーのメールアドレス |
| `--github-userinfo INFO` | GitHubアカウント情報(`--git-hosting github` と併用) |
| `--gitlab-userinfo INFO` | GitLabアカウント情報(`--git-hosting gitlab` と併用) |
| `-T, --git-repository-name NAME` | リモートリポジトリ名(デフォルト: プロジェクト/モジュール名から導出) |
| `-H, --git-hosting {github,gitlab}` | リモート作成に使用するGitホスティングサービス |
| `-z, --git-protocol {http,https,ssh}` | リモートへの接続に使用するプロトコル |
| `-U, --git-remote-url URL` | 明示的なリモートURL(ホスト/アカウント/パスからの自動構築を上書き) |
| `-l, --git-remote-account NAME` | GitHub/GitLab/リモートホスト上のアカウント名 |
| `-L, --git-remote-host HOST` | リモートgitホスト名 |
| `--git-remote-port PORT` | リモートホストへの接続に使用するポート |
| `-w, --git-remote-path PATH` | リモートホスト上のリポジトリ格納ディレクトリのパス |
| `-X, --git-remote-sshopts OPT` | リモート接続用の追加sshオプション(繰り返し指定可。先頭の `-` は `\-` としてエスケープ) |
| `-Z, --git-remote-cmd CMD` | リモートホスト上で使用するgitコマンド |
| `--git-remote-share MODE` | リモートホスト上で `git init --shared=<MODE>` に渡す値 |
| `--git-remote-name NAME` | 登録するgitリモートの名前(デフォルト: `origin`) |
| `--ssh-command CMD` | 使用するsshコマンド |
| `--gh-command CMD` | 使用する `gh`(GitHub CLI)コマンド |
| `--glab-command CMD` | 使用する `glab`(GitLab CLI)コマンド |

```bash
# ローカルリポジトリを作成し、SSH経由で新規GitHubリポジトリにpushする
mng_encase init_git \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-hosting github --git-remote-account my_git_account --git-protocol ssh

# ローカルリポジトリを作成し、通常のSSHホスト上のベアリポジトリにpushする
mng_encase init_git \
  --git-user-name my_git_account --git-user-email my_git_account@my_git_host.domain \
  --git-set-upstream --git-remote-setup \
  --git-remote-account remote_account --git-remote-host remotehost.remotedomain \
  --git-remote-path '~/git_repositories/' --git-remote-share group --git-protocol ssh
```

---

## 作者
    Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
    Nanigashi Uji (4423013-nanigashi_uji@users.noreply.gitlab.com)

    GitHub: https://github.com/nanigashi-uji/py-encase
    GitLab: https://gitlab.com/nanigashi_uji/py-encase
    PyPI:   https://pypi.org/project/py-encase/
