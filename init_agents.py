import autogen
from config.config_list_LLM import CONFIG_LLM_GPT4
from config.system_messages import SYS_MSG_MANAGER_CONFIG, SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG
from finance.LLM_get_financial import get_related_companies, quick_ratio
from finance.LLM_get_qualitative import extract_business_info, get_company_data
from finance.profit_margin import calculate_profit_margins
from finance.profit_multipliers import price_to_EBIT_ratio, ratios

class InitAgents():
    def __init__(self):        
        self.liquidity_agent = autogen.AssistantAgent(
            name="Liquidity_Analyst",
            llm_config = {
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
                "functions": [
                    {
                        "name": "quick_ratio",
                        "description": "Calculates the Quick Ratio for a given stock symbol and year.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock ticker symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the quick ratio is calculated.",
                                }
                            },
                            "required": ["symbol", "year"],
                        },
                    },
                ],
            },
            system_message=SYSTEM_MSG_LIQUIDITY_CONFIG,
            human_input_mode="NEVER",
            function_map={"quick_ratio": quick_ratio}
        )
        
        # self.historical_margin_multiplier_analyst = autogen.AssistantAgent(
        #     name="Historical_Margin_Multiplier_Analyst",
        #     llm_config={
        #         "config_list": CONFIG_LLM_GPT4,
        #         "temperature": 0.4,
        #         "functions": [
        #             {
        #                 "name": "price_to_EBIT_ratio",
        #                 "description": "Calculate the Price/EBIT ratio for a given stock symbol and year.",
        #                 "parameters": {
        #                     "type": "object",
        #                     "properties": {
        #                         "symbol": {
        #                             "type": "string",
        #                             "description": "Stock symbol for the company.",
        #                         },
        #                         "year": {
        #                             "type": "integer",
        #                             "description": "Year for which the ratio is calculated."
        #                         }
        #                     },
        #                     "required": ["symbol", "year"]
        #                 }
        #             }
        #         ],
        #     },
        #     system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
        #     human_input_mode="NEVER",
        #     function_map={"price_to_EBIT_ratio":price_to_EBIT_ratio}
        # )

        self.historical_margin_multiplier_analyst = autogen.AssistantAgent(
            name="Historical_Margin_Multiplier_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
                "functions": [
                    {
                        "name": "price_to_EBIT_ratio",
                        "description": "Calculate the Price/EBIT ratio for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the ratio is calculated."
                                }
                            },
                            "required": ["symbol", "year"]
                        }
                    },
                    {
                        "name": "ratios",
                        "description": "Calculate the ratios for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the ratio is calculated."
                                }
                            },
                            "required": ["symbol", "year"]
                        }
                    },
                    {
                        "name": "calculate_profit_margins",
                        "description": "Calculate profit margins for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the ratio is calculated."
                                }
                            },
                            "required": ["symbol", "year"]
                        }
                    }
                ],
            },
            system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
            human_input_mode="NEVER",
            function_map={"price_to_EBIT_ratio":price_to_EBIT_ratio,"ratios": ratios, "calculate_profit_margins": calculate_profit_margins}
        )

        # self.historical_margin_multiplier_analyst = autogen.AssistantAgent(
        #     name="Historical_Margin_Multiplier_Analyst",
        #     llm_config={
        #         "config_list": CONFIG_LLM_GPT4,
        #         "temperature": 0.4,
        #         "functions": [
        #             {
        #                 "name": "quick_ratio",
        #                 "description": "Calculates the Quick Ratio for a given stock symbol and year.",
        #                 "parameters": {
        #                     "type": "object",
        #                     "properties": {
        #                         "symbol": {
        #                             "type": "string",
        #                             "description": "Stock ticker symbol for the company.",
        #                         },
        #                         "year": {
        #                             "type": "integer",
        #                             "description": "Year for which the quick ratio is calculated.",
        #                         }
        #                     },
        #                     "required": ["symbol", "year"],
        #                 },
        #             },
        #         ],
        #     },
        #     system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
        #     human_input_mode="NEVER",
        #     function_map={"quick_ratio": quick_ratio}
        # )

        self.competative_margin_multiplier_analyst = autogen.AssistantAgent(
            name="Competative_Margin_Multiplier_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
                "functions": [
                    {
                        "name": "get_related_companies",
                        "description": "Get related companies for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The symbol of the company to get related companies for"
                                },
                            },
                            "required": ["symbol"]
                        }
                    },
                    {
                        "name": "price_to_EBIT_ratio",
                        "description": "Calculate the Price/EBIT ratio for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the ratio is calculated."
                                }
                            },
                            "required": ["symbol", "year"]
                        }
                    },
                    {
                        "name": "ratios",
                        "description": "Calculate the ratios for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the ratio is calculated."
                                }
                            },
                            "required": ["symbol", "year"]
                        }
                    },
                    {
                        "name": "calculate_profit_margins",
                        "description": "Calculate profit margins for a given stock symbol.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol for the company.",
                                },
                                "year": {
                                    "type": "integer",
                                    "description": "Year for which the ratio is calculated."
                                }
                            },
                            "required": ["symbol", "year"]
                        }
                    }
                ]
            },
            system_message=SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG,
            human_input_mode="NEVER",
            function_map={"get_related_companies": get_related_companies, "ratios": ratios, "price_to_EBIT_ratio": price_to_EBIT_ratio,"calculate_profit_margins": calculate_profit_margins}
        )


        self.qualitative_analyst = autogen.AssistantAgent(
            name="Qualitative_Analyst",
            llm_config={
                "config_list": CONFIG_LLM_GPT4,
                "temperature": 0.4,
                "functions": [
                    {
                        "name": "extract_business_info",
                        "description": "Extract strategic elements from company information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The stock symbol of the company."
                                }
                            },
                            "required": ["symbol"]
                        }
                    },
                    {
                        "name": "get_company_data",
                        "description": "Fetch news articles related to the company.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The stock symbol."
                                }
                            },
                            "required": ["symbol"]
                        }
                    }
                ]
            },
            system_message=SYSTEM_MSG_QUALITATIVE_CONFIG,
            human_input_mode="NEVER",
            function_map={"extract_business_info": extract_business_info, "get_company_data": get_company_data}
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