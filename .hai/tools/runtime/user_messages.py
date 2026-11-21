"""Plain-language notices for hosts displaying HAI runtime results."""


def usage_notice(summary, *, has_sources):
    if not has_sources:
        text = ('I can’t estimate the cost yet because I haven’t linked the saved conversation for this work. '
                'You can keep working. There’s nothing you need to do right now.')
    elif summary['coverage'] != 'observed':
        text = ('I can’t read all the usage for this work right now. Any figures shown may be out of date. '
                'You can keep working.')
    elif summary['estimated_credits'] is None:
        text = ('I found the usage for this work. I can estimate costs for models with known prices. '
                'A full estimate needs prices for every model used. You can keep working.')
    else:
        text = 'The usage estimate is ready. There’s nothing you need to do.'
    return {'action_owner': 'none', 'message': text}


def session_notice(status):
    if status == 'needs_binding':
        return {'action_owner': 'host', 'message':
                'I’ll look for the saved conversation for this session and check where this work began. '
                'You can keep working.'}
    if status == 'needs_boundary':
        return {'action_owner': 'host', 'message':
                'I found the saved conversation. I’ll check where this work began before using it to estimate costs. '
                'You can keep working.'}
    if status in ('needs_session_identity', 'unavailable'):
        return {'action_owner': 'host', 'message':
                'I couldn’t find the saved conversation for this session. I’ll check again on the next turn. '
                'You can keep working.'}
    return None
