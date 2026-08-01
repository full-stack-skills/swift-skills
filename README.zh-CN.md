# Swift Skills

[English](README.md)

面向 AI 编程代理的生产级 Swift 技能包。仓库沿用 `rust-skills` 的分层方法，但全部采用 Swift 原生边界：语言语义、SwiftPM、结构化并发、测试、审查和 Java 无损迁移。

技能组合与验收流程见[仓库架构](docs/ARCHITECTURE.md)。

## 初始技能集（7 个）

| 技能 | 职责 |
|---|---|
| `swift-stable` | Swift 稳定语言语义、所有权、协议与错误处理 |
| `swift-package-manager` | SwiftPM 产品、Target、依赖、资源与 CI |
| `swift-concurrency` | async/await、actor、Task、取消与 Sendable 安全 |
| `swift-testing` | XCTest/Swift Testing、异步、集成与端到端测试 |
| `swift-code-review` | 以正确性为先的 Swift 代码审查 |
| `swift-java-migration` | Java 到 Swift 的无损实现流程 |
| `swift-java-migration-testing` | 源测试、测试资产和逐用例差分验收 |

## 迁移完成标准

只有当源项目生产对象和公开契约全部入账、源语言测试及具体用例 100% 在 Swift 中无损实现、测试资产逐字节一致、两套完整测试均通过且每个差分用例均为 `MATCH` 时，才可声明迁移完成。覆盖率只是辅助证据，不是完成标准。

大型迁移必须建立独立的 `<project>-test` 验收 Package，或边界清晰的集成测试 Target；生产 Target 内的测试只承担局部验证。

## 验证

```bash
python3 scripts/validate_skills.py
python3 scripts/validate_skills.py --check-examples
```

第二条命令会构建每个 golden Package，并运行其中的可执行契约校验器。

## 许可证

Apache License 2.0。
