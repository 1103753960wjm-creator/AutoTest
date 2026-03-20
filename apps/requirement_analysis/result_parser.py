import re


def parse_generated_results(content):
    if not content:
        return []

    clean_content = re.sub(r"\*\*([^*]+)\*\*", r"\1", content)
    lines = [line.strip() for line in clean_content.split("\n") if line.strip()]
    table_rows = []

    for line in lines:
        if "|" in line and not line.startswith("|-"):
            columns = [cell.strip() for cell in line.split("|") if cell.strip()]
            if len(columns) > 1:
                table_rows.append(columns)

    if len(table_rows) > 1:
        headers = [header.lower() for header in table_rows[0]]
        results = []
        for index, row in enumerate(table_rows[1:], start=1):
            item = {
                "index": index,
                "case_id": "",
                "scenario": "",
                "precondition": "",
                "steps": "",
                "expected": "",
                "priority": "P2",
            }
            for col_index, header in enumerate(headers):
                value = row[col_index] if col_index < len(row) else ""
                value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
                if "用例" in header or header == "id":
                    item["case_id"] = value
                elif "场景" in header or "目标" in header or "标题" in header:
                    item["scenario"] = value
                elif "前置" in header:
                    item["precondition"] = value
                elif "步骤" in header and "预期" not in header:
                    item["steps"] = value
                elif "预期" in header or "结果" in header:
                    item["expected"] = value
                elif "优先级" in header or header == "priority":
                    item["priority"] = value or "P2"
            if item["scenario"] or item["case_id"]:
                results.append(item)
        return results

    results = []
    current_case = None
    for line in lines:
        if line.startswith(("1.", "2.", "3.", "4.", "5.")) or "测试用例" in line or "Test Case" in line:
            if current_case:
                results.append(current_case)
            current_case = {
                "index": len(results) + 1,
                "case_id": f"TC{len(results) + 1:03d}",
                "scenario": re.sub(r"^(\d+\.|测试用例[:：]?\s*|Test Case[:：]?\s*)", "", line).strip(),
                "precondition": "",
                "steps": "",
                "expected": "",
                "priority": "P2",
            }
        elif current_case and ("前置条件" in line or "前提" in line):
            current_case["precondition"] = re.sub(r".*?[:：]\s*", "", line).strip()
        elif current_case and ("测试步骤" in line or "操作步骤" in line or "步骤" in line):
            current_case["steps"] = re.sub(r".*?[:：]\s*", "", line).strip()
        elif current_case and ("预期结果" in line or "Expected" in line):
            current_case["expected"] = re.sub(r".*?[:：]\s*", "", line).strip()
        elif current_case and "优先级" in line:
            current_case["priority"] = re.sub(r".*?[:：]\s*", "", line).strip() or "P2"

    if current_case:
        results.append(current_case)

    return results


__all__ = ["parse_generated_results"]
