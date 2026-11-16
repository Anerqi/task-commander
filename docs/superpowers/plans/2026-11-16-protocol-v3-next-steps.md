# Protocol v3 Next Steps Implementation Plan

> Historical execution record. The structural convention in this plan is superseded by `2026-11-16-unify-v3-compact-context.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 在最新远端基线上明确协议合并约定，完成 v3、状态章节兼容和统一校验限制。

**Architecture:** 保留文件协议、现有角色和任务状态机。状态校验器与渲染器使用同一套章节及限制约定。协议说明、模板、测试和 CI 随行为变更一并更新。

**Tech Stack:** Python 3.10+，仅标准库；Markdown；unittest；GitHub Actions。

**Spec:** 用户提供的原会话预览（conversation `6af99c73-f540-83ec-bc4d-013273df341e`）与 `docs/plans/2026-11-02-authority-and-attention.md`。预览只证明存在这些讨论项，不能替代完整规格或当前授权。

## Global Constraints

- 用户后续已授权子代理并行实现与清理，并进一步授权清理缓存后提交和推送。
- 更新基线：`a52ecec`，由 `499283d` 快进合并远端 12 个提交。
- 保留 `.qoder/` 和远端新增的 Commander 范围、决策确认及评测规则。
- 保持 Python 3.10+、零第三方运行时依赖和 Windows/macOS/Linux 支持。
- 旧状态文件保持有效；不重写任务 ID、状态历史或在途任务合同。
- 英文遵循当前 SKILL.md 的清晰写作原则；代码、字段名和正式状态标签保持准确。
- 上述执行子技能当前未提供；进入实现时按实际可用能力选择执行方法，不声称已加载它们。

## Review Focus

- 旧版独立章节与新版嵌套章节应被校验器和渲染器一致解释。
- 空表、文件末尾、相邻同级标题不能让章节解析吞入其他表格。
- Completed 数量为 10 与 11 时，警告边界必须准确；警告不应使文件无效。
- Completed 与 Cancelled 必须按确认后的统计口径区分。
- 新共享模块必须随脚本一起分发，并纳入语法检查及缺失依赖提示。

---

### Task 1: 补齐合并规格与变更清单

**Files:**

- Create: `docs/plans/2026-11-16-protocol-v3-contract.md`
- Read: `references/23-protocol-upgrade.md`, `references/10-context-orchestration.md`, `references/20-knowledge-layer.md`
- Read: `templates/project-status.md`, `templates/task-state-spec.txt`

**Interfaces:**

- Consumes: 原会话的完整方案、具体 diff 或用户补充的缺失细节。
- Produces: 新章节的精确父标题和层级、额外文件名单、限制值与警告口径、grill-with-docs 与 ROADMAP 的具体解释。

- [x] 对照原会话与更新后源码，逐项区分已落地、未落地、缺少规格的内容。
- [x] 将未恢复的历史细节标明，并记录本轮采用的章节、文件范围和方法边界约定。
- [x] 写出明确的合同和验收矩阵，并标注每项依据；实施前解决影响实现的缺口。

**Completion:** 后续任务所需的标题、字段、限制值和文件范围均有可追溯依据。

### Task 2: 完成状态文件行为与向后兼容

**Files:**

- Create: `scripts/validation_limits.py`
- Modify: `scripts/validate-project-state.py`, `scripts/render-workflow.py`, `scripts/validate-knowledge.py`
- Modify: `templates/project-status.md`, `templates/task-state-spec.txt`
- Test: `tests/test_attention_and_revision.py`, `tests/test_status_table_cli.py`, `tests/test_knowledge_validator.py`

**Interfaces:**

- Consumes: Task 1 的精确章节和限制合同。
- Produces: 新旧结构兼容的状态读取；Completed 超过 10 条的非致命警告；共享限制定义。
- 现有状态 JSON 字段保持兼容；新增警告列表与现有 `valid` / `errors` 分开。

- [x] 添加有实际行为断言的回归用例：新旧标题、空章节、边界标题、旧文件省略新增字段。
- [x] 添加 Completed 数量为 10 和 11 的边界用例，断言后者产生警告且仍有效；按合同覆盖 Cancelled。
- [x] 先运行针对性测试确认新增用例失败，再同步修改模板、校验与渲染行为。
- [x] 将合同指定的限制集中到 `validation_limits.py`；不借机新增配置或改变既有限制值。
- [x] 覆盖知识校验器共享限制的原有边界行为，并运行对应测试。

**Completion:** 校验与渲染得到一致的任务及注意力数据；旧文件通过；警告不变为失败。

### Task 3: 同步 v3 协议并完成验收

**Files:**

- Modify: `README.md`, `references/23-protocol-upgrade.md`, `references/11-task-state-machine.md`
- Modify: `references/02-commander.md`, `references/10-context-orchestration.md`, `references/20-knowledge-layer.md`
- Modify: `.github/workflows/ci.yml`, `tests/test_document_contracts.py`
- Include: Task 1 明确列出的额外文件，仅限合同范围。

**Interfaces:**

- Consumes: Task 2 的行为和兼容结果。
- Produces: 与实现一致的 v3 说明、采用流程、文件分发约束和验证证据。

- [x] 更新当前版本和采用说明；保留 v2 历史，不全局替换历史版本文本。
- [x] 按合同补齐 grill-with-docs、ROADMAP 和额外文件的解释；保留最近修复的 Commander 约束。
- [x] 更新文档合同断言、脚本分发说明和 CI 语法检查，覆盖新增共享模块。
- [x] 运行 `py -3 -m unittest discover -s tests -q`，要求全部通过或仅出现有依据的平台跳过。
- [x] 运行 `py -3 scripts/validate-project-state.py --path templates/project-status.md`，要求 `valid: true`。
- [x] 运行 `py -3 scripts/render-workflow.py templates/project-status.md --format json`，核对模板内容与输出一致。
- [x] 运行 `py -3 scripts/validate-knowledge.py --project-root .`；无知识层的既有提示不算缺陷。
- [x] 检查完整 diff，分别核对规格覆盖和实际行为；未经真实运行不声称通过跨平台 CI 或模型评测。

**Completion:** 已确认的合并合同全部满足，测试通过，剩余限制明确记录；提交与发布遵循届时用户指令。

## Execution result — 2026-11-16

两个实现子代理并行完成状态校验与文档模板，当前会话完成共享解析、限制、渲染及整合。
另一个只读子代理发现嵌套历史任务表覆盖当前状态的问题；新增回归用例先复现失败，再修复标题层级过滤。
独立复查未发现该修复引入新的可操作问题。

- 完整回归：203 项测试，4 项平台跳过，其余通过。
- 六份原有行为样例的状态文件全部通过校验。
- 七个脚本模块通过 Python 3.10 语法兼容检查；本机实际运行环境为 Python 3.14.0。
- 模板校验、JSON 渲染与可选知识层检查通过；知识层缺省仅产生既有提示。
- 没有运行远端模型评测或跨平台 CI；用户已授权清理后提交和推送。
- 原会话未包含的细节按本轮实现约定处理，来源边界保存在 `docs/plans/2026-11-16-protocol-v3-contract.md`。
- 临时状态文件已由测试清理；`scripts/__pycache__` 和 `tests/__pycache__` 已清理，并验证两个目录均不存在。
