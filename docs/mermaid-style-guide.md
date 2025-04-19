# Mermaidスタイルガイド

## 1. 概要

このドキュメントでは、xlsx-value-pickerプロジェクトのドキュメント内で使用するMermaid図表のスタイリングガイドラインを定義します。図表は視覚的な情報伝達において重要な役割を果たすため、一貫性のあるスタイルとアイコンを使用することで、ドキュメント全体の理解しやすさを向上させます。

## 2. 要素の分類とスタイル

Mermaidの図表では、主に以下の種類の要素を区別します：

### 2.1 ファイル・データ要素

ファイルやデータを表す要素には、以下のスタイルを適用します：

```mermaid
flowchart TD
    %% ファイル形式のスタイル
    classDef fileStyle fill:#f9f9f9,stroke:#999,stroke-width:1px,color:#333
    
    file1[(設定ファイル<br>YAML/JSON形式)]:::fileStyle
    file2[(Excelファイル)]:::fileStyle
    file3[(出力ファイル)]:::fileStyle
    
    file1 --> file2 --> file3
```

### 2.2 処理コンポーネント要素

処理やロジックを表すコンポーネントには、以下のスタイルを適用します：

```mermaid
flowchart TD
    %% 処理コンポーネントのスタイル
    classDef processStyle fill:#e1f5fe,stroke:#4fc3f7,stroke-width:1px,color:#0277bd
    
    process1[セル値取得]:::processStyle
    process2[バリデーション]:::processStyle
    process3[テンプレート<br>レンダリング]:::processStyle
    
    process1 --> process2 --> process3
```

### 2.3 結果・出力要素

結果や出力を表す要素には、以下のスタイルを適用します：

```mermaid
flowchart TD
    %% 結果・出力のスタイル
    classDef resultStyle fill:#f1f8e9,stroke:#aed581,stroke-width:1px,color:#33691e
    
    result1{検証結果}:::resultStyle
    result2[JSON/YAML<br>出力]:::resultStyle
    
    result1 --> result2
```

## 3. 形状オプション

Mermaidでは、様々な形状を使用して要素の種類を視覚的に区別することが可能です：

```mermaid
flowchart TD
    %% 様々な形状の例
    A[矩形] --> B(丸角矩形)
    B --> C([丸い形])
    C --> D[[角が強調された形]]
    D --> E[(データベース/シリンダー)]
    E --> F((円形))
    F --> G>非対称形]
    G --> H{ひし形/分岐}
    H --> I{{六角形}}
    I --> J[/平行四辺形/]
    J --> K[\逆平行四辺形\]
    K --> L[/梯子形\]
```

## 4. バリデーション機能のアーキテクチャ図用スタイル

バリデーション機能のアーキテクチャ図には、以下のスタイルを適用します：

### 4.1 要素の分類

- **ファイル・データ要素**: 設定ファイル、Excelファイル、出力ファイル
- **処理コンポーネント要素**: セル値取得、バリデーション、テンプレートレンダリング、JSON/YAML出力
- **結果要素**: 検証結果

### 4.2 改善例

```mermaid
flowchart TD
    %% スタイル定義
    classDef fileStyle fill:#f9f9f9,stroke:#999,stroke-width:1px,color:#333
    classDef processStyle fill:#e1f5fe,stroke:#4fc3f7,stroke-width:1px,color:#0277bd
    classDef resultStyle fill:#f1f8e9,stroke:#aed581,stroke-width:1px,color:#33691e
    
    %% ファイル・データ要素
    config[(設定ファイル<br>YAML/JSON形式)]:::fileStyle
    excel[(Excelファイル)]:::fileStyle
    output1[(出力ファイル)]:::fileStyle
    output2[(出力ファイル)]:::fileStyle
    
    %% 処理コンポーネント要素
    cell_value[セル値取得]:::processStyle
    validation[バリデーション]:::processStyle
    template[テンプレート<br>レンダリング]:::processStyle
    json_yaml[JSON/YAML<br>出力]:::processStyle
    
    %% 結果要素
    result{検証結果}:::resultStyle
    
    %% フロー
    config --> validation
    config --> cell_value
    
    excel --> cell_value
    cell_value --> validation
    validation --> result
    
    validation --> template
    validation --> json_yaml
    
    template --> output1
    json_yaml --> output2
```

## 5. 適用のガイドライン

1. **一貫性を保つ**: すべての図表で同じスタイル規則を適用する
2. **シンプルさを維持**: 過度な装飾は避け、情報伝達を優先する
3. **色とアイコンの意味**: 色やアイコンには一貫した意味を持たせる
   - シリンダー形状`[(名前)]`: ファイル・データ
   - 四角形`[名前]`: 処理コンポーネント
   - ひし形`{名前}`: 結果・判断

## 6. Mermaidにおける注意点

1. **改行の扱い**: テキスト内の改行は`\n`ではなく、`<br>`タグを使用する
2. **形状指定**: 形状は`shape:cylinder`のようなスタイル指定ではなく、`[(`と`)]`のような記法で指定する
3. **スタイルプロパティ**: classDefで使用できるプロパティは限られており、形状は直接的には指定できない

## 7. 参考資料

- [Mermaid公式ドキュメント](https://mermaid-js.github.io/mermaid/#/)
- [Mermaidフローチャート構文](https://mermaid-js.github.io/mermaid/#/flowchart)
- [MermaidスタイルとクラスJS](https://mermaid-js.github.io/mermaid/#/flowchart?id=styling-and-classes)

---

このドキュメントは、プロジェクト内の図表の視覚的一貫性を確保するためのガイドラインです。必要に応じて随時更新していきます。