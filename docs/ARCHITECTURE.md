# Repository architecture

```mermaid
flowchart LR
  R[User request] --> S{swift-stable}
  S --> P[swift-package-manager]
  S --> C[swift-concurrency]
  S --> T[swift-testing]
  S --> V[swift-code-review]
  J[Java source project] --> M[swift-java-migration]
  M --> A[swift-java-migration-testing]
  P --> A
  C --> A
  T --> A
  A --> G[Parity gate: 100% tests + assets + MATCH]
```

The core skills solve Swift-native engineering tasks independently. The migration pair composes them: implementation owns the source-object and contract ledger; acceptance owns source-test parity, copied assets, whole-project `<project>-test` execution, differential comparison, and Swift-only risk tests.

