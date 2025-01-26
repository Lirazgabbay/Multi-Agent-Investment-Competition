import autogen
from config.available_functions import LIQUIDITY_AVAILABLE_FUNCTIONS, MARGIN_MULTIPLIER_AVAILABLE_FUNCTIONS, QUALITATIVE_AVAILABLE_FUNCTIONS
from config.config_list_LLM import CONFIG_LLM_GPT4
from config.system_messages import SYS_MSG_MANAGER_CONFIG, SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG
from finance.LLM_get_financial import quick_ratio
from finance.LLM_get_qualitative import extract_business_info, get_company_data
from finance.profit_margin import gross_profit_margin, net_profit_margin, operational_profit_margin
from finance.profit_multipliers import price_earnings_to_growth_ratio, price_sales_ratio, price_to_EBIT_ratio, price_to_book_value_ratio, price_to_earnings_ratio

class InitAgents():
    def __init__(self):        
        self.liquidity_agent = autogen.AssistantAgent(
            name="Liquidity_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
            },
            system_message=SYSTEM_MSG_LIQUIDITY_CONFIG,
            human_input_mode="NEVER",
        )

        self.historical_margin_multiplier_analyst = autogen.AssistantAgent(
            name="Historical_Margin_Multiplier_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
            },
            system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
            human_input_mode="NEVER",
        )

        self.competative_margin_multiplier_analyst = autogen.AssistantAgent(
            name="Competative_Margin_Multiplier_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
            },
            system_message=SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG,
            human_input_mode="NEVER",
        )


        self.qualitative_analyst = autogen.AssistantAgent(
            name="Qualitative_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
            },
            system_message=SYSTEM_MSG_QUALITATIVE_CONFIG,
            human_input_mode="NEVER"
        )

        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("DISCUSSION_END"),
            code_execution_config=False,
            system_message="The agent that initialize the conversation",
        )

        self.manager_agent = autogen.AssistantAgent(
            name="Manager",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
            },
            system_message=SYS_MSG_MANAGER_CONFIG,
            human_input_mode="NEVER",
        )

        self.summary_agent = autogen.AssistantAgent(
            name="Summary_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
            },
            system_message="Provide the consensus that the agents have reached and a short summary on the final decision.",
            human_input_mode="NEVER",
        )