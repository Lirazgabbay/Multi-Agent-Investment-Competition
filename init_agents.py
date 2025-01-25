import autogen
from config.agent_config import COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, HISTORICAL_MARGIN_MULTIPLIER_CONFIG, MODERATOR_CONFIG, QUALITATIVE_CONFIG, SOCIAL_ANALYST_CONFIG, LIQUIDITY_CONFIG
from config.system_messages import SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG
# TODO: refactor all base on the agents  

class InitAgents():
    def __init__(self):        
        # Create the agents

        # is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        # max_consecutive_auto_reply: Optional[int] = None,

        self.liquidity_agent = autogen.AssistantAgent(
            name=LIQUIDITY_CONFIG["name"],
            llm_config=LIQUIDITY_CONFIG["llm_config"],
            system_message=SYSTEM_MSG_LIQUIDITY_CONFIG,
            human_input_mode="NEVER"
        )

        self.historical_margin_multiplier_analyst = autogen.AssistantAgent(
            name=HISTORICAL_MARGIN_MULTIPLIER_CONFIG["name"],
            llm_config=SOCIAL_ANALYST_CONFIG["llm_config"],
            system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
            human_input_mode="NEVER"
        )

        self.competative_margin_multiplier_analyst = autogen.AssistantAgent(
            name=COMPETATIVE_MARGIN_MULTIPLIER_CONFIG["name"],
            llm_config=COMPETATIVE_MARGIN_MULTIPLIER_CONFIG["llm_config"],
            system_message=SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG,
            human_input_mode="NEVER"
        )

        self.quantitative_analyst = autogen.AssistantAgent(
            name=QUALITATIVE_CONFIG["name"],
            llm_config=QUALITATIVE_CONFIG["llm_config"],
            system_message=SYSTEM_MSG_QUALITATIVE_CONFIG,
            human_input_mode="NEVER"
        )



        # self.moderator = autogen.AssistantAgent(
        #     name="Investment_Moderator",
        #     system_message=MODERATOR_CONFIG["system_message"],
        #     llm_config=MODERATOR_CONFIG["llm_config"]
        # )

        # # Create the user proxy
        # self.user_proxy = autogen.UserProxyAgent(
        #     name="user_proxy",
        #     human_input_mode="NEVER",
        #     max_consecutive_auto_reply=10,
        #     is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("DISCUSSION_END"),
        #     code_execution_config=False,
        # )
