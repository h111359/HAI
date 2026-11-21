# HAI environment

The environment is the persistent, workspace-specific configuration, fixed instructions, Activities and optional records in `.hai_env/`, separate from reusable `.hai/` framework resources. Product code and specifications remain in their canonical workspace locations.

The fixed `.hai_env/config/agent_instructions.md` is loaded independently of state validity. A readable empty file is valid; missing or unreadable instructions block dependent work, while diagnosis remains possible. Compatible `.hai_env/config/state.json` defines the mandatory Activity location; conversation recording has no optional switch. Safely absent state differs from invalid or incompatible state; startup is read-only, initialization creates minimal state, and existing-state repair or migration requires covering authority.

Activities retain stable identity and work continuity across chats; record operations preserve provenance, prior revisions and actual outcomes. The runtime administers supported state and Activity operations. The host coordinator supplies the user's scope, choices and evidence and reports actual results. See the [Activity concept](activity.md), [state convention](../conventions/state_conv.md), and [runtime commands](../tools/runtime/README.md).

Conversation recording is always enabled. Human entries and delivered assistant replies share the Activity chat; registered native sources are checked for missing messages each turn. Operational state contains references, not duplicate text. Unavailable sources produce honest coverage warnings. See the [recording contract](../conventions/chronicles_conv.md).

Optional workspace role packages and their catalogue live under `.hai_env/roles/`; their package-owned settings live separately under `.hai_env/config/roles/`. Core initialization and administration require no agent or model profile. Installing, registering and using an optional extension are distinct operations and require the appropriate scope and actual host support. See [role concept](role.md) and [role configuration](role-configuration.md).

Installed skills live separately in .hai_env/skills/ and may be used directly
within the user task scope or selected by a role. Any source packages are caller-selected data, never required workspace
collections or installed execution origins. Core uses only .hai/ and .hai_env/
unless a task or environment setting explicitly supplies another location. Workflow location choices
are stored separately under .hai_env/config/workflows/; reusable definitions keep
the artifact names and contracts, while each environment chooses safe output bases.
Accepted workflow evidence and source lineage remain with the owning Activity.
