import { useState, useEffect } from 'react'
import { Tag, Typography, Progress, Collapse } from 'antd'
import {
  CheckCircleFilled,
  LoadingOutlined,
  ClockCircleOutlined,
  CloseCircleFilled,
  CaretDownOutlined,
  CodeOutlined,
} from '@ant-design/icons'
import type { StepInfo } from '../stores/chatStore'

const { Text, Paragraph } = Typography
const { Panel } = Collapse

interface StepPanelProps {
  steps: StepInfo[]
  isLoading?: boolean
  showInSidebar?: boolean
}

// 节点标签映射 - 更新为包含所有新节点
const NODE_LABELS: Record<string, { label: string; category: string }> = {
  // 入口层
  gate: { label: '指令门控', category: '理解' },
  router: { label: '意图路由', category: '理解' },
  // 理解层
  entity_extractor: { label: '实体抽取', category: '理解' },
  query_rewriter: { label: '查询改写', category: '理解' },
  planner: { label: '任务规划', category: '理解' },
  // 映射层
  schema_search: { label: 'Schema 检索', category: '映射' },
  term_mapper: { label: '术语映射', category: '映射' },
  column_selector: { label: '列选择', category: '映射' },
  clarifier: { label: '歧义澄清', category: '映射' },
  // SQL 层
  sql_generator: { label: 'SQL 生成', category: 'SQL' },
  sql_validator: { label: 'SQL 验证', category: 'SQL' },
  sql_optimizer: { label: 'SQL 优化', category: 'SQL' },
  sql_executor: { label: 'SQL 执行', category: 'SQL' },
  sql_fixer: { label: 'SQL 修复', category: 'SQL' },
  // 数据层
  result_validator: { label: '结果验证', category: '数据' },
  data_cleaner: { label: '数据清洗', category: '数据' },
  metric_calculator: { label: '指标计算', category: '数据' },
  // 分析层
  analyzer: { label: '数据分析', category: '分析' },
  trend_analyzer: { label: '趋势分析', category: '分析' },
  anomaly_detector: { label: '异常检测', category: '分析' },
  comparison_analyzer: { label: '对比分析', category: '分析' },
  correlation_analyzer: { label: '相关性分析', category: '分析' },
  distribution_analyzer: { label: '分布分析', category: '分析' },
  attribution_analyzer: { label: '归因分析', category: '分析' },
  forecast_generator: { label: '预测生成', category: '分析' },
  kpi_monitor: { label: 'KPI 监控', category: '分析' },
  // 洞察层
  insight_extractor: { label: '洞察提取', category: '洞察' },
  recommendation_generator: { label: '建议生成', category: '洞察' },
  // 可视化层
  chart_recommender: { label: '图表推荐', category: '可视化' },
  visualizer: { label: '可视化生成', category: '可视化' },
  dashboard_builder: { label: '仪表盘构建', category: '可视化' },
  // 输出层
  summary_generator: { label: '摘要生成', category: '输出' },
  narrative_generator: { label: '报告格式化', category: '输出' },
  answer_generator: { label: '答案生成', category: '输出' },
  reporter: { label: '报告输出', category: '输出' },
  // 文件处理
  file_parser: { label: '文件解析', category: '文件' },
  file_analyzer: { label: '文件分析', category: '文件' },
}

const CATEGORY_COLORS: Record<string, string> = {
  '理解': '#667eea',
  '映射': '#764ba2',
  'SQL': '#5AD8A6',
  '数据': '#36CFC9',
  '分析': '#F6BD16',
  '洞察': '#E86452',
  '可视化': '#9254DE',
  '输出': '#1890FF',
  '文件': '#FA8C16',
}

const STATUS_CONFIG: Record<string, { icon: React.ReactNode; color: string; text: string }> = {
  completed: { 
    icon: <CheckCircleFilled style={{ color: '#52c41a' }} />, 
    color: '#52c41a',
    text: '已完成'
  },
  running: { 
    icon: <LoadingOutlined style={{ color: '#667eea' }} spin />, 
    color: '#667eea',
    text: '执行中'
  },
  pending: { 
    icon: <ClockCircleOutlined style={{ color: '#d9d9d9' }} />, 
    color: '#d9d9d9',
    text: '等待中'
  },
  failed: { 
    icon: <CloseCircleFilled style={{ color: '#ff4d4f' }} />, 
    color: '#ff4d4f',
    text: '失败'
  },
}

export default function StepPanel({ steps, isLoading, showInSidebar = false }: StepPanelProps) {
  const [expandedKeys, setExpandedKeys] = useState<string[]>([])
  const [autoExpand, setAutoExpand] = useState(true)

  const completedCount = steps.filter((s) => s.status === 'completed').length
  const totalCount = steps.length
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  // 自动展开正在执行的步骤
  useEffect(() => {
    if (autoExpand) {
      const runningStep = [...steps].reverse().find(s => s.status === 'running')
      if (runningStep) {
        setExpandedKeys(prev => 
          prev.includes(runningStep.id) ? prev : [...prev, runningStep.id]
        )
      }
    }
  }, [steps, autoExpand])

  // 侧边栏模式 - 类似图片中的执行过程面板
  if (showInSidebar) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* 头部 */}
        <div style={{ 
          padding: '16px 20px', 
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CodeOutlined style={{ color: '#667eea', fontSize: 16 }} />
            <Text strong style={{ fontSize: 15 }}>执行过程</Text>
          </div>
          {isLoading && (
            <Tag color="processing" style={{ borderRadius: 10, margin: 0 }}>
              执行中
            </Tag>
          )}
        </div>

        {/* 进度条 */}
        <div style={{ padding: '12px 20px', borderBottom: '1px solid #f5f5f5' }}>
          <Progress 
            percent={progress} 
            size="small" 
            strokeColor={{
              '0%': '#667eea',
              '100%': '#52c41a',
            }}
            format={() => `${completedCount}/${totalCount}`}
          />
        </div>

        {/* 步骤列表 */}
        <div style={{ flex: 1, overflow: 'auto', padding: '8px 0' }}>
          {steps.map((step, index) => {
            const nodeInfo = NODE_LABELS[step.node] || { label: step.title || step.node, category: '其他' }
            const config = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending
            const categoryColor = CATEGORY_COLORS[nodeInfo.category] || '#8c8c8c'
            const isExpanded = expandedKeys.includes(step.id)

            return (
              <div key={step.id} style={{ padding: '0 16px' }}>
                {/* 步骤头部 */}
                <div
                  onClick={() => {
                    setExpandedKeys(prev => 
                      prev.includes(step.id) 
                        ? prev.filter(k => k !== step.id)
                        : [...prev, step.id]
                    )
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '12px 0',
                    cursor: 'pointer',
                    borderBottom: index < steps.length - 1 ? '1px solid #f5f5f5' : 'none',
                  }}
                >
                  {/* 状态图标 */}
                  <div style={{ flexShrink: 0 }}>
                    {config.icon}
                  </div>

                  {/* 步骤信息 */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Text strong style={{ fontSize: 13 }}>
                        Step {index + 1}
                      </Text>
                      <Text style={{ fontSize: 13, color: '#595959' }}>
                        {nodeInfo.label}
                      </Text>
                    </div>
                    {step.detail && (
                      <Text 
                        type="secondary" 
                        style={{ fontSize: 12, display: 'block', marginTop: 2 }}
                        ellipsis
                      >
                        {step.detail}
                      </Text>
                    )}
                  </div>

                  {/* 分类标签 */}
                  <Tag 
                    style={{ 
                      borderRadius: 4, 
                      fontSize: 11,
                      border: 'none',
                      background: `${categoryColor}15`,
                      color: categoryColor,
                      margin: 0,
                    }}
                  >
                    {nodeInfo.category}
                  </Tag>

                  {/* 展开图标 */}
                  <CaretDownOutlined 
                    style={{ 
                      fontSize: 10, 
                      color: '#bfbfbf',
                      transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.2s',
                    }} 
                  />
                </div>

                {/* 展开内容 */}
                {isExpanded && step.data && Object.keys(step.data).length > 0 && (
                  <div style={{ 
                    padding: '12px 16px', 
                    marginLeft: 28,
                    marginBottom: 8,
                    background: '#fafafa', 
                    borderRadius: 8,
                    fontSize: 12,
                  }}>
                    <pre style={{ 
                      margin: 0, 
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-all',
                      color: '#595959',
                      fontFamily: 'Monaco, Menlo, monospace',
                      fontSize: 11,
                    }}>
                      {JSON.stringify(step.data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )
          })}

          {steps.length === 0 && (
            <div style={{ 
              padding: '40px 20px', 
              textAlign: 'center', 
              color: '#bfbfbf' 
            }}>
              <ClockCircleOutlined style={{ fontSize: 32, marginBottom: 12 }} />
              <div>等待执行...</div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // 内嵌模式 - 在消息气泡中显示
  return (
    <div
      style={{
        background: 'white',
        borderRadius: 12,
        overflow: 'hidden',
        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        border: '1px solid #f0f0f0',
      }}
    >
      {/* 头部进度 */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f5f5f5' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          marginBottom: 8,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ fontSize: 13 }}>执行步骤</Text>
            {isLoading && (
              <Tag color="processing" style={{ borderRadius: 10, fontSize: 11 }}>
                执行中
              </Tag>
            )}
          </div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {completedCount}/{totalCount} 完成
          </Text>
        </div>
        <Progress 
          percent={progress} 
          size="small" 
          showInfo={false}
          strokeColor={{
            '0%': '#667eea',
            '100%': '#52c41a',
          }}
        />
      </div>

      {/* 步骤列表 */}
      <div style={{ padding: '8px 16px 12px' }}>
        {steps.map((step, index) => {
          const nodeInfo = NODE_LABELS[step.node] || { label: step.title || step.node, category: '其他' }
          const config = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending
          const categoryColor = CATEGORY_COLORS[nodeInfo.category] || '#8c8c8c'

            return (
              <div
              key={step.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                gap: 10,
                padding: '8px 0',
                position: 'relative',
              }}
            >
              {/* 连接线 */}
              {index < steps.length - 1 && (
                <div
                  style={{
                    position: 'absolute',
                    left: 8,
                    top: 26,
                    bottom: -8,
                    width: 2,
                    background: step.status === 'completed' ? '#52c41a' : '#f0f0f0',
                    borderRadius: 1,
                  }}
                />
              )}
              
              {/* 状态图标 */}
              <div style={{ flexShrink: 0, marginTop: 2, zIndex: 1 }}>
                {config.icon}
              </div>
              
              {/* 步骤信息 */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                  <Text style={{ fontSize: 13, color: '#262626', fontWeight: 500 }}>
                    {nodeInfo.label}
                  </Text>
                  <Tag 
                    style={{ 
                      borderRadius: 4, 
                      fontSize: 10,
                      lineHeight: '16px',
                      padding: '0 6px',
                      border: 'none',
                      background: `${categoryColor}15`,
                      color: categoryColor,
                      margin: 0,
                    }}
                  >
                    {nodeInfo.category}
                  </Tag>
                </div>
                {step.detail && (
                  <Text 
                    type="secondary" 
                    style={{ fontSize: 12, display: 'block', marginTop: 2 }}
                  >
                    {step.detail}
                  </Text>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
