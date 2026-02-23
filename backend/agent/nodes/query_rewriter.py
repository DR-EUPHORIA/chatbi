"""查询改写 Node — 将用户自然语言问题改写为结构化查询"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.query_rewriter import QUERY_REWRITER_SYSTEM_PROMPT, QUERY_REWRITER_USER_PROMPT
from agent.llm import get_llm


def query_rewriter_node(state: AgentState) -> dict:
    """将用户的自然语言问题改写为更结构化、更明确的查询表达"""

    user_message = state.get("user_message", "")
    extracted_entities = state.get("extracted_entities", {})
    conversation_history = state.get("conversation_history", [])

    step = {
        "node_name": "query_rewriter",
        "status": NodeStatus.RUNNING.value,
        "title": "查询改写",
        "detail": "正在改写用户查询...",
        "data": {},
    }

    llm = get_llm()
    prompt = QUERY_REWRITER_USER_PROMPT.format(
        user_message=user_message,
        extracted_entities=json.dumps(extracted_entities, ensure_ascii=False),
        conversation_history=json.dumps(conversation_history[-5:], ensure_ascii=False) if conversation_history else "[]",
    )

    response = llm.invoke([
        {"role": "system", "content": QUERY_REWRITER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response.content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                result = {}
        else:
            result = {}

    if not isinstance(result, dict):
        result = {
            "rewritten_query": user_message,
            "query_type": "unknown",
            "confidence": 0.5,
        }

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"查询改写完成，类型: {result.get('query_type', 'unknown')}"
    step["data"] = {
        "original_query": user_message,
        "rewritten_query": result.get("rewritten_query", ""),
        "query_type": result.get("query_type", ""),
    }

    return {
        "rewritten_query": result.get("rewritten_query", user_message),
        "query_type": result.get("query_type", "unknown"),
        "query_confidence": result.get("confidence", 0.5),
        "steps": [step],
    }
