import { Button, Space, Tooltip, message } from 'antd'
import {
  CopyOutlined,
  ReloadOutlined,
  DownloadOutlined,
  ShareAltOutlined,
} from '@ant-design/icons'

interface QuickActionsProps {
  content?: string
  sql?: string
  chartConfig?: Record<string, unknown>
  onRetry?: () => void
  disabled?: boolean
}

export default function QuickActions({
  content,
  sql,
  chartConfig,
  onRetry,
  disabled = false,
}: QuickActionsProps) {
  const handleCopyContent = async () => {
    if (!content) return
    try {
      await navigator.clipboard.writeText(content)
      message.success('已复制回答内容')
    } catch {
      message.error('复制失败')
    }
  }

  const handleCopySql = async () => {
    if (!sql) return
    try {
      await navigator.clipboard.writeText(sql)
      message.success('已复制 SQL')
    } catch {
      message.error('复制失败')
    }
  }

  const handleExportChart = () => {
    if (!chartConfig) return
    const dataStr = JSON.stringify(chartConfig, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `chart_config_${Date.now()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    message.success('图表配置已导出')
  }

  const handleShare = async () => {
    const shareContent = content || sql || ''
    if (!shareContent) return
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'ChatBI 分析结果',
          text: shareContent,
        })
      } catch {
        await navigator.clipboard.writeText(shareContent)
        message.success('已复制到剪贴板')
      }
    } else {
      await navigator.clipboard.writeText(shareContent)
      message.success('已复制到剪贴板')
    }
  }

  return (
    <Space size={4}>
      {content && (
        <Tooltip title="复制回答">
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={handleCopyContent}
            disabled={disabled}
            style={{ color: '#8c8c8c', fontSize: 12 }}
          />
        </Tooltip>
      )}
      
      {sql && (
        <Tooltip title="复制 SQL">
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={handleCopySql}
            disabled={disabled}
            style={{ color: '#8c8c8c', fontSize: 12 }}
          >
            SQL
          </Button>
        </Tooltip>
      )}
      
      {chartConfig && (
        <Tooltip title="导出图表配置">
          <Button
            type="text"
            size="small"
            icon={<DownloadOutlined />}
            onClick={handleExportChart}
            disabled={disabled}
            style={{ color: '#8c8c8c', fontSize: 12 }}
          />
        </Tooltip>
      )}
      
      <Tooltip title="分享">
        <Button
          type="text"
          size="small"
          icon={<ShareAltOutlined />}
          onClick={handleShare}
          disabled={disabled || (!content && !sql)}
          style={{ color: '#8c8c8c', fontSize: 12 }}
        />
      </Tooltip>
      
      {onRetry && (
        <Tooltip title="重新生成">
          <Button
            type="text"
            size="small"
            icon={<ReloadOutlined />}
            onClick={onRetry}
            disabled={disabled}
            style={{ color: '#8c8c8c', fontSize: 12 }}
          />
        </Tooltip>
      )}
    </Space>
  )
}
