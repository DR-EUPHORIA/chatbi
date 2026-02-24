"""意图路由 Node — 识别用户意图并路由到对应处理流程"""

import json
from agent.state import AgentState, IntentType, NodeStatus
from agent.prompts.router import ROUTER_SYSTEM_PROMPT, ROUTER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt

VALID_INTENTS = {t.value for t in IntentType}


def router_node(state: AgentState) -> dict:
    """识别用户意图，路由到对应的处理流程"""

    user_message = state.get("user_message", "")

    step = {
        "node_name": "router",
        "status": NodeStatus.RUNNING.value,
        "title": "意图识别",
        "detail": "正在识别您的分析意图...",
        "data": {},
    }

    llm = get_llm()
    prompt = safe_format_prompt(ROUTER_USER_PROMPT, 
        user_message=user_message,
        enhanced_query=user_message,
    )

    response = llm.invoke([
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"intent": "data_query", "reasoning": "默认作为数据查询处理", "chat_response": ""}

    intent_str = result.get("intent", "data_query")
    if intent_str not in VALID_INTENTS:
        intent_str = "data_query"

    updates: dict = {"intent": intent_str}

    if intent_str == IntentType.CHAT.value:
        updates["final_answer"] = result.get("chat_response", "你好！我是 ChatBI 智能分析助手，有什么数据分析需求可以告诉我。")
        step["detail"] = "识别为闲聊，直接回复"
    else:
        step["detail"] = f"识别意图：{intent_str}（{result.get('reasoning', '')}）"

    step["status"] = NodeStatus.SUCCESS.value
    step["data"] = {"intent": intent_str, "reasoning": result.get("reasoning", "")}

    updates["steps"] = [step]
    return updates