# nununu

Threads アカウントを AI エージェントで自動運用するシステムです。

## 概要

6 つの AI エージェントが連携して Threads アカウントを運用し、収益化を支援します。

| エージェント | 役割 |
|---|---|
| **Researcher** | ネタ収集・トレンド調査 |
| **Analyst** | 投稿パフォーマンス分析 |
| **Writer** | 投稿テキスト自動生成 |
| **Poster** | Threads API で投稿実行 |
| **Fetcher** | 閲覧数・いいね等のデータ取得 |
| **Supervisor** | 全体の監視・異常検知・パイプライン制御 |

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、値を入力します。

```bash
cp .env.example .env
```

必要な値:

| 変数名 | 説明 |
|---|---|
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) で取得 |
| `THREADS_ACCESS_TOKEN` | Meta for Developers で取得した長期アクセストークン |
| `THREADS_USER_ID` | Threads のユーザー ID（数値文字列） |

## 使い方

### パイプラインを実行する

```bash
# 通常実行（Threads に投稿される）
python main.py --niche "テクノロジー" --count 3

# 投稿せずにパイプラインをテスト
python main.py --niche "ライフスタイル" --count 2 --dry-run
```

### 個別エージェントを使う

```python
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent

researcher = ResearcherAgent()
topics = researcher.collect_topics(niche="テクノロジー", count=5)

writer = WriterAgent()
post_text = writer.generate_post(topics[0])
print(post_text)
```

## アーキテクチャ

```
Supervisor
  ├── Fetcher   → 既存投稿の閲覧数・いいね取得
  ├── Analyst   → パフォーマンス分析・改善提案
  ├── Researcher → トレンドトピック収集
  ├── Writer    → 投稿テキスト生成
  └── Poster    → Threads API 投稿
```

## Streamlit デモアプリ

旧来の Streamlit デモは引き続き起動できます。

```bash
streamlit run app.py
```
