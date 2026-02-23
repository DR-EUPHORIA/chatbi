# ChatBI Mini — 对话式智能数据分析平台

基于 LangChain / LangGraph 的 mini 版 ChatBI，用自然语言探索你的数据。

## 技术栈

- **后端**：Python 3.11+ / FastAPI / LangChain / LangGraph / SQLAlchemy
- **前端**：React 18 / TypeScript / Ant Design 5.x / ECharts / Zustand
- **LLM**：OpenAI GPT-4o（可替换为任何兼容 OpenAI API 的模型）

## 核心功能

### 数据分析能力

- 🛡️ **指令门控**：不清晰的问题打回 + 引导追问
- 🔀 **意图路由**：自动识别数据查询 / 报告生成 / 大屏 / 闲聊
- ⚡ **Text-to-SQL**：基于 Schema + 语义层 + Few-shot 生成 SQL
- 📊 **智能可视化**：自动推荐图表类型，生成 ECharts 配置
- 📝 **报告生成**：一键导出 HTML / Excel / PPT
- 📈 **数字大屏**：深色主题数据大屏，支持全屏展示
- 🔄 **SSE 流式推送**：实时展示 Agent 执行步骤

### 前端交互功能

| 功能 | 说明 |
|------|------|
| 对话界面 | 左右分栏，左侧对话区 + 右侧执行过程面板 |
| 历史会话 | 侧边栏管理历史对话，支持搜索、重命名、删除 |
| 步骤可视化 | 实时展示 Agent 执行步骤，支持展开查看详情 |
| SQL 高亮 | 语法高亮、一键复制 |
| 数据表格 | 分页展示、CSV 导出 |
| 图表渲染 | ECharts 集成，支持全屏、下载图片 |
| 报告卡片 | 摘要、洞察、HTML 预览、导出 |
| 数据大屏 | 深色主题仪表盘，KPI 卡片 + 多图表 |
| 智能推荐 | 根据数据集和对话上下文推荐分析问题 |
| 文件上传 | 支持 Excel、CSV、PDF 等格式 |
| 主题切换 | 浅色/深色/跟随系统 |
| 导出对话 | 支持 Markdown、HTML、JSON 格式 |
| 快捷操作 | 复制、导出、重新生成 |
| 多轮对话 | 支持上下文理解和追问 |
| 歧义澄清 | 问题不明确时提供选项让用户选择 |

## 快速开始

### 1. 初始化 Demo 数据库

```bash
cd chatbi-mini
python scripts/init_demo_db.py
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
EOF

# 启动服务
python main.py
```

后端默认运行在 `http://localhost:8000`

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认运行在 `http://localhost:3000`，已配置代理转发 `/api` 到后端。

## 项目结构

```
chatbi-mini/
├── backend/
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 全局配置
│   ├── requirements.txt        # Python 依赖
│   ├── agent/
│   │   ├── state.py            # Agent 状态定义
│   │   ├── graph.py            # LangGraph 工作流编排
│   │   ├── llm.py              # LLM 实例工厂
│   │   ├── nodes/              # 所有执行节点
│   │   │   ├── gate.py         # 指令门控
│   │   │   ├── router.py       # 意图路由
│   │   │   ├── planner.py      # 任务规划
│   │   │   ├── schema_search.py# Schema 检索
│   │   │   ├── clarifier.py    # 歧义澄清
│   │   │   ├── sql_generator.py# SQL 生成
│   │   │   ├── sql_executor.py # SQL 执行
│   │   │   ├── sql_fixer.py    # SQL 修正
│   │   │   ├── analyzer.py     # 数据分析
│   │   │   ├── visualizer.py   # 可视化
│   │   │   └── reporter.py     # 报告生成
│   │   └── prompts/            # Prompt 模板
│   ├── tools/                  # 工具层
│   │   ├── database.py         # 数据库连接
│   │   ├── file_reader.py      # 文件读取
│   │   ├── file_writer.py      # 文件导出
│   │   ├── chart.py            # 图表配置
│   │   └── code_runner.py      # 代码执行
│   ├── knowledge/              # 知识层
│   │   ├── semantic_layer.py   # 语义层/指标字典
│   │   ├── few_shot.py         # Few-shot 示例库
│   │   └── glossary.py         # 业务术语
│   ├── data/datasets/          # 数据集管理
│   └── api/                    # API 路由
├── frontend/
│   ├── src/
│   │   ├── pages/              # 页面
│   │   │   ├── ChatPage.tsx    # 对话主界面
│   │   │   ├── DashboardPage.tsx # 数字大屏
│   │   │   └── DemoPage.tsx    # Demo 数据集
│   │   ├── components/         # 组件
│   │   │   ├── MessageBubble   # 消息气泡
│   │   │   ├── StepPanel       # 执行步骤面板
│   │   │   ├── SqlBlock        # SQL 代码块
│   │   │   ├── DataTable       # 数据表格
│   │   │   ├── ChartCard       # 图表卡片
│   │   │   └── ReportCard      # 报告卡片
│   │   ├── stores/             # 状态管理
│   │   ├── hooks/              # 自定义 Hook
│   │   └── utils/              # 工具函数
│   └── package.json
└── scripts/
    └── init_demo_db.py         # Demo 数据初始化
```

## Agent 工作流

8 层 33 个 Node 的 LangGraph 工作流：

```
入口层 → 理解层 → 映射层 → SQL层 → 数据层 → 分析层 → 洞察层 → 可视化层 → 输出层
```

| 层级 | Node |
|------|------|
| 入口层 | gate, router |
| 理解层 | entity_extractor, query_rewriter, planner |
| 映射层 | schema_search, term_mapper, column_selector, clarifier |
| SQL层 | sql_generator, sql_validator, sql_optimizer, sql_executor, sql_fixer |
| 数据层 | result_validator, data_cleaner, metric_calculator |
| 分析层 | analyzer, trend_analyzer, anomaly_detector, comparison_analyzer, correlation_analyzer, distribution_analyzer, attribution_analyzer, forecast_generator, kpi_monitor |
| 洞察层 | insight_extractor, recommendation_generator |
| 可视化层 | chart_recommender, visualizer, dashboard_builder |
| 输出层 | summary_generator, narrative_generator, answer_generator, reporter |

## 使用示例

### 数据查询

```
用户：最近30天的销售额是多少？
助手：根据查询，最近30天的总销售额为 1,523.5 万元，环比增长 15.3%。
```

### 图表生成

```
用户：各品类销售额排名，用柱状图展示
助手：[生成柱状图] 电子产品销售额最高，达 523 万，占比 34.3%...
```

### 分析报告

```
用户：帮我生成一份销售周报
助手：[生成报告] 
- 核心指标：总销售额 1,523.5 万，订单量 52,341 单
- 关键发现：电子产品增长 26.9%，华东区贡献 54.9% 增长
- 建议：关注客单价下降趋势
```

## Prompt 调试

核心 Prompt 模板位于 `backend/agent/prompts/` 目录，每个文件对应一个节点：

- `gate.py` — 门控判断 Prompt
- `router.py` — 意图识别 Prompt
- `planner.py` — 任务规划 Prompt
- `sql_generator.py` — SQL 生成 Prompt（最核心）
- `analyzer.py` — 数据分析 Prompt
- `visualizer.py` — 可视化推荐 Prompt
- `reporter.py` — 报告生成 Prompt

调试建议：先从 `sql_generator.py` 开始，确保 SQL 生成准确，再逐步优化其他节点。

## License

MIT
