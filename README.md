# OpenAIAgentHub

這是一個基於 OpenAI 的 Agent 框架，用於構建和管理多個專業 Agent，實現不同領域的智能對話和服務。現在支持通過 FastAPI 提供 API 服務。

## 項目結構

```
├── api.py                    # FastAPI API 服務入口
├── src/                      # 源代碼目錄
│   ├── agent_center.py       # Agent中心，管理所有Agent
│   ├── agents.yaml           # 主要Agent配置文件
│   ├── agents_dispatcher.yaml # Dispatcher Agent配置文件
│   ├── base_config.yaml       # 基礎配置文件
│   ├── modules/               # 功能模組目錄 (可自行擴展)
│   │   ├── modules/           # 模組名稱
│   │   │   ├── config.yaml    # 模組配置
│   │   │   ├── guardrail/     # 安全檢查
│   │   │   ├── tool/          # 翻譯工具
│   │   │   └── handoff/       # 專業領域Agent
│   └── utils/                 # 工具類
│       └── agent_loader.py    # Agent加載器
└── .env                       # 環境變數配置
```

## 配置文件說明

### base_config.yaml
基礎配置文件，定義所有 Agent 共用的基本配置，如模型參數等。

### agents.yaml
主要 Agent 配置文件，定義所有讀取的模組。

### agents_dispatcher.yaml
Dispatcher Agent 配置文件，定義 Dispatcher Agent 的行為和配置，負責決定使用哪個專業 Agent 處理用戶請求。

### 模組配置文件
每個功能模組都有自己的配置文件，定義該模組的具體行為和設定。

## 如何擴展新的模組

1. 在 `src/modules` 目錄下創建新的模組目錄
2. 創建模組配置文件 `config.yaml`
3. 實現所需的 Agent 功能（工具、Guardrail、Handoff 等）
4. 在 `src/agents.yaml` 中添加新模組的配置引用

## 加載機制說明

系統使用 `AgentManager` 從配置文件加載所有 Agent，並通過 `AgentCenter` 提供統一的接口來獲取、註冊和管理各種類型的 Agent。

- **AgentManager**: 負責從 YAML 配置文件加載和管理所有 Agent
- **AgentCenter**: 作為整個系統的核心組件，負責管理和協調所有 Agent

## API 服務

系統支持通過 FastAPI 提供 API 服務，可以通過 HTTP 請求與 Agent 系統進行交互。

### API 端點

- **POST /callback**: 處理用戶問題，並返回 Agent 的回答

### POST FORMAT

```json
{
  "question": "用戶問題",
  "workflow_name": "工作流名稱",
  "group_id": "群組ID"
}
```

## 設定 OPENAI_API_KEY

在運行前，請確保已設置 OPENAI_API_KEY 環境變量。可以在 `.env` 文件中設置：

```
OPENAI_API_KEY=your_api_key_here
```

## 運行方式

### 啟動 API 服務

```bash
python api.py
```

API 服務將在 `http://0.0.0.0:8000` 上啟動，可以通過 HTTP 請求與 Agent 系統進行交互。
