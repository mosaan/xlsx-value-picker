# Required/IsEmpty 表現の実装計画

## 概要

現在の `RequiredFieldExpression` クラスは他の Expression クラスと異なり、ルートレベルでどの Expression であるかを判別する専用のプロパティを持っていません。これにより、他の式と比較して一貫性がなく、使用する際の直感性も低下しています。

今回の実装では以下の改善を行います：

1. `RequiredFieldExpression` を完全に置き換える新しい `RequiredExpression` を実装する
2. 複数フィールドに対応するために、単一フィールドと配列の両方をサポートする
3. 相補的な機能として `IsEmptyExpression` を新たに実装する

これにより、より直感的かつ一貫性のある YAML 記法で条件式を記述できるようになります。

## 要件

### 1. RequiredExpression の実装

- 単一フィールドの必須を示す省略記法：
  ```yaml
  required: "field1"
  ```
- 複数フィールドを一括して必須であることを示す記法：
  ```yaml
  required:
    - "field1"
    - "field2"
  ```

### 2. IsEmptyExpression の実装

- 単一フィールドが空であることを示す記法：
  ```yaml
  is_empty: "field1"
  ```
- 複数フィールドが空であることを示す記法：
  ```yaml
  is_empty:
    - "field1"
    - "field2"
  ```

### 3. 実装における注意点

- 既存の `RequiredFieldExpression` は完全に廃止し、新しい `RequiredExpression` に置き換える
- 型の安全性を確保する（Pydantic モデルの適切な使用）
- バリデーションの挙動に一貫性を持たせる
- 誤った使用方法に対して適切なエラーメッセージを提供する

## 実装計画

### ステップ 1: RequiredExpression クラスの実装

1. 既存の `RequiredFieldExpression` を完全に置き換える新しい `RequiredExpression` クラスを作成
2. 単一文字列または文字列リストを受け取れるようにモデル定義を行う
3. `validate_in` メソッドを実装して、単一/複数フィールドのどちらも正しく検証できるようにする

### ステップ 2: IsEmptyExpression クラスの実装

1. `IsEmptyExpression` クラスを新規作成
2. 単一文字列または文字列リストを受け取れるようにモデル定義を行う
3. `validate_in` メソッドを実装して、フィールドが空であるか検証するロジックを記述

### ステップ 3: Expression 検出と変換機能の更新

1. `detect_expression_type` 関数を更新して、新しい式型を検出できるようにする
2. `convert_expression` 関数を更新して新しい式型に対応させる
3. 既存の `RequiredFieldExpression` に関連するコードを削除

### ステップ 4: テストコードの作成と既存テストの修正

1. `RequiredExpression` の各種パターンに対するユニットテストの作成
2. `IsEmptyExpression` の各種パターンに対するユニットテストの作成
3. 複合条件（例：`any_of` と組み合わせたケース）のテスト作成
4. 既存のテストでRequiredFieldExpressionを使用しているものを修正

## 影響範囲

- `validation_expressions.py`: 主要な変更点
- `validation.py`: 関連する検証ロジック
- テストコード
- 仕様、ドキュメント

## 検証方法

1. ユニットテストによる機能動作の確認
2. サンプル YAML を使った統合テストによる動作確認

## 完了条件

- [ ] 新しい `RequiredExpression` および `IsEmptyExpression` クラスの実装
- [ ] 両クラスの単一/複数フィールド対応
- [ ] 式検出ロジックの更新
- [ ] 既存の `RequiredFieldExpression` の完全な削除
- [ ] テストコードの作成と修正、実行成功
- [ ] サンプル YAML による動作確認

