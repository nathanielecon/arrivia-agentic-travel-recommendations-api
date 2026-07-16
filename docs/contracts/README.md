# Frozen reliability contracts

`partner-policy.schema.json` is the machine-readable upstream contract and
`partner-policy.example.json` is its canonical example. Partner policy is read-only and
required: malformed JSON, schema-invalid values, unknown properties, or conflicting
`exclude_cruise`/`exclude_cruises` values fail closed as `upstream_invalid_payload`.

Known values take effect dynamically. `null` means no per-session cap; a non-negative integer
is the cap. `exclude_cruise` is canonical and `exclude_cruises` is the only legacy alias. A new
property, type, or meaning requires model, evaluator, contract-test, and versioned deployment
support before upstream activation.
