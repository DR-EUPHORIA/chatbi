"""实体抽取 Node — 从用户问题中提取关键实体"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.entity_extractor import ENTITY_EXTRACTOR_SYSTEM_PROMPT, ENTITY_EXTRACTOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def entity_extractor_node(state: AgentState) -> dict:
    """从用户问题中提取时间、维度、指标、过滤条件等关键实体"""

    user_message = state.get("user_message", "")
    schema_info = state.get("matched_tables", [])
    glossary = state.get("glossary", {})

    step = {
        "node_name": "entity_extractor",
        "status": NodeStatus.RUNNING.value,
        "title": "实体抽取",
        "detail": "正在从问题中提取关键实体...",
        "data": {},
    }

    llm = get_llm()
    dataset_info = json.dumps(schema_info, ensure_ascii=False) if schema_info else "[]"
    glossary_info = json.dumps(glossary, ensure_ascii=False) if glossary else "暂无业务术语表"

    # 同时提供 dataset_info/schema_info，兼容不同版本的 Prompt 占位符命名
    prompt = safe_format_prompt(ENTITY_EXTRACTOR_USER_PROMPT, 
        user_message=user_message,
        dataset_info=dataset_info,
        schema_info=dataset_info,
        glossary=glossary_info,
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
        result = {}

    # 兼容两种输出结构：
    # 1) *_entities（当前节点期望）
    # 2) metrics/dimensions/time/filters（Prompt 示例）
    time_entities = result.get("time_entities")
    if time_entities is None:
        time_value = result.get("time")
        if isinstance(time_value, list):
            time_entities = time_value
        elif isinstance(time_value, dict):
            time_entities = [time_value]
        else:
            time_entities = []

    dimension_entities = result.get("dimension_entities")
    if dimension_entities is None:
        dimension_entities = result.get("dimensions", [])

    metric_entities = result.get("metric_entities")
    if metric_entities is None:
        metric_entities = result.get("metrics", [])

    filter_entities = result.get("filter_entities")
    if filter_entities is None:
        filter_entities = result.get("filters", [])

    if not isinstance(time_entities, list):
        time_entities = []
    if not isinstance(dimension_entities, list):
        dimension_entities = []
    if not isinstance(metric_entities, list):
        metric_entities = []
    if not isinstance(filter_entities, list):
        filter_entities = []

    result["time_entities"] = time_entities
    result["dimension_entities"] = dimension_entities
    result["metric_entities"] = metric_entities
    result["filter_entities"] = filter_entities

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"提取到 {len(metric_entities)} 个指标实体"
    step["data"] = {
        "time_count": len(time_entities),
        "dimension_count": len(dimension_entities),
        "metric_count": len(metric_entities),
        "filter_count": len(filter_entities),
    }

    return {
        "extracted_entities": result,
        "time_entities": time_entities,
        "dimension_entities": dimension_entities,
        "metric_entities": metric_entities,
        "filter_entities": filter_entities,
        "steps": [step],
    }
