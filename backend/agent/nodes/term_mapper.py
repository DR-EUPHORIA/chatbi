"""术语映射 Node — 将业务术语映射到数据库字段"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.term_mapper import TERM_MAPPER_SYSTEM_PROMPT, TERM_MAPPER_USER_PROMPT
from agent.llm import get_llm


def term_mapper_node(state: AgentState) -> dict:
    """将用户使用的业务术语映射到数据库中的实际字段"""

    user_message = state.get("user_message", "")
    extracted_entities = state.get("extracted_entities", {})
    matched_tables = state.get("matched_tables", [])
    glossary = state.get("glossary", {})

    step = {
        "node_name": "term_mapper",
        "status": NodeStatus.RUNNING.value,
        "title": "术语映射",
        "detail": "正在映射业务术语...",
        "data": {},
    }

    llm = get_llm()
    prompt = TERM_MAPPER_USER_PROMPT.format(
        user_message=user_message,
        extracted_entities=json.dumps(extracted_entities, ensure_ascii=False),
        matched_tables=json.dumps(matched_tables, ensure_ascii=False),
        glossary=json.dumps(glossary, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": TERM_MAPPER_SYSTEM_PROMPT},
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
            "term_mappings": {},
            "unmapped_terms": [],
            "mapping_confidence": {},
            "mapping_notes": [],
        }

    term_mappings = result.get("term_mappings", {})
    unmapped_terms = result.get("unmapped_terms", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"映射了 {len(term_mappings)} 个术语，{len(unmapped_terms)} 个未映射"
    step["data"] = {
        "mapped_count": len(term_mappings),
        "unmapped_count": len(unmapped_terms),
    }

    return {
        "term_mappings": term_mappings,
        "unmapped_terms": unmapped_terms,
        "mapping_confidence": result.get("mapping_confidence", {}),
        "mapping_notes": result.get("mapping_notes", []),
        "steps": [step],
    }
