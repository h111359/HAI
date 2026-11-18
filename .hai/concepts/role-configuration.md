# Role configuration

## Definition

Role configuration is a role's declared, versioned set of installation-specific
settings. Only an actual settings owner needs a configuration contract; a settings-free role omits it. Legacy declared empty contracts remain valid. A workspace file is needed only
when values are saved; its absence has the contract's declared meaning.

## Purpose

Keep settings with their responsible owner while preserving reusable packages and
workspace choices independently during upgrades.

## Explanation

The installed package supplies the contract and defaults. Workspace values live
outside packages at `.hai_env/config/roles/<role-name>.json`. Replacing a package
therefore does not replace user settings. A new contract can require assessment or
migration without silently changing existing values. Golden library packages are
source data; runtime contracts come from installed packages.

Ownership is distinct from independence. A role can depend on shared environment,
Activity, feature or model-profile assurance and another owner's validated result.
Configuration does not register a role, prove credentials or grant task permission.
An invalid optional configuration affects its dependent work, rather than every
other role. Missing values use declared defaults; malformed values do not become
defaults merely because a caller cannot use them.

Core state remains shared. Activity location and chronicles retain their runtime owner.
Specification-manager owns specification enabled/location separately from core
format 3; format 2 is migration context, not a runtime settings fallback.
Activity checkpoints, transcript coverage and worker progress are working records,
not configuration. Role configuration contains no credentials or live readiness
claims and does not override fixed instructions or reusable role rules.

## Supporting Terms

- [term:configuration contract]: package-owned data declaring supported setting names, types, defaults and configuration-format versions.
- [term:workspace configuration]: saved role-owned settings outside the role package, interpreted only under its installed contract.

## References

- [Role configuration convention](../conventions/role-configuration_conv.md): representation, safe paths and validation.
- [Role concept](role.md): ownership, selection and source boundaries.
- [Environment](environment.md): shared setup and continuity.

Direct skills may use an installed service owner contract and its existing saved settings without selecting the owner role. Settings stay once at their existing owner path; no skill-specific duplicate is created.
