"""文件解析 Node — 解析上传的文件"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.file_parser import FILE_PARSER_SYSTEM_PROMPT, FILE_PARSER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def file_parser_node(state: AgentState) -> dict:
    """解析上传的文件，提取数据结构和内容"""

    user_message = state.get("user_message", "")
    file_path = state.get("file_path", "")
    file_content = state.get("file_content", "")
    file_type = state.get("file_type", "")

    step = {
        "node_name": "file_parser",
        "status": NodeStatus.RUNNING.value,
        "title": "文件解析",
        "detail": f"正在解析文件: {file_path}...",
        "data": {},
    }

    content_preview = file_content[:5000] if file_content else ""
    
    llm = get_llm()
    prompt = safe_format_prompt(FILE_PARSER_USER_PROMPT, 
        user_message=user_message,
        file_path=file_path,
        file_type=file_type,
        content_preview=content_preview,
    )

    response = llm.invoke([
        {"role": "system", "content": FILE_PARSER_SYSTEM_PROMPT},
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
            "file_structure": {},
            "columns": [],
            "row_count": 0,
            "data_types": {},
            "parsing_notes": [],
        }

    columns = result.get("columns", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"解析完成，发现 {len(columns)} 列"
    step["data"] = {
        "column_count": len(columns),
        "row_count": result.get("row_count", 0),
        "file_type": file_type,
    }

    return {
        "parsed_file_structure": result.get("file_structure", {}),
        "parsed_columns": columns,
        "parsed_row_count": result.get("row_count", 0),
        "parsed_data_types": result.get("data_types", {}),
        "parsing_notes": result.get("parsing_notes", []),
        "steps": [step],
    }
