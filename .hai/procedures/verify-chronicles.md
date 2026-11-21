# Verify the Activity conversation

Run `recording verify` with activity_id. It is read-only, validates retained chat references and checks every assigned native source for missing messages, changed retained content and coverage gaps. It does not merely inspect a tail cursor.

When needs_synchronization is returned, apply `recording synchronize` and verify again. Report unavailable/unrecognized source records as incomplete coverage; preserve recognized messages. Existing legacy evidence requires explicit recording migrate, never an implicit empty verified state. Verification does not authenticate caller-supplied messages or establish coverage of unknown sessions.

See [recording](../conventions/chronicles_conv.md).
