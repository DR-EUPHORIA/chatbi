"""答案生成 Node — 生成最终的自然语言回答"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.answer_generator import ANSWER_GENERATOR_SYSTEM_PROMPT, ANSWER_GENERATOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def answer_generator_node(state: AgentState) -> dict:
    """整合所有分析结果，生成最终的自然语言回答"""

    user_message = state.get("user_message", "")
    executive_summary = state.get("executive_summary", "")
    key_insights = state.get("key_insights", [])
    recommendations = state.get("recommendations", [])
    sql_result = state.get("sql_result", [])
    chart_type = state.get("chart_type", "")

    step = {
        "node_name": "answer_generator",
        "status": NodeStatus.RUNNING.value,
        "title": "答案生成",
        "detail": "正在生成最终回答...",
        "data": {},
    }

    llm = get_llm()
    prompt = safe_format_prompt(ANSWER_GENERATOR_USER_PROMPT, 
        user_message=user_message,
        executive_summary=executive_summary,
        key_insights=json.dumps(key_insights, ensure_ascii=False),
        recommendations=json.dumps(recommendations, ensure_ascii=False),
        data_row_count=len(sql_result),
        chart_type=chart_type,
    )

    response = llm.invoke([
        {"role": "system", "content": ANSWER_GENERATOR_SYSTEM_PROMPT},
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
            "answer": response.content,
            "answer_type": "text",
            "confidence": 0.8,
            "sources": [],
        }

    answer = result.get("answer", "")
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"生成了 {len(answer)} 字的回答"
    step["data"] = {
        "answer_length": len(answer),
        "answer_type": result.get("answer_type", "text"),
        "confidence": result.get("confidence", 0.8),
    }

    return {
        "final_answer": answer,
        "answer_type": result.get("answer_type", "text"),
        "answer_confidence": result.get("confidence", 0.8),
        "answer_sources": result.get("sources", []),
        "steps": [step],
    }
