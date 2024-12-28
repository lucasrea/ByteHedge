from autogen import AssistantAgent, UserProxyAgent
from pathlib import Path
from autogen.coding import LocalCommandLineCodeExecutor
from agents.llm_configs import ManagerConfig  # Import the ManagerConfig

# Setting up the code executor
workdir = Path("coding")
workdir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=workdir)

class ManagerAgent:
    def __init__(self, name: str):
        self.agent = AssistantAgent(
            name=name,
            system_message=f"""You are a hedge fund manager. Your role is to analyze the summaries provided by the analysts and make informed investment decisions.
            Focus on:
            1. Combining insights from technical and fundamental analyses.
            2. Evaluating risks and opportunities based on market conditions.
            3. Providing clear recommendations for investment strategies.
            
            Provide a concise decision based on the analysis provided by the analysts.""",
            llm_config={
                "config_list": [{
                    "model": ManagerConfig.LLM_MODEL,
                    "base_url": ManagerConfig.BASE_URL,
                    "api_key": ManagerConfig.API_KEY,
                }],
                "temperature": ManagerConfig.TEMPERATURE
            }
        )

    async def make_decision(self, analyst_summaries: list) -> str:
        """Make a decision based on analysts' summaries."""
        user_proxy_agent = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            code_execution_config={"executor": code_executor},
            is_termination_msg=lambda msg: True,  # Automatically proceed without waiting for input
        )
        
        # Prepare the request message for the manager agent
        request = f"Here are the analyst summaries:\n" + "\n".join(analyst_summaries) + "\n\nBased on this information, please provide your investment decision."
        
        # Call initiate_chat and get the result directly
        chat_result =  user_proxy_agent.initiate_chat(self.agent, message=request)
        
        # Return the decision from the chat result
        return chat_result.summary  # Use 'summary' instead of 'content'