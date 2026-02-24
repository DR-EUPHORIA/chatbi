"""术语映射 Node — 将业务术语映射到数据库字段"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.term_mapper import TERM_MAPPER_SYSTEM_PROMPT, TERM_MAPPER_USER_PROMPT
from agent.llm import get_llm
from knowledge.semantic_layer import get_glossary_text
from agent.prompt_utils import safe_format_prompt


def term_mapper_node(state: AgentState) -> dict:
    """将用户使用的业务术语映射到数据库中的实际字段"""

    user_message = state.get("user_message", "")
    dataset_id = state.get("dataset_id")
    extracted_entities = state.get("extracted_entities", {})
    matched_tables = state.get("matched_tables", [])
    schema_context = state.get("schema_context", "")
    glossary = state.get("glossary", {})

    step = {
        "node_name": "term_mapper",
        "status": NodeStatus.RUNNING.value,
        "title": "术语映射",
        "detail": "正在映射业务术语...",
        "data": {},
    }

    entities_text = json.dumps(extracted_entities, ensure_ascii=False)
    schema_text = schema_context if schema_context else json.dumps(matched_tables, ensure_ascii=False)
    if not schema_text:
        schema_text = "暂无表结构信息"

    if glossary:
        glossary_text = json.dumps(glossary, ensure_ascii=False)
    else:
        glossary_text = get_glossary_text(dataset_id) or "暂无业务术语表"

    llm = get_llm()
    prompt = safe_format_prompt(TERM_MAPPER_USER_PROMPT, 
        user_message=user_message,
        entities=entities_text,
        schema_context=schema_text,
        glossary=glossary_text,
        # 兼容历史 Prompt 占位符命名
        extracted_entities=entities_text,
        matched_tables=schema_text,
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
        result = {}

    term_mappings = result.get("term_mappings")
    mapping_confidence = result.get("mapping_confidence", {})
    mapping_notes = result.get("mapping_notes", [])

    # 兼容 Prompt 示例输出：mappings / mapping_summary / required_joins
    if term_mappings is None:
        term_mappings = {}
        mappings = result.get("mappings", [])
        if isinstance(mappings, list):
            for item in mappings:
                if not isinstance(item, dict):
                    continue
                term = item.get("term")
                if not isinstance(term, str) or not term.strip():
                    continue
                term_mappings[term] = {
                    "mapping_type": item.get("mapping_type"),
                    "table": item.get("table"),
                    "field": item.get("field"),
                    "expression": item.get("expression"),
                    "alias": item.get("alias"),
                    "source": item.get("source"),
                }
                confidence = item.get("confidence")
                if isinstance(confidence, (int, float)):
                    mapping_confidence[term] = float(confidence)

    if not isinstance(term_mappings, dict):
        term_mappings = {}
    if not isinstance(mapping_confidence, dict):
        mapping_confidence = {}
    if not isinstance(mapping_notes, list):
        mapping_notes = []

    unmapped_raw = result.get("unmapped_terms", [])
    unmapped_terms: list[str] = []
    if isinstance(unmapped_raw, list):
        for item in unmapped_raw:
            if isinstance(item, str):
                unmapped_terms.append(item)
            elif isinstance(item, dict):
                term = item.get("term")
                if isinstance(term, str) and term:
                    unmapped_terms.append(term)
                reason = item.get("reason")
                if isinstance(reason, str) and reason:
                    mapping_notes.append(f"未映射原因[{term or 'unknown'}]: {reason}")

    mapping_summary = result.get("mapping_summary")
    if isinstance(mapping_summary, str) and mapping_summary:
        mapping_notes.append(mapping_summary)

    required_joins = result.get("required_joins")
    if isinstance(required_joins, list) and required_joins:
        mapping_notes.append(f"建议关联关系数量: {len(required_joins)}")
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"映射了 {len(term_mappings)} 个术语，{len(unmapped_terms)} 个未映射"
    step["data"] = {
        "mapped_count": len(term_mappings),
        "unmapped_count": len(unmapped_terms),
    }

    return {
        "term_mappings": term_mappings,
        "unmapped_terms": unmapped_terms,
        "mapping_confidence": mapping_confidence,
        "mapping_notes": mapping_notes,
        "steps": [step],
    }
