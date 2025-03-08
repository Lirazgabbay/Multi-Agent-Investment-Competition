import streamlit as st

def load_custom_styles():
    """Loads custom CSS for chat styling."""
    st.markdown(
        """
        <style>
            .chat-container {
                display: flex;
                flex-direction: column;
            }
            .chat-bubble {
                max-inline-size: 75%;
                padding: 10px 15px;
                margin: 5px;
                border-radius: 15px;
                font-size: 16px;
                word-wrap: break-word;
                white-space: pre-wrap;
                display: inline-block;
            }
            .user-message {
                background-color: #0084ff;
                color: white;
                align-self: flex-end;
            }
            .agent-message {
                background-color: #f1f0f0;
                color: black;
                align-self: flex-start;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
