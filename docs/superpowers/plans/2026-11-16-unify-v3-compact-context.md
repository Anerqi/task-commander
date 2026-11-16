# Unify Protocol v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以 compact-context 为唯一 v3 规范，保留共享解析及历史表修复，再适配 PR #2。

**Architecture:** 在现有 checkout 的整合分支合并 compact-context。章节解析只保留一个实现，保留标题层级与父章节。v3 模板使用顶层 Needs you now、其下 Blocked/Pending；旧文件按实际结构兼容。

**Tech Stack:** Python 3.10+ 标准库、Markdown、unittest、Git。

**Spec:** 用户当前分支审阅；`origin/protocol-v3/compact-context` at `79a7dba`；PR #2 at `d7feb31`；main at `aa39f92`。

## Global Constraints

- 使用当前 checkout 和 `codex/` 整合分支；保留 `.qoder/`。
- v3 结构与 compact-context 一致；统一规范发布日期为 2026-11-16，历史日期保留。
- 保留 main 的共享解析、围栏处理、嵌套历史表修复及有意义的回归测试。
- 保留 compact-context 的技能清单整合、按需 glossary/knowledge、精简决策、阶段收尾与 case 08。
- v1/v2 和已发布的 main 临时 v3 结构作为兼容输入；新模板仅产生一种结构。
- 不改变任务状态、用户授权、验收门槛和现有证据。
- PR #2 当前为 Draft；实际模型 token 测量和 Behavior Judge 尚未重跑，不能宣称已满足该验收项。
- 先生成并验证本地整合结果；main 仅快进同步，PR #2 的 rebase 发布使用已核对旧提交的 force-with-lease，保留 Draft 验收条件。

## Review Focus

- Blocked/Pending 必须位于 Needs you now 下；错误父章节不能产生当前状态。
- Task list 仅取规范层级；历史同名子标题不能覆盖当前任务。
- 注意力表到下一标题即停止；围栏中的标题与表格不产生记录。
- 旧格式与临时 main v3 仍可读取，规范新模板不再分叉。
- handoff-only 缺版本、版本低于 3 或无法确认版本时走完整路径；可选文件仅存在时读取。

### Task 1: 统一 v3

**Files:** `scripts/markdown_table.py`, `scripts/validate-project-state.py`, `scripts/render-workflow.py`, `scripts/validation_limits.py`, `templates/project-status.md`, `templates/task-state-spec.txt`, 协议 references、测试与 case 08。

**Interfaces:** 共享解析输出标题层级、父章节和直接正文；validator/renderer 使用同一结果。

- [x] 合并 compact-context，按上述所有权解决冲突。
- [x] 将嵌套 Blocked/Pending 的位置校验整合进共享解析；保持旧版兼容与 Completed 警告。
- [x] 保留两边有意义的行为测试，修正依赖旧模板结构的夹具构建方式。
- [x] 标记先前 main v3 合同为已被本次规范取代，统一当前协议日期。
- [x] 完整 unittest、旧版夹具、语法兼容和模板校验通过后记录本地 v3 整合提交。

### Task 2: 将 handoff-only 适配到统一 v3

**Files:** `SKILL.md`, `references/01-context-brief.md`, `templates/commander-handoff.md`, `evals/scripts/check_02_context_handoff.py`, `tests/test_document_contracts.py`, `tests/test_eval_config.py`。

**Interfaces:** 复用 Task 1 的 v3 结构与可选记录约定。

- [x] 在统一 v3 后 rebase PR #2 的五个原始提交，另行提交适配修复。
- [x] 仅明确且唯一的当前版本 3 可进入 handoff-only；缺失、旧版、重复、非法和未知未来版本均走完整路径。
- [x] 技能清单以 background/01 的 Available skills 为主，02 与 CONTEXT 只在存在时读；保留 AGENTS 无变化不重写。
- [x] 恢复 checker 的 100755 模式，验证新旧路径、缺可选记录及 AGENTS 保留规则。
- [ ] 完整回归与独立审查，清理临时产物；报告实际模型评测仍待完成，不自动合并 Draft PR。

## Execution evidence

- 统一 v3 合并：`5507930`。共享解析保留层级、父章节和直接正文，隔离历史表及围栏示例。
- 独立复核发现修订号可能误读围栏示例；先复现再修复，并加入回归测试。修复提交 `c186ef2`；复核未发现剩余可操作问题。
- 统一 v3 基线：222 项 unittest，4 项平台相关跳过；旧版状态夹具、模板及兼容性检查通过。
- PR #2 已在本地 rebase 并完成版本与可选记录适配；最终回归和发布记录在适配分支补充。
- Case 02 原夹具保留无版本旧格式以覆盖恢复路径；另以临时 v3 状态、缺 CONTEXT/02 的项目验证磁盘检查与状态校验兼容。磁盘检查不能证明模型交接行为或 token 改善。
- 模型评测未运行：仓库未配置 EVAL 变量/密钥，本机也未安装 skill-up；PR #2 保持 Draft。
