# Replacement candidate distinct-image rollback

- Candidate B: source `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c`, image `sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4`.
- Retained target A: source `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a`, image `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`.
- Snapshot: `arrivia-cert-snapshot-f5e9dc4`; SQLite database size 49152 bytes.

Session `rollback-f5e9dc4` was consumed to its cap on B. With the API stopped, the data volume was copied entirely inside Docker's Linux locking domain. A returned zero recommendations for the capped session and passed the full deployment verifier. B was restored without rebuilding or database restore, returned zero recommendations for the same session, and passed the verifier.

No database restore was used; active state remained intact across B→A→B.
