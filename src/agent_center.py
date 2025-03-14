from typing import Dict, Optional, List, Any
from pathlib import Path
from agents import Agent

# 導入所需的加載器
from .utils.agent_loader import agent_manager

class AgentCenter:
    """
    Agent中心，作為整個系統的核心組件，負責管理和協調所有Agent
    提供統一的接口來獲取、註冊和管理各種類型的Agent
    """
    def __init__(self):
        self.agent_manager = agent_manager
        self._agents_cache: Dict[str, Agent] = {}
    
    def get_agent(self, agent_type: str) -> Optional[Agent]:
        """
        獲取指定類型的Agent
        首先嘗試從緩存中獲取，如果緩存中不存在，則從agent_manager中加載
        
        Args:
            agent_type: Agent類型名稱
            
        Returns:
            Agent實例，如果不存在則返回None
        """
        # 檢查 cache
        if agent_type in self._agents_cache:
            return self._agents_cache[agent_type]
        
        # 從 agent_manager 中加載
        agent = self.agent_manager.get_agent(agent_type)
        if agent:
            self._agents_cache[agent_type] = agent
            return agent
            
        return None
    
    def get_dispatcher_agent(self) -> Agent:
        """
        獲取dispatcher agent，用於決定使用哪個agent處理用戶請求
        
        Returns:
            Dispatcher Agent實例
        """
        return self.get_agent("dispatcher") or self.agent_manager.get_dispatcher_agent()
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """
        獲取所有已加載的Agent
        
        Returns:
            所有Agent的字典，鍵為Agent類型，值為Agent實例
        """
        # 返回agent_manager中的所有agent
        return self.agent_manager.agents
    
    def register_agent(self, agent_type: str, agent: Agent) -> None:
        """
        註冊一個新的Agent
        
        Args:
            agent_type: Agent類型名稱
            agent: Agent實例
        """
        self._agents_cache[agent_type] = agent

# 創建全局Agent中心實例
agent_center = AgentCenter()

# 導出dispatcher agent供main.py使用
dispatcher_agent = agent_center.get_dispatcher_agent()