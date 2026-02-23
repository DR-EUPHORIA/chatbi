"""文件读取工具 — 支持 Excel/CSV/PDF"""

import json
from pathlib import Path
from typing import Any

import pandas as pd


def parse_uploaded_file(file_path: str, file_type: str) -> dict[str, Any]:
    """解析上传的文件，返回数据摘要"""

    if file_type in (".csv",):
        return _parse_csv(file_path)
    elif file_type in (".xlsx", ".xls"):
        return _parse_excel(file_path)
    elif file_type in (".pdf",):
        return _parse_pdf(file_path)
    else:
        return {"error": f"不支持的文件类型：{file_type}"}


def _parse_csv(file_path: str) -> dict[str, Any]:
    """解析 CSV 文件"""
    dataframe = pd.read_csv(file_path)
    return _dataframe_summary(dataframe, "csv")


def _parse_excel(file_path: str) -> dict[str, Any]:
    """解析 Excel 文件"""
    excel_file = pd.ExcelFile(file_path)
    sheets = {}
    for sheet_name in excel_file.sheet_names:
        dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
        sheets[sheet_name] = _dataframe_summary(dataframe, "excel")

    return {
        "file_type": "excel",
        "sheet_count": len(sheets),
        "sheets": sheets,
    }


def _parse_pdf(file_path: str) -> dict[str, Any]:
    """解析 PDF 文件，提取文本和表格"""
    import pdfplumber

    text_content = []
    tables = []

    with pdfplumber.open(file_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # 提取文本
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"--- 第 {page_idx + 1} 页 ---\n{page_text}")

            # 提取表格
            page_tables = page.extract_tables()
            for table_idx, table in enumerate(page_tables):
                if table and len(table) > 1:
                    headers = table[0]
                    rows = table[1:]
                    tables.append({
                        "page": page_idx + 1,
                        "table_index": table_idx,
                        "headers": headers,
                        "row_count": len(rows),
                        "preview": rows[:5],
                    })

    return {
        "file_type": "pdf",
        "page_count": len(text_content),
        "text_preview": "\n".join(text_content[:3])[:2000],
        "table_count": len(tables),
        "tables": tables,
    }


def read_file_as_dataframe(file_path: str) -> pd.DataFrame:
    """将文件读取为 Pandas DataFrame"""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持转换为 DataFrame 的文件类型：{suffix}")


def _dataframe_summary(dataframe: pd.DataFrame, file_type: str) -> dict[str, Any]:
    """生成 DataFrame 的数据摘要"""
    columns_info = []
    for col in dataframe.columns:
        col_info = {
            "name": str(col),
            "dtype": str(dataframe[col].dtype),
            "non_null_count": int(dataframe[col].notna().sum()),
            "null_count": int(dataframe[col].isna().sum()),
        }
        if dataframe[col].dtype in ("int64", "float64"):
            col_info["min"] = float(dataframe[col].min()) if not dataframe[col].isna().all() else None
            col_info["max"] = float(dataframe[col].max()) if not dataframe[col].isna().all() else None
            col_info["mean"] = float(dataframe[col].mean()) if not dataframe[col].isna().all() else None
        elif dataframe[col].dtype == "object":
            col_info["unique_count"] = int(dataframe[col].nunique())
            col_info["sample_values"] = dataframe[col].dropna().head(5).tolist()

        columns_info.append(col_info)

    return {
        "file_type": file_type,
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "columns": columns_info,
        "preview": json.loads(dataframe.head(5).to_json(orient="records", force_ascii=False)),
    }
