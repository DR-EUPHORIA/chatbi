"""Few-shot 示例库 — 存储和检索"问题 → SQL"的历史示例"""

import json
from pathlib import Path
from typing import Any

# 示例库存储路径
_FEW_SHOT_DIR = Path(__file__).parent / "examples"

# 内存缓存
_examples_cache: dict[str, list[dict]] = {}


def get_all_examples(dataset_id: str | None = None) -> list[dict[str, str]]:
    """获取指定数据集的所有 Few-shot 示例"""
    cache_key = dataset_id or "default"
    if cache_key in _examples_cache:
        return _examples_cache[cache_key]

    # 尝试从文件加载
    examples_path = _FEW_SHOT_DIR / f"{cache_key}_examples.json"
    if examples_path.exists():
        with open(examples_path, "r", encoding="utf-8") as f:
            examples = json.load(f)
            _examples_cache[cache_key] = examples
            return examples

    # 返回默认的电商 Demo 示例
    default_examples = [
        {
            "question": "最近30天的总成交金额是多少",
            "sql": "SELECT SUM(total_amount) AS total_gmv FROM orders WHERE order_date >= date('now', '-30 days');",
            "explanation": "查询最近30天所有订单的总金额",
        },
        {
            "question": "各品类的销售额排名",
            "sql": "SELECT c.category_name, SUM(o.total_amount) AS sales FROM orders o JOIN products p ON o.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id GROUP BY c.category_name ORDER BY sales DESC;",
            "explanation": "按品类分组统计销售额并降序排列",
        },
        {
            "question": "最近7天每天的订单量趋势",
            "sql": "SELECT order_date, COUNT(*) AS order_count FROM orders WHERE order_date >= date('now', '-7 days') GROUP BY order_date ORDER BY order_date;",
            "explanation": "查询最近7天每天的订单数量",
        },
        {
            "question": "哪个地区的销售额最高",
            "sql": "SELECT region, SUM(total_amount) AS sales FROM orders GROUP BY region ORDER BY sales DESC LIMIT 1;",
            "explanation": "按地区分组统计销售额，取最高的一个",
        },
        {
            "question": "本月的客单价是多少",
            "sql": "SELECT AVG(total_amount) AS avg_order_amount FROM orders WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now');",
            "explanation": "计算本月所有订单的平均金额",
        },
        {
            "question": "销售额环比增长了多少",
            "sql": "SELECT curr.sales - prev.sales AS growth, ROUND((curr.sales - prev.sales) * 100.0 / prev.sales, 2) AS growth_rate FROM (SELECT SUM(total_amount) AS sales FROM orders WHERE order_date >= date('now', '-30 days')) curr, (SELECT SUM(total_amount) AS sales FROM orders WHERE order_date >= date('now', '-60 days') AND order_date < date('now', '-30 days')) prev;",
            "explanation": "对比最近30天和前30天的销售额，计算环比增长",
        },
    ]

    _examples_cache[cache_key] = default_examples
    return default_examples


def get_similar_examples(question: str, dataset_id: str | None = None, top_k: int = 3) -> str:
    """根据用户问题检索最相似的 Few-shot 示例（简单关键词匹配版本）"""
    examples = get_all_examples(dataset_id)

    if not examples:
        return ""

    # 简单的关键词匹配评分
    scored_examples = []
    question_lower = question.lower()
    question_chars = set(question_lower)

    for example in examples:
        example_question = example["question"].lower()
        example_chars = set(example_question)

        # 计算字符重叠度
        overlap = len(question_chars & example_chars)
        total = len(question_chars | example_chars)
        score = overlap / total if total > 0 else 0

        # 关键词加分
        keywords = ["销售", "金额", "订单", "品类", "趋势", "排名", "环比", "同比", "客单价", "用户", "地区"]
        for keyword in keywords:
            if keyword in question and keyword in example["question"]:
                score += 0.3

        scored_examples.append((score, example))

    # 按分数降序排列，取 top_k
    scored_examples.sort(key=lambda x: x[0], reverse=True)
    top_examples = [ex for _, ex in scored_examples[:top_k]]

    # 格式化为文本
    lines = []
    for idx, ex in enumerate(top_examples, 1):
        lines.append(f"示例 {idx}:")
        lines.append(f"  问题：{ex['question']}")
        lines.append(f"  SQL：{ex['sql']}")
        lines.append(f"  说明：{ex['explanation']}")
        lines.append("")

    return "\n".join(lines)


def add_example(question: str, sql: str, explanation: str, dataset_id: str | None = None) -> None:
    """添加新的 Few-shot 示例"""
    cache_key = dataset_id or "default"
    examples = get_all_examples(dataset_id)
    examples.append({
        "question": question,
        "sql": sql,
        "explanation": explanation,
    })
    _examples_cache[cache_key] = examples

    # 持久化到文件
    _FEW_SHOT_DIR.mkdir(parents=True, exist_ok=True)
    examples_path = _FEW_SHOT_DIR / f"{cache_key}_examples.json"
    with open(examples_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
