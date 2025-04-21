# CompareExpressionの仕様変更計画

## 1. 目的

JSONスキーマの`CompareExpression`の仕様を変更し、フィールドを明示的に指定する`left_field`と`right_field`を新設する。

## 2. 現状の確認

現在の`CompareExpression`のJSONスキーマ定義は以下の通りです：

```json
"CompareExpression": {
  "type": "object",
  "properties": {
    "compare": {
      "type": "object",
      "properties": {
        "left": { "type": "string" },
        "operator": {
          "type": "string",
          "enum": ["==", "!=", ">", ">=", "<", "<="]
        },
        "right": { "oneOf": [{ "type": "string" }, { "type": "number" }] }
      },
      "required": ["left", "operator", "right"]
    }
  },
  "required": ["compare"]
}
```

## 3. コード実装との整合性

`src/xlsx_value_picker/validation_expressions.py`の`CompareExpressionParams`クラスと`CompareExpression`クラスを確認しました。すでに以下の実装が確認できます：

1. `left_field`と`right_field`フィールドの定義
2. これらのフィールドを利用した値取得メソッド（`get_left_value`、`get_right_value`）
3. 値の取得とバリデーション処理

## 4. 変更内容

JSONスキーマの`CompareExpression`定義を更新し、以下の変更を加えます：

1. `left_field`プロパティを追加（文字列型）
2. `right_field`プロパティを追加（文字列型）
3. 必須項目の条件を変更（`left`または`left_field`のいずれかが必須、`right`または`right_field`のいずれかが必須）

## 5. 新しいJSONスキーマ

```json
"CompareExpression": {
  "type": "object",
  "properties": {
    "compare": {
      "type": "object",
      "properties": {
        "left": { "type": "string" },
        "left_field": { "type": "string" },
        "operator": {
          "type": "string",
          "enum": ["==", "!=", ">", ">=", "<", "<="]
        },
        "right": { "oneOf": [{ "type": "string" }, { "type": "number" }] },
        "right_field": { "type": "string" }
      },
      "required": ["operator"],
      "allOf": [
        {
          "oneOf": [
            { "required": ["left"] },
            { "required": ["left_field"] }
          ]
        },
        {
          "oneOf": [
            { "required": ["right"] },
            { "required": ["right_field"] }
          ]
        }
      ]
    }
  },
  "required": ["compare"]
}
```

## 6. 作業計画

1. JSONスキーマファイル（`docs/spec/rule-schema.json`）の`CompareExpression`定義を上記の新しい定義に更新する
2. 変更内容が既存の実装と整合性があることを確認する
3. `/README.md`や`/docs/`配下の文書に変更内容を反映する
4. 変更内容が正しく反映されているかテストを実施する

## 7. リスクと考慮事項

既存のJSONスキーマを利用している場合、以下のリスクがあります：
- 既存のルール定義で`left`と`right`を必須としていた部分が緩和されるため、バリデーションが通る内容が増える
- `left_field`と`right_field`を使用する新しいルール定義が可能になる

すでにコードの実装が対応済みであるため、実際の動作に影響はないと考えられます。

## 8. 作業結果

以下の作業を実施し、すべて完了しました：

1. JSONスキーマファイル（`docs/spec/rule-schema.json`）の`CompareExpression`定義を新しい定義に更新
2. バリデーション関連のテストを実行して、変更が既存の機能に影響を与えていないことを確認
3. READMEに新しい機能（`left_field`と`right_field`）の説明を追加

テストはすべて成功し、機能が正常に動作することを確認しました。
