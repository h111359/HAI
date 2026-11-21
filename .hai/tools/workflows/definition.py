"""Parse versioned workflow Markdown contracts without executing their content."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import stat

from path_contract import relative_parts, is_link_or_reparse


NAMES = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')
META = {'workflow_format', 'name', 'revision', 'entry', 'max_step_attempts', 'max_run_attempts'}
SECTIONS = ['Purpose', 'Inputs', 'Outcomes', 'Steps']
STEP_SECTIONS = ['Role', 'Instruction', 'Inputs', 'Outputs', 'Results']
FILE_SECTIONS = ['Inputs', 'Intermediate Files', 'Final Files']


class DefinitionError(ValueError):
    """An invalid or unsupported definition, with source/section/line context."""


def identifier(value, where='identifier'):
    if not isinstance(value, str) or len(value) > 64 or not NAMES.fullmatch(value):
        raise DefinitionError(f'{where}: expected a lowercase kebab-case identifier of at most 64 characters')
    return value


def artifact_path(value, *, output=False, where='path'):
    """Check portable literal path syntax; filesystem containment is a runtime check."""
    try:
        parts = relative_parts(value)
    except ValueError as exc:
        raise DefinitionError(f'{where}: {exc}') from exc
    if any('`' in part for part in parts):
        raise DefinitionError(f'{where}: path references must be literal, not Markdown or expressions')
    if output and (parts[0].casefold() in ('assignment.json', 'result.json')
                   or re.fullmatch(r'rejection-[0-9]+\.json', parts[0], re.I)):
        raise DefinitionError(f'{where}: output collides with runtime-owned attempt metadata')
    return value


def _reference(value, prefixes, where, *, output=False):
    if ':' not in value:
        raise DefinitionError(f'{where}: expected one of {", ".join(p + ":" for p in prefixes)}')
    prefix, suffix = value.split(':', 1)
    if prefix not in prefixes:
        raise DefinitionError(f'{where}: unsupported reference prefix {prefix!r}')
    if prefix == 'accepted':
        parts = suffix.split('/')
        if len(parts) != 3:
            raise DefinitionError(f'{where}: accepted source requires step/result/output')
        for part in parts:
            identifier(part, where)
    elif prefix in ('workflow', 'incoming', 'feedback', 'step', 'end'):
        identifier(suffix, where)
    else:
        artifact_path(suffix, output=output, where=where)
        if prefix == 'workspace':
            lower = suffix.casefold().split('/')
            if (lower[0] in ('.git', '.aws', '.codex', '.agents')
                    or lower[:2] == ['.hai_env', 'config']):
                raise DefinitionError(f'{where}: protected metadata/configuration input is not an artifact')
    return prefix, suffix


def _masked_headings(lines, source):
    """Keep original line coordinates; reject disguised structure inside fences."""
    headings, fence = [], None
    for number, line in lines:
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            char, length = marker[1][0], len(marker[1])
            if fence is None:
                fence = (char, length, number)
            elif char == fence[0] and length >= fence[1] and not marker[2].strip():
                fence = None
            continue
        heading = re.match(r'^(#{1,6}) (.+?)\s*$', line)
        if re.match(r'^ {1,3}#{1,4}\s', line):
            raise DefinitionError(f'{source}: line {number}: structural headings must start at column one')
        if fence:
            if heading and len(heading[1]) <= 4:
                raise DefinitionError(f'{source}: line {number}: code fence imitates a structural heading')
            continue
        if heading:
            headings.append((number, len(heading[1]), heading[2]))
    if fence:
        raise DefinitionError(f'{source}: line {fence[2]}: unclosed code fence')
    return headings


def _sections(lines, level, source, expected=None):
    matches = [(i, n, title) for i, (n, line) in enumerate(lines)
               if (m := re.match(r'^(#{1,6}) (.+?)\s*$', line)) and len(m[1]) == level
               for title in [m[2]]]
    if expected is not None and [title for _, _, title in matches] != expected:
        raise DefinitionError(f'{source}: expected sections in order: {", ".join(expected)}')
    if matches and any(line.strip() for _, line in lines[:matches[0][0]]):
        raise DefinitionError(f'{source}: unexpected content before first section')
    result = {}
    for index, (start, number, title) in enumerate(matches):
        if title in result:
            raise DefinitionError(f'{source}: line {number}: duplicate section {title!r}')
        end = matches[index + 1][0] if index + 1 < len(matches) else len(lines)
        result[title] = (lines[start + 1:end], number)
    return result


def _text(lines):
    return '\n'.join(line for _, line in lines).strip()


def _table(section, headers, where):
    lines, number = section
    nonblank = [(n, line.strip()) for n, line in lines if line.strip()]
    if len(nonblank) < 2:
        raise DefinitionError(f'{where}: line {number}: expected one table with headers {headers}')
    cells = []
    for n, line in nonblank:
        if not line.startswith('|') or not line.endswith('|') or '\\|' in line:
            raise DefinitionError(f'{where}: line {n}: only a single literal pipe table is allowed')
        values = [v.strip() for v in line[1:-1].split('|')]
        if len(values) != len(headers):
            raise DefinitionError(f'{where}: line {n}: expected {len(headers)} cells; literal/escaped pipes are unsupported')
        cells.append((n, values))
    if cells[0][1] != headers or any(not re.fullmatch(r':?-{3,}:?', c) for c in cells[1][1]):
        raise DefinitionError(f'{where}: line {cells[0][0]}: expected table headers {headers}')
    rows = []
    for row_number, (n, values) in enumerate(cells[2:], 1):
        if any(not value for value in values):
            raise DefinitionError(f'{where}: row {row_number}, line {n}: empty cells are not allowed')
        row = dict(zip((h.lower() for h in headers), values))
        row['_where'] = f'{where}: row {row_number}, line {n}'
        rows.append(row)
    return rows


def _named(rows):
    result = {}
    for row in rows:
        name = identifier(row['name'], row['_where'] + ' name')
        if name in result:
            raise DefinitionError(f'{row["_where"]}: duplicate name {name!r}')
        result[name] = row
    return result


def file_location(value, *, output=False, where='Location'):
    prefix, separator, tail = value.partition(':')
    if not separator:
        prefix, tail = 'workspace', value
    if prefix not in (('workspace', 'activity', 'run') if output else ('workspace', 'activity')):
        raise DefinitionError(f'{where}: unsupported file root {prefix!r}')
    if prefix == 'run' and not tail.startswith('files/'):
        raise DefinitionError(f'{where}: run destinations must be under run:files/')
    location = prefix + ':' + tail
    _reference(location, (prefix,), where)
    return location


def _file_lists(sections):
    catalogues = {}
    for section in FILE_SECTIONS:
        inputs = section == 'Inputs'
        headers = ['Name', 'Mode', 'Location', 'Format', 'Expectation']
        if inputs:
            headers.insert(1, 'Required')
        if section == 'Final Files':
            headers.insert(1, 'Action')
        rows = _named(_table(sections[section], headers, section))
        for row in rows.values():
            mode, location = row['mode'], row['location']
            if mode not in ('fixed', 'default', 'ask') or (mode == 'ask') != (location == '-'):
                raise DefinitionError(f'{row["_where"]}: use fixed/default with a path or ask with -')
            if mode != 'ask':
                row['location'] = file_location(location, output=not inputs, where=row['_where'])
            if inputs:
                if row['required'] not in ('yes', 'no'):
                    raise DefinitionError(f'{row["_where"]}: Required must be yes or no')
                row['required'] = row['required'] == 'yes'
            elif section == 'Final Files' and row['action'] not in ('create', 'update'):
                raise DefinitionError(f'{row["_where"]}: Action must be create or update')
        catalogues[section] = rows
    names = [name for rows in catalogues.values() for name in rows]
    if len(names) != len(set(names)):
        raise DefinitionError('File names must be unique across the three file lists')
    return [catalogues[section] for section in FILE_SECTIONS]


def _output_names(row, column, *, empty=False):
    if empty and row[column] == '-':
        return []
    names = [name.strip() for name in row[column].split(',')]
    if len(names) != len(set(names)):
        raise DefinitionError(f'{row["_where"]}: expected distinct output names')
    for name in names:
        identifier(name, row['_where'])
    return names


def _validate_inventory(definition):
    final = definition['final_files']
    declared = set(definition['intermediate_files']) | set(final)
    producers = {}
    for sid, step in definition['steps'].items():
        for name in step['outputs']:
            if name in producers:
                raise DefinitionError(f'{name}: file must have a single producing step')
            producers[name] = sid
    if set(producers) != declared:
        raise DefinitionError(f'Files without a producing step: {sorted(declared - set(producers))}')
    delivered = set()
    for outcome in definition['outcomes'].values():
        for name in outcome['files']:
            if name not in final:
                raise DefinitionError(f'Outcome {outcome["name"]}: {name!r} is not a declared final file')
            delivered.add(name)
    if delivered != set(final):
        raise DefinitionError(f'Final files without an outcome: {sorted(set(final) - delivered)}')
    available = {definition['entry']: set()}
    pending = [definition['entry']]
    while pending:
        sid = pending.pop()
        step = definition['steps'][sid]
        for result in step['results'].values():
            kind, target = result['next'].split(':', 1)
            after = (available[sid] - step['outputs'].keys()) | set(result['outputs'])
            if kind == 'end':
                missing = set(definition['outcomes'][target]['files']) - after
                if missing:
                    raise DefinitionError(f'{sid}/{result["name"]}: outcome requires unavailable files {sorted(missing)}')
            elif target not in available or not available[target] <= after:
                available[target] = available.get(target, after) & after
                pending.append(target)


def _validate_graph(definition):
    steps, outcomes = definition['steps'], definition['outcomes']
    entry = definition['entry']
    if entry not in steps:
        raise DefinitionError(f'entry: unknown step {entry!r}')
    edges, endings = {name: set() for name in steps}, {name: set() for name in steps}
    for sid, step in steps.items():
        for name, inp in step['inputs'].items():
            kind, source = inp['source'].split(':', 1)
            if kind == 'workflow':
                if source not in definition['inputs']:
                    raise DefinitionError(f'step {sid}/Inputs/{name}: unknown workflow input {source!r}')
                if inp['format'] != definition['inputs'][source]['format']:
                    raise DefinitionError(f'step {sid}/Inputs/{name}: Format differs from workflow input {source!r}')
            elif kind == 'accepted':
                parts = source.split('/')
                producer = steps.get(parts[0])
                result = producer and producer['results'].get(parts[1])
                if not result or parts[2] not in result['outputs']:
                    raise DefinitionError(f'step {sid}/Inputs/{name}: unknown accepted step/result/output')
                if inp['format'] != producer['outputs'][parts[2]]['format']:
                    raise DefinitionError(f'step {sid}/Inputs/{name}: Format differs from accepted output')
                if sid == entry and inp['required']:
                    raise DefinitionError(f'step {sid}/Inputs/{name}: entry cannot require accepted output')
            elif sid == entry and inp['required']:
                raise DefinitionError(f'step {sid}/Inputs/{name}: entry cannot require an incoming artifact')
        used = set()
        for label, row in step['results'].items():
            where = f'step {sid}/Results/{label}'
            for out in row['outputs']:
                if out not in step['outputs']:
                    raise DefinitionError(f'{where}: unknown output {out!r}')
                used.add(out)
            kind, target = row['next'].split(':', 1)
            if kind == 'end':
                if target not in outcomes:
                    raise DefinitionError(f'{where}: unknown outcome {target!r}')
                endings[sid].add(target)
                continue
            if target not in steps:
                raise DefinitionError(f'{where}: unknown target step {target!r}')
            edges[sid].add(target)
            for local, inp in steps[target]['inputs'].items():
                if not inp['source'].startswith(('incoming:', 'feedback:')):
                    continue
                output_name = inp['source'].split(':', 1)[1]
                if output_name not in row['outputs']:
                    if inp['required']:
                        raise DefinitionError(f'{where} -> step {target}/Inputs/{local}: required incoming output {output_name!r} is missing on this result')
                elif step['outputs'][output_name]['format'] != inp['format']:
                    raise DefinitionError(f'{where} -> step {target}/Inputs/{local}: input/output Format descriptions differ')
        if used != set(step['outputs']):
            raise DefinitionError(f'step {sid}/Outputs: unused declared outputs {sorted(set(step["outputs"]) - used)}')
    reachable, pending = set(), [entry]
    while pending:
        sid = pending.pop()
        if sid not in reachable:
            reachable.add(sid); pending.extend(edges[sid])
    if reachable != set(steps):
        raise DefinitionError(f'Steps: unreachable steps {sorted(set(steps) - reachable)}')
    reachable_outcomes = set().union(*(endings[sid] for sid in reachable))
    if reachable_outcomes != set(outcomes):
        raise DefinitionError(f'Outcomes: unreachable outcomes {sorted(set(outcomes) - reachable_outcomes)}')
    can_end = {sid for sid in steps if endings[sid]}
    while True:
        expanded = can_end | {sid for sid in steps if edges[sid] & can_end}
        if expanded == can_end:
            break
        can_end = expanded
    if can_end != set(steps):
        raise DefinitionError(f'Steps: no possible terminal path from {sorted(set(steps) - can_end)}')


def parse_definition(raw, source='<definition>', *, allow_legacy=False):
    """Return JSON-serializable contract data or raise DefinitionError. No I/O."""
    try:
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        if not isinstance(raw, bytes):
            raise DefinitionError('definition must be UTF-8 bytes or text')
        text = raw.decode('utf-8')
        if text.startswith('\ufeff') or '\x00' in text:
            raise DefinitionError('BOM and NUL are not supported')
        text = text.replace('\r\n', '\n')
        if '\r' in text:
            raise DefinitionError('only LF and CRLF line endings are supported')
        lines = text.split('\n')
        if not lines or lines[0] != '---':
            raise DefinitionError('line 1: YAML frontmatter must begin with ---')
        try:
            end = lines.index('---', 1)
        except ValueError as exc:
            raise DefinitionError('frontmatter: missing closing ---') from exc
        metadata = {}
        for n, line in enumerate(lines[1:end], 2):
            if not line:
                continue
            match = re.fullmatch(r'([a-z_]+): ([a-z0-9-]+)', line)
            if not match:
                raise DefinitionError(f'frontmatter: line {n}: expected a bare scalar key: value; full YAML syntax is unsupported')
            key, value = match.groups()
            if key not in META or key in metadata:
                raise DefinitionError(f'frontmatter: line {n}: unknown or duplicate key {key!r}')
            if key in ('name', 'entry'):
                metadata[key] = identifier(value, f'frontmatter line {n}/{key}')
            else:
                if not re.fullmatch(r'[0-9]+', value) or int(value) < 1:
                    raise DefinitionError(f'frontmatter: line {n}/{key}: expected a positive decimal integer')
                metadata[key] = int(value)
        if set(metadata) != META:
            raise DefinitionError(f'frontmatter: missing keys {sorted(META - set(metadata))}')
        if metadata['workflow_format'] not in (1, 2, 3, 4):
            raise DefinitionError('workflow_format: unsupported version')
        if metadata['workflow_format'] == 1 and not allow_legacy:
            raise DefinitionError('Legacy workflow_format 1 requires explicit role migration')
        role_section = 'Agent' if metadata['workflow_format'] == 1 else 'Role'
        step_sections_contract = [role_section, *STEP_SECTIONS[1:]]
        body = [(i + 1, line) for i, line in enumerate(lines) if i > end]
        while body and not body[0][1].strip():
            body.pop(0)
        if not body or not re.fullmatch(r'# \S.*', body[0][1]):
            raise DefinitionError('expected one H1 title immediately after frontmatter')
        title = body.pop(0)[1][2:].strip()
        headings = _masked_headings(body, source)
        if any(level == 1 for _, level, _ in headings):
            raise DefinitionError('expected exactly one H1 title')
        version3 = metadata['workflow_format'] == 3
        inventory = metadata['workflow_format'] == 4
        section_names = SECTIONS
        if version3:
            section_names = ['Purpose', 'Locations', *SECTIONS[1:]]
        if inventory:
            section_names = ['Purpose', *FILE_SECTIONS, 'Outcomes', 'Steps']
        sections = _sections(body, 2, source, section_names)
        locations = _named(_table(sections['Locations'], ['Name', 'Purpose', 'Contents'], 'Locations')) if version3 else None
        if version3 and not locations:
            raise DefinitionError('Locations: at least one configured output base is required')
        purpose = _text(sections['Purpose'][0])
        if not purpose:
            raise DefinitionError('Purpose: nonempty explanation required')
        for name in ('Purpose', 'Inputs', 'Outcomes'):
            if any(level in (3, 4) for _, level, _ in _masked_headings(sections[name][0], name)):
                raise DefinitionError(f'{name}: nested structural headings are unsupported')
        if inventory:
            inputs, intermediate, final = _file_lists(sections)
            files = {**intermediate, **final}
        else:
            inputs = _named(_table(sections['Inputs'], ['Name', 'Location', 'Format', 'Expectation'], 'Inputs'))
            for row in inputs.values():
                _reference(row['location'], ('workspace', 'activity'), row['_where'] + '/Location')
        outcomes = _named(_table(sections['Outcomes'], ['Name', 'Meaning', *(['Files'] if inventory else [])], 'Outcomes'))
        if inventory:
            for row in outcomes.values():
                row['files'] = _output_names(row, 'files', empty=True)
        if not outcomes:
            raise DefinitionError('Outcomes: at least one terminal outcome is required')
        step_sections = _sections(sections['Steps'][0], 3, 'Steps')
        if not step_sections:
            raise DefinitionError('Steps: at least one step is required')
        steps = {}
        for sid, (step_lines, number) in step_sections.items():
            identifier(sid, f'Steps line {number}')
            pieces = _sections(step_lines, 4, f'step {sid}', step_sections_contract)
            role = identifier(_text(pieces[role_section][0]), f'step {sid}/{role_section}')
            instruction = _text(pieces['Instruction'][0])
            if not instruction:
                raise DefinitionError(f'step {sid}/Instruction: nonempty instruction required')
            inp = _named(_table(pieces['Inputs'], ['Name', 'Source', 'Required', 'Format', 'Expectation'], f'step {sid}/Inputs'))
            for row in inp.values():
                _reference(row['source'], ('workflow', 'incoming', 'feedback', 'accepted') if version3 or inventory else ('workflow', 'incoming'), row['_where'] + '/Source')
                if row['required'] not in ('yes', 'no'):
                    raise DefinitionError(f'{row["_where"]}/Required: expected yes or no')
                row['required'] = row['required'] == 'yes'
            headers = ['Name'] if inventory else ['Name', 'Location', 'Format', 'Expectation']
            outputs = _named(_table(pieces['Outputs'], headers, f'step {sid}/Outputs'))
            if inventory:
                for name, row in outputs.items():
                    if name not in files:
                        raise DefinitionError(f'{row["_where"]}: undeclared output file {name!r}')
                    outputs[name] = {**files[name], 'location': 'attempt:files/' + name}
            if not outputs and not inventory:
                raise DefinitionError(f'step {sid}/Outputs: at least one output is required')
            output_paths = []
            for row in outputs.values():
                if version3:
                    prefix, _, tail = row['location'].partition(':')
                    key, _, pattern = tail.partition('/')
                    if prefix != 'configured' or key not in locations:
                        raise DefinitionError(f'{row["_where"]}/Location: expected configured:location/pattern')
                    if not pattern.startswith(sid + '-{execution}-') or pattern.count('{execution}') != 1 or '/' in pattern:
                        raise DefinitionError(f'{row["_where"]}/Location: filename must be step-{{execution}}-filename')
                    artifact_path(pattern.replace('{execution}', '001'), output=True, where=row['_where'])
                    if '{' in pattern.replace('{execution}', '') or '}' in pattern.replace('{execution}', ''):
                        raise DefinitionError('unsupported output pattern token')
                    location = key + '/' + pattern
                else:
                    _, location = _reference(row['location'], ('attempt',), row['_where'] + '/Location', output=True)
                lower = location.casefold()
                if any(lower == prior or lower.startswith(prior + '/') or prior.startswith(lower + '/') for prior in output_paths):
                    raise DefinitionError(f'{row["_where"]}/Location: duplicate, case-alias or overlapping output path')
                output_paths.append(lower)
            results = _named(_table(pieces['Results'], ['Name', 'When', 'Outputs', 'Next', *(['Gate'] if version3 or inventory else [])], f'step {sid}/Results'))
            if not results:
                raise DefinitionError(f'step {sid}/Results: at least one named result is required')
            for row in results.values():
                if (version3 or inventory) and row['gate'] not in ('none', 'human'):
                    raise DefinitionError('Results/Gate: expected none or human')
                row['outputs'] = _output_names(row, 'outputs', empty=inventory)
                _reference(row['next'], ('step', 'end'), row['_where'] + '/Next')
            steps[sid] = {'id': sid, 'role': role, 'instruction': instruction, 'inputs': inp, 'outputs': outputs, 'results': results}
        definition = {**metadata, 'title': title, 'purpose': purpose, 'inputs': inputs,
                      'outcomes': outcomes, 'steps': steps, 'sha256': hashlib.sha256(raw).hexdigest()}
        if version3:
            definition['locations'] = locations
            used_locations = {out['location'].split(':', 1)[1].split('/')[0] for step in steps.values() for out in step['outputs'].values()}
            if used_locations != set(locations):
                raise DefinitionError('Locations: every location must be used by an output')
        if inventory:
            definition.update(intermediate_files=intermediate, final_files=final)
        _validate_graph(definition)
        if inventory:
            _validate_inventory(definition)
        for rows in [inputs, outcomes, *([intermediate, final] if inventory else []), *[s[k] for s in steps.values() for k in ('inputs', 'outputs', 'results')]]:
            for row in rows.values():
                row.pop('_where', None)
        if locations:
            for row in locations.values():
                row.pop('_where', None)
        return definition
    except (UnicodeError, ValueError) as exc:
        detail = str(exc)
        raise DefinitionError(detail if detail.startswith(source + ':') else f'{source}: {detail}') from exc


def load_definition(path):
    """Read a canonical, singly-linked regular file and enforce filename identity."""
    path = Path(path).absolute()
    try:
        if path.resolve(strict=True) != path:
            raise DefinitionError('definition path must be canonical')
        for ancestor in (path, *path.parents):
            if is_link_or_reparse(ancestor.lstat()):
                raise DefinitionError('linked definition paths are prohibited')
        before = path.stat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise DefinitionError('definition must be a singly-linked regular file')
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise DefinitionError('definition changed during reading')
        result = parse_definition(raw, str(path))
        if path.name != result['name'] + '.md':
            raise DefinitionError('definition filename must exactly match name + .md')
        return result
    except OSError as exc:
        raise DefinitionError(f'{path}: {exc}') from exc
