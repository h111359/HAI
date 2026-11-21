"""Read one explicitly supplied Codex JSONL source without changing any files."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import stat
import sys

try:
    from .adapters import ADAPTERS, event_message
except ImportError:  # Direct CLI invocation.
    from adapters import ADAPTERS, event_message

sys.dont_write_bytecode = True


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value):
    if not nonblank(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0
    except ValueError:
        return False


def reviewed_metadata(kind, payload):
    """Known non-conversation envelopes; unfamiliar shapes remain visible gaps."""
    if kind == 'token_usage_record':
        ids = {'thread_id', 'turn_id', 'session_id', 'root_turn_id', 'response_id'}
        counters = {'usage', 'turn_token_usage', 'thread_token_usage'}
        return (set(payload) == ids | counters
                and all(isinstance(payload[k], str) for k in ids)
                and all(isinstance(payload[k], dict) for k in counters))
    if kind == 'inter_agent_communication_metadata':
        return set(payload) == {'trigger_turn'} and type(payload['trigger_turn']) is bool
    if kind == 'world_state':
        return (set(payload) == {'full', 'state'} and type(payload['full']) is bool
                and isinstance(payload['state'], dict))
    return False


def read_source(path, representation, expected_session=None, *, allow_partial=False, include_commentary=False):
    """Read exact text; opt-in partial mode retains unsupported-record gaps."""
    if representation == 'auto':
        # Select one representation, never concatenate duplicate views of a turn.
        events = read_source(path, 'event_msg', expected_session, allow_partial=allow_partial, include_commentary=include_commentary)
        if not events['usable'] or events['messages'] or events['gaps']:
            return events
        return read_source(path, 'response_item', expected_session, allow_partial=allow_partial, include_commentary=include_commentary)
    result = {"ok": False, "source_session_id": None, "original_started_at": None,
              "representation": representation, "source_sha256": None, "messages": [], "issues": [],
              "adapters": [], "usable": False, "complete": False, "gaps": []}
    if representation not in {"event_msg", "response_item"}:
        result["issues"].append("an explicit supported representation is required")
        return result
    path = Path(path).absolute()
    result["durable_path"] = str(path)
    try:
        if path.resolve(strict=True) != path or not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError("source must be a canonical regular nonlinked file")
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError("source changed during reading")
        text = raw.decode("utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        result["issues"].append(str(error))
        return result
    result["source_sha256"] = hashlib.sha256(raw).hexdigest()
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    for position, line in enumerate(lines):
        if not line.strip():
            result["issues"].append(f"source_position {position}: blank JSONL record")
            break
        recoverable = False
        try:
            record = json.loads(line, object_pairs_hook=unique_pairs,
                                parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid constant: {value}")))
            if not isinstance(record, dict):
                raise ValueError("record must be an object")
            kind = record.get("type")
            recoverable = kind != 'session_meta'
            if not isinstance(record.get("payload"), dict):
                raise ValueError("record payload must be an object")
            payload = record["payload"]
            if not nonblank(kind):
                raise ValueError("record type discriminator is missing or invalid")
            if kind == "session_meta":
                identity = payload.get("id")
                started = payload.get("timestamp", record.get("timestamp"))
                if not nonblank(identity) or not timestamp(started):
                    raise ValueError("original session ID or UTC start time is missing")
                if result["source_session_id"] is not None and (
                        identity != result["source_session_id"] or started != result["original_started_at"]):
                    raise ValueError("conflicting original session identity or start time")
                result["source_session_id"], result["original_started_at"] = identity, started
                continue
            if kind != representation:
                if kind not in ('event_msg', 'response_item', 'turn_context', 'compacted') and not reviewed_metadata(kind, payload):
                    raise ValueError('unsupported record type: ' + kind)
                continue
            recoverable = True
            if not nonblank(payload.get("type")):
                raise ValueError("selected representation payload type discriminator is missing or invalid")
            if representation == "event_msg":
                adapted = event_message(payload, include_commentary=include_commentary)
                if adapted is None:
                    continue
                payload, adapter = adapted
                if adapter not in result['adapters']:
                    result['adapters'].append(adapter)
                message_type = payload['type']
                role = "user" if message_type == "user_message" else "assistant"
                content = payload.get("message")
            else:
                if payload["type"] != "message":
                    if (payload['type'] == 'agent_message' and nonblank(payload.get('author'))
                            and nonblank(payload.get('recipient'))):
                        continue  # Native inter-agent assignment, not human conversation.
                    if payload['type'] in ('reasoning', 'function_call', 'function_call_output',
                            'custom_tool_call', 'custom_tool_call_output', 'additional_tools',
                            'configuration_update', 'web_search_call', 'file_search_call',
                            'computer_call', 'computer_call_output', 'image_generation_call',
                            'local_shell_call', 'local_shell_call_output', 'tool_search_call',
                            'tool_search_output') and 'role' not in payload:
                        continue
                    raise ValueError('unsupported response item type')
                if payload.get("role") in {"system", "developer"}:
                    continue
                if payload.get("role") not in {"user", "assistant"}:
                    raise ValueError("message role is missing or unsupported")
                role, content = payload["role"], payload.get("content")
                if 'codex-response-message-v1' not in result['adapters']:
                    result['adapters'].append('codex-response-message-v1')
            if role == "assistant":
                phase = payload.get("phase")
                if phase == "analysis" or (phase == "commentary" and not include_commentary):
                    continue
                if phase != "final_answer" and not (include_commentary and phase == "commentary"):
                    raise ValueError("assistant final-message phase is missing or unsupported")
            if representation == "response_item":
                if not isinstance(content, list) or not content:
                    raise ValueError("message text blocks are missing")
                parts = []
                for block in content:
                    allowed = {"input_text", "text"} if role == "user" else {"output_text", "text"}
                    if not isinstance(block, dict) or block.get("type") not in allowed or not isinstance(block.get("text"), str):
                        raise ValueError("unsupported or incomplete message content")
                    parts.append(block["text"])
                content = "".join(parts)
            if not isinstance(content, str):
                raise ValueError("message text is not a string")
            if not timestamp(record.get("timestamp")):
                raise ValueError("actual message UTC timestamp is missing")
            message = {"source_position": position, "role": role, "text": content,
                       "timestamp": record["timestamp"]}
            if nonblank(payload.get("id")):
                message["message_id"] = payload["id"]
            if nonblank(record['payload'].get('turn_id')):
                message['turn_id'] = record['payload']['turn_id']
            result["messages"].append(message)
        except (TypeError, ValueError) as error:
            if allow_partial and recoverable:
                result['gaps'].append({'source_position': position, 'reason': str(error)})
                continue
            result["issues"].append(f"source_position {position}: {error}")
            break
    if result["source_session_id"] is None:
        result["issues"].append("authoritative session metadata is missing")
    if expected_session is not None and expected_session != result["source_session_id"]:
        result["issues"].append("source session does not match the assigned session")
    for message in result["messages"]:
        message["source_session_id"] = result["source_session_id"]
    result["usable"] = not result["issues"]
    result["complete"] = result["usable"] and not result["gaps"]
    result["ok"] = result["complete"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--representation", default='auto', choices=["auto", "event_msg", "response_item"])
    parser.add_argument("--expected-session")
    parser.add_argument("--allow-partial", action="store_true", help="Retain supported messages and report unsupported-record gaps")
    args = parser.parse_args()
    result = read_source(args.source, args.representation, args.expected_session, allow_partial=args.allow_partial)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["usable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
