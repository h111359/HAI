"""Reviewed, deterministic Codex message adapters. Source data never loads code."""

ADAPTERS = (
    {'name': 'codex-event-message-v1', 'representation': 'event_msg',
     'recognition': 'user_message / agent_message'},
    {'name': 'codex-completed-item-v1', 'representation': 'event_msg',
     'recognition': 'item_completed with UserMessage / AgentMessage'},
    {'name': 'codex-response-message-v1', 'representation': 'response_item',
     'recognition': 'message with user / assistant role'},
)


def blocks(content, allowed):
    if not isinstance(content, list) or not content:
        raise ValueError('message text blocks are missing')
    parts = []
    for block in content:
        if (not isinstance(block, dict) or block.get('type') not in allowed
                or not isinstance(block.get('text'), str)):
            raise ValueError('unsupported or incomplete message content')
        parts.append(block['text'])
    return ''.join(parts)


def event_message(payload, *, include_commentary=False):
    """Return normalized payload and adapter, or None for excluded events."""
    kind = payload.get('type')
    if kind in ('user_message', 'agent_message'):
        return payload, 'codex-event-message-v1'
    if kind == 'item_completed':
        item = payload.get('item')
        if not isinstance(item, dict) or not isinstance(item.get('type'), str):
            raise ValueError('completed item discriminator is missing or invalid')
        item_type = item['type']
        if item_type == 'ContextCompaction':
            # Observed completed compactions are lifecycle markers, not chat.
            # Reject a changed/message-bearing shape rather than lose content.
            if (set(item) != {'type', 'id'} or not isinstance(item['id'], str)
                    or not item['id'].strip()):
                raise ValueError('unsupported or incomplete context compaction item')
            return None
        if item_type == 'Extension' and item.get('kind') == 'web.search':
            # Reviewed host web-search/open-page tool records are not messages.
            if (set(item) != {'type', 'kind', 'id', 'query', 'action', 'results'}
                    or not isinstance(item['id'], str) or not item['id'].strip()
                    or not isinstance(item['query'], str)
                    or not isinstance(item['action'], dict)
                    or not isinstance(item['results'], list)):
                raise ValueError('unsupported or incomplete web-search extension item')
            return None
        if item_type not in ('UserMessage', 'AgentMessage'):
            if item_type in ('Reasoning', 'McpToolCall', 'CommandExecution', 'FileChange',
                             'WebSearch', 'ImageView', 'Plan', 'CollabAgentToolCall',
                             'SubAgentActivity'):
                return None
            raise ValueError('unsupported completed item type: ' + item_type)
        user = item_type == 'UserMessage'
        # Historical recording excludes progress; unified capture includes visible commentary.
        if not user and (item.get('phase') == 'analysis' or (item.get('phase') == 'commentary' and not include_commentary)):
            return None
        normalized = {'type': 'user_message' if user else 'agent_message',
                      'message': blocks(item.get('content'), {'text', 'Text'}),
                      'phase': item.get('phase')}
        if isinstance(item.get('id'), str):
            normalized['id'] = item['id']
        return normalized, 'codex-completed-item-v1'
    if 'message' in payload and kind not in ('error', 'warning'):
        raise ValueError('unsupported event message type')
    # A new message-shaped event must not disappear as harmless metadata.
    if any(key in payload for key in ('item', 'content', 'role', 'text')):
        raise ValueError('unsupported message-shaped event')
    if kind in ('task_started', 'task_complete', 'thread_settings_applied',
                'token_count', 'error', 'warning', 'agent_reasoning',
                'agent_reasoning_raw_content', 'tool_call', 'tool_result',
                'exec_command_begin', 'exec_command_end', 'turn_aborted',
                'context_compacted', 'session_configured'):
        return None
    raise ValueError('unsupported event type: ' + str(kind))
