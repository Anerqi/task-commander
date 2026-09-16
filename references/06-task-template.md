# Outcome-First Task Prompts

> Read when composing any startup or continuation instruction. This is a composition guide and completeness check, not a form to reproduce. Keep scheduling metadata in the saved task brief; write the executor's instruction in the user's language, as natural, concrete commands. For continuation/recovery-specific decisions, also use `templates/task-continuation.md`.

## Separate the contract from the message

The internal contract is durable; the message is tailored to the current window and work. A short prompt must not erase requirements, while a complete contract need not be pasted in full on every round.

Before dispatch, save the contract in the task directory (for example `00_task_brief.md`). Commander may write this coordination brief; that is not executing the task. Keep the original contract and record authorized changes with provenance rather than replacing it with the latest narrow prompt. In a prompt-only environment without file access, include necessary context in the message or refer to explicitly available conversation context; never claim a brief was saved/read if it was not.

### Internal contract (save, do not mechanically print)

- **Objective and provenance**: the original user request, the saved objective in context, genuine later user corrections, their source pointers, and this task's contribution to the whole project. A short saved objective is an index to the full request, not a substitute for it. Keep agent suggestions and unconfirmed scope changes separate.
- **Assignment**: task ID, primary role, target window, priority/risk/kind, original brief location, concrete intended outcome, and explicit in/out-of-scope boundaries. Identify remaining substantive work as well as already accepted results.
- **Inputs and ownership**: shared context revision, relevant input/artifact versions, absolute role/source/output paths, satisfied dependencies, read/write scope, isolation, integration owner and active-task conflicts. Include relevant terms, decisions and skill pointers, not every document by default.
- **Authority and recovery**: effective network/subagent/skill permissions and their policy source, resource/experiment/revision budgets, concrete reasons for restrictions, backup coverage/prerequisites, and pending human actions. Research permission does not authorize sensitive transfer, publishing, payment or destructive actions.
- **Acceptance and return**: observable criteria, original quality bar, required Reviewer/QA gates and reasons, existing valid evidence, material unresolved findings, output paths and a concise receipt per `templates/task-receipt.md`.

Runtime, collaboration, state and quality references are resolved under the Skill root and loaded when applicable per `SKILL.md`. Preserve role and gate separation; Executor integration and self-validation do not replace a required independent review. Gate briefs (`04_review_brief.md`, `05_qa_brief.md`) reference the execution contract without overwriting it.

## Compose the actual instruction

1. **Lead with the outcome.** Use "Build…", "Complete…", "Continue…", "完成…", or "继续…". Say what usable result must emerge and enough of its breadth to avoid a one-file or one-issue interpretation. A bounded task can contain substantial work; bounded does not mean tiny.
2. **Choose the largest coherent ready remainder.** Bundle necessary fixes, implementation, integration, relevant tests and documentation within the task's authorized scope. Let the executor choose routine steps and useful authorized delegation. Do not assign one prompt per file, setup step, test, or minor issue, or require another prompt after each. Keep a genuinely narrow user request narrow.
3. **Anchor without dumping.** A new window needs its task/role, original objective and assigned outcome, absolute brief/essential-input/output paths, and enough instructions to start. A continuing window needs the unchanged objective, the useful remaining outcome and the material delta; reference the original brief/current evidence rather than reprinting it. A recovery window needs the fuller reconstruction context described in `templates/task-continuation.md`.
4. **Surface operative constraints.** State effective network/subagent permissions compactly at startup, and changed permissions on continuation. Put critical write boundaries, backup conditions, authorization limits, blockers or required gates inline when they affect this round. Other unchanged metadata can remain behind precise readable pointers. Prompt compression never hides a safety precondition or grants broader authority.
5. **Set a useful finish line.** Ask for the requested outcome with relevant validation and a short evidence/blocker receipt, not an unrelated progress report. Reuse established results; refresh checks only for changed inputs, new evidence or a material requirement-related improvement. Questions only the user can answer remain explicit; independent authorized work can continue.

Use paragraphs, a short list, or a small checklist only when it helps the executor. There are no mandatory visible headings, bracketed fields, sentence counts, or boilerplate "none/not applicable" entries. Do not append every potential risk to a harmless task. Concise means removing repetition, not omitting necessary scope or constraints.

## Delivery to the user

- For one ready instruction, output the instruction directly, without a preface, praise, status dashboard, explanation of your reasoning, or claims that you executed anything. It is a message to the executor, not the executor's answer.
- For several independent instructions, use a minimal task/window label outside each separately copyable block. A batch table is optional when dependencies/routing would otherwise be unclear. Never combine conflicting owners into one assignment merely to make it larger.
- Inside instructions, use direct commands rather than "I'll fix…", "Spawning now…", or an assertion that you checked/changed something. Refer to existing evidence by path/version, not by invented personal action claims.
- Ask a real blocking user question or communicate acceptance in a separate appropriate Commander response instead of disguising it as an executor instruction. Normal Commander coordination can inspect files and update records; prompt-only composition is not execution authority.
- If explicitly asked to generate prompts only from supplied context, generate only the next instruction without tools or state writes. Do not apply that restriction to all Commander work, and do not invent missing evidence to compensate.

Native chat does not require JSON or the token `NO_REPLY`. When the requested outcome is established, stop issuing executor instructions and give only the appropriate brief acceptance/user response. A machine adapter may explicitly request `{"action":"continue","reply":"<instruction>"}` or `{"action":"stop","reply":""}`; use that wrapper only when requested. Blocked/unknown is not complete: request the missing input or evidence rather than returning stop. If a prompt-only adapter cannot ask the user directly, the next instruction can ask the executor to surface the blocker safely, without unauthorized work or an endless retry loop.

## Examples of natural instructions

Examples show composition, not required wording; replace example paths with resolved absolute paths in real dispatch.

**Startup — a complete feature within its assignment**

> 完成任务 03 的报告导出功能，做到用户能在现有页面选择格式、导出当前筛选结果，并得到明确的失败反馈。先读 `<绝对任务简报路径>` 和其中的角色、接口约定；在指定工作目录内完成实现、页面接入及必要测试，沿用现有设计，不改其他任务负责的模块。可查询公开官方文档并使用已授权的子代理。把可运行结果与简短验证记录交回 `<绝对输出路径>`；需要用户决定的产品取舍请指出，其余常规实现自行处理。

**Continuation — the latest defect is part of unfinished delivery**

> 继续完成任务 03 的导出功能，按原简报的完整范围收尾，不要停在修复刚发现的空文件问题。修复 `<问题证据位置>` 后，把尚未完成的页面接入、异常反馈和相关集成测试一并完成；复用已通过且未受影响的结果，保留其他窗口的修改。权限与写入范围沿用原简报。交回可用功能及本轮相关证据，只有确需用户决定的事项才暂停对应部分。

**Narrow user correction — do not broaden it**

> 只把任务 03 中两处错误的导出按钮文案改成用户确认的用词，位置见 `<绝对问题记录路径>`。核对这两处显示及相关引用即可；保留既有交互，不重做导出功能或全量测试。

## Internal pre-dispatch check

- The full user objective and genuine corrections are preserved, while this window's assigned scope and other tasks' ownership stay clear.
- The proposed round makes substantive progress on the coherent ready remainder; it neither stops at the latest detail nor adds unrelated improvements.
- Dependencies, effective tools, risk gates, backup readiness, budgets and pending user input are respected. Split for real ownership/dependency/risk reasons, not arbitrary file counts.
- Essential paths and pointers are usable from the target window; identity, original brief and accepted evidence survive continuation/recovery. Confirm a referenced brief actually exists before dispatching a pointer-only message.
- Each prompt is independently copyable. Gate windows name the reviewed task/artifact and keep their briefs separate; emitting a prompt alone does not establish pickup, execution, acknowledgment or completion.
