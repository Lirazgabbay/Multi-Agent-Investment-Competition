# judge_agent.py

import os
import autogen

class JudgeAgent:
    def __init__(self):
        self.llm_config = {
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": os.environ.get("OPENAI_API_KEY")
                }
            ],
            "timeout": 90
        }


    def judge_investment_house_outputs(self, house1_final_decision: str, house2_final_decision: str) -> str:
        """Compare two final decisions and return a verdict."""
        
        system_prompt = (
            "You are a financial expert comparing final decisions from two investment houses.\n"
            "Please:\n"
            "1) Compare them on clarity, thoroughness, and logic.\n"
            "2) Decide which one (if any) is better or if it's a tie.\n"
            "3) Provide a short explanation.\n"
        )

        # Create a judge agent
        judge_agent = autogen.AssistantAgent(
            name="Investment_Judge",
            system_message=system_prompt,
            llm_config=self.llm_config
        )

        # Create a user proxy agent
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={"use_docker": False}
        )

        # Prepare the judgment message
        judgment_message = (
            f"=== House 1 Manager Conclusion ===\n{house1_final_decision}\n\n"
            f"=== House 2 Manager Conclusion ===\n{house2_final_decision}\n\n"
        )

        # Create a group chat
        groupchat = autogen.GroupChat(
            agents=[user_proxy, judge_agent],
            messages=[],
            max_round=2,
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
        )

        # Create a manager
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=self.llm_config
        )

        # Initiate chat and get the response
        user_proxy.initiate_chat(manager, message=judgment_message)
        # Return the last message from the judge
        return groupchat.messages[-1]["content"]


# # Test the JudgeAgent
# manager_content1 = (
#     """As the Manager, I appreciate all the valuable insights provided by the team. The consensus is clear: we have a """
#     """balanced and diversified portfolio that captures both stability and growth potential.\n\n"""
#     """Here is the final allocation of our $100,000 investment:\n"""
#     """\n"""
#     """- AAPL: $30,000 for 200 shares\n"""
#     """- LULU: $30,000 for 150 shares\n"""
#     """- JNJ: $30,000 for 176 shares\n"""
#     """- NFLX: $5,000 for 10 shares\n"""
#     """- TSLA: $5,000 for 7 shares\n"""
#     """\n"""
#     """This allocation reflects the strong performance and lower risk of AAPL, LULU, and JNJ, while still providing """
#     """some exposure to the potential upside of NFLX and TSLA.\n"""
#     """\n"""
#     """Let's proceed with this investment plan and continue to monitor the performance of these investments, adjusting """
#     """the portfolio as necessary based on market changes and opportunities."""
# )

# judge = JudgeAgent()
# verdict = judge.judge_investment_house_outputs(manager_content1, manager_content1)

# print("\n======================= VERDICT =======================")
# print(verdict)
# print("======================================================")