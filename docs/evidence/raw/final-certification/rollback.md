# Final candidate distinct-image rollback

- Candidate B: source `3156cf8869563b9683f5c3ff67b4104d95dc1b40`, image `sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee`.
- Retained target A: source `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a`, image `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`.
- Shared volume: `arrivia-cert-data`.
- Snapshot volume: `arrivia-cert-snapshot-3156cf8`; database size 32768 bytes.

The session `rollback-3156cf8` was consumed to its cap on B. The API was stopped, and the SQLite database was copied entirely inside Docker's Linux locking domain. A was started against the unchanged data volume and returned zero recommendations for the capped session; the complete deployment verifier passed. B was then restored without rebuilding or restoring the database, returned zero recommendations for the same session, and passed the verifier again.

No database restore was used. The exercise preserved active counts and kept routine code rollback distinct from corruption recovery.
