"""实体抽取 Node — 从用户问题中提取关键实体"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.entity_extractor import ENTITY_EXTRACTOR_SYSTEM_PROMPT, ENTITY_EXTRACTOR_USER_PROMPT
from agent.llm import get_llm


def entity_extractor_node(state: AgentState) -> dict:
    """从用户问题中提取时间、维度、指标、过滤条件等关键实体"""

    user_message = state.get("user_message", "")
    schema_info = state.get("matched_tables", [])

    step = {
        "node_name": "entity_extractor",
        "status": NodeStatus.RUNNING.value,
        "title": "实体抽取",
        "detail": "正在从问题中提取关键实体...",
        "data": {},
    }

    llm = get_llm()
    prompt = ENTITY_EXTRACTOR_USER_PROMPT.format(
        user_message=user_message,
        schema_info=json.dumps(schema_info, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": ENTITY_EXTRACTOR_SYSTEM_PROMPT},
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
            "time_entities": [],
            "dimension_entities": [],
            "metric_entities": [],
            "filter_entities": [],
            "aggregation_type": None,
        }

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"提取到 {len(result.get('metric_entities', []))} 个指标实体"
    step["data"] = {
        "time_count": len(result.get("time_entities", [])),
        "dimension_count": len(result.get("dimension_entities", [])),
        "metric_count": len(result.get("metric_entities", [])),
        "filter_count": len(result.get("filter_entities", [])),
    }

    return {
        "extracted_entities": result,
        "time_entities": result.get("time_entities", []),
        "dimension_entities": result.get("dimension_entities", []),
        "metric_entities": result.get("metric_entities", []),
        "filter_entities": result.get("filter_entities", []),
        "steps": [step],
    }
