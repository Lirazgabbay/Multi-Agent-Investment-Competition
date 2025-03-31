"""
test_agents.py

This test suite verifies that all agents in the `InitAgents` class:
1. Are initialized correctly.
2. Return appropriate responses to messages.
3. Call their assigned tools when needed.
"""
import pytest
from unittest.mock import MagicMock
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from group_chats.init_agents import InitAgents
from finance.LLM_get_financial import quick_ratio
from finance.agents_functions import competative_func, historical_func, qualitative_func
from autogen_core.tools import FunctionTool


@pytest.fixture
def agents():
    """Fixture to initialize agents before running tests."""
    return InitAgents()


@pytest.mark.parametrize("agent_attr,expected_name,expected_tool_functions", [
    ("liquidity_agent", "Liquidity_Analyst", [quick_ratio]),
    ("historical_margin_multiplier_analyst", "Historical_Margin_Multiplier_Analyst", [historical_func]),
    ("competative_margin_multiplier_analyst", "Competative_Margin_Multiplier_Analyst", [competative_func]),
    ("qualitative_analyst", "Qualitative_Analyst", [qualitative_func]),
])
def test_agents_initialization(agents, agent_attr, expected_name, expected_tool_functions):
    """
    Ensure that all agents are correctly initialized with expected names and tools.
    """
    agent = getattr(agents, agent_attr)
    assert agent.name == expected_name
    assert agent._model_client is not None
    
    # Compare tool functions by name
    agent_tool_names = []
    for tool in agent._tools:
        if isinstance(tool, FunctionTool):
            agent_tool_names.append(tool._func.__name__)
        else:
            agent_tool_names.append(tool.__name__)

    
    expected_tool_names = [func.__name__ for func in expected_tool_functions]
    assert set(agent_tool_names) == set(expected_tool_names), f"Tool mismatch: {agent_tool_names} != {expected_tool_names}"


@pytest.mark.asyncio
@pytest.mark.parametrize("agent_attr,query,expected_keyword", [
    ("liquidity_agent", "Analyze AAPL liquidity", "liquid"),
    ("historical_margin_multiplier_analyst", "Analyze historical margin for TSLA", "historical"),
    ("competative_margin_multiplier_analyst", "Analyze competitive market for AMZN", "competitive"),
    ("qualitative_analyst", "Qualitative assessment of MSFT", "qualitative"),
])
async def test_agents_responses(agents, agent_attr, query, expected_keyword):
    """
    Run the actual on_messages() function and ensure it behaves as expected.
    """
    agent = getattr(agents, agent_attr)

    response = await agent.on_messages(
        [TextMessage(content=query, source="user")],
        CancellationToken()
    )

    assert response is not None, "Response should not be None"
    assert hasattr(response, "chat_message"), "Response should have 'chat_message' attribute"
    assert hasattr(response.chat_message, "content"), "chat_message should have 'content' attribute"
    assert isinstance(response.chat_message.content, str), "Response content should be a string"


@pytest.mark.asyncio
@pytest.mark.parametrize("agent_attr,tool_func_name,query", [
    ("liquidity_agent", "quick_ratio", "Analyze AAPL liquidity"),
    ("historical_margin_multiplier_analyst", "historical_func", "Analyze historical margin for TSLA"),
    ("competative_margin_multiplier_analyst", "competative_func", "Analyze competitive market for AMZN"),
    ("qualitative_analyst", "qualitative_func", "Qualitative assessment of MSFT"),
])
async def test_agents_tool_usage(agents, agent_attr, tool_func_name, query, monkeypatch):
    """
    Ensure agents correctly use their assigned tools by mocking the actual functions.
    """
    agent = getattr(agents, agent_attr)
    
    mock_function = MagicMock(return_value="Test Response") # Create a mock function that we'll use to replace the real function
    
    for i, tool in enumerate(agent._tools):
        if isinstance(tool, FunctionTool) and tool._func.__name__ == tool_func_name:
            original_function = tool._func
            tool._func = mock_function
            break
    
    try:
        await agent.on_messages(
            [TextMessage(content=query, source="user")],
            CancellationToken()
        )
        
        assert mock_function.called, f"The tool function {tool_func_name} was not called"
    
    finally:
        for i, tool in enumerate(agent._tools):
            if isinstance(tool, FunctionTool) and tool._func == mock_function:
                tool._func = original_function
                break


@pytest.mark.asyncio
async def test_search_agent_tool_exists(agents):
    """
    Test that the search agent is properly initialized and can respond to queries.
    """
    agent = agents.search_agent
    assert agent.name == "Google_Search_Agent"
    assert agent._model_client is not None
    
    assert len(agent._tools) > 0
    
    has_search_tool = False
    for tool in agent._tools:
        if isinstance(tool, FunctionTool) and 'search' in tool.name.lower():
            has_search_tool = True
            break
    
    assert has_search_tool, "Search agent should have a search tool"
    
@pytest.mark.asyncio
async def test_search_agent_functionality(agents, monkeypatch):
    """
    Test that the search agent is properly initialized and can perform search operations.
    Directly targets the _func attribute which is used in this implementation.
    """
    agent = agents.search_agent
    assert agent.name == "Google_Search_Agent"
    assert agent._model_client is not None
    
    search_tool = None
    for tool in agent._tools:
        if isinstance(tool, FunctionTool) and 'search' in str(tool.name).lower():
            search_tool = tool
            break
    
    assert search_tool is not None, "Search agent should have a search tool"
    
    assert hasattr(search_tool, '_func'), "Search tool should have a _func attribute"
    
    mock_search_results = {
        "results": [
            {
                "title": "Tesla Stock Performance 2023",
                "link": "https://example.com/tesla-stock",
                "snippet": "Tesla stock has shown significant growth in recent quarters.",
                "body": "This is detailed information about Tesla stock performance."
            }
        ]
    }
    
    original_func = search_tool._func
    
    mock_search = MagicMock(return_value=mock_search_results)
    
    monkeypatch.setattr(search_tool, '_func', mock_search)
    
    try:
        # Test with a direct query that should trigger the search tool
        response = await agent.on_messages(
            [TextMessage(
                content="I need information about Tesla stock performance. Please search for this specific query.", 
                source="red_flags_agent"  # Simulate request from another agent
            )],
            CancellationToken()
        )
        
        response_content = response.chat_message.content
        
        assert response_content, "Response should not be empty"
        assert len(response_content) > 50, "Response should be substantial"
        
    
    finally:
        if getattr(search_tool, '_func', None) is mock_search:
            search_tool._func = original_func


@pytest.mark.asyncio
async def test_search_agent_basic_functionality(agents):
    """
    A simplified test that just verifies the search agent responds to messages,
    without trying to mock the underlying search functionality.
    """
    agent = agents.search_agent
    
    response = await agent.on_messages(
        [TextMessage(content="Can you search for information about stock markets?", source="user")],
        CancellationToken()
    )
    
    assert response is not None
    assert hasattr(response, "chat_message")
    assert response.chat_message.content, "Response should not be empty"
    
    content = response.chat_message.content.lower()
    relevant_terms = ['search', 'information', 'data', 'result', 'find']
    has_relevant_term = any(term in content for term in relevant_terms)
    
    assert has_relevant_term, "Response should mention search or information-related terms"