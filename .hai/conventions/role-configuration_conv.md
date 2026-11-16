# Role configuration

## Declaration and ownership

Every installed HAI role declares the quoted string metadata
`hai-configuration-contract: "configuration/contract.json"` in `ROLE.md` and
ships that package-local JSON file. Roles with no local settings declare an empty settings object. The host
coordinator is not a built-in role package. The six required ROLE.md sections
and specialist execution metadata are defined by the role convention.

The installed registered role owns its supported settings, validation, requested
setup and scoped migration. Role-definition-manager owns contracts as definition
resources, not live settings. runtime retains core state, Activity location, chronicles, profiles
and startup policy. Specification-manager owns its enabled/location settings in
its own file. Core format 3 removes only the former specification feature entry;
chronicles stays central. Format 2 is recognized read-only migration context. Other-role configuration dependencies pass through host coordinator.

## Contract format 3

A contract is strict UTF-8 JSON without duplicate keys or nonstandard constants:

```json
{
  "contract_format_version": 3,
  "role": "git-manager",
  "current_config_format_version": 1,
  "supported_config_format_versions": [1],
  "settings": {
    "git.enabled": {"type": "boolean", "default": false},
    "git.auto_push.enabled": {"type": "boolean", "default": false},
    "github.enabled": {"type": "boolean", "default": false}
  }
}
```

These are the exact required root keys. Versions are positive JSON integers,
excluding Booleans; supported versions are unique and include the current version.
Contract format 3 supports Boolean leaves and `workspace-relative-directory` leaves
with nonblank string defaults. Legacy formats 1 and 2 use the old agent identity
and require explicit role migration; live role commands do not accept them. Each settings entry has exactly `type` and `default`, with the default matching
the declared supported type. A `boolean` default is a JSON Boolean. Directory
defaults/overrides follow the safe-directory rules below even when disabled.
Dotted setting paths contain lower-case snake_case components; no path may be an
ancestor of another declared leaf. Defaults are authoritative here, not in another
template. Unsupported contract features are errors, not implicit extensions.

The contract role matches the installed folder/ROLE.md identity. Its canonical path
resolves to a readable regular file inside that same package and workspace, with
no hardlink alias. Source
contracts are reviewed as package data and validated in a disposable installed
layout. Runtime never loads the library as a fallback.

A role without customizable settings declares `settings: {}`. It needs no
workspace configuration file. A saved empty settings object is valid; nonempty
settings are invalid for this contract. Do not invent settings merely to populate
an otherwise empty declaration.

A typed directory contract uses, for example:

```json
{
  "contract_format_version": 3,
  "role": "specification-manager",
  "current_config_format_version": 1,
  "supported_config_format_versions": [1],
  "settings": {
    "enabled": {"type": "boolean", "default": false},
    "location": {"type": "workspace-relative-directory", "default": ".hai_env/specifications"}
  }
}
```

Directory values are relative to the workspace, never a configurable override-file
location. Reject root/escaping/traversal/nonportable paths, reserved resources and
Activity/config/profile collisions; validate existing directory type and aliases.
An absent directory is valid, and reference changes do not create or move content.
The shared `workspace_directory_path(workspace, value, reserved_paths=())` API
validates candidates; a role's own current directory is not a collision with itself.

## Saved values and absence

Workspace settings use only the fixed
`.hai_env/config/roles/<role-name>.json` path, independently of runtime origin:

```json
{
  "config_format_version": 1,
  "settings": {
    "git": {"enabled": false, "auto_push": {"enabled": false}},
    "github": {"enabled": false}
  }
}
```

A saved file is an object with a supported positive integer `config_format_version`
and an object `settings`. Missing files and supported leaves use declared defaults;
a present wrong-type container/leaf, invalid version, unreadable file, duplicate
key, invalid JSON or unsafe path is never silently replaced by defaults. Report
invalid versus unverified status and pause only affected work. A missing file is
valid even before `.hai_env/` exists; readers never create it.

For contracts with settings, unrecognized additional root/nested values are opaque:
preserve them during authorized updates, ignore them for capabilities, and do not
echo them in tool results. A no-settings contract rejects nonempty saved settings.
Owner-specific validation may impose additional independent constraints, such as
Git auto-push requiring enabled Git. A generic configuration result is not evidence
that credentials, tools, remote access or operation authority have been checked.

Keep credentials, tokens and live readiness evidence out of these files. Saved
configuration cannot override instructions, register a role, configure chronicles or change model-profile mappings. The shared configuration helper reports
only known effective values and their provenance; unknown data is not an output.

## Paths and preservation

Reserve `.hai_env/config/` for saved configuration, outside `.hai/`, `.git/`,
role packages, state, fixed instructions, profiles and catalogues. Activity and
specification roots cannot equal, contain or fall inside that location, even when
disabled. Config files cannot alias another role's configuration or a reserved
resource, including through hard links, symlinks or junctions. Resolve and validate
existing ancestors and target types before reading and immediately before writing;
reject escaping/dangling links, traversal, alternate/absolute path syntax and
nonportable device/trailing-dot aliases. Configured content paths retain the
shared state's safe-path rules. Never relocate configuration through its contents.

Writers preserve unchosen settings and unknown values, recheck inspected bytes and
containment, and stop on concurrent changes or partial failure. Only explicit
initialization/migration/repair scope can replace invalid owned data. Loading,
validation, definition installation and registration do not create defaults files,
change settings, migrate formats or activate capabilities. Package updates preserve
external workspace files and report incompatible versions as dependencies.

## Compatibility and migration

Role configuration versions are independent of core state format, release SemVer,
specification-tree compatibility and package identity. Changing accepted settings
or defaults requires an explicit compatibility assessment; configuration migration
belongs to the owner under an approved mapping, not a version-marker edit.

An extraction from state verifies the destination before removing the migrated
owned fields. Different old/new values require an explicit decision; do not merge,
select precedence or continue indefinite dual reads. Unknown siblings stay in
state. Preserve recoverable prior bytes and report partial multi-file transitions;
coordinated writes are not a transaction and do not justify automatic retry,
rollback, deletion or resetting settings. Unchanged enablement during extraction
is not a new capability choice or proof of live readiness.

## References

- [Role configuration concept](../concepts/role-configuration.md): meaning and boundaries.
- [State](state_conv.md): retained core/feature contract and safe paths.
- [Role format](role_conv.md): identity, authoring and source-package ownership.
- [Configuration tools](../tools/configuration/README.md): read-only validation API and limits.
