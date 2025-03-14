import os
import yaml
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from agents import Agent, InputGuardrail, OutputGuardrail, ModelSettings
import copy

class AgentManager:
    """
    Agent管理器，負責從YAML配置文件加載和管理所有agent
    """
    def __init__(
            self, 
            config_file: str = "src/agents.yaml", 
            base_config_file: str = "src/base_config.yaml", 
            dispatcher_config_file: str = "src/agents_dispatcher.yaml"
            ):
        self.dispatcher_config_file = Path(dispatcher_config_file)
        self.config_file = Path(config_file)
        self.base_config_file = Path(base_config_file)
        self.base_config = {}
        self.agents: Dict[str, Agent] = {}
        self.load_base_config()
        self.load_all_agents()
    
    def load_base_config(self) -> None:
        """
        加載基礎配置文件
        """
        if self.base_config_file.exists():
            with open(self.base_config_file, "r", encoding="utf-8") as f:
                self.base_config = yaml.safe_load(f) or {}
        else:
            print(f"警告: 基礎配置文件 {self.base_config_file} 不存在，使用空配置")
            self.base_config = {}
    
    def load_all_agents(self) -> None:
        """
        加載所有agent配置文件
        """
        # 確保配置文件存在
        if not self.config_file.exists():
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在")
        
        # 加載配置文件
        with open(self.config_file, "r", encoding="utf-8") as f:
            main_config = yaml.safe_load(f)
        
        # 加載所有agent
        for agent_type, agent_config in main_config.items():
            self._load_agent(agent_type, agent_config)
            
        # 加載dispatcher配置
        self._load_dispatcher_agent()
    
    def _load_agent(self, agent_type: str, agent_config: Dict[str, Any]) -> None:
        """
        根據配置創建Agent實例
        """
        # 檢查是否啟用
        if not agent_config.get("enabled", True):
            return
        
        # 創建Agent實例
        try:
            # 獲取基本配置
            name = agent_config.get("name", f"{agent_type}_agent")
            instructions = agent_config.get("instructions", "")
            
            # 獲取模型設置，優先使用agent_config中的設置，如果沒有則使用基礎配置
            model_settings_config = agent_config.get("model_settings", self.base_config.get("model_settings", {}))
            model_settings = ModelSettings(
                temperature=model_settings_config.get("temperature", 0.7),
                top_p=model_settings_config.get("top_p", 0.9)
            )
            
            # 創建Agent實例
            agent_instance = Agent(
                name=name,
                instructions=instructions,
                model_settings=model_settings
            )
            
            # 處理工具配置
            if "tools" in agent_config:
                tools = []
                for tool_config in agent_config["tools"]:
                    # 加載工具agent模塊
                    from importlib import import_module
                    tool_module = import_module(tool_config["agent_module"])
                    tool_agent = getattr(tool_module, tool_config["agent_var_name"])
                    
                    # 添加工具
                    tools.append(tool_agent.as_tool(
                        tool_name=tool_config["tool_name"],
                        tool_description=tool_config["tool_description"]
                    ))
                
                # 設置工具
                agent_instance.tools = tools
            
            # 處理handoffs配置
            if "handoffs" in agent_config:
                handoffs = []
                for handoff_config in agent_config["handoffs"]:
                    # 加載handoff agent模塊
                    from importlib import import_module
                    handoff_module = import_module(handoff_config["agent_module"])
                    handoff_agent = getattr(handoff_module, handoff_config["agent_var_name"])
                    
                    # 添加handoff
                    handoffs.append(handoff_agent)
                
                # 設置handoffs
                agent_instance.handoffs = handoffs
            
            # 處理guardrail配置
            if "input_guardrail" in agent_config:
                guardrail_config = copy.deepcopy(agent_config["input_guardrail"])
                                
                from importlib import import_module
                guardrail_module = import_module(guardrail_config["module"])
                guardrail_function = getattr(guardrail_module, guardrail_config["function"])
                
                # 設置guardrail
                agent_instance.input_guardrails = InputGuardrail(guardrail_function=guardrail_function)

            if "output_guardrail" in agent_config:
                guardrail_config = copy.deepcopy(agent_config["output_guardrail"])
                                
                from importlib import import_module
                guardrail_module = import_module(guardrail_config["module"])
                guardrail_function = getattr(guardrail_module, guardrail_config["function"])
                
                # 設置guardrail
                agent_instance.output_guardrails = OutputGuardrail(guardrail_function=guardrail_function)

            
            # 將agent添加到字典中
            self.agents[agent_type] = agent_instance
        except Exception as e:
            print(f"無法創建agent {agent_type}: {e}")
    
    def get_agent(self, agent_type: str) -> Optional[Agent]:
        """
        獲取指定類型的agent
        """
        return self.agents.get(agent_type)
    
    def _load_dispatcher_agent(self) -> None:
        """
        從dispatcher.yaml加載dispatcher agent配置
        """
        # 確保配置文件存在
        if not self.dispatcher_config_file.exists():
            print(f"警告: Dispatcher配置文件 {self.dispatcher_config_file} 不存在，將使用默認配置")
            return
        
        # 加載配置文件
        with open(self.dispatcher_config_file, "r", encoding="utf-8") as f:
            dispatcher_config = yaml.safe_load(f)
        
        # 檢查是否啟用
        if not dispatcher_config.get("enabled", True):
            return
        
        # 獲取基本配置
        name = dispatcher_config.get("name", "Dispatcher Agent")
        instructions = dispatcher_config.get("instructions", "決定使用者的問題應該如何處理並分發到適當的專業Agent")
        
        # 獲取模型設置，優先使用dispatcher_config中的設置，如果沒有則使用基礎配置
        model_settings_config = dispatcher_config.get("model_settings", self.base_config.get("model_settings", {}))
        model_settings = ModelSettings(
            temperature=model_settings_config.get("temperature", 0.7),
            top_p=model_settings_config.get("top_p", 0.9)
        )
        
        # 獲取所有可用的handoff agents
        handoffs = []
        handoff_types = dispatcher_config.get("handoff_types", [])
        for agent_type in handoff_types:
            agent = self.get_agent(agent_type)
            if agent:
                handoffs.append(agent)
        
        # 創建dispatcher agent
        dispatcher_agent = Agent(
            name=name,
            instructions=instructions,
            model_settings=model_settings,
            handoffs=handoffs
        )
        
        # 將創建的dispatcher agent添加到agents字典中
        self.agents["dispatcher"] = dispatcher_agent
    
    def get_dispatcher_agent(self) -> Agent:
        """
        獲取dispatcher agent，用於決定使用哪個agent處理用戶請求
        """
        # 首先嘗試從已加載的agents中獲取
        dispatcher_agent = self.get_agent("dispatcher")
        
        # 如果沒有找到dispatcher agent，則創建一個基本的dispatcher agent
        if not dispatcher_agent:
            # 獲取所有可用的handoff agents
            handoffs = []
            for agent_type, agent in self.agents.items():
                if agent_type != "dispatcher":
                    handoffs.append(agent)
            
            # 創建dispatcher agent
            dispatcher_agent = Agent(
                name="Dispatcher Agent",
                instructions="決定使用者的問題應該如何處理並分發到適當的專業Agent",
                handoffs=handoffs
            )
            
            # 將創建的dispatcher agent添加到agents字典中
            self.agents["dispatcher"] = dispatcher_agent
        
        return dispatcher_agent

# 創建全局agent管理器實例
agent_manager = AgentManager()