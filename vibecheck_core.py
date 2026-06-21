"""VibeCheck 计算引擎 — 解析 Claude Code transcript JSONL，计算效率指标，输出紧凑 JSON。

用法:
    python vibecheck_core.py [--session-id SESSION_ID] [--mode report|watch]

输出:
    单行 JSON 到 stdout，包含 session 元数据、5 个指标的数值与评级、告警列表。
    所有指标计算均为纯数学运算，不调用 LLM。
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone


def find_transcript_dir() -> Path:
    """定位 transcript JSONL 根目录。"""
    home = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
    transcript_dir = home / ".claude" / "projects"
    if not transcript_dir.exists():
        print(json.dumps({"error": f"Transcript directory not found: {transcript_dir}"}))
        sys.exit(1)
    return transcript_dir


def find_jsonl(transcript_dir: Path, session_id: str | None) -> Path:
    """找到目标 JSONL 文件。

    优先级:
    1. 指定 session_id → 在所有子目录中匹配 <session_id>.jsonl
    2. 未指定 → 取最近修改的 .jsonl 文件
    """
    jsonl_files = list(transcript_dir.rglob("*.jsonl"))
    if not jsonl_files:
        print(json.dumps({"error": "No transcript JSONL files found"}))
        sys.exit(1)

    if session_id:
        for f in jsonl_files:
            if f.stem == session_id:
                return f
        print(json.dumps({"error": f"Session not found: {session_id}"}))
        sys.exit(1)

    # 返回最近修改的文件
    jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return jsonl_files[0]


def is_meta_user_message(msg: dict) -> bool:
    """判断是否为元数据用户消息（本地命令回显，不应计入交互轮次）。"""
    if msg.get("type") != "user":
        return True
    if msg.get("isMeta"):
        return True
    content = msg.get("message", {}).get("content", "")
    if isinstance(content, str):
        stripped = content.strip()
        if not stripped:
            return True
        # 本地命令回显特征：以 XML 标签开头或 <local-command-* 包裹
        if stripped.startswith("<command-name>"):
            return True
        if stripped.startswith("<command-message>"):
            return True
        if stripped.startswith("<command-args>"):
            return True
        if stripped.startswith("<local-command-stdout>"):
            return True
        if stripped.startswith("<local-command-caveat>"):
            return True
    return False


def parse_jsonl(filepath: Path) -> dict:
    """解析 JSONL 文件，返回聚合数据结构。

    返回:
        {
            "session_id": str,
            "model": str,
            "user_messages": [{"content": str, "timestamp": str}, ...],
            "total_input_tokens": int,
            "total_output_tokens": int,
            "total_cache_read": int,
            "total_cache_creation": int,
            "thinking_char_count": int,
            "output_char_count": int,
            "first_ts": str,
            "last_ts": str,
        }
    """
    seen_message_ids: set[str] = set()
    result = {
        "session_id": "",
        "model": "",
        "user_messages": [],
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cache_read": 0,
        "total_cache_creation": 0,
        "thinking_char_count": 0,
        "output_char_count": 0,
        "first_ts": None,
        "last_ts": None,
    }

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            # 提取 session_id（首条有效消息获取）
            if not result["session_id"] and msg.get("sessionId"):
                result["session_id"] = msg["sessionId"]

            ts = msg.get("timestamp", "")
            if ts:
                if result["first_ts"] is None:
                    result["first_ts"] = ts
                result["last_ts"] = ts

            # 处理 assistant 消息 — 按 message.id 去重
            if msg.get("type") == "assistant":
                msg_id = msg.get("message", {}).get("id", "")
                if msg_id in seen_message_ids:
                    continue
                seen_message_ids.add(msg_id)

                # 提取模型名
                if not result["model"]:
                    result["model"] = msg.get("message", {}).get("model", "")

                usage = msg.get("message", {}).get("usage", {})
                result["total_input_tokens"] += usage.get("input_tokens", 0)
                result["total_output_tokens"] += usage.get("output_tokens", 0)
                result["total_cache_read"] += usage.get("cache_read_input_tokens", 0)
                result["total_cache_creation"] += usage.get("cache_creation_input_tokens", 0)

                # 统计 thinking 和 output 字符长度（用于 TTR 估算）
                for content_item in msg.get("message", {}).get("content", []):
                    if content_item.get("type") == "thinking":
                        result["thinking_char_count"] += len(content_item.get("thinking", ""))
                    elif content_item.get("type") == "text":
                        result["output_char_count"] += len(content_item.get("text", ""))

            # 处理真实用户消息
            if not is_meta_user_message(msg):
                content = msg.get("message", {}).get("content", "")
                if isinstance(content, str) and content.strip():
                    result["user_messages"].append({
                        "content": content,
                        "timestamp": ts,
                    })

    return result


def grade_ter(value: float) -> str:
    if value > 0.40:
        return "优秀"
    elif value >= 0.25:
        return "良好"
    elif value >= 0.15:
        return "一般"
    else:
        return "低效"


def grade_chr(value: float) -> str:
    if value > 0.70:
        return "优秀"
    elif value >= 0.40:
        return "良好"
    else:
        return "低效"


def grade_ttr(value: float) -> str:
    if value < 0.30:
        return "高效"
    elif value <= 0.60:
        return "正常"
    else:
        return "过载"


def grade_ipt(value: int) -> str:
    if value <= 2:
        return "优秀"
    elif value <= 5:
        return "良好"
    elif value <= 10:
        return "一般"
    else:
        return "低效"


def compute_metrics(parsed: dict) -> dict:
    """从解析后的数据计算 4 个数值指标 + 提取 RCS prompts。"""
    total_input = parsed["total_input_tokens"]
    total_output = parsed["total_output_tokens"]
    total_cache_read = parsed["total_cache_read"]
    total_cache_creation = parsed["total_cache_creation"]
    thinking_chars = parsed["thinking_char_count"]
    output_chars = parsed["output_char_count"]

    # TER: output / (input + output + thinking_estimate)
    # thinking_tokens 估算 = thinking 字符数 * 0.3（粗略近似）
    thinking_tokens_est = int(thinking_chars * 0.3)
    total_tokens = total_input + total_output + thinking_tokens_est
    ter = round(total_output / total_tokens, 4) if total_tokens > 0 else 0.0

    # CHR: cache_read / (cache_read + cache_creation)
    total_cache = total_cache_read + total_cache_creation
    chr_val = round(total_cache_read / total_cache, 4) if total_cache > 0 else 0.0

    # TTR: thinking 字符长度占比（非推理模型为 0）
    total_chars = thinking_chars + output_chars
    ttr = round(thinking_chars / total_chars, 4) if total_chars > 0 else 0.0

    # IPT: 有效 user→assistant 交互轮数
    ipt = len(parsed["user_messages"])

    # RCS prompts: 每条 user prompt 截断到 200 字符
    rcs_prompts = []
    for um in parsed["user_messages"]:
        content = um["content"].strip()
        if len(content) > 200:
            content = content[:200] + "..."
        rcs_prompts.append(content)

    return {
        "TER": {"value": ter, "grade": grade_ter(ter)},
        "CHR": {"value": chr_val, "grade": grade_chr(chr_val)},
        "TTR": {"value": ttr, "grade": grade_ttr(ttr)},
        "IPT": {"value": ipt, "grade": grade_ipt(ipt)},
        "RCS": {"prompts": rcs_prompts},
    }


def check_alerts(metrics: dict, mode: str) -> list[str]:
    """按阈值预判告警，返回告警代码列表。"""
    alerts = []
    ter = metrics["TER"]["value"]
    chr_val = metrics["CHR"]["value"]
    ttr = metrics["TTR"]["value"]
    ipt = metrics["IPT"]["value"]

    if ter < 0.15:
        alerts.append("TER_low")
    if chr_val < 0.40:
        alerts.append("CHR_low")
    if ttr > 0.60:
        alerts.append("TTR_high")
    if ipt > 6:
        alerts.append("IPT_high")

    return alerts


def compute_duration_min(first_ts: str | None, last_ts: str | None) -> float:
    """计算 session 耗时（分钟）。"""
    if not first_ts or not last_ts:
        return 0.0
    try:
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        start = datetime.strptime(first_ts, fmt)
        end = datetime.strptime(last_ts, fmt)
        return round((end - start).total_seconds() / 60, 1)
    except (ValueError, TypeError):
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="VibeCheck 计算引擎")
    parser.add_argument("--session-id", type=str, default=None, help="Session ID")
    parser.add_argument("--mode", type=str, default="report",
                        choices=["report", "watch"], help="运行模式")
    args = parser.parse_args()

    transcript_dir = find_transcript_dir()
    jsonl_path = find_jsonl(transcript_dir, args.session_id)
    parsed = parse_jsonl(jsonl_path)
    metrics = compute_metrics(parsed)
    alerts = check_alerts(metrics, args.mode)
    duration_min = compute_duration_min(parsed["first_ts"], parsed["last_ts"])

    output = {
        "session_id": parsed["session_id"],
        "model": parsed["model"],
        "message_count": len(parsed["user_messages"]),
        "duration_min": duration_min,
        "metrics": metrics,
        "alerts": alerts,
    }

    # 输出紧凑 JSON（无换行无缩进，省 Token）
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
