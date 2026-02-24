
/**
 * 智能推荐问题组件 - 根据数据集和对话上下文动态推荐分析问题
 */

import { useState, useEffect } from 'react'
import { Typography, Tag, Tooltip, Spin } from 'antd'
import {
  BulbOutlined,
  LineChartOutlined,
  PieChartOutlined,
  BarChartOutlined,
  TableOutlined,
  AlertOutlined,
  ReloadOutlined,
} from '@ant-design/icons'

const { Text } = Typography

interface SmartSuggestionsProps {
  datasetId: string
  lastQuery?: string
  lastResult?: Record<string, unknown>
  onSelect: (question: string) => void
  disabled?: boolean
}

interface Suggestion {
  id: string
  question: string
  category: 'trend' | 'comparison' | 'distribution' | 'anomaly' | 'summary' | 'detail'
  icon: React.ReactNode
  isFollowUp?: boolean
}

// 根据数据集生成基础推荐问题
const BASE_SUGGESTIONS: Record<string, Suggestion[]> = {
  demo_ecommerce: [
    { id: '1', question: '本月销售额是多少？环比增长了多少？', category: 'summary', icon: <BarChartOutlined /> },
    { id: '2', question: '最近30天的销售趋势如何？', category: 'trend', icon: <LineChartOutlined /> },
    { id: '3', question: '各品类销售额占比是多少？', category: 'distribution', icon: <PieChartOutlined /> },
    { id: '4', question: '哪些商品销量异常下降？', category: 'anomaly', icon: <AlertOutlined /> },
    { id: '5', question: '各地区销售额排名Top10', category: 'comparison', icon: <TableOutlined /> },
    { id: '6', question: '客单价最高的用户群体是哪些？', category: 'detail', icon: <BulbOutlined /> },
  ],
  demo_finance: [
    { id: '1', question: '本季度营收和利润情况如何？', category: 'summary', icon: <BarChartOutlined /> },
    { id: '2', question: '近12个月的现金流趋势', category: 'trend', icon: <LineChartOutlined /> },
    { id: '3', question: '各业务线收入占比分析', category: 'distribution', icon: <PieChartOutlined /> },
    { id: '4', question: '哪些成本项目增长异常？', category: 'anomaly', icon: <AlertOutlined /> },
    { id: '5', question: '应收账款账龄分布', category: 'comparison', icon: <TableOutlined /> },
    { id: '6', question: '毛利率最高的产品线是哪个？', category: 'detail', icon: <BulbOutlined /> },
  ],
  demo_marketing: [
    { id: '1', question: '本月各渠道的转化率是多少？', category: 'summary', icon: <BarChartOutlined /> },
    { id: '2', question: '近30天的用户增长趋势', category: 'trend', icon: <LineChartOutlined /> },
    { id: '3', question: '各营销渠道的ROI对比', category: 'distribution', icon: <PieChartOutlined /> },
    { id: '4', question: '哪些广告计划效果异常差？', category: 'anomaly', icon: <AlertOutlined /> },
    { id: '5', question: '用户来源渠道Top5', category: 'comparison', icon: <TableOutlined /> },
    { id: '6', question: '复购率最高的用户画像', category: 'detail', icon: <BulbOutlined /> },
  ],
}

// 根据上一次查询生成追问建议
function generateFollowUpSuggestions(lastQuery: string, lastResult?: Record<string, unknown>): Suggestion[] {
  const followUps: Suggestion[] = []
  
  // 时间维度追问
  if (lastQuery.includes('本月') || lastQuery.includes('这个月')) {
    followUps.push({
      id: 'f1',
      question: '上个月的情况呢？',
      category: 'trend',
      icon: <LineChartOutlined />,
      isFollowUp: true,
    })
    followUps.push({
      id: 'f2',
      question: '和去年同期相比如何？',
      category: 'comparison',
      icon: <BarChartOutlined />,
      isFollowUp: true,
    })
  }
  
  if (lastQuery.includes('趋势') || lastQuery.includes('变化')) {
    followUps.push({
      id: 'f3',
      question: '是什么原因导致的？',
      category: 'anomaly',
      icon: <AlertOutlined />,
      isFollowUp: true,
    })
    followUps.push({
      id: 'f4',
      question: '预测下个月会怎样？',
      category: 'trend',
      icon: <LineChartOutlined />,
      isFollowUp: true,
    })
  }
  
  // 维度拆分追问
  if (lastQuery.includes('销售额') || lastQuery.includes('收入')) {
    followUps.push({
      id: 'f5',
      question: '按地区拆分看看',
      category: 'distribution',
      icon: <PieChartOutlined />,
      isFollowUp: true,
    })
    followUps.push({
      id: 'f6',
      question: '按品类拆分看看',
      category: 'distribution',
      icon: <PieChartOutlined />,
      isFollowUp: true,
    })
  }
  
  // 排名类追问
  if (lastQuery.includes('排名') || lastQuery.includes('Top')) {
    followUps.push({
      id: 'f7',
      question: '最后几名是哪些？',
      category: 'comparison',
      icon: <TableOutlined />,
      isFollowUp: true,
    })
  }
  
  // 通用追问
  followUps.push({
    id: 'f8',
    question: '帮我生成一份分析报告',
    category: 'summary',
    icon: <BulbOutlined />,
    isFollowUp: true,
  })
  
  return followUps.slice(0, 4)
}

const CATEGORY_COLORS: Record<string, string> = {
  trend: '#667eea',
  comparison: '#764ba2',
  distribution: '#5AD8A6',
  anomaly: '#E86452',
  summary: '#F6BD16',
  detail: '#36CFC9',
}

export default function SmartSuggestions({
  datasetId,
  lastQuery,
  lastResult,
  onSelect,
  disabled = false,
}: SmartSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    
    // 模拟异步加载（实际可以调用后端 API 获取智能推荐）
    const timer = setTimeout(() => {
      let newSuggestions: Suggestion[] = []
      
      if (lastQuery) {
        // 有上一次查询，生成追问建议
        newSuggestions = generateFollowUpSuggestions(lastQuery, lastResult)
      } else {
        // 没有查询历史，显示基础推荐
        newSuggestions = BASE_SUGGESTIONS[datasetId] || BASE_SUGGESTIONS.demo_ecommerce
      }
      
      setSuggestions(newSuggestions)
      setLoading(false)
    }, 300)
    
    return () => clearTimeout(timer)
  }, [datasetId, lastQuery, lastResult])

  const handleRefresh = () => {
    // 随机打乱推荐顺序
    setSuggestions(prev => [...prev].sort(() => Math.random() - 0.5))
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '12px 0' }}>
        <Spin size="small" />
      </div>
    )
  }

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#8c8c8c' }}>
          <BulbOutlined />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {lastQuery ? '继续追问' : '智能推荐'}
          </Text>
        </div>
        <Tooltip title="换一批">
          <ReloadOutlined
            style={{ fontSize: 12, color: '#bfbfbf', cursor: 'pointer' }}
            onClick={handleRefresh}
          />
        </Tooltip>
      </div>
      
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {suggestions.map((suggestion) => (
          <Tag
            key={suggestion.id}
            icon={suggestion.icon}
            onClick={() => !disabled && onSelect(suggestion.question)}
            style={{
              padding: '4px 10px',
              borderRadius: 16,
              border: 'none',
              background: `${CATEGORY_COLORS[suggestion.category]}15`,
              color: CATEGORY_COLORS[suggestion.category],
              fontSize: 12,
              cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.5 : 1,
              transition: 'all 0.2s',
            }}
          >
            {suggestion.question}
          </Tag>
        ))}
      </div>
    </div>
  )
}
