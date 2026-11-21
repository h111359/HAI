"""Recording availability policy; integrity failures are never downgraded."""
from .storage import SafetyError


class RecordingInterruption(SafetyError):
    """A source compatibility/availability gap, not damaged retained evidence."""


def effective(state, mandatory=False):
    config = state['features'].get('chronicles', {'enabled': True})
    enabled = config['enabled']
    mode = config.get('mode', 'best_effort')
    if type(enabled) is not bool or type(mandatory) is not bool or mode not in ('best_effort', 'required'):
        raise ValueError('Invalid chronicles enabled, mode or mandatory policy')
    return {'enabled': enabled, 'mode': mode, 'mandatory': mandatory,
            'required': mandatory or (enabled and mode == 'required')}


def recoverable(error):
    return isinstance(error, RecordingInterruption) and not getattr(error, 'changed_files', [])
