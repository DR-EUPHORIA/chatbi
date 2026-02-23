"""语义层 / 指标字典 — 业务术语到物理字段的映射"""

import json
from pathlib import Path
from typing import Any

# 语义层配置文件路径
_SEMANTIC_LAYER_DIR = Path(__file__).parent / "configs"

# 内存缓存
_glossary_cache: dict[str, list[dict]] = {}


def get_glossary(dataset_id: str | None = None) -> list[dict[str, str]]:
    """获取指定数据集的业务术语映射表"""
    if dataset_id and dataset_id in _glossary_cache:
        return _glossary_cache[dataset_id]

    # 尝试从配置文件加载
    config_path = _SEMANTIC_LAYER_DIR / f"{dataset_id or 'default'}_glossary.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            glossary = json.load(f)
            _glossary_cache[dataset_id or "default"] = glossary
            return glossary

    # 返回默认的电商 Demo 术语表
    default_glossary = [
        {"term": "GMV", "definition": "成交总额，即所有已支付订单的金额总和", "field": "orders.total_amount", "formula": "SUM(orders.total_amount)"},
        {"term": "成交金额", "definition": "同 GMV，所有已支付订单的金额总和", "field": "orders.total_amount", "formula": "SUM(orders.total_amount)"},
        {"term": "订单量", "definition": "订单总数", "field": "orders.order_id", "formula": "COUNT(orders.order_id)"},
        {"term": "客单价", "definition": "平均每个订单的金额", "field": "orders.total_amount", "formula": "AVG(orders.total_amount)"},
        {"term": "用户数", "definition": "去重用户数", "field": "orders.user_id", "formula": "COUNT(DISTINCT orders.user_id)"},
        {"term": "复购率", "definition": "购买2次及以上的用户占比", "field": "orders.user_id", "formula": "下单>=2次的用户数 / 总用户数"},
        {"term": "退款率", "definition": "退款订单数占总订单数的比例", "field": "orders.status", "formula": "COUNT(status='refunded') / COUNT(*)"},
        {"term": "利润", "definition": "销售收入减去成本", "field": "orders.profit", "formula": "SUM(orders.profit)"},
        {"term": "利润率", "definition": "利润占销售额的比例", "field": "orders.profit, orders.total_amount", "formula": "SUM(profit) / SUM(total_amount)"},
    ]

    _glossary_cache[dataset_id or "default"] = default_glossary
    return default_glossary


def get_glossary_text(dataset_id: str | None = None) -> str:
    """获取格式化的术语映射文本，用于注入 Prompt"""
    glossary = get_glossary(dataset_id)
    if not glossary:
        return ""

    lines = []
    for item in glossary:
        line = f"- {item['term']}：{item['definition']}。对应字段：{item['field']}，计算公式：{item['formula']}"
        lines.append(line)

    return "\n".join(lines)


def add_glossary_term(dataset_id: str, term: str, definition: str, field: str, formula: str) -> None:
    """添加新的术语映射"""
    glossary = get_glossary(dataset_id)
    glossary.append({
        "term": term,
        "definition": definition,
        "field": field,
        "formula": formula,
    })
    _glossary_cache[dataset_id] = glossary

    # 持久化到文件
    _SEMANTIC_LAYER_DIR.mkdir(parents=True, exist_ok=True)
    config_path = _SEMANTIC_LAYER_DIR / f"{dataset_id}_glossary.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
