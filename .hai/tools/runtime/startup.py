from pathlib import Path
import sys
import os
import platform
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'startup'))
import startup_context

def handle(operation, workspace, request, apply):
    if operation not in ('', 'check', 'context') or request or apply:
        raise ValueError('startup accepts no operation, request, or apply')
    result = startup_context.context(workspace)
    result['execution_context'] = {
        'os': platform.system(), 'sys_platform': sys.platform, 'os_name': os.name,
        'python_version': platform.python_version(), 'python_executable': sys.executable,
        'workspace_path_format': 'posix-relative',
    }
    if result['environment'] == 'valid' and result['instructions_status'] == 'loaded':
        from .source_discovery import readiness
        from .activities import add_workflow_context
        from .user_messages import session_notice
        add_workflow_context(Path(workspace), result['activity_context'])
        recording = readiness(workspace, result['activity_context'])
        notice = session_notice(recording['status'])
        if notice:
            recording['user_notice'] = notice
        result['recording_context'] = recording
    else:
        result['recording_context'] = {'status': 'unverified', 'details': 'Core prerequisites are not valid'}
    return {'ok': result['ok'], 'status': 'valid' if result['ok'] else 'blocked', 'result': result,
            'issues': result['issues'], 'changed_files': []}

def require_mutation_context(workspace):
    from .storage import SafetyError
    core = startup_context.check(workspace)
    if core['environment'] != 'valid' or core['instructions_status'] != 'loaded' or core.get('state_format_version') != 3:
        raise SafetyError('Valid current core state and readable mandatory instructions are required for mutation')
    return core
