"""文件分析 Node — 分析上传文件的内容"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.file_analyzer import FILE_ANALYZER_SYSTEM_PROMPT, FILE_ANALYZER_USER_PROMPT
from agent.llm import get_llm


def file_analyzer_node(state: AgentState) -> dict:
    """分析上传文件的内容，提取关键信息和洞察"""

    user_message = state.get("user_message", "")
    file_path = state.get("file_path", "")
    parsed_columns = state.get("parsed_columns", [])
    parsed_data_types = state.get("parsed_data_types", {})
    file_content = state.get("file_content", "")

    step = {
        "node_name": "file_analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "文件分析",
        "detail": "正在分析文件内容...",
        "data": {},
    }

    content_preview = file_content[:8000] if file_content else ""
    
    llm = get_llm()
    prompt = FILE_ANALYZER_USER_PROMPT.format(
        user_message=user_message,
        file_path=file_path,
        columns=json.dumps(parsed_columns, ensure_ascii=False),
        data_types=json.dumps(parsed_data_types, ensure_ascii=False),
        content_preview=content_preview,
    )

    response = llm.invoke([
        {"role": "system", "content": FILE_ANALYZER_SYSTEM_PROMPT},
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
            "file_summary": "",
            "key_findings": [],
            "data_quality_assessment": {},
            "recommended_analyses": [],
        }

    key_findings = result.get("key_findings", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"发现 {len(key_findings)} 个关键发现"
    step["data"] = {
        "finding_count": len(key_findings),
        "has_quality_issues": len(result.get("data_quality_assessment", {}).get("issues", [])) > 0,
    }

    return {
        "file_summary": result.get("file_summary", ""),
        "file_key_findings": key_findings,
        "file_data_quality": result.get("data_quality_assessment", {}),
        "recommended_analyses": result.get("recommended_analyses", []),
        "steps": [step],
    }
