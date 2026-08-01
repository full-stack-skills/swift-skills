# Swift Skills

[中文](README.zh-CN.md)

Production-oriented Swift skills for AI coding agents. The repository follows the layered `rust-skills` model while using Swift-native boundaries: language semantics, SwiftPM, structured concurrency, testing, review, and lossless Java migration.

See [repository architecture](docs/ARCHITECTURE.md) for the composition and acceptance flow.

## Initial skill set (7)

| Skill | Responsibility |
|---|---|
| `swift-stable` | Stable Swift language semantics, ownership, protocols, and error handling |
| `swift-package-manager` | SwiftPM products, targets, dependencies, resources, and CI |
| `swift-concurrency` | async/await, actors, tasks, cancellation, and Sendable safety |
| `swift-testing` | XCTest/Swift Testing, async tests, integration, and end-to-end testing |
| `swift-code-review` | Correctness-first Swift review with actionable findings |
| `swift-java-migration` | Lossless Java-to-Swift implementation workflow |
| `swift-java-migration-testing` | Complete source-test parity, asset parity, and differential acceptance |

## Migration completion contract

A migration is complete only when all source production objects and public contracts are accounted for, 100% of source tests and concrete cases are implemented in Swift, source test assets are byte-identical, both complete suites pass, and every differential case is `MATCH`. Coverage is supporting evidence, not the completion criterion.

Large migrations must add a dedicated `<project>-test` acceptance package or clearly separated integration test target. Tests inside production targets remain local unit or component tests.

## Validation

```bash
python3 scripts/validate_skills.py
python3 scripts/validate_skills.py --check-examples
```

The second command builds every golden package and runs its executable contract verifier.

## License

Apache License 2.0.
