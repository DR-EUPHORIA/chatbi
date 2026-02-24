"""门控 Node — 评估用户输入是否足够清晰"""

import json
from agent.state import AgentState, NodeStatus
from agent.prompts.gate import GATE_SYSTEM_PROMPT, GATE_USER_PROMPT
from agent.llm import get_llm
from data.datasets.manager import dataset_manager
from agent.prompt_utils import safe_format_prompt


def gate_node(state: AgentState) -> dict:
    """评估用户输入的清晰度，不清晰则打回并给出引导"""

    user_message = state.get("user_message", "")
    dataset_id = state.get("dataset_id")

    step = {
        "node_name": "gate",
        "status": NodeStatus.RUNNING.value,
        "title": "意图门控",
        "detail": "正在评估您的问题是否足够清晰...",
        "data": {},
    }

    # 获取数据集信息
    dataset_info = "暂无数据集"
    if dataset_id:
        schema = dataset_manager.get_schema(dataset_id)
        if schema:
            dataset_info = json.dumps(schema, ensure_ascii=False, indent=2)

    llm = get_llm()
    prompt = safe_format_prompt(GATE_USER_PROMPT, 
        user_message=user_message,
        dataset_info=dataset_info,
    )

    response = llm.invoke([
        {"role": "system", "content": GATE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"is_clear": True, "feedback": "", "enhanced_query": user_message}

    is_clear = result.get("is_clear", True)
    gate_feedback = result.get("feedback", "")
    updates: dict = {
        "is_clear": is_clear,
        "gate_feedback": gate_feedback,
    }

    if is_clear:
        enhanced = result.get("enhanced_query", user_message)
        if enhanced:
            updates["user_message"] = enhanced
        step["status"] = NodeStatus.SUCCESS.value
        step["detail"] = "问题清晰，可以继续分析"
    else:
        step["status"] = NodeStatus.WAITING_USER.value
        step["detail"] = gate_feedback
        updates["final_answer"] = gate_feedback

    updates["steps"] = [step]
    return updates