# Role configuration tools

`configuration_tools.py` provides a read-only Python 3.11+ standard-library
loader for settings owned by one selected role. Role packages declare
`hai-configuration-contract: "configuration/contract.json"` in their `ROLE.md`.
The contract stays with the package; workspace overrides live at
`.hai_env/config/roles/<role-name>.json`.

Run a bounded check for one selected role from the workspace root:

```text
<absolute-python-executable> -B .hai/tools/configuration/configuration_tools.py \
  --role git-manager \
  --contract .hai_env/roles/git-manager/configuration/contract.json
<absolute-python-executable> -B .hai/tools/configuration/test_configuration_tools.py
```

Pass `--workspace /path/to/workspace` when running from elsewhere. The contract
argument must be the canonical `configuration/contract.json` inside that role's
framework or workspace package. The command reads that one contract and that
role's saved configuration. It does not scan catalogues, definitions, or other
roles' configurations.

Contract format 3 declares a matching `role` name, current and supported positive
configuration versions, and a `settings` object. It supports Boolean leaves and
`workspace-relative-directory` leaves with string defaults. Legacy contract
formats 1 and 2 require the explicit role migration. Each dotted setting name declares exactly a `type`
and compatible `default`. A settings-free role needs no contract or saved file; legacy declared empty contracts remain supported. Saved files use a
`config_format_version` and nested `settings` object. Missing files and missing
declared leaves use contract defaults. A present malformed file, unsupported
version, wrong container, or wrong type is reported as invalid and never silently
falls back to defaults. Unknown values in a configurable role's file are ignored
and never returned as active settings; a settings-free role's nonempty override is
invalid.

The Python API is `load_contract(path, expected_role)`,
`read_configuration(workspace, role, contract)`, `configuration_path(workspace,
role)`, `workspace_directory_path(workspace, value, reserved_paths=())`, and
`load_json(path)`. `workspace_directory_path` checks workspace containment,
reserved core/config/profile/Activity paths and existing directory type even when
the owning setting is disabled. It accepts extra caller-supplied reservation paths
for candidate-state validation. `load_contract` and `load_json` raise
`ConfigurationError` for invalid or unreadable input. `read_configuration` returns
`status` (`defaulted`, `configured`, `invalid`, or `unverified`), the canonical
configuration path, effective declared settings, configured dotted fields, and
isolated issues. It performs no writes. Configuration targets that escape the
workspace or overlap core state, mandatory instructions, profiles, Activities,
specifications, or other role configuration files are rejected.

The command emits JSON. Exit `0` means the selected role's saved file is valid or
absent and its defaults can be used; exit `1` reports an isolated configuration
path/file/schema issue; exit `2` reports an invalid command input or contract.
Core state is validated independently by the startup helper. A missing role
configuration remains `defaulted` even when core state is invalid; an invalid
state does not silently become valid or block unrelated read-only configuration
diagnostics.

The startup helper reserves `.hai_env/config` against core state, Activity,
specification, profile, and mandatory-instructions paths. Normal startup does not
open role definitions. It checks only the registered Specification-manager
contract and configuration; other configuration checks belong to the selected role.
Legacy or incomplete role migration blocks live configuration access so old saved
settings cannot silently become new defaults.

Direct skills can consume an actual installed service-owner contract and the same saved settings through skills resolve, without selecting the owner role or duplicating configuration.

Core `configuration read` reports `not_required` for a settings-free installed role, without creating a contract or saved file. Existing saved values without a declared owner contract block the affected operation for explicit ownership resolution. Package replacement validates chosen values against the candidate owner contract and blocks an update that would orphan or invalidate them.
