import yaml
from pathlib import Path
from agents import Agent, ModelSettings

# 讀取基礎配置
base_config_path = Path("src/base_config.yaml")
base_config = {}
if base_config_path.exists():
    with open(base_config_path, "r", encoding="utf-8") as f:
        base_config = yaml.safe_load(f) or {}

# 獲取模型設置
model_settings_config = base_config.get("model_settings", {})
model_settings = ModelSettings(
    temperature=model_settings_config.get("temperature", 0.7),
    top_p=model_settings_config.get("top_p", 0.9)
)

french_agent = Agent(
    name="French agent",
    instructions="翻譯成法語",
    model_settings=model_settings,
)