"""Actual portable source-to-installed bootstrap, checked with source removed."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import traceback
import urllib.parse

OUT = Path(__file__).resolve().parent
W = next(p for p in OUT.parents if (p / '.hai/tools/hai.py').is_file())
WORK = OUT / 'test-work'
os.environ.update(HAI_TEST_TMP=str(WORK), TMP=str(WORK / 'tmp'), TEMP=str(WORK / 'tmp'), TMPDIR=str(WORK / 'tmp'))
os.chdir(WORK)
sys.path[:0] = [str(W / '.hai/tools'), str(W / '.hai/tools/skills')]
from test_skill_tools import SkillTests
from runtime import skills, packages, activities

case = SkillTests()
case.setUp()
report = {'scenario': 'fresh actual role and settings-owner skill bootstrap with source absent'}
try:
    assert case.root.resolve().is_relative_to(OUT)
    case.environment_only()
    shutil.copytree(W / '.hai', case.root / '.hai', dirs_exist_ok=True)
    created = activities.handle('create', case.root, {'layout_version': 2, 'initial_input': 'Explicit isolated fresh-install verification', 'provenance': case.prov}, True)
    assert created['ok'], created
    for collection, names in [('roles', ['quality-assurance', 'backlog-manager']),
                              ('skills', ['quality-verification', 'backlog-management'])]:
        for name in names:
            shutil.copytree(W / collection / name, case.root / collection / name)
    source_skill = case.root / 'skills/quality-verification/SKILL.md'
    illustrative = '\n```markdown\n[Illustrative catalogue entry](new/example.md)\n```\n'
    source_skill.write_text(source_skill.read_text(encoding='utf-8') + illustrative, encoding='utf-8')
    source_before = {p.relative_to(case.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for collection in ('roles', 'skills') for p in (case.root / collection).rglob('*') if p.is_file()}
    operations = []
    for name in ('quality-verification', 'backlog-management'):
        response = skills.handle('install', case.root, {'source': 'skills/' + name, 'name': name, 'provenance': case.prov}, True)
        operations.append({'operation': 'skills install', 'name': name, 'ok': response['ok'], 'status': response['status'], 'issues': response['issues']})
        assert response['ok'], response
    pre_owner = skills.handle('resolve', case.root, {'name': 'backlog-management'}, False)
    assert not pre_owner['ok'], pre_owner
    for name in ('quality-assurance', 'backlog-manager'):
        response = packages.handle('install', case.root, {'source': 'roles/' + name, 'name': name, 'register': True, 'provenance': case.prov}, True)
        operations.append({'operation': 'roles install', 'name': name, 'ok': response['ok'], 'status': response['status'], 'issues': response['issues']})
        assert response['ok'], response
    defaults = skills.handle('resolve', case.root, {'name': 'backlog-management'}, False)
    assert defaults['ok'], defaults
    assert defaults['result']['configuration']['settings']['location'] == 'backlog'
    assert defaults['result']['configuration']['status'] == 'defaulted'
    chosen = case.write('.hai_env/config/roles/backlog-manager.json', json.dumps({'config_format_version': 1, 'settings': {'location': 'queues/backlog'}, 'fixture_owner_note': 'preserve exactly'}))
    chosen_bytes = chosen.read_bytes()
    request = {'source': 'skills/backlog-management', 'name': 'backlog-management', 'replace': True, 'reviewed_differences': [], 'provenance': case.prov}
    preview = skills.handle('install', case.root, request, False)
    assert preview['ok'], preview
    repeated = skills.handle('install', case.root, {**request, 'reviewed_differences': preview['result']['differences']}, True)
    assert repeated['ok'], repeated
    assert chosen.read_bytes() == chosen_bytes
    source_after = {p.relative_to(case.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for collection in ('roles', 'skills') for p in (case.root / collection).rglob('*') if p.is_file()}
    assert source_before == source_after
    assert illustrative in (case.root / '.hai_env/skills/quality-verification/SKILL.md').read_text(encoding='utf-8')
    for collection in ('roles', 'skills'):
        target = (case.root / collection).resolve()
        assert target.is_relative_to(case.root.resolve()) and target.name == collection
        shutil.rmtree(target)
    links, broken = 0, []
    for collection in ('.hai_env/roles', '.hai_env/skills'):
        for p in (case.root / collection).rglob('*.md'):
            text = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', p.read_text(encoding='utf-8-sig'))
            for raw in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
                target = urllib.parse.unquote(raw.split(' "', 1)[0].strip('<>').split('#', 1)[0])
                if not target or re.match(r'[a-z][a-z0-9+.-]*:', target, re.I) or any(x in target for x in '<>{}'):
                    continue
                links += 1
                if not (p.parent / target).resolve().exists():
                    broken.append({'file': p.relative_to(case.root).as_posix(), 'target': target})
    assert not broken, broken
    for name in ('quality-assurance', 'backlog-manager'):
        response = packages.handle('validate', case.root, {'definition': '.hai_env/roles/' + name + '/ROLE.md'}, False)
        assert response['ok'], response
        selected = packages.handle('skills', case.root, {'definition': '.hai_env/roles/' + name + '/ROLE.md'}, False)
        assert selected['ok'], selected
    actual = skills.handle('resolve', case.root, {'name': 'backlog-management'}, False)
    assert actual['ok'] and actual['result']['configuration']['settings']['location'] == 'queues/backlog', actual
    assert skills.handle('resolve', case.root, {'name': 'quality-verification'}, False)['ok']
    report.update(passed=True, operations=operations, before_owner_resolution=pre_owner,
                  owner_default_settings=defaults['result']['configuration'], chosen_setting_bytes_preserved=True,
                  final_chosen_settings=actual['result']['configuration'], source_bytes_unchanged=True,
                  source_collections_removed=True, installed_local_links_checked=links, broken_installed_links=broken,
                  fenced_example_preserved=True)
except Exception:
    report.update(passed=False, exception=traceback.format_exc())
finally:
    case.doCleanups()
(OUT / 'fresh-install-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report.get('passed') else 1)
