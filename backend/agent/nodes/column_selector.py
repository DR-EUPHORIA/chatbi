"""列选择 Node — 根据用户问题选择相关的数据列"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.column_selector import COLUMN_SELECTOR_SYSTEM_PROMPT, COLUMN_SELECTOR_USER_PROMPT
from agent.llm import get_llm
from knowledge.semantic_layer import get_glossary_text
from agent.prompt_utils import safe_format_prompt


def column_selector_node(state: AgentState) -> dict:
    """根据用户问题和提取的实体，选择最相关的数据列"""

    user_message = state.get("user_message", "")
    dataset_id = state.get("dataset_id")
    matched_tables = state.get("matched_tables", [])
    schema_context = state.get("schema_context", "")
    extracted_entities = state.get("extracted_entities", {})

    step = {
        "node_name": "column_selector",
        "status": NodeStatus.RUNNING.value,
        "title": "列选择",
        "detail": "正在选择相关数据列...",
        "data": {},
    }

    schema_text = schema_context if schema_context else json.dumps(matched_tables, ensure_ascii=False)
    if not schema_text:
        schema_text = "暂无表结构信息"
    glossary = get_glossary_text(dataset_id)

    llm = get_llm()
    prompt = safe_format_prompt(COLUMN_SELECTOR_USER_PROMPT, 
        user_message=user_message,
        schema_context=schema_text,
        glossary=glossary if glossary else "暂无业务术语映射",
        # 兼容历史 Prompt 占位符命名
        matched_tables=schema_text,
        extracted_entities=json.dumps(extracted_entities, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": COLUMN_SELECTOR_SYSTEM_PROMPT},
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
            "selected_columns": [],
            "dimension_columns": [],
            "metric_columns": [],
            "filter_columns": [],
        }

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"选择了 {len(result.get('selected_columns', []))} 个相关列"
    step["data"] = {
        "total_columns": len(result.get("selected_columns", [])),
        "dimension_columns": result.get("dimension_columns", []),
        "metric_columns": result.get("metric_columns", []),
    }

    return {
        "selected_columns": result.get("selected_columns", []),
        "dimension_columns": result.get("dimension_columns", []),
        "metric_columns": result.get("metric_columns", []),
        "filter_columns": result.get("filter_columns", []),
        "steps": [step],
    }
