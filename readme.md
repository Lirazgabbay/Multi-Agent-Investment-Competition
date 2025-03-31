# 🧠 Multi-Agent-Investment-Competition

This project explores a bold idea: a team of AI agents, each with a specialized role, working collaboratively to make strategic investment decisions.

This system explores collaborative intelligence using domain-specific roles, real-time conversation logic, financial APIs, and LLMs.

## Overview
This system simulates an AI-powered investment competition between two virtual investment houses. Each house consists of multiple agents with domain-specific roles who analyze data, discuss strategies, and make investment decisions.

Inputs
    - Budget
    - Stock symbol
    - Range of years for analysis

Outputs
    - Investment House 1: Discussion and Final Decision
    - Investment House 2: Discussion and Final Decision
    - Judges Panel: Evaluation and Final Verdict

All conversations are presented in real-time using a Streamlit interface.

## AI Agent Roles
### Investment House Agents
| Role | Description |
|------|-------------|
| Manager | Guides the discussion and ensures all perspectives are considered |
| Liquidity Analyst | Evaluates short-term liquidity using the `quick_ratio()` function |
| Historical Margin Analyst | Analyzes margins and valuation using `historical_func()` |
| Competitive Analyst | Compares the company to peers using financial ratios and benchmarks |
| Qualitative Analyst | Evaluates leadership, strategy, and market conditions |
| Red Flags Analyst | Identifies hidden financial risks |
| Red Flags Liquidity Analyst | Detects potential issues with liquidity |
| Solid Analyst | Challenges overly optimistic views and presents risk scenarios |
| Google Search Analyst | Retrieves relevant web content using live search |
| Summary Analyst | Summarizes the discussion and final decision |

### Judges Panel Agents
| Role | Description |
|------|-------------|
| Manager | Coordinates the conversation and delivers the final verdict |
| Profit Judge | Calculates actual profit or loss based on historical prices |
| Web Surfer Judge | Brings in relevant external context such as news and market trends |
| Decision Quality Judge | Evaluates the logic and completeness of the investment decision |
| Qualitative Analyst | Assesses strategic and qualitative factors |

## System Flow
1. Each investment house initiates an internal group chat.
2. The Selector agent dynamically chooses which agent should speak next based on the conversation.
3. The discussion ends either by consensus among all agents or by exceeding the message threshold.
4. A panel of independent judge agents evaluates the decisions from both investment houses.
5. The panel declares which house made the better investment decision.

## Agents’ Tools
- **Liquidity Analyst**
  - `quick_ratio()`: Measures immediate liquidity

- **Historical Analyst**
  - `calculate_profit_margins()`: Computes gross, operating, and net profit margins
  - `price_to_EBIT_ratio()`: Valuation based on EBIT
  - `ratios()`: Retrieves P/E, P/B, PEG, and P/S ratios

- **Competitive Analyst**
  - `get_related_companies()`: Identifies peers via external API
  - `price_to_EBIT_ratio()`, `ratios()`: Peer comparison

- **Qualitative Analyst**
  - `extract_business_info()`: Retrieves business description
  - `get_company_data()`: Fetches recent news

- **Search Agent**
  - `google_search()`: Web scraping for external context

- **Judges**
  - `judge_profit()`: Computes investment performance
  - `get_investment_house_discussion()`: Reviews decision quality

## APIs and Database
- Financial data is retrieved using FMP and Polygon.io APIs.
- API calls are cached using SQLite to reduce redundant requests, improve speed, and manage rate limits.
- Caching is implemented by checking for existing entries before making new requests.

## Models
The system uses multiple language models optimized for different roles:
- **GPT-3.5-Turbo**: Manager agents for coordinating and routing messages
- **GPT-4o**: Judges and summary roles requiring complex reasoning
- **GPT-4o Mini**: Tool-augmented agents requiring structured financial logic
- **Gemini (via OpenRouter)**: Used for summary and risk analysis to ensure diversity in reasoning styles