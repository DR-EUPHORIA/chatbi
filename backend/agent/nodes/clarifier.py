"""歧义澄清 Node — 检测用户问题中的歧义并主动反问"""

import json
from agent.state import AgentState, NodeStatus
from agent.prompts.clarifier import CLARIFIER_SYSTEM_PROMPT, CLARIFIER_USER_PROMPT
from agent.llm import get_llm
from knowledge.semantic_layer import get_glossary_text


def clarifier_node(state: AgentState) -> dict:
    """检测用户问题中的歧义，如有歧义则生成选项供用户选择"""

    user_message = state.get("user_message", "")
    schema_context = state.get("schema_context", "")
    dataset_id = state.get("dataset_id")

    step = {
        "node_name": "clarifier",
        "status": NodeStatus.RUNNING.value,
        "title": "歧义检测",
        "detail": "正在检查问题是否存在歧义...",
        "data": {},
    }

    glossary = get_glossary_text(dataset_id)

    llm = get_llm()
    prompt = CLARIFIER_USER_PROMPT.format(
        user_message=user_message,
        schema_context=schema_context,
        glossary=glossary if glossary else "暂无业务术语表",
    )

    response = llm.invoke([
        {"role": "system", "content": CLARIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"has_ambiguity": False}

    has_ambiguity = result.get("has_ambiguity", False)
    updates: dict = {"has_ambiguity": has_ambiguity}

    if has_ambiguity:
        clarify_options = result.get("options", [])
        updates["clarify_options"] = clarify_options
        updates["final_answer"] = f"发现歧义：{result.get('description', '')}，请选择："
        step["status"] = NodeStatus.WAITING_USER.value
        step["detail"] = f"发现{result.get('ambiguity_type', '歧义')}：{result.get('description', '')}"
        step["data"] = {"options": clarify_options}
    else:
        step["status"] = NodeStatus.SUCCESS.value
        step["detail"] = "无歧义，继续执行"

    updates["steps"] = [step]
    return updates
