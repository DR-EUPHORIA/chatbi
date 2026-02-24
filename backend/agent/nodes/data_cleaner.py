"""数据清洗 Node — 清洗和预处理数据"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.data_cleaner import DATA_CLEANER_SYSTEM_PROMPT, DATA_CLEANER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def data_cleaner_node(state: AgentState) -> dict:
    """清洗和预处理数据，处理缺失值、异常值、格式问题等"""

    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])

    step = {
        "node_name": "data_cleaner",
        "status": NodeStatus.RUNNING.value,
        "title": "数据清洗",
        "detail": "正在清洗数据...",
        "data": {},
    }

    data_preview = sql_result[:50]
    
    llm = get_llm()
    prompt = safe_format_prompt(DATA_CLEANER_USER_PROMPT, 
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        total_rows=len(sql_result),
    )

    response = llm.invoke([
        {"role": "system", "content": DATA_CLEANER_SYSTEM_PROMPT},
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
            "data_quality_issues": [],
            "cleaning_actions": [],
            "cleaned_data_summary": {},
            "data_quality_score": 0.8,
        }

    issues = result.get("data_quality_issues", [])
    actions = result.get("cleaning_actions", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"发现 {len(issues)} 个数据质量问题，执行 {len(actions)} 项清洗操作"
    step["data"] = {
        "issue_count": len(issues),
        "action_count": len(actions),
        "data_quality_score": result.get("data_quality_score", 0.8),
    }

    return {
        "data_quality_issues": issues,
        "cleaning_actions": actions,
        "cleaned_data_summary": result.get("cleaned_data_summary", {}),
        "data_quality_score": result.get("data_quality_score", 0.8),
        "steps": [step],
    }
