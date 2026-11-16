# Optional workspace roles

An optional workspace role is a reusable set of domain instructions and supporting resources. A registered installed role package is discoverable in `.hai_env/roles/catalogue.md`; `hai_roles_library/roles/` contains source packages, not an execution origin. Installing, registering, selecting and authorizing work are separate decisions.

HAI core is a Python runtime, independent of role packages. The host coordinator interprets the user request and decides whether an available extension is appropriate under the host's actual capabilities and permissions. A definition or model profile does not prove that the host can invoke an agent. Core initialization, environment operations and Activity administration do not require optional extensions. The [role convention](../conventions/role_conv.md) describes the compatibility format for installed packages.

Each extension may declare its own settings contract and domain knowledge; saved settings remain outside the package and are preserved on replacement. Activity context, source provenance, actual results and unresolved dependencies remain relevant to extensions using those facilities. See [role configuration](role-configuration.md) and [Activity](activity.md).

A role definition and a separate sub-agent invocation are distinct. In direct
execution the host follows the role's instructions itself; a spawned sub-agent is
a separate host execution instance with its own invocation identity. Independent
review separates the reviewer from the implementation author. The shared
[execution policy](../conventions/role_conv.md#role-execution-and-delegation)
defines mode selection and reporting; the
[invocation convention](../conventions/agent-invocation_conv.md) owns working
folders and launch handoff.
