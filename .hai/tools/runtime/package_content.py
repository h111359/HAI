"""Bounded logical relocation of Markdown package references during installation.

Only actual Markdown links outside fenced examples are adapted. Sources remain
unchanged. Own resources stay local; recognized source peers map to installed
owners, while core and existing canonical owners keep their locations.
"""
from pathlib import Path
import hashlib,os,re
from .storage import SafetyError,checked_path

LINK=re.compile(r'(?<=\])\(([^()\n]+)\)')

def links(text,convert):
    # Backtick code spans can cross lines; match complete equal-length delimiter
    # runs, and transform only Markdown outside them and fenced examples.
    inline=re.compile(r"(?<!`)(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)")
    def prose(segment):
        output=[];cursor=0
        for match in inline.finditer(segment):
            output.append(LINK.sub(lambda m:'('+convert(m[1])+')',segment[cursor:match.start()]))
            output.append(match[0]);cursor=match.end()
        output.append(LINK.sub(lambda m:'('+convert(m[1])+')',segment[cursor:]))
        return ''.join(output)
    output=[];buffer=[];fence=None
    for line in text.splitlines(keepends=True):
        marker=re.match(r'^\s*(`{3,}|~{3,})(.*)$',line)
        if marker:
            if buffer:output.append(prose(''.join(buffer)));buffer=[]
            token,suffix=marker.groups()
            if fence is None:fence=token
            elif token[0]==fence[0] and len(token)>=len(fence) and not suffix.strip():fence=None
            output.append(line)
        elif fence:output.append(line)
        else:buffer.append(line)
    if buffer:output.append(prose(''.join(buffer)))
    return ''.join(output)

def target(root,source,href):
    path,mark,fragment=href.partition('#')
    if not path or '://' in path or path.startswith('mailto:'):return None
    if path.startswith(('/','\\')) or '\\' in path or ':' in path or '?' in path:raise SafetyError('Unsafe package reference: '+href)
    resolved=(source.parent/path).resolve()
    if not resolved.is_relative_to(root):raise SafetyError('Package reference escapes workspace: '+href)
    return resolved,mark,fragment

def prepare(root,source,destination,manifest):
    root=Path(root).resolve(strict=True);src=checked_path(root,source,allow_missing=False);dest=checked_path(root,destination)
    content={};relocated=[]
    for name in manifest:
        original=checked_path(root,source+'/'+name,allow_missing=False).read_bytes();candidate=original
        if name.endswith('.md'):
            def convert(href):
                found=target(root,src/name,href)
                if found is None:return href
                resolved,mark,fragment=found
                if resolved.is_relative_to(src):mapped=dest/resolved.relative_to(src)
                else:
                    relative=resolved.relative_to(root);parts=relative.parts
                    if len(parts)>=2 and parts[0] in ('roles','skills'):mapped=root/'.hai_env'/relative
                    else:mapped=resolved
                return os.path.relpath(mapped,(dest/name).parent).replace('\\','/')+('#'+fragment if mark else '')
            candidate=links(original.decode('utf-8'),convert).encode('utf-8')
        content[name]=candidate
        if candidate!=original:relocated.append(name)
    unresolved=validate(root,destination,content)
    return content,relocated,unresolved

def validate(root,destination,content):
    root=Path(root).resolve(strict=True);dest=checked_path(root,destination);unresolved=[]
    for name,data in content.items():
        if not name.endswith('.md'):continue
        def inspect(href):
            found=target(root,dest/name,href)
            if found is None:return href
            resolved,_,_=found
            if resolved.is_relative_to(dest):
                local=resolved.relative_to(dest).as_posix()
                if local!='.' and local not in content and not any(x.startswith(local+'/') for x in content):raise SafetyError('Missing package-local reference: '+name+' -> '+href)
            else:
                relative=resolved.relative_to(root).as_posix();p=checked_path(root,relative)
                if not p.exists():
                    if relative.startswith(('.hai_env/roles/','.hai_env/skills/')):unresolved.append({'file':name,'target':relative,'status':'unavailable peer/owner dependency; no source fallback'})
                    else:raise SafetyError('Missing package/core reference: '+name+' -> '+href)
            return href
        links(data.decode('utf-8'),inspect)
    return unresolved

def hashes(content):return {name:hashlib.sha256(data).hexdigest() for name,data in content.items()}
