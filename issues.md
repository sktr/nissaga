# Nissaga - コード改善点リスト

このドキュメントは、Nissagaリポジトリにおけるコードの問題点と改善提案をまとめたものです。

## 🔴 重大な問題

### 1. 重複ファイルの存在
**問題**: `nissaga/models copy.py` というバックアップファイルが本番コードに含まれている
- **場所**: `nissaga/models copy.py`
- **影響**: リポジトリの混乱、メンテナンス性の低下
- **改善案**: 
  - ファイルを削除する
  - `.gitignore` に `*copy.py` や `* copy.*` パターンを追加してバックアップファイルを除外する

### 2. 未インポートの関数使用
**問題**: `models.py` で `error` 関数を使用しているが、インポートされていない
- **場所**: `nissaga/models.py:210-211`
- **現状**: `from consolemsg import warn, step` のみ
- **影響**: 実行時エラーの可能性
- **改善案**: `from consolemsg import warn, step, error` に変更する

### 3. デバッグコードの残留
**問題**: 例外処理に `print(dir(exception))` というデバッグコードが残っている
- **場所**: `nissaga/models.py:209`
- **影響**: 本番環境での不要な出力
- **改善案**: 削除するか、適切なロギングに置き換える

## 🟡 コード品質の問題

### 4. type() の使用
**問題**: `type(x) is/== Type` の比較が複数箇所で使われている
- **場所**: 
  - `nissaga/models.py:161`
  - `nissaga/models copy.py:161`
  - `nissaga/render.py:18, 35`
  - `nissaga/styles.py:105`
- **影響**: Pythonのベストプラクティスに反する
- **改善案**: `isinstance(x, Type)` を使用する

```python
# 現状
if type(person) is str:

# 改善後
if isinstance(person, str):
```

### 5. 不完全な例外処理
**問題**: 例外メッセージが不明瞭で、エラー情報が不十分
- **場所**: `nissaga/models.py:208-211`
- **現状**: 
```python
except graphviz.backend.CalledProcessError as exception:
    print(dir(exception))
    error(exception.stderr)
    error("Intermediate dot file dumped as output.dot")
```
- **改善案**: より具体的なエラーメッセージとログレベルを使用

### 6. ハードコーディングされた値
**問題**: マジックナンバーやハードコーディングされた値が複数存在
- **場所**: 
  - `nissaga/render.py:219` - `picsize = 40, 40` (TODO付き)
  - `nissaga/render.py:5-14` - `familyColors` の色リスト
- **改善案**: 
  - 設定ファイルや定数として定義
  - 設定フレームワークの実装（TODO.mdにも記載あり）

### 7. 不完全なドキュメント
**問題**: TODOコメントが残されたまま
- **場所**: 
  - `nissaga/models.py:27, 30` - id, name, fullname, aliasの違いの説明が未完成
  - `nissaga/render.py:17` - escape関数のレビュー未完了
  - `nissaga/styles.py:104` - レビュー未完了
- **改善案**: ドキュメントを完成させるか、該当機能を実装する

### 8. タイポ（誤字）
**問題**: 英単語のスペルミス
- **場所**: 
  - `nissaga/models.py:15` - "happenned" → "happened"
  - `nissaga/models.py:54` - "regardin" → "regarding"
  - `nissaga/models.py:115` - "regardin" → "regarding"
  - `nissaga/models.py:108` - "displayeed" → "displayed"
  - `nissaga/anniversaries.py`, `nissaga/anniversaries_test.py`, `nissaga/cli.py` - "compileAniversaries" → "compileAnniversaries" (複数ファイル)
- **改善案**: スペルチェッカーを実行し修正

## 🟢 軽微な問題・改善提案

### 9. Python 3.6互換性コード
**問題**: Python 3.6用の回避策コメントが複数箇所に残っている
- **場所**: `nissaga/render.py:97, 104, 203, 210`
- **現状**: `# TODO: Pydantic in python 3.6 turns bools into ints`
- **影響**: CI/CDではPython 3.7+を使用しているため不要
- **改善案**: 
  - Python 3.6のサポートを正式に終了する場合は削除
  - サポートを継続する場合は適切な処理を実装

### 10. スキップされたテスト
**問題**: 実装されていない警告機能のテストがスキップされている
- **場所**: `nissaga/models_test.py:252`
- **テスト**: `test_normalize_unrelated_warns`
- **改善案**: 警告機能を実装するか、テストを削除

### 11. 未解決のTODO（テストコード内）
**問題**: テストコード内の動作仕様が未決定
- **場所**: 
  - `nissaga/models_test.py:222` - 重複した人物詳細でどのバージョンを優先すべきか
  - `nissaga/models_test.py:246` - 同上
  - `nissaga/render_test.py:147` - 名前の空白処理の修正
- **改善案**: 仕様を決定し、適切に実装・テストする

### 12. コードの一貫性
**問題**: スペーシング（空白）の一貫性がない
- **場所**: 
  - `nissaga/render.py:18` - `type(s)==str` (空白なし)
  - `nissaga/render.py:35` - `type(lines) == str` (空白あり)
- **改善案**: コードフォーマッター（black, autopep8等）を導入

### 13. 未使用の引数
**問題**: 関数引数で `Tuple` がインポートされているが使用されていない可能性
- **場所**: `nissaga/models.py:5`
- **改善案**: 使用されていない場合は削除

### 14. 未実装機能のドキュメント化不足
**問題**: README.mdとTODO.mdに記載されている機能の実装状況が不明確
- **TODO.md記載の未実装項目**:
  - Schema documentation on GitHub
  - parents2 and children2 from kingraph
  - GraphViz FORMATSの使用
  - pets機能
  - CLI機能（output filename制御、autoview、dash入出力）
  - Python<=3.7対応
  - クォートのエスケープ処理
  - 設定フレームワーク
  - 日付フォーマット設定
  - アバターサイズ設定
  - 画像・ドキュメントディレクトリプレフィックス
- **改善案**: 
  - 優先順位を明確にする
  - 実装予定のないものは削除
  - Issue trackingシステムで管理

### 15. CLIコマンドの不整合
**問題**: `dates` コマンドがテストモジュールから関数をインポートしている
- **場所**: `nissaga/cli.py:100` - `from .anniversaries_test import compileAniversaries`
- **影響**: テストコードが本番コードに依存している
- **改善案**: 
  - `compileAniversaries` を `anniversaries.py` に移動
  - 関数名のタイポを修正: `compileAniversaries` → `compileAnniversaries`

### 16. コメントアウトされたコード
**問題**: コメントアウトされたコードが残っている
- **場所**: `nissaga/cli.py:64, 96` - `#allow_dash=True`
- **改善案**: 実装予定がある場合はIssueとして管理し、コメントは削除

## 📋 アーキテクチャ・設計の改善提案

### 17. 設定管理の欠如
**問題**: 設定ファイルやフレームワークが存在しない
- **現状**: ハードコーディングされた設定値
- **改善案**: 
  - YAML設定ファイルの導入
  - Pydanticを使った設定バリデーション
  - デフォルト設定とユーザー設定のマージ機能

### 18. エラーハンドリングの改善
**問題**: エラーハンドリングが不十分
- **改善案**:
  - カスタム例外クラスの定義
  - 一貫したエラーメッセージフォーマット
  - ユーザーフレンドリーなエラーメッセージ

### 19. ロギングの標準化
**問題**: `print()`, `step()`, `error()`, `warn()` が混在
- **改善案**: 標準ライブラリの `logging` モジュールに統一

### 20. テストカバレッジの向上
**問題**: TODO.mdによると以下の機能のカバレッジが不足
- born: None
- died: None
- escape without quotes
- final format rendering failures
- unrelated persons warning
- **改善案**: テストケースを追加

## 🛠️ 開発環境・ツールの改善

### 21. コードフォーマッターの導入
**改善案**: 
- `black` の導入
- `isort` によるimportの整理
- pre-commitフックの設定

### 22. 静的解析ツールの導入
**改善案**:
- `pylint` または `flake8`
- `mypy` による型チェック
- `bandit` によるセキュリティチェック

### 23. ドキュメント生成の自動化
**改善案**:
- `sphinx` によるAPI ドキュメント生成
- docstringの標準化（Google/NumPy形式）

### 24. CI/CDパイプラインの強化
**改善案**:
- コードカバレッジの閾値設定
- 自動フォーマットチェック
- 自動セキュリティスキャン

## 📝 ドキュメントの改善

### 25. README.mdの改善
**問題**: 開発者向けの情報が末尾に雑然と記載
- **場所**: README.md末尾の "develop cli" セクション
- **改善案**: 
  - CONTRIBUTING.md を作成
  - 開発環境のセットアップ手順を詳細化
  - コーディング規約の明記

### 26. CHANGELOGの更新
**問題**: バージョン0.3.0以降のUnreleasedセクションが更新されていない
- **改善案**: リリース前に変更点を適切に記録

## 🔒 セキュリティ・保守性

### 27. 依存関係の管理
**問題**: 依存パッケージのバージョンが固定されていない
- **場所**: `requirements.txt`
- **リスク**: セキュリティ脆弱性、互換性問題
- **改善案**: 
  - バージョン範囲の指定（例: `pydantic>=1.8,<2.0`）
  - `requirements-dev.txt` で開発用依存を分離
  - Dependabotの有効化

### 28. 入力バリデーションの強化
**問題**: ファイルパスや外部入力の検証が不十分
- **改善案**: 
  - パストラバーサル対策
  - ファイルサイズ制限
  - 入力サニタイゼーション

## 優先順位

1. **高**: 問題1, 2, 3（重大な問題）
2. **中**: 問題4-15（コード品質）
3. **低**: 問題16-28（改善提案）

## 実装の推奨順序

1. 重複ファイルの削除とimport修正（1, 2）
2. デバッグコードの削除（3）
3. type()の修正（4）
4. タイポ修正（8）
5. テストコード依存の修正（15）
6. 設定管理の実装（17）
7. テストカバレッジの向上（20）
8. 開発ツールの導入（21, 22）
9. ドキュメントの整備（25, 26）
10. 依存関係管理の改善（27）
