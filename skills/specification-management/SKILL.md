---
name: specification-management
description: "Configure, locate, author, organize and verify durable specification knowledge, using explicit roots and preserving meaning, identities and approval history."
metadata:
  hai-settings-owner: "specification-manager"
---

# Specification management

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

Settings have one owner: `specification-manager`. Use `skills resolve` to validate the installed owner contract and read `.hai_env/config/roles/specification-manager.json` once; absent values use that contract defaults, invalid values block dependent operations. Selecting this skill does not select the owner role.

## Method constraints

- **Configuration independence:** The operator MUST NOT require an enabled specification or adopted tree to diagnose or explicitly configure its owned settings.
- **No legacy fallback:** The operator MUST NOT obtain active enablement or location from `state.features.specification`.
- **Compatible environment:** The operator MUST require verified compatible environment settings before HAI-managed specification work.
- **Enabled specification:** The operator MUST require locally validated owner settings showing specification enabled before HAI-managed tree work.
- **Settings freshness:** The operator MUST revalidate owner settings when their source, core path context or inputs change rather than rely on stale caller assurance.
- **Configured specification folder:** The operator MUST use the supplied workspace and specification folder that match the verified settings for HAI-managed work.
- **No standalone bypass:** The operator MUST NOT reclassify HAI-managed work as standalone to bypass missing, invalid, disabled or differing HAI context.
- **Package contract:** The operator MUST apply the independent package contract to specification work rather than make it a general HAI startup requirement.
- **Incompatible trees:** The operator MUST keep unmarked, older, newer or invalid trees read-only until the applicable approved adoption, migration or repair.
- **Tree format:** The operator MUST follow the specification concept and relevant registered leaf conventions for metadata, identity, topology, balance, content, lifecycle and the root-only derived catalogue.
- **No fabricated structure:** The operator MUST NOT invent topics, content or types to satisfy structural limits.
- **Supplied roots:** The operator MUST use an explicit caller root in standalone work and the validated owner location for HAI work, rejecting a supplied HAI root that differs rather than guessing or searching.
- **Linked paths:** The operator MUST reject root or descendant symlinks and junctions under the helper's path contract.
- **Workspace location:** The operator MUST keep the specification tree inside the supplied workspace when the caller supplies that boundary.
- **Relevant knowledge:** The operator MUST limit its working knowledge to task-relevant package/type information, supplied source lifecycle and authorized evidence.
- **Knowledge reuse:** The operator MAY reuse unchanged knowledge already available in context.
- **Content sources:** The operator MUST obtain meaningful required sources before content writes.
- **Existing-tree inspection:** The operator MAY inspect an authorized existing tree without new product sources.
- **Product discovery scope:** The operator MUST limit product discovery to explicit verified source roots, caller privacy/exclusions and the workspace-structure contract.
- **Excluded implementation:** The operator MUST NOT reverse-engineer reusable frameworks, working records or dependency descendants into product facts.
- **Governing material:** The operator MAY read governing instructions and the established specification despite product-discovery exclusions.
- **Live marker order:** The operator MUST NOT write the live target marker before checks confirm that the agreed changes meet the target requirements and preserve existing information.
- **Staged marker check:** The operator MAY test the target marker on a staged candidate before asserting live compliance.
- **Marker evidence:** The operator MUST NOT treat a marker alone as completed migration evidence.
- **Migration completion:** The operator MUST NOT report a migration as complete before its required final checks succeed.
- **Helper evidence:** The operator MUST limit helper-success claims to the documented mechanical checks.
- **Semantic evidence:** The operator MUST support claims about content meaning, sources/approval, external references, classification and compatibility with relevant semantic verification.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Configure specification settings | HAI specification settings need validation, explicit setup or scoped repair. | [Configure specification settings](procedures/configure-specification.md) |
| Locate and inspect the specification | Specification work begins or an explicitly supplied tree needs read-only assessment. | [Locate and inspect the specification](procedures/locate-and-inspect.md) |
| Adopt or migrate specification | Explicit specification adoption, compatibility migration or marker repair is requested. | [Adopt or migrate specification](procedures/adopt-or-migrate.md) |
| Enter and update information | Authorized durable product information needs entry or revision. | [Enter and update information](procedures/enter-and-update.md) |
| Discover workspace information | Workspace paths are registered or implementation is reverse-engineered into product specification. | [Discover workspace information](procedures/discover-workspace.md) |
| Organize, split, and balance | Authorized specification restructuring, split, merge or rebalancing is needed. | [Organize, split, and balance](procedures/organize.md) |
| Verification and handoff | Before handing off specification changes or a requested assessment. | [Verification and handoff](procedures/verify-and-handoff.md) |

## References

- [Role configuration](../../.hai/conventions/role-configuration_conv.md) and [owned contract](../../roles/specification-manager/configuration/contract.json) — required for HAI settings and dependent HAI work; standalone explicit-root tree work needs no HAI files.
- [HAI configuration convention](conventions/configuration_conv.md) and [settings helper](scripts/specification_configuration.py) — required for HAI settings validation/setup; independent of tree compatibility.

- [Specification format](concepts/specification.md) - structure, classification, type registry, and lifecycle - required before specification work.
- [Contract versioning](conventions/contract-versioning_conv.md) and [package contract](contract.json) - target version, baseline, transition ledger, adoption/migration gates and verification - required when specification work begins; not general startup.
- This package's `conventions/<type>_conv.md` files - leaf content formats - conditional for types created or changed; read only those types.
- [Workspace structure convention](conventions/workspace-structure_conv.md#discovery-boundaries) - discovery exclusions and library boundaries - required before mapping workspace paths or reverse-engineering implementation.
- [Audit helper instructions](scripts/README.md) - runtime, paths, usage, and limits - required on first audit use.
- [Audit fixture tests](scripts/test_audit_specification.py) - helper verification - conditional when changing the helper itself.
- Caller-supplied workspace instructions, HAI validation context, and source lifecycle information — required as applicable to HAI-managed work, including separate core/Activity and locally validated owner enablement/location assurance; standalone package invocation requires no HAI files, but HAI-managed work must not be reclassified as standalone to bypass missing or invalid context.
- [term:Caller] → [Specification invocation](concepts/invocation.md) — required when interpreting invocation authority.
- [term:specification] → [Specification format](concepts/specification.md) — required before specification work.
