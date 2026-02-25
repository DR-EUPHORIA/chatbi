import { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { Button, Select, Space, Typography, Row, Col, Card, Spin } from 'antd'
import {
  FullscreenOutlined,
  FullscreenExitOutlined,
  ReloadOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons'

const { Title, Text } = Typography

// KPI 数据
const MOCK_KPI = [
  { title: '总成交额 (GMV)', value: 12856432, prefix: '¥', suffix: '', change: 12.5 },
  { title: '订单量', value: 98432, prefix: '', suffix: '单', change: 8.3 },
  { title: '客单价', value: 130.6, prefix: '¥', suffix: '', change: -2.1 },
  { title: '活跃用户', value: 4521, prefix: '', suffix: '人', change: 15.7 },
]

const TEMPLATES = [
  { value: 'sales_overview', label: '📊 销售总览' },
  { value: 'category_analysis', label: '📦 品类分析' },
  { value: 'regional_map', label: '🗺️ 区域分布' },
  { value: 'user_portrait', label: '👤 用户画像' },
]

// 销售趋势图配置
function getSalesTrendOption() {
  const dates = Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - 29 + i)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })
  const salesData = dates.map(() => Math.floor(Math.random() * 500000 + 200000))
  const orderData = dates.map(() => Math.floor(Math.random() * 3000 + 1500))

  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额', '订单量'], textStyle: { color: '#ccc' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: dates, 
      axisLabel: { color: '#aaa' }, 
      axisLine: { lineStyle: { color: '#444' } } 
    },
    yAxis: [
      { 
        type: 'value', 
        name: '销售额', 
        axisLabel: { color: '#aaa', formatter: (v: number) => `${(v / 10000).toFixed(0)}万` }, 
        splitLine: { lineStyle: { color: '#333' } }, 
        axisLine: { lineStyle: { color: '#444' } } 
      },
      { 
        type: 'value', 
        name: '订单量', 
        axisLabel: { color: '#aaa' }, 
        splitLine: { show: false }, 
        axisLine: { lineStyle: { color: '#444' } } 
      },
    ],
    series: [
      { 
        name: '销售额', 
        type: 'line', 
        data: salesData, 
        smooth: true, 
        itemStyle: { color: '#667eea' }, 
        areaStyle: { 
          color: { 
            type: 'linear', 
            x: 0, y: 0, x2: 0, y2: 1, 
            colorStops: [
              { offset: 0, color: 'rgba(102,126,234,0.3)' }, 
              { offset: 1, color: 'rgba(102,126,234,0.02)' }
            ] 
          } 
        } 
      },
      { 
        name: '订单量', 
        type: 'bar', 
        yAxisIndex: 1, 
        data: orderData, 
        itemStyle: { color: 'rgba(90,216,166,0.6)', borderRadius: [4, 4, 0, 0] } 
      },
    ],
  }
}

// 品类占比饼图
function getCategoryPieOption() {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { 
      orient: 'vertical', 
      left: 'left', 
      top: 'middle', 
      textStyle: { color: '#ccc', fontSize: 12 } 
    },
    series: [{
      type: 'pie', 
      radius: ['40%', '70%'],
      itemStyle: { borderRadius: 8, borderColor: '#0a0e27', borderWidth: 3 },
      label: { show: true, color: '#ccc', formatter: '{b}\n{d}%' },
      data: [
        { value: 3580, name: '电子产品', itemStyle: { color: '#667eea' } },
        { value: 2450, name: '服装鞋帽', itemStyle: { color: '#764ba2' } },
        { value: 1890, name: '食品饮料', itemStyle: { color: '#5AD8A6' } },
        { value: 1560, name: '家居家装', itemStyle: { color: '#F6BD16' } },
        { value: 1230, name: '美妆个护', itemStyle: { color: '#E86452' } },
      ],
    }],
  }
}

// 地区柱状图
function getRegionBarOption() {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { 
      type: 'value', 
      axisLabel: { color: '#aaa', formatter: (v: number) => `${(v / 10000).toFixed(0)}万` }, 
      splitLine: { lineStyle: { color: '#333' } } 
    },
    yAxis: { 
      type: 'category', 
      data: ['西南', '华中', '华南', '华北', '华东'], 
      axisLabel: { color: '#ccc' }, 
      axisLine: { lineStyle: { color: '#444' } } 
    },
    series: [{
      type: 'bar', 
      data: [
        { value: 1850000, itemStyle: { color: '#E86452' } },
        { value: 2100000, itemStyle: { color: '#F6BD16' } },
        { value: 2800000, itemStyle: { color: '#5AD8A6' } },
        { value: 3200000, itemStyle: { color: '#764ba2' } },
        { value: 3900000, itemStyle: { color: '#667eea' } },
      ],
      barWidth: 20, 
      itemStyle: { borderRadius: [0, 6, 6, 0] },
    }],
  }
}

// 支付方式环形图
function getPaymentDonutOption() {
  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', 
      radius: ['55%', '75%'], 
      center: ['50%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: '#0a0e27', borderWidth: 2 },
      label: { show: true, color: '#ccc', fontSize: 11 },
      data: [
        { value: 35, name: '支付宝', itemStyle: { color: '#667eea' } },
        { value: 30, name: '微信支付', itemStyle: { color: '#5AD8A6' } },
        { value: 15, name: '银行卡', itemStyle: { color: '#F6BD16' } },
        { value: 12, name: '花呗', itemStyle: { color: '#764ba2' } },
        { value: 8, name: '信用卡', itemStyle: { color: '#E86452' } },
      ],
    }],
  }
}

// 时段分布热力图
function getHourlyHeatmapOption() {
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const data: [number, number, number][] = []
  
  for (let i = 0; i < 7; i++) {
    for (let j = 0; j < 24; j++) {
      const baseValue = j >= 9 && j <= 22 ? 80 : 20
      const weekendBonus = i >= 5 ? 30 : 0
      const peakBonus = (j >= 10 && j <= 12) || (j >= 19 && j <= 21) ? 40 : 0
      data.push([j, i, Math.floor(Math.random() * 50 + baseValue + weekendBonus + peakBonus)])
    }
  }

  return {
    tooltip: { 
      position: 'top',
      formatter: (params: { data: [number, number, number] }) => {
        return `${days[params.data[1]]} ${hours[params.data[0]]}<br/>订单量: ${params.data[2]}`
      }
    },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: hours, 
      splitArea: { show: true },
      axisLabel: { color: '#aaa', fontSize: 10 }
    },
    yAxis: { 
      type: 'category', 
      data: days, 
      splitArea: { show: true },
      axisLabel: { color: '#aaa' }
    },
    visualMap: {
      min: 0,
      max: 200,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      textStyle: { color: '#aaa' },
      inRange: { color: ['#0a0e27', '#667eea', '#764ba2'] }
    },
    series: [{
      type: 'heatmap',
      data: data,
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  }
}

export default function DashboardPage() {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [template, setTemplate] = useState('sales_overview')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800)
    return () => clearTimeout(timer)
  }, [])

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      document.documentElement.requestFullscreen?.()
    } else {
      document.exitFullscreen?.()
    }
    setIsFullscreen(!isFullscreen)
  }

  const handleRefresh = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 500)
  }

  const cardStyle = {
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 12,
    marginBottom: 16,
  }

  const cardHeadStyle = { 
    borderBottom: '1px solid rgba(255,255,255,0.06)',
    color: '#e6e6e6',
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0a0e27',
        padding: isFullscreen ? '16px 24px' : '0 24px 24px',
        color: 'white',
      }}
    >
      {/* 顶部栏 */}
      <div
        style={{
          height: 56,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          marginBottom: 20,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Title level={4} style={{ color: 'white', margin: 0, fontSize: 18 }}>
            📊 数据大屏
          </Title>
          <Select
            value={template}
            onChange={setTemplate}
            options={TEMPLATES}
            style={{ width: 160 }}
            size="small"
          />
        </div>
        <Space>
          <Button
            type="text"
            icon={<ReloadOutlined spin={loading} />}
            style={{ color: '#aaa' }}
            onClick={handleRefresh}
          />
          <Button
            type="text"
            icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
            style={{ color: '#aaa' }}
            onClick={toggleFullscreen}
          />
        </Space>
      </div>

      <Spin spinning={loading} size="large">
        {/* KPI 指标卡 */}
        <Row gutter={16} style={{ marginBottom: 20 }}>
          {MOCK_KPI.map((kpi) => (
            <Col span={6} key={kpi.title}>
              <Card style={cardStyle} styles={{ body: { padding: '16px 20px' } }}>
                <Text style={{ color: '#8c8c8c', fontSize: 12 }}>{kpi.title}</Text>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginTop: 4 }}>
                  <span style={{ color: 'white', fontSize: 28, fontWeight: 700 }}>
                    {kpi.prefix}
                    {typeof kpi.value === 'number' && kpi.value > 10000
                      ? `${(kpi.value / 10000).toFixed(1)}万`
                      : kpi.value.toLocaleString()}
                  </span>
                  <span style={{ color: '#8c8c8c', fontSize: 13 }}>{kpi.suffix}</span>
                </div>
                <div style={{ marginTop: 4, fontSize: 12 }}>
                  {kpi.change > 0 ? (
                    <span style={{ color: '#52c41a' }}>
                      <ArrowUpOutlined /> {kpi.change}%
                    </span>
                  ) : (
                    <span style={{ color: '#ff4d4f' }}>
                      <ArrowDownOutlined /> {Math.abs(kpi.change)}%
                    </span>
                  )}
                  <span style={{ color: '#595959', marginLeft: 4 }}>较上期</span>
                </div>
              </Card>
            </Col>
          ))}
        </Row>

        {/* 图表区域 */}
        <Row gutter={16}>
          {/* 销售趋势 */}
          <Col span={16}>
            <Card
              title={<span style={{ color: '#e6e6e6', fontSize: 14 }}>📈 销售趋势（近30天）</span>}
              style={cardStyle}
              styles={{ header: cardHeadStyle, body: { padding: '12px 16px' } }}
            >
              <ReactECharts option={getSalesTrendOption()} style={{ height: 300 }} />
            </Card>
          </Col>

          {/* 品类占比 */}
          <Col span={8}>
            <Card
              title={<span style={{ color: '#e6e6e6', fontSize: 14 }}>🥧 品类占比</span>}
              style={cardStyle}
              styles={{ header: cardHeadStyle, body: { padding: '12px 16px' } }}
            >
              <ReactECharts option={getCategoryPieOption()} style={{ height: 300 }} />
            </Card>
          </Col>

          {/* 地区销售 */}
          <Col span={12}>
            <Card
              title={<span style={{ color: '#e6e6e6', fontSize: 14 }}>🗺️ 区域销售排名</span>}
              style={cardStyle}
              styles={{ header: cardHeadStyle, body: { padding: '12px 16px' } }}
            >
              <ReactECharts option={getRegionBarOption()} style={{ height: 260 }} />
            </Card>
          </Col>

          {/* 支付方式 */}
          <Col span={12}>
            <Card
              title={<span style={{ color: '#e6e6e6', fontSize: 14 }}>💳 支付方式分布</span>}
              style={cardStyle}
              styles={{ header: cardHeadStyle, body: { padding: '12px 16px' } }}
            >
              <ReactECharts option={getPaymentDonutOption()} style={{ height: 260 }} />
            </Card>
          </Col>

          {/* 时段热力图 */}
          <Col span={24}>
            <Card
              title={<span style={{ color: '#e6e6e6', fontSize: 14 }}>🕐 订单时段分布热力图</span>}
              style={cardStyle}
              styles={{ header: cardHeadStyle, body: { padding: '12px 16px' } }}
            >
              <ReactECharts option={getHourlyHeatmapOption()} style={{ height: 280 }} />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}
