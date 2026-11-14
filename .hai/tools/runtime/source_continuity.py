"""Conservative exact-message continuity proofs; never fuzzy-match transcripts."""
import json
from .storage import SafetyError


def token(message):
    return ('## Prompt:\n\n' if message['role'] == 'user' else '## Outcome:\n\n') + message['text'] + '\n\n'


def snapshot(messages):
    return [{k: m[k] for k in ('source_position', 'role', 'text', 'timestamp', 'message_id', 'turn_id') if k in m}
            for m in messages]


def legacy_matches(transcript, candidates):
    """Find a unique exact rendering without splitting headings inside message text."""
    header = '# Activity transcript\n\n## Source:\n\n'
    if not transcript.startswith(header):
        raise SafetyError('Unsupported retained transcript header')
    try:
        _, end = json.JSONDecoder().raw_decode(transcript[len(header):])
    except ValueError as exc:
        raise SafetyError('Invalid retained transcript metadata') from exc
    body = transcript[len(header) + end:]
    if not body.startswith('\n\n'):
        raise SafetyError('Invalid retained transcript body')
    body = body[2:]
    # Iterative search, capped to refuse pathological/ambiguous legacy evidence.
    stack, solutions, visited = [(0, -1, [])], [], 0
    rendered = [token(m) for m in candidates]
    while stack:
        offset, previous, path = stack.pop()
        visited += 1
        if visited > 100000:
            raise SafetyError('Legacy continuity proof exceeds safe search bound')
        if offset == len(body):
            solutions.append(path)
            if len(solutions) > 1:
                raise SafetyError('Ambiguous retained messages; explicit reconciliation required')
            continue
        for n in range(previous + 1, len(candidates)):
            if body.startswith(rendered[n], offset):
                stack.append((offset + len(rendered[n]), n, path + [n]))
    if len(solutions) != 1:
        raise SafetyError('Retained messages changed or disappeared; explicit reconciliation required')
    matched = [candidates[n] for n in solutions[0]]
    # Old plain Markdown has no escaping or message-count index. If its text
    # contains a complete framing delimiter, original message boundaries cannot
    # be proved from that representation alone, even with one current rendering.
    if any(repr_marker in m['text'] for m in matched
           for repr_marker in ('## Prompt:\n\n', '## Outcome:\n\n')):
        raise SafetyError('Legacy transcript contains ambiguous framing; explicit reconciliation required')
    return matched


def indexed_matches(index, candidates):
    selected, previous = [], -1
    for old in index:
        matches = [m for m in candidates if m['source_position'] > previous
                   and m['role'] == old['role'] and m['text'] == old['text']
                   and (m.get('turn_id') == old['turn_id'] if old.get('turn_id')
                        else not old.get('message_id') or m.get('message_id') == old['message_id'])]
        if len(matches) != 1:
            raise SafetyError('Changed, missing or ambiguous recorded message identity')
        selected.append(matches[0]); previous = matches[0]['source_position']
    return selected


def rebase(binding, previous, extracted, transcript):
    """Only a single continuously enabled live assignment can move automatically."""
    intervals = binding['enabled_intervals']
    if (binding['end_position'] is not None or len(intervals) != 1
            or intervals[0]['end'] is not None
            or intervals[0]['start']['source_position'] != binding['start_position']):
        raise SafetyError('Closed or discontinuous recording boundaries require explicit reconciliation')
    candidates = extracted['messages']
    index = previous.get('message_index')
    matched = indexed_matches(index, candidates) if index else legacy_matches(transcript, candidates)
    if not matched or matched[0]['role'] != 'user':
        raise SafetyError('Reconciled assignment must begin with its recorded work prompt')
    first, last = matched[0]['source_position'], matched[-1]['source_position']
    # Never silently admit newly inserted exchanges among recorded ones.
    between = [m for m in candidates if first <= m['source_position'] <= last]
    if between != matched:
        raise SafetyError('New or reordered exchanges inside retained recording')
    binding['start_position'] = first
    intervals[0]['start']['source_position'] = first
    return matched
