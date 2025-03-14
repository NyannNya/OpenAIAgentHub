import yaml
from pathlib import Path
from agents import Agent, GuardrailFunctionOutput, Runner, ModelSettings, trace
from pydantic import BaseModel

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

# 定義安全檢查模型
class SafetyGuard(BaseModel):
    is_valid: bool
    reasoning: str

# guardrail agent 設定
input_guardrail_config = {
    "name": "Homework Guardrail",
    "instructions": "判斷是否想要詢問課業問題"
}

guardrail_agent = Agent(
    name=input_guardrail_config["name"],
    instructions=input_guardrail_config["instructions"],
    model_settings=model_settings,
    output_type=SafetyGuard)

async def input_validate_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(guardrail_agent.output_type)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_valid,
    )