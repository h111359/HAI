"""Human navigation, without a second Activity status database."""
from .storage import checked_path

START = '<!-- hai-navigation:start -->'
END = '<!-- hai-navigation:end -->'


def initial(state, summary=None):
    objective = summary or 'The objective has not been summarized. See the original message in the conversation.'
    return ('# Activity\n\nActivity: `' + state['activity_id'] + '`\n\n## Objective\n\n' + objective +
            '\n\nOriginal message: `' + str(state.get('initial_message_id') or 'not supplied') +
            '` in [conversation](system/chat.jsonl).\n').encode('utf-8')


def navigation(root, base, raw):
    content = raw.decode('utf-8')
    if content.count(START) != content.count(END) or content.count(START) > 1:
        raise ValueError('README navigation markers require inspection')
    links = []
    for relative, label in [('system/chat.jsonl', 'Conversation'), ('system/log.md', 'Work log'),
                            ('system/usage.md', 'Usage'), ('results', 'Reviewable outputs'),
                            ('evidence', 'Verification evidence'),
                            ('workflow-runs', 'Workflow runs'), ('history', 'Previous versions')]:
        if checked_path(root, base + '/' + relative).exists():
            links.append('- [' + label + '](' + relative + ')')
    block = START + '\n## Navigation\n\n' + '\n'.join(links) + '\n' + END
    if START in content:
        before, rest = content.split(START, 1)
        _, after = rest.split(END, 1)
        return (before + block + after).encode('utf-8')
    separator = '\n' if content.endswith('\n') else '\n\n'
    return (content + separator + block + '\n').encode('utf-8')
