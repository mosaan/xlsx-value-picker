# JSONスキーマに基づく設定データ読み込み機能の設計

## 1. 概要

本ドキュメントでは、xlsx-value-pickerにおけるJSONスキーマに準拠した設定データの読み込み機能の設計と実装方針について詳述します。設定ファイルは、フィールドマッピング、バリデーションルール、出力形式の定義を含み、JSONスキーマに基づいて検証されます。

## 2. 設定ファイルの構造

設定ファイルはYAMLまたはJSON形式で記述され、以下の構造を持ちます：

```yaml
# 設定ファイル構造の例
fields:  # セル値取得のためのマッピング定義
  animal_select: Sheet1!B5
  animal_free_text: Sheet1!D5
  email: Sheet1!E5
  product_code: Sheet2!A1
  quantity: Sheet2!B1

rules:  # バリデーションルール定義
  - name: "その他選択時の自由記入必須"
    expression:
      any_of:
        - compare:
            left: "animal_select"
            operator: "!="
            right: "その他"
        - field: "animal_free_text"
          required: true
    error_message: "「その他」を選んだ場合は内容を記入してください。"

output:  # 出力設定
  format: "json"  # "json", "yaml", "jinja2"
  template_file: "template.j2"  # テンプレート使用時のファイルパス
```

## 3. JSONスキーマによる検証

設定ファイルは`rule-schema.json`に定義されたJSONスキーマに基づいて検証されます。このスキーマは、設定ファイルの構造を定義し、必須フィールドやフィールドの型などを規定します。

## 4. 設定データ読み込み機能のアーキテクチャ

設定データ読み込み機能は以下のコンポーネントで構成されます：

```mermaid
flowchart TD
    %% スタイル定義
    classDef fileStyle fill:#f9f9f9,stroke:#999,stroke-width:1px,color:#333
    classDef processStyle fill:#e1f5fe,stroke:#4fc3f7,stroke-width:1px,color:#0277bd
    classDef modelStyle fill:#fff9c4,stroke:#ffd54f,stroke-width:1px,color:#ff6f00
    
    %% ファイル・データ要素
    config[("設定ファイル<br>(YAML/JSON形式)")]:::fileStyle
    jsonschema[("JSONスキーマ<br>定義ファイル")]:::fileStyle
    
    %% 処理コンポーネント要素
    parser[設定ファイル<br>パーサー]:::processStyle
    validator[JSONスキーマ<br>バリデーター]:::processStyle
    factory[ルール<br>ファクトリー]:::processStyle
    
    %% モデル要素
    config_model[設定モデル<br>オブジェクト]:::modelStyle
    rules_model[ルール<br>オブジェクト]:::modelStyle
    
    %% フロー
    config --> parser
    jsonschema --> validator
    parser --> validator
    validator --> config_model
    config_model --> factory
    factory --> rules_model
```

## 5. 主要コンポーネントの設計

### 5.1 設定ファイルパーサー（ConfigParser）

設定ファイル（YAMLまたはJSON）を読み込み、Python辞書に変換する役割を担います。

```python
class ConfigParser:
    @staticmethod
    def parse_file(file_path: str) -> dict:
        """設定ファイルを読み込み、辞書に変換する"""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
            elif file_path.endswith('.json'):
                import json
                return json.load(f)
            else:
                raise ValueError(f"サポートされていないファイル形式です: {file_path}")
```

### 5.2 JSONスキーマバリデーター（SchemaValidator）

JSONスキーマを使用して、設定ファイルの内容を検証します。

```python
class SchemaValidator:
    def __init__(self, schema_path: str):
        """スキーマファイルを読み込む"""
        with open(schema_path, 'r', encoding='utf-8') as f:
            import json
            self.schema = json.load(f)
    
    def validate(self, config_data: dict) -> None:
        """設定データをスキーマに基づいて検証する"""
        import jsonschema
        try:
            jsonschema.validate(instance=config_data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ConfigValidationError(f"設定ファイルの検証に失敗しました: {e}")
```

### 5.3 設定モデル（ConfigModel）

設定データを表現するPydanticモデル。JSONスキーマから自動的にモデルを生成することも検討します。

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any

class Expression(BaseModel):
    """バリデーション式の基底クラス"""
    pass

class CompareExpression(Expression):
    """比較式"""
    compare: Dict[str, Any]

class RequiredExpression(Expression):
    """必須項目式"""
    field: str
    required: bool = True

class RegexMatchExpression(Expression):
    """正規表現マッチ式"""
    regex_match: Dict[str, str]

class EnumExpression(Expression):
    """列挙型式"""
    enum: Dict[str, Any]

class AllOfExpression(Expression):
    """全条件一致式"""
    all_of: List[Expression]

class AnyOfExpression(Expression):
    """いずれかの条件一致式"""
    any_of: List[Expression]

class NotExpression(Expression):
    """否定式"""
    not_: Expression = Field(..., alias='not')

class Rule(BaseModel):
    """バリデーションルール"""
    name: str
    expression: Expression
    error_message: str

class OutputFormat(BaseModel):
    """出力形式設定"""
    format: str = "json"
    template_file: Optional[str] = None
    template: Optional[str] = None

class ConfigModel(BaseModel):
    """設定ファイルのモデル"""
    fields: Dict[str, str]
    rules: List[Rule]
    output: OutputFormat = Field(default_factory=OutputFormat)
```

### 5.4 ルールファクトリー（RuleFactory）

モデルオブジェクトから実際のルールオブジェクトを生成します。

```python
class RuleFactory:
    @staticmethod
    def create_rule(rule_model: Rule) -> ValidationRule:
        """ルールモデルからルールオブジェクトを生成する"""
        # ルール式の型に基づいて適切なルールオブジェクトを作成
        expression = rule_model.expression
        if isinstance(expression, CompareExpression):
            return CompareRule(...)
        elif isinstance(expression, RequiredExpression):
            return RequiredRule(...)
        # その他のルールタイプも同様に処理
        
        raise ValueError(f"サポートされていない式タイプです: {type(expression)}")
```

### 5.5 設定ローダー（ConfigLoader）

上記のコンポーネントを統合し、設定ファイルからモデルオブジェクトとルールオブジェクトを生成します。

```python
class ConfigLoader:
    def __init__(self, schema_path: str = None):
        """初期化"""
        self.schema_path = schema_path or os.path.join(os.path.dirname(__file__), "rule-schema.json")
        self.validator = SchemaValidator(self.schema_path)
    
    def load_config(self, config_path: str) -> ConfigModel:
        """設定ファイルを読み込み、モデルオブジェクトを返す"""
        # 設定ファイルのパース
        config_data = ConfigParser.parse_file(config_path)
        
        # JSONスキーマによる検証
        self.validator.validate(config_data)
        
        # モデルオブジェクトの生成
        return ConfigModel.model_validate(config_data)
    
    def load_rules(self, config_path: str) -> List[ValidationRule]:
        """設定ファイルを読み込み、ルールオブジェクトのリストを返す"""
        config_model = self.load_config(config_path)
        
        # ルールオブジェクトの生成
        rules = []
        for rule_model in config_model.rules:
            rule = RuleFactory.create_rule(rule_model)
            rules.append(rule)
        
        return rules
```

## 6. 実装方針

1. まずはJSONスキーマの検証部分を実装し、既存の設定ファイル読み込み機能を置き換えます。
2. 次に、バリデーションルールのモデルクラス階層を実装します。
3. ルールファクトリーを実装し、モデルからルールオブジェクトを生成できるようにします。
4. CLIインターフェースと統合します。

## 7. 拡張性と保守性への配慮

- Pydanticモデルを使用することで、型安全性とバリデーション機能を得られます。
- ファクトリーパターンを採用することで、新しいルールタイプの追加が容易になります。
- JSONスキーマを使用することで、設定ファイルの検証が容易になります。

## 8. テスト方針

1. **単体テスト**
   - 各コンポーネント（パーサー、バリデーター、ファクトリーなど）の動作確認
   - 正常なケースと異常なケースの両方をテスト

2. **統合テスト**
   - 実際の設定ファイルを使用したE2Eテスト
   - 異なる形式（YAML、JSON）での動作確認

3. **エッジケース**
   - 空の設定ファイル
   - 必須項目の欠落
   - 無効な式の検証

## 9. 実装ステップ

1. JSONスキーマバリデーション機能の実装
2. 設定モデルの定義
3. ルールファクトリーの実装
4. 設定ローダーの実装
5. CLIとの統合
6. テストの作成と実行
7. ドキュメント更新

## 10. 今後の拡張性

将来的には以下の拡張も検討します：

- 設定ファイルのGUIエディタの開発
- リモート設定ファイルの読み込みサポート
- 動的なルール生成機能
- 設定ファイルの暗号化サポート

---

このドキュメントは実装を進める中で随時更新していきます。