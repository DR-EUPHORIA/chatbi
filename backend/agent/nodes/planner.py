"""规划 Node — 将用户需求拆解为细粒度执行计划"""

import json
from agent.state import AgentState, NodeStatus
from agent.prompts.planner import PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT
from agent.llm import get_llm
from data.datasets.manager import dataset_manager
from agent.prompt_utils import safe_format_prompt


def planner_node(state: AgentState) -> dict:
    """将用户的分析需求拆解为分步骤的执行计划"""

    user_message = state.get("user_message", "")
    dataset_id = state.get("dataset_id")
    intent = state.get("intent", "data_query")

    step = {
        "node_name": "planner",
        "status": NodeStatus.RUNNING.value,
        "title": "制定分析计划",
        "detail": "正在规划分析步骤...",
        "data": {},
    }

    dataset_info = "暂无数据集"
    if dataset_id:
        schema = dataset_manager.get_schema(dataset_id)
        if schema:
            dataset_info = json.dumps(schema, ensure_ascii=False, indent=2)

    llm = get_llm()
    prompt = safe_format_prompt(PLANNER_USER_PROMPT, 
        user_message=user_message,
        intent=intent,
        dataset_info=dataset_info,
    )

    response = llm.invoke([
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {
            "plan_title": "数据分析",
            "steps": [{"step_id": 1, "type": "查询数据", "description": "查询相关数据", "depends_on": []}],
            "expected_output": "数据分析结果",
        }

    plan = [
        f"Step {s['step_id']}: [{s['type']}] {s['description']}"
        for s in result.get("steps", [])
    ]

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"计划：{result.get('plan_title', '数据分析')}（共 {len(plan)} 步）"
    step["data"] = result

    return {"plan": plan, "steps": [step]}