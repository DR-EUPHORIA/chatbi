"""Python 代码执行工具 — 在受限环境中执行数据分析代码"""

import io
import sys
import traceback
from typing import Any


def execute_python_code(code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """执行 Python 代码并返回结果

    Args:
        code: 要执行的 Python 代码
        context: 预注入的变量上下文（如 DataFrame）

    Returns:
        包含 stdout、结果变量、错误信息的字典
    """
    # 准备执行环境
    exec_globals = {
        "__builtins__": __builtins__,
    }

    # 注入常用库
    try:
        import pandas as pd
        import json
        exec_globals["pd"] = pd
        exec_globals["json"] = json
    except ImportError:
        pass

    # 注入上下文变量
    if context:
        exec_globals.update(context)

    # 捕获 stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    result = {
        "success": False,
        "stdout": "",
        "result": None,
        "error": "",
    }

    try:
        exec(code, exec_globals)
        result["success"] = True
        result["stdout"] = captured_output.getvalue()

        # 尝试获取 result 变量
        if "result" in exec_globals:
            result_value = exec_globals["result"]
            if hasattr(result_value, "to_dict"):
                result["result"] = result_value.to_dict(orient="records")
            elif isinstance(result_value, (dict, list, str, int, float, bool)):
                result["result"] = result_value
            else:
                result["result"] = str(result_value)

    except Exception:
        result["error"] = traceback.format_exc()

    finally:
        sys.stdout = old_stdout

    return result
