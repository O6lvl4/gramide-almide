# gramide-almide

[gramide-cli](https://github.com/O6lvl4/gramide-cli) の Almide。字句解析の spec、値としての文法、
その文法をコンパイルした表、そしてどのノードが名前を宣言するかの規則。ひとつの Almide パッケージ
`gramide_almide` で、依存は [gramide](https://github.com/O6lvl4/gramide) だけです。
`gramide` コマンド（[gramide-cli](https://github.com/O6lvl4/gramide-cli)）はこれを出荷し、このリポジトリはこれ単体をテスト・計測・リリースする場所です。

[English](README.md)

```
almide build cli/main.almd -o gramide_almide     # .almd だけの gramide
./gramide_almide check src/*.almd
./gramide_almide outline src/parser.almd
./gramide_almide gen-table > src/table.almd      # 文法を変えたら
```

## カバー範囲

[Almide](https://github.com/almide/almide) リポジトリの全 `.almd` ファイル — 意図的に
非 Almide 構文を試す 2 ディレクトリを除いた 3,382 ファイル:

| ファイル | 結果 |
|---|---|
| 正しい 3,317 ファイル | すべてパース |
| `broken.almd` 診断フィクスチャ 65 | すべて拒否。いずれも `almide check` も拒否する（57 は構文エラー、8 は専用の構文診断） |
| その他の `broken.almd` 720 | パースは通り、意図どおり型検査で落ちる |

保証は一方向です。このパッケージが拒否するファイルはコンパイラにとっても壊れている。構文ゲートに
必要なのはその向きです。既知の数箇所ではコンパイラより寛容で、どれも構文ではなく名前解決や
個数の規則です: 連鎖比較 `a < b < c`、任意の右辺を取る `|>`、`f<Int>(x)` のジェネリクス、`t.0.1`
（浮動小数として字句解析される）、名前付き引数の後の位置引数、文字列なしの `todo`、
`@attr(x = -1)`、一部の `fan.bounded` 引数の形、区切りなしで 1 行に 2 文。`${…}` の内側は
パースしません。

コーパス全体の `check`（リポジトリの `.git`・`.claude`・`target`・`worktrees` 以外すべて、
4,105 ファイル）は 1 プロセス、byte 量で均した 8 スライドの並列で **0.118 秒**（42 MB/s）
（[証拠](docs/evidence/corpus-check-almide.json)、計測は gramide の `bench/corpus_check.py`）。

キー入力 1 回は item 1 つを読み直すだけです。エンジンはパース済みのファイルを recover item
（ここでは各宣言と、ブロック内の各文）の入れ子として持ち、編集が触れた最小の item を読み直します
（[仕組み](https://github.com/O6lvl4/gramide/blob/main/docs/incremental.md)）。gramide の
`src/parser.almd`（89 KB）で、長い単語の 6 文字目に文字を打つ・消す編集 1,000 回の中央値は 39 µs、
90 パーセンタイルは 52 µs で、丸ごとのパースは 2.6 ms。50 回に 1 回は丸ごとのパースと照合しています。
リポジトリの追跡下 `.almd` 4,027 ファイルのうち十分長い単語を持つ 1,273 ファイルに各 10 回のランダム編集
（12,730 回、毎回トークンとノードを丸ごとのパースと照合）で差はゼロ、4 回はファイル全体を読みました
（うち 3 回は構文エラーの隣。[証拠](docs/evidence/incremental-corpus-almide-repo.json)）。
`ci/incremental_check.py` がこれを回し、1 回の編集は `reparse --edit START:OLD_END:NEW_END --new FILE` です。

## 書き方

- **`src/lexer.almd`** — 共用字句解析器への `Spec`。キーワード、演算子、`//` と入れ子の `/* */`、
  `NL_EVERY`（改行は文の区切り、連続は 1 つに）、行頭 `-` の `neg` トークン、大文字始まりは型名、
  バッククォート名。`&&`・`||` と外来キーワード 4 つは、書き手が打ったもの全体をエラーが名指しできる
  ように字句解析します。
- **`src/grammar.almd`** — Almide リポジトリの `docs/GRAMMAR.md` と並べて書いた文法。規則名は
  それに従います。宣言は `name`・`body` フィールド付きのノード、式はより浅い木（二項演算子は
  `binary` に畳み、後置の連鎖は平ら）。`decl_head` 規則は本体が書きかけの宣言の種類と名前を
  残すので、`fn parse(` もアウトラインに出ます。
- **`src/symbols.almd`** — 関数・型・let・test・protocol・variant・field が名前を宣言し、
  型と protocol がその中のメソッドを所有します。
- **`src/table.almd`** — `gen-table` の生成物。古ければ CI が落ちます。

## 検査

`bash ci/check.sh`: `almide test`（64 テスト — 字句解析、全宣言種、回復、読み手の出力）、表の
一致検査、バイナリのスモーク、構造化範囲のフィクスチャ（[ci/README.md](ci/README.md)）。

## ライセンス

MIT または Apache-2.0、お好みで。
