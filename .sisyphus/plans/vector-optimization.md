# Plan: 向量化效率优化 (Vectorization Efficiency Enhancement)

## TL;DR
> **Summary**: 通过添加批量大小和并发控制，将2600条数据的向量化时间从~43分钟缩短至~5分钟。
> **Deliverables**: UI新增批量大小/并发配置 + 并行化API调用逻辑 + 缓存优化
> **Effort**: Medium
> **Parallel**: NO (sequential dependency)
> **Critical Path**: UI配置 → API改造 → 验证测试

## Context
### Original Request
用户反馈2600+条数据向量化时间过长（~43分钟），希望优化效率。

### Interview Summary
- 当前实现：batch=20, 并发=1（串行），共130批次
- 目标：通过批量大小和并发优化，缩短至5分钟左右
- API：阿里云 DashScope text-embedding-v3
- 缓存机制：已有 vector_cache/ 目录

### Metis Review (gaps addressed)
**识别的问题**：
1. 并发调用需保证结果顺序正确（嵌入结果必须按输入顺序映射回去）
2. API速率限制需防护（需退避重试机制）
3. 高并发下内存使用需监控
4. 缓存失效策略需明确

**Guardrails**：
- 使用信号量限制最大并发数
- 结果按索引排序确保顺序
- 提供缓存失效触发选项

## Work Objectives

### Core Objective
将2600条数据向量化时间从~43分钟缩短至~5分钟（8倍提升）

### Deliverables
1. UI增加批量大小选择器（20/40/64/128）
2. UI增加并发数控制（1/2/4/6/8）
3. 修改 get_embeddings_with_retry 支持并行批量调用
4. 添加 ThreadPoolExecutor 并发执行逻辑
5. 添加速率限制保护（Semaphore + 退避重试）

### Definition of Done (verifiable conditions with commands)
- [ ] 2600条数据向量化完成时间 < 6分钟
- [ ] UI可配置批量大小和并发数
- [ ] 配置可持久化到 config.json
- [ ] 启用"跳过向量化"后缓存正确加载

### Must Have
- 并行化向量化调用
- 可配置的批量大小和并发数
- 结果顺序正确性保证
- API速率限制保护

### Must NOT Have
- 不经测试直接使用过高的并发值
- 破坏现有缓存机制
- 引入阻塞UI的操作

## Verification Strategy
- Test decision: tests-after (手动验证 + 日志分析)
- QA policy: 每个任务包含happy path和failure场景
- Evidence: 日志输出 + 时间测量

## Execution Strategy

### Dependency Matrix
```
[Wave 1: UI配置] 
    ↓
[Wave 2: API并行化改造] 
    ↓
[Wave 3: 验证测试]
```

### Agent Dispatch Summary
单一任务，无需并行。

## TODOs

- [ ] 1. 添加UI配置控件（批量大小 + 并发数 + 默认值配置）

  **What to do**: 在frame_file区域添加批量大小下拉框和并发数下拉框，默认值 batch=40, concurrency=4
  
  **Must NOT do**: 不修改现有API调用逻辑

  **Recommended Agent Profile**:
  - Category: `visual-engineering` - Reason: UI修改
  - Skills: [] - 不需要特殊技能

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: Task 2 | Blocked By: none

  **References**:
  - Pattern: `main.py:92-97` - 现有变量定义模式（tk.StringVar, tk.IntVar）
  - UI: `main.py:336-343` - 现有控件布局位置

  **Acceptance Criteria**:
  - [ ] 界面上有"批量大小"下拉框，选项包含20/40/64/128
  - [ ] 界面上有"并发数"下拉框，选项包含1/2/4/6/8
  - [ ] 默认值显示为 batch=40, concurrency=4
  - [ ] 配置保存后重启程序仍保持

  **QA Scenarios**:
  ```
  Scenario: UI控件正常显示和交互
    Tool: 手动测试
    Steps: 启动程序 python main.py，检查界面是否有"批量大小"和"并发数"控件，修改值后重启验证持久化
    Expected: 控件正常显示，修改值保存成功
    Evidence: 界面正常渲染，config.json包含新配置项

  Scenario: 默认值正确
    Tool: 检查config.json
    Steps: 删除config.json，重新启动程序，检查默认值
    Expected: batch=40, concurrency=4
    Evidence: config.json中batch_size=40, concurrency=4
  ```

  **Commit**: YES | Message: `feat(ui): add batch_size and concurrency controls` | Files: [main.py]

- [ ] 2. 修改API调用支持并行批量处理

  **What to do**: 修改 get_embeddings_batch_parallel 函数，使用 ThreadPoolExecutor 并行执行多个批次，添加信号量限制最大并发数，结果按顺序合并
  
  **Must NOT do**: 不改变现有单批次重试逻辑

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: 核心逻辑修改
  - Skills: [] - 不需要特殊技能

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: Task 3 | Blocked By: Task 1

  **References**:
  - API函数: `main.py:44-59` - get_embeddings_with_retry
  - 批处理: `main.py:197-211` - 现有批处理循环
  - ThreadPoolExecutor: `main.py:271` - 已有使用示例

  **Acceptance Criteria**:
  - [ ] 2600条数据向量化时间 < 6分钟
  - [ ] 日志显示并行执行（如"并发数: 4"）
  - [ ] 结果顺序与输入一致

  **QA Scenarios**:
  ```
  Scenario: 向量化效率提升验证
    Tool: 时间测量 + 日志
    Steps: 删除缓存，设定batch=40, concurrency=4，选择B表，记录开始时间和完成时间
    Expected: 2600条数据向量化完成时间 < 6分钟
    Evidence: 日志显示"向量化完成"，时间差 < 6分钟

  Scenario: 高并发下API稳定性
    Tool: 日志分析
    Steps: 设置batch=64, concurrency=8，运行向量化，检查是否有API错误
    Expected: 无API速率限制错误，或有正确的退避重试
    Evidence: 日志无"rate limit"错误，或有"重试"记录

  Scenario: 结果顺序正确性
    Tool: Python脚本验证
    Steps: 用10条已知顺序的数据测试，检查输出向量顺序
    Expected: 输出向量索引与输入顺序一致
    Evidence: Python验证脚本输出"Order: Correct"
  ```

  **Commit**: YES | Message: `feat(vector): add parallel batch processing with configurable concurrency` | Files: [main.py]

- [ ] 3. 整体验证和日志优化

  **What to do**: 添加更详细的进度日志，显示当前批次/总批次、预计剩余时间；验证整体功能
  
  **Must NOT do**: 不修改核心逻辑

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: 验证和小调整
  - Skills: [] - 不需要特殊技能

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: none | Blocked By: Task 2

  **References**:
  - 进度更新: `main.py:205-206` - 现有进度更新代码

  **Acceptance Criteria**:
  - [ ] 日志显示进度百分比和预计剩余时间
  - [ ] 向量化完成后状态灯变蓝

  **QA Scenarios**:
  ```
  Scenario: 进度显示正常
    Tool: 观察UI
    Steps: 运行向量化，观察进度条和日志
    Expected: 进度条实时更新，日志显示"已处理X/2600"
    Evidence: 进度条从0%到100%，日志包含进度信息
  ```

  **Commit**: YES | Message: `feat(log): add progress logging with ETA` | Files: [main.py]

## Final Verification Wave (MANDATORY)
> 手动验证为主，代码检查为辅

- [ ] F1. Plan Compliance Audit — 检查所有TODO是否完成
- [ ] F2. 时间性能验证 — 2600条 < 6分钟
- [ ] F3. 功能回归验证 — 匹配结果正确性

## Commit Strategy
每个Wave完成后单独提交，提交信息包含Wave标识。

## Success Criteria
1. UI配置正常显示和保存
2. 2600条数据向量化时间 < 6分钟（相比原43分钟提升7倍+）
3. 匹配结果准确性不下降
4. 日志清晰可追溯