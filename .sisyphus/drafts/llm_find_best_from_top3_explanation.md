# Draft: llm_find_best_from_top3 业务逻辑解释

## 目的
- 解释 main.py 中 llm_find_best_from_top3 函数的业务逻辑及实现要点，帮助后续评审与改造。

## 函数签名
- llm_find_best_from_top3(a_text, top3_data, api_key, log_func=print)

## 核心行为概览
- 将 top3_data 转换为一个候选项文本块 b_list_str，格式化为可读的候选清单：
  [0] 名称:..., 规格:..., 尺寸:...
- 构造一个明确的提示给 LLM：设定角色为“物料匹配专家”，任务是从 B 候选的三条物料中找出与 A 材料最相似的一条，并给出相似度评分，输出必须是 JSON 格式：{"index": 0, "score": 85}
- 使用模型 gpt/qwen 系列的远程接口 CHAT_URL 调用，模型为 qwen3.5-plus，传入包含 prompt 的消息，以及温度等参数。
- 从响应中提取文本内容，尝试解析其中的 JSON 对象以获得 index 与 score；如果解析成功且索引在候选集合范围内，则返回一个六元组：
  (idx, code, name, spec, size, score)
  其中 item 为 top3_data 中对应的条目 (code, name, spec, size, txt)。
- 若 JSON 解析失败，尝试从文本中提取一个数字索引作为兜底，并将分数设为 100（表示最高确定性）。
- 若发生异常或无法得到有效索引，则返回 (-1, None, None, None, None, 0)。
- 过程中的日志记录包括：请求发送、LLM 返回、文本提取、JSON/数字提取结果、错误信息等，便于调试。

## 数据结构
- top3_data 的结构：[(code, name, spec, size, txt), ...]，长度等于 3。
- a_text 为 A 表材料文本。

## 关键决策点
- 采用强制 JSON 输出结构的设计（{index, score}），以便下游逻辑明确映射结果。
- 提供一个兜底的数字索引解析策略，避免由于 LLM 输出格式微小偏差而导致完全失败。
- 分数的含义：若直接使用 JSON，则 score 为 JSON 给出的分数；若兜底解析，则分数设为 100，表示最高置信度。

## 边界情况与鲁棒性
- LLM 请求失败或返回非预期格式时，返回 (-1, ...) 及分数 0。
- top3_data 缺失值或字段不齐时，会导致返回的 code/name/spec/size 可能为 None，调用方需做好空值处理。

## 测试要点
- 模拟 LLM 返回有效 JSON：应返回对应 top3_data 的条目及分数。
- 模拟 LLM 返回仅包含数字的文本：应从文本提取数字索引并映射。
- 模拟 API 调用失败：应返回带有 -1 的索引和 0 分。

## 关联与依赖
- 依赖 CHAT_URL、api_key 的正确性，以及网络连通性。

## 后续扩展点（可选）
- 增强对 top3_data 的容错处理，例如处理不足 3 条候选的情况。
- 将 JSON 输出格式的严格性下放为可配置项，以支持不同的 LLM 输出形式。
