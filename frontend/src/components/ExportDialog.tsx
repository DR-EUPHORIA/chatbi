import React, { useState } from 'react'
import { Modal, Button, Radio, Space, message } from 'antd'
import { DownloadOutlined, CopyOutlined } from '@ant-design/icons'
import type { ChatMessage } from '../stores/chatStore'

interface ExportDialogProps {
  visible: boolean
  onClose: () => void
  messages: ChatMessage[]
  sessionTitle?: string
}

type ExportFormat = 'markdown' | 'json' | 'text'

const ExportDialog: React.FC<ExportDialogProps> = ({
  visible,
  onClose,
  messages,
  sessionTitle = '对话记录'
}) => {
  const [format, setFormat] = useState<ExportFormat>('markdown')

  const formatMessages = (): string => {
    const timestamp = new Date().toLocaleString('zh-CN')
    
    switch (format) {
      case 'markdown':
        let md = `# ${sessionTitle}\n\n`
        md += `> 导出时间: ${timestamp}\n\n`
        md += `---\n\n`
        messages.forEach((msg) => {
          const role = msg.role === 'user' ? '👤 用户' : '🤖 助手'
          md += `### ${role}\n\n${msg.content}\n\n`
        })
        return md

      case 'json':
        return JSON.stringify({
          title: sessionTitle,
          exportTime: timestamp,
          messages: messages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp
          }))
        }, null, 2)

      case 'text':
        let text = `${sessionTitle}\n`
        text += `导出时间: ${timestamp}\n`
        text += `${'='.repeat(50)}\n\n`
        messages.forEach((msg) => {
          const role = msg.role === 'user' ? '用户' : '助手'
          text += `[${role}]\n${msg.content}\n\n`
        })
        return text

      default:
        return ''
    }
  }

  const getFileExtension = (): string => {
    switch (format) {
      case 'markdown': return 'md'
      case 'json': return 'json'
      case 'text': return 'txt'
      default: return 'txt'
    }
  }

  const handleDownload = () => {
    const content = formatMessages()
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${sessionTitle}_${new Date().toISOString().slice(0, 10)}.${getFileExtension()}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    message.success('导出成功')
    onClose()
  }

  const handleCopy = async () => {
    const content = formatMessages()
    try {
      await navigator.clipboard.writeText(content)
      message.success('已复制到剪贴板')
    } catch {
      message.error('复制失败，请手动复制')
    }
  }

  return (
    <Modal
      title="导出对话"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button key="copy" icon={<CopyOutlined />} onClick={handleCopy}>
          复制
        </Button>,
        <Button key="download" type="primary" icon={<DownloadOutlined />} onClick={handleDownload}>
          下载
        </Button>
      ]}
    >
      <div style={{ marginBottom: 16 }}>
        <p style={{ marginBottom: 8, color: '#666' }}>选择导出格式：</p>
        <Radio.Group value={format} onChange={(e) => setFormat(e.target.value)}>
          <Space direction="vertical">
            <Radio value="markdown">Markdown (.md) - 适合文档阅读</Radio>
            <Radio value="json">JSON (.json) - 适合数据处理</Radio>
            <Radio value="text">纯文本 (.txt) - 通用格式</Radio>
          </Space>
        </Radio.Group>
      </div>
      <div style={{ padding: 12, background: '#f5f5f5', borderRadius: 6, fontSize: 12, color: '#888' }}>
        将导出 {messages.length} 条消息
      </div>
    </Modal>
  )
}

export default ExportDialog
