from autogen import AssistantAgent, UserProxyAgent
from pathlib import Path
from autogen.coding import LocalCommandLineCodeExecutor
from agents.llm_configs import AnalystConfig  # Import the AnalystConfig

# Setting up the code executor
workdir = Path("coding")
workdir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=workdir)

class AnalystAgent:
    def __init__(self, name: str, focus: str):
        self.agent = AssistantAgent(
            name=name,
            system_message=f"""
            You are an expert financial analyst focusing on {focus}. Analyze the provided data and provide a summary.
            Focus on:
            1. Key insights
            2. Current market position
            3. Potential risks and opportunities
            
            Provide clear, actionable insights based on your analysis.""",
            llm_config={
                "config_list": [{
                    "model": AnalystConfig.LLM_MODEL,
                    "base_url": AnalystConfig.BASE_URL,
                    "api_key": AnalystConfig.API_KEY,
                }],
                "temperature": AnalystConfig.TEMPERATURE
            }
        )

    async def analyze(self, request: str) -> str:
        """Analyze the market data."""
        user_proxy_agent = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            code_execution_config={"executor": code_executor},
            is_termination_msg=lambda msg: True,  # Automatically proceed without waiting for input
        )
        
        # Call initiate_chat and get the result directly
        chat_result = user_proxy_agent.initiate_chat(self.agent, message=request)
        
        # Return the summary from the chat result
        return chat_result.summary  # Use 'summary' instead of 'content'