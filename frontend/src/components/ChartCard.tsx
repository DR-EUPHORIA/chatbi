import { useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { Button, Tooltip, Space, Typography } from 'antd'
import { ExpandOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons'

const { Text } = Typography

interface ChartCardProps {
  chartType: string
  chartConfig: Record<string, unknown>
}

export default function ChartCard({ chartType, chartConfig }: ChartCardProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)

  // 合并默认配置
  const mergedOption = {
    ...chartConfig,
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: chartConfig.title ? '15%' : '8%',
      containLabel: true,
      ...(chartConfig.grid as Record<string, unknown> || {}),
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#f0f0f0',
      textStyle: { color: '#262626', fontSize: 13 },
      ...(chartConfig.tooltip as Record<string, unknown> || {}),
    },
  }

  const handleDownloadImage = () => {
    const chartDom = document.querySelector('.echarts-for-react canvas') as HTMLCanvasElement
    if (chartDom) {
      const url = chartDom.toDataURL('image/png')
      const link = document.createElement('a')
      link.href = url
      link.download = `chart_${Date.now()}.png`
      link.click()
    }
  }

  const chartHeight = isFullscreen ? 'calc(100vh - 80px)' : 360

  const chartContent = (
    <div
      className="chart-card"
      style={{
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : undefined,
        left: isFullscreen ? 0 : undefined,
        right: isFullscreen ? 0 : undefined,
        bottom: isFullscreen ? 0 : undefined,
        zIndex: isFullscreen ? 9999 : undefined,
        background: isFullscreen ? '#fff' : undefined,
        borderRadius: isFullscreen ? 0 : 12,
      }}
    >
      {/* 工具栏 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 8,
        }}
      >
        <Text type="secondary" style={{ fontSize: 12 }}>
          {chartType === 'line' && '📈 折线图'}
          {chartType === 'bar' && '📊 柱状图'}
          {chartType === 'pie' && '🥧 饼图'}
          {chartType === 'radar' && '🕸️ 雷达图'}
          {chartType === 'gauge' && '🎯 仪表盘'}
          {chartType === 'funnel' && '🔻 漏斗图'}
          {!['line', 'bar', 'pie', 'radar', 'gauge', 'funnel'].includes(chartType) && '📊 图表'}
        </Text>
        <Space size={4}>
          <Tooltip title="下载图片">
            <Button type="text" size="small" icon={<DownloadOutlined />} onClick={handleDownloadImage} />
          </Tooltip>
          <Tooltip title={isFullscreen ? '退出全屏' : '全屏'}>
            <Button
              type="text"
              size="small"
              icon={<ExpandOutlined />}
              onClick={() => setIsFullscreen(!isFullscreen)}
            />
          </Tooltip>
        </Space>
      </div>

      {/* ECharts 图表 */}
      <ReactECharts
        option={mergedOption}
        style={{ height: chartHeight, width: '100%' }}
        notMerge
        lazyUpdate
      />
    </div>
  )

  return chartContent
}
