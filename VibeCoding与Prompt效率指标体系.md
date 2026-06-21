# Vibe Coding 与 Prompt 效率衡量指标体系

> 编制时间：2026-06-18
> 数据来源：学术研究（EPI/YapBench/CodeHalu/DORA）、行业报告（GitClear/Anthropic/OpenAI/Google/Stack Overflow/NVIDIA）、极客社区（Reddit/Hacker News/Dev.to）
> 适用场景：Vibe Coding 效率评估、Prompt 工程优化追踪、AI 辅助编程质量监控

---

## 一、指标体系总览

### 1.1 设计原则

1. **可量化性**：每个指标有明确的数学公式和计量方法，杜绝主观打分
2. **可追溯性**：每个指标都能追溯到具体的 session/文件/代码行，支持 drill-down 分析
3. **多维互补**：单一指标无法反映全貌，本体系从效率、质量、认知、交付四个维度交叉验证
4. **防退化**：所有指标标记了"向好方向"和"退化警示"，防止片面追求速度而忽视质量
5. **场景敏感性**：指标区分适用场景（日常监控 / 深度审计 / 趋势分析），避免一刀切

### 1.2 指标全景

```
                    ┌──────────────────────────────┐
                    │   Vibe Coding & Prompt 效率   │
                    │         衡量指标体系            │
                    └──────────────┬───────────────┘
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
    ┌──────▼──────┐        ┌──────▼──────┐        ┌──────▼──────┐
    │  效率维度    │        │  质量维度    │        │  认知维度    │
    │ (Efficiency) │        │  (Quality)  │        │ (Cognitive) │
    └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
           │                       │                       │
    ① Token使用效率          ④ 幻觉率                ⑩ 认知负荷指数
    ② 采纳度与接受度         ⑤ 返工与迭代            ⑪ 开发者信任度
    ③ 上下文利用效率         ⑥ 代码质量与安全        ⑫ 技能增长指数
                             ⑦ PR/Review 质量
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
    ┌──────▼──────┐        ┌──────▼──────┐        ┌──────▼──────┐
    │  产出维度    │        │  综合指标    │        │  成本维度    │
    │  (Output)   │        │ (Composite) │        │   (Cost)    │
    └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
           │                       │                       │
    ⑧ DORA 交付指标          ⑬ Vibe 效率综合分        ⑯ 实际金钱成本
    ⑨ 任务完成效率           ⑭ Prompt 质量分           ⑰ 能源消耗指数
                             ⑮ 技术债务累积率
```

### 1.3 指标分类

| 类别 | 指标数 | 适用频率 | 数据来源 |
|------|--------|---------|---------|
| 一类（核心监控） | 8 个 | 每次 session 自动采集 | transcript JSONL + SQLite |
| 二类（周期审计） | 6 个 | 每周/每月统计 | 代码仓库 + CI/CD + 测试报告 |
| 三类（深度分析） | 3 个 | 按需触发 | 人工标注 + 专项评估 |

---

## 二、Token 使用效率（一类指标）

### 2.1 Token 效率比（Token Efficiency Ratio, TER）

**内涵**：衡量单位 Token 投入产生的有效产出。反映 Prompt 的"性价比"——用更少的 Token 完成更多任务。

**核心公式**：

```
TER = 有效产出 Token / 总消耗 Token

其中：
  有效产出 Token = output_tokens（模型输出的代码/文本）
  总消耗 Token   = input_tokens + output_tokens + thinking_tokens（如果模型支持）
```

**变体公式（区分缓存效益）**：

```
TER_cache_aware = output_tokens / (input_tokens × (1 - cache_hit_rate) + output_tokens)
```

**测算标准**：

| 等级 | TER 范围 | 解读 |
|------|---------|------|
| 优秀 | > 0.40 | 每 1K Token 产出 400+ Token 有效代码 |
| 良好 | 0.25 - 0.40 | 正常水平 |
| 一般 | 0.15 - 0.25 | 存在冗余 Prompt |
| 低效 | < 0.15 | 严重 Token 浪费，需优化 Prompt |

**数据采集方式**：从 transcript JSONL 的 `usage` 字段提取 `input_tokens`、`output_tokens`、`cache_read_input_tokens`。

**向好方向**：TER 升高（同等任务下）；退化警示：TER 持续下降超过 20%。

**来源依据**：
- COLING 2025 Economical Prompting Index (EPI) 提出的成本-性能权衡框架
- Anthropic 官方 cache 定价（缓存命中节省 90% 输入成本）
- 学术研究 Token-to-Parameter Ratio 的效率公式

---

### 2.2 经济 Prompt 指数（Economical Prompting Index, EPI）

**内涵**：将任务成功率与 Token 消耗结合，衡量 Prompt 的"综合经济性"——不仅是便宜，还要管用。直击"便宜但无用 vs 昂贵但有效"的权衡。

**核心公式**：

```
EPI = Success_Rate / log₂(Total_Tokens)

其中：
  Success_Rate = 该 Vibe 是否达成目标（0 或 1，或按完成度打分 0-1）
  Total_Tokens = input_tokens + output_tokens
```

**多 Vibe 汇总公式**：

```
EPI_aggregated = Σ(Success_Rate_i) / Σ(log₂(Total_Tokens_i))
```

**测算标准**：

| 等级 | EPI 范围（单 Vibe）| 解读 |
|------|-------------------|------|
| 优秀 | > 0.10 | 高成功率 + 低 Token 消耗 |
| 良好 | 0.06 - 0.10 | 均衡 |
| 警告 | < 0.04 | 高 Token 消耗但低成功率 |

**Success_Rate 判定标准（三级制）**：
- **1.0**：AI 输出被直接采纳（IDE 'Accept' + 未被后续 revert）
- **0.5**：AI 输出被采纳但经人工大幅修改（>30% 行变更）
- **0.0**：AI 输出被拒绝或 revert

**来源依据**：COLING 2025 论文 "Economical Prompting Index"，覆盖 10 个 LLM + 6 种 Prompt 技术 + 4 个数据集。

---

### 2.3 缓存命中率（Cache Hit Rate, CHR）

**内涵**：衡量重复上下文的复用程度。高缓存命中率意味着系统提示、项目规范、代码上下文等常驻内容被有效缓存，避免重复计费。

**核心公式**：

```
CHR = cache_read_input_tokens / (cache_read_input_tokens + cache_creation_input_tokens)

其中：
  cache_read_input_tokens = 从缓存读取的 Token 数（已命中缓存）
  cache_creation_input_tokens = 新写入缓存的 Token 数
```

**测算标准**：

| 等级 | CHR | 解读 |
|------|-----|------|
| 优秀 | > 70% | 大量复用常驻上下文，如 CLAUDE.md、项目规范 |
| 良好 | 40% - 70% | 正常缓存利用 |
| 低效 | < 40% | 每次请求传大量新内容，未充分利用缓存能力 |

**优化建议**：
- 将项目规范、编码约定放入 CLAUDE.md（Anthropic 研究：结构化上下文文件使错误减少 40%，完成速度提升 55%）
- 固定系统提示放在对话开头（Anthropic cache 按前缀匹配）

**来源依据**：Anthropic API 定价文档（cache_read 价格仅为基础 input 的 10%），Claude Code 400K session 分析报告。

---

### 2.4 思考 Token 占比（Thinking Token Ratio, TTR）

**内涵**：衡量模型"思考"（推理链）的 Token 消耗比例。推理模型（如 Claude Opus 的 extended thinking）的思考 Token 按输出价格计费，是 2026 年最大的隐性成本来源。

**核心公式**：

```
TTR = thinking_tokens / total_tokens

其中：
  thinking_tokens = 模型的内部推理 Token
  total_tokens = input_tokens + output_tokens + thinking_tokens
```

**测算标准**：

| 等级 | TTR | 解读 |
|------|-----|------|
| 高效 | < 30% | 推理投入适中 |
| 正常 | 30% - 60% | 复杂任务正常推理开销 |
| 过载 | > 60% | 思考 Token 超过有效输出，可能 Prompt 不够清晰 |

**注意**：TTR 不是越低越好——复杂任务需要更多推理。应结合任务复杂度分档评估。

**来源依据**：2026 LLM Pricing Guide（推理模型单次调用可能消耗 30K thinking tokens），GPT-5.2 Pro / Claude Opus 4.6 定价数据。

---

## 三、采纳度与接受度（一类指标）

### 3.1 IDE 层采纳率（IDE Acceptance Rate, IAR）

**内涵**：AI 生成的代码在 IDE 层面被开发者"接受"（Accept）的比例。这是最浅层的采纳信号，但**不能**等同于代码真正可用。

**核心公式**：

```
IAR = IDE_Accept_Count / AI_Suggestion_Count × 100%
```

**测算标准**：

| 等级 | IAR | 解读 |
|------|-----|------|
| 高 | > 80% | AI 建议频繁被接受（但需警惕"接受即后悔"） |
| 中 | 50% - 80% | 正常范围 |
| 低 | < 50% | 建议相关性差，或开发者谨慎度高 |

**关键警示**：行业研究显示 IDE 接受率 80-90%，但**合并后存活率仅 10-30%**。该指标必须与 PMS 联合使用才有意义。

**来源依据**：Redwerk 2026 分析（"Accept ≠ Survive"），GitHub Copilot / Claude Code 使用数据。

---

### 3.2 合并后存活率（Post-Merge Survival Rate, PMS）

**内涵**：AI 生成的代码在合并到主分支后，经过一段时间（建议 30 天）未被 revert 或大幅重写的比例。这是衡量 AI 代码"真正有用"的核心指标。

**核心公式**：

```
PMS = Surviving_AI_Lines_After_30Days / Total_AI_Lines_Merged × 100%

其中：
  Surviving_AI_Lines = 合并 30 天后仍存在于代码库且未大幅修改（<30% diff）的 AI 生成行
```

**测算标准**：

| 等级 | PMS | 解读 |
|------|-----|------|
| 优秀 | > 65% | AI 代码质量高，长期可用 |
| 良好 | 45% - 65% | 正常水平 |
| 警告 | 25% - 45% | 存在较多返工 |
| 严重 | < 25% | AI 代码大面积被废弃 |

**对比基准**：人工编写代码 30 天存活率约 92%，AI 代码当前行业均值约 65%。

**来源依据**：Exceeds AI 2026 报告，GitClear 211M LOC 分析，Redwerk 2026 研究。

---

### 3.3 采纳深度指数（Adoption Depth Index, ADI）

**内涵**：不只衡量"接受了多少"，还衡量"接受得有多深"——是完全信任直接合并，还是经过大量手动修改。

**核心公式**：

```
ADI = Σ(Adoption_Depth_i × Weight_i) / Total_Accepted_Suggestions

其中 Adoption_Depth 分四级：
  4 = 直接采纳（Accept All，无修改）         → 权重 1.0
  3 = 小幅修改采纳（修改 < 15% 行）           → 权重 0.7
  2 = 中等修改采纳（修改 15% - 30% 行）       → 权重 0.4
  1 = 大幅修改采纳（修改 > 30% 行）           → 权重 0.1
```

**测算标准**：

| 等级 | ADI | 解读 |
|------|-----|------|
| 深度信任 | > 0.80 | 大部分 AI 代码被直接采纳 |
| 协同修改 | 0.50 - 0.80 | 适度修改后采纳 |
| 重度修改 | < 0.50 | AI 输出主要作为"灵感"或"草稿" |

**来源依据**：METR 2025 研究（仅 39% 的 AI 代码生成被原样接受），DORA/SPACE 框架中的协作质量维度。

---

## 四、幻觉率（一类 + 二类指标）

### 4.1 幻觉分类体系

在衡量幻觉之前，需先明确幻觉类型——不同类型的幻觉危害不同，检测方式也不同。基于 CodeHalu (AAAI 2025) 分类法：

| 幻觉类型 | 内涵 | 危害等级 | 检测方式 |
|---------|------|---------|---------|
| **映射幻觉** (Mapping) | 需求到代码的错误映射——实现了非预期的功能 | 高 | 人审 + 测试验证 |
| **命名幻觉** (Naming) | 使用不存在的变量名/函数名/包名 | 极高（安全风险） | 静态分析 + 包验证 |
| **资源幻觉** (Resource) | 调用不存在的 API、引用不存在的文件 | 极高 | 静态分析 + 编译 |
| **逻辑幻觉** (Logic) | 代码语法正确但逻辑错误 | 高 | 测试用例 + 执行验证 |
| **知识幻觉** (Knowledge) | 使用过时或错误的领域知识 | 中 | 人审 + 事实核查 |

### 4.2 幻觉检出率（Hallucination Detection Rate, HDR）

**内涵**：通过多方法组合（静态分析 + 测试验证 + 人类审查）发现的幻觉数占总生成代码的比率。这是可操作的上限估计——真实幻觉数通常更高。

**核心公式**：

```
HDR = Detected_Hallucinations / Total_Generated_Blocks × 100%

其中：
  Detected_Hallucinations = 静态分析检出 + 测试失败定位 + 人工审查发现
  Total_Generated_Blocks = AI 生成的独立代码块数
```

**分类型测算**：

```
HDR_naming = 不存在的包/函数引用数 / 总引用数 × 100%
HDR_logic  = 逻辑错误导致测试失败数 / 总生成函数数 × 100%
HDR_resource = 无效的文件/API 引用数 / 总资源引用数 × 100%
```

**测算标准（总体 HDR 基准）**：

| 等级 | HDR | 解读 |
|------|-----|------|
| 优秀 | < 5% | 幻觉控制良好 |
| 正常 | 5% - 20% | 行业典型水平 |
| 偏高 | 20% - 50% | 需加强审查流程 |
| 严重 | > 50% | 该方向/领域的 AI 生成不可信 |

**行业对照数据**：
- Python 包名幻觉：5.2%（16 个模型平均）
- JavaScript 包名幻觉：21.7%（npm 生态更易混淆）
- 代码审查评论幻觉：~50%
- 通用代码任务幻觉：约 32% "意图冲突" + 32% "不一致"

**检测方法矩阵**：

| 检测方法 | 检出类型 | 成本 | 适用场景 |
|---------|---------|------|---------|
| 静态分析（linter/SAST） | 命名/资源 | 低 | 持续集成自动触发 |
| 编译/语法检查 | 命名/资源 | 低 | 保存时触发 |
| 单元测试 | 逻辑/映射 | 中 | PR 门禁 |
| 集成测试 | 逻辑/映射 | 高 | 每日构建 |
| 人工审查 | 全部类型 | 极高 | PR Review |
| SelfCheckGPT（采样相似度） | 综合 | 中 | 无测试用例时的替代方案 |

**来源依据**：CodeHalu (AAAI 2025)，SelfCheckGPT for Code (IPSJ 2025)，Liu et al. IJCNLP-AACL 2025，Spracklen et al. 包名幻觉研究。

---

### 4.3 幻觉风险指数（Hallucination Risk Index, HRI）

**内涵**：综合衡量特定方向/模型/用户的幻觉倾向，用于风险评估和预防性审查。

**核心公式**：

```
HRI = HDR × Severity_Weight × Frequency_Weight

其中：
  Severity_Weight：按类型危害等级加权
    - 命名/资源幻觉：权重 3.0（可导致安全漏洞）
    - 逻辑/映射幻觉：权重 2.0（功能缺陷）
    - 知识幻觉：权重 1.0（可能过时但不直接出错）

  Frequency_Weight：按出现频次取对数平滑
    - Weight = log₂(count + 1)
```

**测算标准**：

| HRI 范围 | 风险等级 | 行动建议 |
|---------|---------|---------|
| < 1.0 | 低风险 | 常规审查 |
| 1.0 - 3.0 | 中风险 | 加强该方向的人工审查 |
| > 3.0 | 高风险 | 暂停该方向的 AI 直接生成，改为人工主导 |

---

## 五、返工与迭代（一类 + 二类指标）

### 5.1 代码流失率（Code Churn Rate, CCR）

**内涵**：AI 生成的代码在合并后的指定窗口内被修改、重写或删除的比例。这是衡量 AI 代码"一次性质量"的最直接指标。

**核心公式**：

```
CCR_30d = (Added_Lines + Modified_Lines + Deleted_Lines)_within_30d / Total_AI_Lines_Merged × 100%

其中：
  - 追踪窗口建议为 30 天（GitClear 标准）
  - 排除格式化变更、import 重新排序等非实质性修改
```

**测算标准（30 天窗口）**：

| 等级 | CCR | 解读 |
|------|-----|------|
| 健康 | < 12% | AI 代码质量与人工代码接近 |
| 警告 | 12% - 25% | 技术债务正在累积 |
| 危险 | 25% - 50% | 需立即加强审查 |
| 危机 | > 50% | AI 生成策略需要根本性调整 |

**行业基准对比**：

| 代码来源 | 30 天 Churn | 数据来源 |
|---------|------------|---------|
| 纯人工编写 | ~3.3%（2021 基线） | GitClear |
| 低 AI 辅助 | ~5% | GitClear |
| 高 AI 辅助 | ~7.1%（2025）→ 预计 2026 更高 | GitClear 211M LOC |
| 重 AI 使用（>40% 代码） | 可达人工的 9× | GitClear 2026 |

**AI/Human Churn 比（ACHR）**：

```
ACHR = CCR_AI_touched_files / CCR_Human_only_files
```

- ACHR < 1.5×：健康
- ACHR 1.5× - 3.0×：警告
- ACHR > 3.0×：严重——AI 代码质量明显低于人工

**来源依据**：GitClear 2025-2026 分析（211M LOC），Exceeds AI 七指标框架。

---

### 5.2 单任务迭代轮次（Iterations Per Task, IPT）

**内涵**：完成一个开发任务所需的 AI 交互轮次（Prompt → 审核 → 反馈 → 重新生成）。反映 Prompt 的"一次性精准度"。

**核心公式**：

```
IPT = 1 + Rework_Rounds_Per_Task

其中：
  Rework_Rounds = 针对同一任务目标，开发者发送的"修复/修改"类后续 Prompt 数量
  "同一任务"的判定 = session 内连续 Prompt 的语义相似度 > 0.7 且目标文件未切换
```

**测算标准**：

| 等级 | IPT | 解读 |
|------|-----|------|
| 优秀 | 1 - 2 | 一次或两次交互即完成，Prompt 精准 |
| 良好 | 3 - 5 | 需少量迭代 |
| 一般 | 6 - 10 | 存在明显的返工循环 |
| 低效 | > 10 | 陷入"修复-引入新问题-再修复"循环 |

**关联分析**：IPT 应与 HDR（幻觉率）联动分析——高 IPT + 高 HDR = AI 生成质量差；高 IPT + 低 HDR = 需求表达不够清晰（Prompt 问题）。

**来源依据**：METR 2025 研究（开发者使用 AI 后完成时间反而慢 19%），Stack Overflow 2025（45.2% 开发者认为调试 AI 代码更耗时）。

---

### 5.3 需求收敛度（Requirement Convergence Score, RCS）

**内涵**：衡量 Prompt 序列是否在向"任务完成"方向收敛，而非在原地打转或发散——即开发者是否在逐步逼近目标。

**核心公式**：

```
RCS = Σ(Progress_Gain_i) / Total_Rounds

其中：
  Progress_Gain_i = 第 i 轮相对于第 i-1 轮的 diff 减少量（归一化）
  - 如果 diff 缩小 → Progress_Gain > 0（收敛）
  - 如果 diff 增大 → Progress_Gain < 0（发散）
  - 如果 diff 不变 → Progress_Gain = 0（停滞）
```

**测算标准**：

| 等级 | RCS | 解读 |
|------|-----|------|
| 高效收敛 | > 0.3 | 每次迭代有效推进 |
| 缓慢收敛 | 0.1 - 0.3 | 有进展但效率低 |
| 停滞 | 0 - 0.1 | 迭代无实质推进 |
| 发散 | < 0 | 越改越糟——可能需切换方案 |

**应用建议**：当 RCS < 0.05 且 IPT > 5 时触发"返工循环警报"，提示开发者考虑切换方案或重新描述需求。

**来源依据**：Anthropic "Build > Prompt" 理念，ReAct 框架中的 self-correction 研究，OpenAI Agent Prompt 停止条件设计。

---

## 六、代码质量与安全性（二类指标）

### 6.1 AI 代码缺陷密度（AI Defect Density, ADD）

**内涵**：AI 生成代码中每千行（KLOC）含有的缺陷数，与人工代码的对比差距。

**核心公式**：

```
ADD = Defects_Found_in_AI_Code / AI_Generated_KLOC

其中：
  Defects = 静态分析告警 + 测试发现的 bug + 生产事故追溯到 AI 代码的案例
  KLOC = 千行 AI 生成代码（按 git blame 归因）
```

**对比指标**：

```
Defect_Density_Ratio (DDR) = ADD / Human_Defect_Density
```

**行业基准**：

| 指标 | AI 代码 | 人工代码 | 比率 |
|------|--------|---------|------|
| 逻辑错误/KLOC | 4.7 | 1.4 | 3.4× |
| 安全漏洞/KLOC | 2.8 | 0.6 | 4.7× |
| 总体缺陷/KLOC | 1.7× 高于人工 | — | 1.7× |
| 生产事故归因 | 78% 领导者报告增长 | — | — |

**测算标准**：

| DDR 范围 | 质量等级 |
|----------|---------|
| < 1.2× | 优秀——AI 代码质量接近人工 |
| 1.2× - 2.0× | 正常——符合行业水平 |
| 2.0× - 3.5× | 警告——需加强审查和测试 |
| > 3.5× | 严重——该方向 AI 代码不可直接合并 |

**来源依据**：Veracode 2025（45% AI 代码含安全缺陷），New Relic 2026（78% 领导者报告 AI 代码导致事故增长），CodeRabbit 470 开源 PR 分析。

---

### 6.2 硬编码密钥泄露率（Secret Exposure Rate, SER）

**内涵**：AI 生成的代码中包含硬编码密钥、Token、密码等敏感信息的比率。这是一个独立指标，因为其危害远超一般代码缺陷。

**核心公式**：

```
SER = AI_Commits_With_Secrets / Total_AI_Commits × 100%
```

**行业基准**：
- AI 辅助提交的密钥泄露率：3.2%（人工提交：1.5%），约为 2.1×
- 2025 年 GitHub 新增 2865 万个硬编码密钥，同比增长 34%

**测算标准**：

| SER | 风险等级 |
|-----|---------|
| < 1.0% | 安全 |
| 1.0% - 2.0% | 需关注 |
| > 2.0% | 需立即引入 pre-commit 密钥扫描 |

**来源依据**：GitHub 2025 年度安全报告，Veracode 2025。

---

### 6.3 代码重复率（Code Duplication Rate, CDR）

**内涵**：AI 生成的代码中与项目已有代码重复（copy-paste）的比例。AI 倾向于复制自己之前生成的结构而非提取抽象。

**核心公式**：

```
CDR = Duplicated_AI_Blocks / Total_AI_Blocks × 100%

其中：
  Duplicated_Block = 与项目内其他代码块相似度 > 85% 的代码段
```

**行业趋势**：2025 年 copy-pasted 代码增加 48%，而有意义的代码重构下降 60%。

**来源依据**：GitClear 2025（153M LOC 分析），AgamiSoft 2026 技术债务报告。

---

## 七、开发体验与认知负荷（二类 + 三类指标）

### 7.1 认知负荷指数（Cognitive Load Index, CLI）

**内涵**：衡量开发者在 AI 辅助编程中所需的认知投入。基于 DevEx 框架（ACM Queue 2023）的"认知负荷"维度。

**核心公式**：

```
CLI = (Context_Preparation_Time + Review_Time + Debug_Time) / Task_Total_Time

其中：
  Context_Preparation_Time = 编写 Prompt 和整理上下文的时间
  Review_Time = 审查 AI 输出的时间
  Debug_Time = 修复 AI 代码问题的时间
```

**测算标准**：

| CLI | 解读 |
|-----|------|
| < 30% | AI 有效降低了认知负担 |
| 30% - 50% | 正常——AI 分担了大量工作但审查仍需精力 |
| 50% - 70% | AI 带来的审查/修复负担与节省的编码时间相当 |
| > 70% | AI 成为了负担——审查和修复的时间超过了亲自编写的成本 |

**来源依据**：DevEx Framework (Noda, Storey, Forsgren, Greiler, ACM Queue 2023)，SPACE 框架的 Efficiency & Flow 维度。

---

### 7.2 开发者信任度（Developer Trust Score, DTS）

**内涵**：开发者对 AI 输出质量的主观信任程度，及其与实际质量的差距（感知偏差）。

**核心公式**：

```
DTS = Perceived_Quality / Actual_Quality

其中：
  Perceived_Quality = 开发者自评的 AI 代码可用率（问卷调查）
  Actual_Quality = 30 天后的 PMS（合并后存活率）
```

**测算标准**：

| DTS | 解读 |
|-----|------|
| 0.8 - 1.2 | 信任校准良好——开发者对 AI 能力的判断准确 |
| > 1.2 | 过度信任——开发者高估了 AI 代码质量 |
| < 0.8 | 信任不足——开发者低估了 AI 的可用性 |

**行业数据**：METR 2025 研究发现存在 39 个百分点的"感知-现实差距"——开发者认为自己借助 AI 快了 20%，实际慢了 19%。

**来源依据**：METR 2025（16 位开源开发者实验），Stack Overflow 2025（仅 3.1% 开发者高度信任 AI，33% 总体信任）。

---

### 7.3 技能增长指数（Skill Growth Index, SGI）

**内涵**：长期使用 Vibe Coding 是否导致开发者的底层编程能力退化——这是学术界和行业共同关注的核心风险。

**核心公式**：

```
SGI = (Current_Baseline_Ability - Previous_Baseline_Ability) / Time_Interval

其中：
  Baseline_Ability = 在无 AI 辅助情况下完成标准编程任务的能力评估
  可通过定期的"无 AI 编程测试"来量化
```

**测算标准**：

| SGI | 解读 |
|-----|------|
| > 0（正增长）| AI 辅助促进了学习，技能在提升 |
| ≈ 0（持平）| AI 未明显影响独立编程能力 |
| < 0（负增长）| 存在能力退化风险，需警惕 |

**风险评估维度**：
- 代码理解深度：能否解释 AI 生成的每段代码？
- 独立排错能力：无 AI 时能否调试复杂问题？
- 架构设计能力：能否独立进行系统设计决策？

**来源依据**：UC Berkeley 多位教授的能力萎缩警告，ACM 通讯评论，Karpathy 本人"理解底层原理的人才能写出更好的 Vibe Code"的观点。

---

## 八、产出与交付指标（二类指标）

### 8.1 AI 任务完成率（AI Task Completion Rate, ATCR）

**内涵**：分配给 AI 的编码任务中，最终达到可合并标准的比例。不同于 IDE 采纳率——这里的"完成"意味着代码经过审查、测试通过、合并成功。

**核心公式**：

```
ATCR = AI_Tasks_Merged / AI_Tasks_Attempted × 100%

其中：
  AI_Tasks_Merged = AI 主导或重度辅助（>50% 代码由 AI 生成）且成功合并的任务数
  AI_Tasks_Attempted = 发起 AI 辅助的总任务数（包括中途放弃的）
```

**行业对照（Claude Code 用户数据）**：

| 用户水平 | 可验证成功率 | 放弃率 |
|---------|------------|--------|
| 新手（Level 1）| 15% | 19% |
| 中级（Level 3）| ~28% | 5-7% |
| 专家（Level 5）| 33% | 5-7% |
| 软件工程师 | 30%（纯代码任务 34%）| — |
| 非软件职业 | 26%（纯代码任务 29%）| — |

**来源依据**：Anthropic 2026 年 6 月 Claude Code 400K session 分析报告。

---

### 8.2 DORA 交付四指标（AI 适配版）

在 DORA 经典四指标基础上，增加按代码来源（AI vs 人工）的分层分析：

**部署频率（Deployment Frequency）**：

```
DF = Deployments_Per_Week
DF_AI_Share = AI_Code_Deployments / Total_Deployments
```

**变更前置时间（Lead Time for Changes）**：

```
LTC = Merge_Time - First_Commit_Time
LTC_AI_vs_Human = Median(LTC_AI_commits) / Median(LTC_Human_commits)
```

**变更失败率（Change Failure Rate）**：

```
CFR = Failed_Deployments / Total_Deployments
CFR_AI_Attribution = Failures_Traced_to_AI_Code / Total_Failures
```

注意：DORA 2025 报告指出，AI 采纳使交付稳定性下降 7.2%。

**平均恢复时间（Mean Time to Restore）**：

```
MTTR = Σ(Recovery_Time_i) / Incident_Count
```

**来源依据**：DORA 2025 报告，Google Cloud 2025-2026 DORA 更新，DX AI Measurement Framework。

---

### 8.3 新能力创造率（New Capability Creation Rate, NCCR）

**内涵**：AI 辅助下完成的任务中，有多少是**此前无法独立完成**的——即 AI 是否真正"扩展"了开发者的能力边界。

**核心公式**：

```
NCCR = New_Capability_Tasks / Total_AI_Tasks × 100%

其中：
  New_Capability_Task = 开发者自评"没有 AI 我无法完成此任务"
```

**行业数据**：Anthropic 报告指出 27% 的 AI 辅助工作是"新能力"——此前不可行的任务。

**来源依据**：Anthropic 2026 Agentic Coding Trends Report。

---

## 九、成本维度（二类指标）

### 9.1 每成功任务成本（Cost Per Successful Task, CPST）

**内涵**：完成一个成功任务的**实际金钱成本**，是比"每 Token 价格"更有意义的成本指标。

**核心公式**：

```
CPST = Total_API_Cost / Successful_Task_Count

其中：
  Total_API_Cost = Σ (input_tokens × input_rate + output_tokens × output_rate + thinking_tokens × output_rate - cache_discount)
  Successful_Task_Count = 达到"成功"标准的任务数（参考 ATCR 中的判定标准）
```

**分模型 CPST 估算示例（编码 Agent 场景）**：

| 模型 | 估算 CPST | 备注 |
|------|----------|------|
| Claude Haiku 4.5 | $0.50 - $2.00 | 简单任务 |
| Claude Sonnet 4.6 | $3.00 - $10.00 | 中等复杂度 |
| Claude Opus 4.6 | $10.00 - $45.00 | 复杂架构任务 |
| GPT-4o-mini | $0.30 - $1.50 | 简单任务 |
| GPT-5.2 Pro | $30.00 - $150.00 | 高端推理任务 |

**团队月度成本估算**：

```
Team_Monthly_Cost = CPST × Tasks_Per_Dev × Dev_Count × Working_Days
```

> 例：20 人团队，每人每天 5 个任务，使用 Claude Sonnet 4.6（CPST ~$5）→ 月成本约 $10,000+

**来源依据**：2026 LLM Pricing Guide（Branch8, Grizzly Peak, FutureAGI），Anthropic/OpenAI 公开定价。

---

### 9.2 能源效率指数（Energy Efficiency Index, EEI）

**内涵**：完成单位任务消耗的能源（电力度量），响应 AI 的环保关切。

**核心公式**：

```
EEI = Estimated_Energy_kWh / Successful_Tasks

其中：
  Estimated_Energy = Total_Tokens × Energy_Per_Token（模型相关常数）
```

**研究结论**：
- "思考步骤"式 Prompt 消耗最多能源但产出最低代码质量（小模型上）
- "仅回答"式 Prompt（无解释）具有最佳的能源-质量比
- 礼貌性 Prompt 增加约 15% 能源消耗但可能提升 50%+ CodeBLEU

**来源依据**：2026 Energy Cost of Prompt Engineering 研究（Luis Cruz et al.）。

---

## 十、综合评估模型

### 10.1 Vibe 效率综合分（Vibe Efficiency Composite Score, VECS）

**内涵**：将多个核心指标加权综合为一个可追踪的总分，便于横向对比和纵向趋势分析。

**核心公式**：

```
VECS = w1 × TER_norm + w2 × PMS_norm + w3 × (1 - HDR_norm) + w4 × (1 - CCR_norm) + w5 × ATCR_norm

其中：
  _norm 表示归一化到 [0, 1] 区间
  w1-w5 为权重（建议初始权重见下）
```

**建议权重**：

| 指标 | 权重 | 理由 |
|------|------|------|
| Token 效率比 (TER) | 0.15 | 基础效率 |
| 合并后存活率 (PMS) | 0.30 | 最重要的质量信号 |
| 幻觉检出率 (1-HDR) | 0.20 | 安全与正确性 |
| 代码流失率 (1-CCR) | 0.20 | 一次性质量 |
| 任务完成率 (ATCR) | 0.15 | 产出能力 |

**测算标准**：

| VECS | 等级 |
|------|------|
| > 0.80 | 优秀——Vibe Coding 实践高效且健康 |
| 0.60 - 0.80 | 良好——整体有效，有优化空间 |
| 0.40 - 0.60 | 一般——需关注改进 |
| < 0.40 | 需干预——Vibe Coding 策略需根本性调整 |

### 10.2 技术债务累积率（Technical Debt Accumulation Rate, TDAR）

**内涵**：AI 代码引入的技术债务增长速率。业界预测：Vibe Coding 项目累积技术债务的速度约为传统开发的 3 倍。

**核心公式**：

```
TDAR = (New_Tech_Debt_AI / Total_New_Code_AI) / (New_Tech_Debt_Human / Total_New_Code_Human)

其中：
  New_Tech_Debt = 新引入的 linter 告警 + 代码异味 + 缺失测试覆盖的代码行
```

**来源依据**：GitClear 2026（预计 2027 年 AI 代码技术债务累计达 $1.5 万亿），AgamiSoft 2026。

---

## 十一、指标实施建议

### 11.1 数据采集架构

```
Claude Code Transcript (JSONL)
          │
          ▼
   ┌─────────────┐
   │  collector   │ ← 解析 token、时间戳、prompt、session
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │   SQLite     │ ← vibes 表（基础数据）+ 新增指标表
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │  analyzer    │ ← 计算 TER/EPI/HDR/CCR 等派生指标
   └──────┬──────┘
          │
     ┌────┴────┐
     ▼         ▼
  仪表盘    Git 仓库分析
 (实时)    (30天周期)
```

### 11.2 指标更新频率

| 频率 | 指标 |
|------|------|
| 每次 Vibe | TER, EPI, TTR, IPT |
| 每日汇总 | IAR, ATCR, CHR |
| 每周统计 | HDR, CLI, DTS |
| 30 天周期 | PMS, CCR, ADD, SER, CDR |
| 季度评估 | SGI, VECS, TDAR |

### 11.3 退化警戒线

| 指标 | 警戒阈值 | 行动 |
|------|---------|------|
| TER | 连续 7 天下降 > 20% | 审查 Prompt 膨胀，检查是否有无效上下文 |
| PMS | < 45% | 加强 AI 代码审查标准 |
| CCR | > 25% | 暂停该方向自动合并，转为人工主导 |
| HDR | > 20% | 引入预生成验证（静态分析 + 测试） |
| IPT | 中位数 > 6 | 提示开发者重新描述需求，而非继续修补 |
| ACHR | > 3.0× | 评估该方向是否适合 Vibe Coding |

### 11.4 数据库扩展建议

在现有数据库 schema 基础上新增以下表和字段，支持本指标体系的完整追踪：

```sql
-- Token 效率追踪表
CREATE TABLE token_efficiency (
    vibe_id         INTEGER PRIMARY KEY,
    ter             REAL,           -- Token 效率比
    epi             REAL,           -- 经济 Prompt 指数
    ttr             REAL,           -- 思考 Token 占比
    cache_hit_rate  REAL,           -- 缓存命中率
    calculated_at   TEXT,
    FOREIGN KEY (vibe_id) REFERENCES vibes(id)
);

-- 幻觉追踪表
CREATE TABLE hallucination_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vibe_id         INTEGER,
    hallucination_type TEXT,        -- mapping/naming/resource/logic/knowledge
    detected_by     TEXT,           -- static_analysis/test/human_review
    severity        TEXT,           -- high/medium/low
    description     TEXT,
    created_at      TEXT
);

-- 30 天代码存活追踪表（需与 Git 分析结合）
CREATE TABLE code_survival (
    commit_hash     TEXT PRIMARY KEY,
    vibe_id         INTEGER,
    ai_lines        INTEGER,
    surviving_lines_30d INTEGER,
    churn_rate_30d  REAL,
    calculated_at   TEXT
);

-- 综合评分表
CREATE TABLE efficiency_score (
    date            TEXT PRIMARY KEY,
    vecs            REAL,           -- Vibe 效率综合分
    tdar            REAL,           -- 技术债务累积率
    ter_avg         REAL,
    pms_avg         REAL,
    hdr_avg         REAL,
    ccr_avg         REAL,
    atcr_avg        REAL,
    calculated_at   TEXT
);
```

---

## 十二、关键结论

### 12.1 核心洞察

1. **"接受 ≠ 存活"**：IDE 层 80-90% 的采纳率是假象，合并后存活率 10-30% 才是真相。**PMS 是比 IAR 重要得多的指标。**

2. **感知偏差是系统性风险**：METR 实验揭示的 39 点"感知-现实差距"说明，开发者**无法仅凭直觉判断 AI 是否提升了效率**——必须依赖客观指标。

3. **Token 效率 ≠ 开发效率**：最便宜的模型每成功任务可能反而最贵。**CPST（每成功任务成本）是比每 Token 价格更有意义的成本指标。**

4. **幻觉问题有解**：CodeHalu 分类体系 + 多方法组合检测（静态分析 + 测试 + 采样相似度）可以捕获大部分幻觉，关键是**必须建立检测流程**。

5. **专家与新手的分化**：Claude Code 数据显示专家 session 产出是新手 5 倍，但**非程序员也能达到接近程序员的成功率**——领域知识比编程背景更重要。

6. **代码流失是最大隐性成本**：GitClear 数据显示重 AI 用户的代码 churn 可达人工的 9 倍，而团队往往只追踪"写了多少代码"却不追踪"多少代码被废弃"。

### 12.2 一句话总结

> **衡量 Vibe Coding 效率需要从"写了多少"转向"活了多少、对了多少、省了多少"——以 30 天代码存活率（PMS）和幻觉检出率（HDR）为双核心，以 Token 效率（TER/EPI）为辅助，构建从数据采集到趋势预警的完整闭环。**

---

*本文档基于对 Vibe Coding 与 Prompt 提示词知识的深度研究，结合学术论文、行业报告、大模型厂商实践、极客社区讨论和自有数据分析综合编制。*
*核心参考来源：Andrej Karpathy (2025), Anthropic Claude Code 400K Session Analysis (2026), GitClear 211M LOC Study (2025-2026), CodeHalu AAAI (2025), COLING EPI (2025), METR Controlled Study (2025), DORA/SPACE/DevEx Framework, YapBench (2026), OpenAI Prompting Guide, Veracode Security Study (2025), Stack Overflow Developer Survey (2025).*
