import { useState, useRef, useEffect } from 'react'
import { Input, Button, Tag, Space, Tooltip, Select, Typography, Modal } from 'antd'
import {
  SendOutlined,
  PlusOutlined,
  ThunderboltOutlined,
  BarChartOutlined,
  TableOutlined,
  FileTextOutlined,
  DashboardOutlined,
  BulbOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  UploadOutlined,
  HistoryOutlined,
  ExportOutlined,
} from '@ant-design/icons'
import { useChat } from '../hooks/useChat'
import { useChatStore } from '../stores/chatStore'
import MessageBubble from '../components/MessageBubble'
import StepPanel from '../components/StepPanel'
import SessionSidebar from '../components/SessionSidebar'
import FileUpload from '../components/FileUpload'
import SmartSuggestions from '../components/SmartSuggestions'
import ExportDialog from '../components/ExportDialog'
import { useTheme, ThemeToggle } from '../contexts/ThemeContext'

const { Text } = Typography

const DATASET_OPTIONS = [
  { value: 'demo_ecommerce', label: '📦 电商销售数据（Demo）' },
  { value: 'demo_finance', label: '💰 财务报表数据（Demo）' },
  { value: 'demo_marketing', label: '📈 营销活动数据（Demo）' },
  { value: 'custom', label: '📁 上传自定义数据' },
]

const SUGGEST_QUESTIONS = [
  { label: '📊 最近30天的总成交金额', value: '最近30天的总成交金额是多少？' },
  { label: '📈 各品类销售额排名', value: '各品类的销售额排名是怎样的？帮我画个柱状图' },
  { label: '📉 最近7天订单量趋势', value: '最近7天每天的订单量趋势如何？' },
  { label: '🗺️ 各地区销售对比', value: '各地区的销售额对比情况，用饼图展示' },
  { label: '💰 客单价分析', value: '本月的客单价是多少？和上月相比有什么变化？' },
  { label: '📋 生成销售周报', value: '帮我生成一份最近一周的销售分析报告' },
]

const FUNCTION_TAGS = [
  { icon: <ThunderboltOutlined />, label: '数据查询', color: '#667eea' },
  { icon: <BarChartOutlined />, label: '图表分析', color: '#764ba2' },
  { icon: <TableOutlined />, label: '数据导出', color: '#5AD8A6' },
  { icon: <FileTextOutlined />, label: '报告生成', color: '#F6BD16' },
  { icon: <DashboardOutlined />, label: '数字大屏', color: '#E86452' },
]

export default function ChatPage() {
  const [inputValue, setInputValue] = useState('')
  const [showStepPanel, setShowStepPanel] = useState(true)
  const [showSidebar, setShowSidebar] = useState(true)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [selectedDataset, setSelectedDataset] = useState('demo_ecommerce')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { isDark } = useTheme()
  const { setDatasetId, setUploadedFileId } = useChatStore()

  const {
    messages,
    isStreaming,
    sendMessage,
    createSession,
    currentSession,
    lastUserQuery,
  } = useChat()

  const currentSteps = messages.length > 0 
    ? messages[messages.length - 1]?.steps || []
    : []
  const hasSteps = currentSteps.length > 0 || isStreaming

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (isStreaming) {
      setShowStepPanel(true)
    }
  }, [isStreaming])

  const handleSend = () => {
    if (!inputValue.trim() || isStreaming) return
    sendMessage(inputValue.trim())
    setInputValue('')
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  const handleSuggestClick = (question: string) => {
    if (isStreaming) return
    sendMessage(question)
  }

  const handleDatasetChange = (value: string) => {
    setSelectedDataset(value)
    if (value === 'custom') {
      setShowUploadModal(true)
    } else {
      setDatasetId(value)
    }
  }

  const handleFileUploadComplete = (fileInfo: { fileId: string }) => {
    setUploadedFileId(fileInfo.fileId)
    setShowUploadModal(false)
  }

  const isEmpty = messages.length === 0

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {showSidebar && <SessionSidebar />}

      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        minWidth: 0,
        background: isDark ? '#141414' : '#f5f7fa',
      }}>
        <div
          style={{
            height: 56,
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`,
            background: isDark ? '#1f1f1f' : 'white',
            flexShrink: 0,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Tooltip title={showSidebar ? '隐藏历史' : '显示历史'}>
              <Button type="text" icon={<HistoryOutlined />} onClick={() => setShowSidebar(!showSidebar)} />
            </Tooltip>
            <Text strong style={{ fontSize: 16 }}>{currentSession?.title || 'ChatBI Mini'}</Text>
            <Select size="small" value={selectedDataset} onChange={handleDatasetChange} style={{ width: 200 }} options={DATASET_OPTIONS} />
          </div>
          <Space>
            <Tooltip title="上传数据"><Button type="text" icon={<UploadOutlined />} onClick={() => setShowUploadModal(true)} /></Tooltip>
            {messages.length > 0 && (
              <Tooltip title="导出对话"><Button type="text" icon={<ExportOutlined />} onClick={() => setShowExportDialog(true)} /></Tooltip>
            )}
            <ThemeToggle />
            <Tooltip title="新建对话"><Button type="text" icon={<PlusOutlined />} onClick={() => createSession()} /></Tooltip>
            {hasSteps && (
              <Tooltip title={showStepPanel ? '隐藏执行过程' : '显示执行过程'}>
                <Button type="text" icon={showStepPanel ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />} onClick={() => setShowStepPanel(!showStepPanel)} />
              </Tooltip>
            )}
          </Space>
        </div>

        <div style={{ flex: 1, overflow: 'auto', padding: '24px 0' }}>
          {isEmpty ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', padding: '0 24px' }}>
              <div style={{ width: 72, height: 72, borderRadius: 18, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24, fontSize: 28, fontWeight: 700, color: 'white', boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)' }}>CB</div>
              <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8, color: isDark ? '#e6e6e6' : '#1a1a2e' }}>ChatBI Mini</h2>
              <p style={{ fontSize: 14, color: '#8c8c8c', marginBottom: 32 }}>智能数据分析平台 — 用自然语言探索数据</p>
              <Space wrap style={{ marginBottom: 32 }}>
                {FUNCTION_TAGS.map((tag) => (
                  <Tag key={tag.label} icon={tag.icon} style={{ padding: '4px 12px', borderRadius: 16, border: 'none', background: `${tag.color}15`, color: tag.color, fontSize: 13 }}>{tag.label}</Tag>
                ))}
              </Space>
              <div style={{ maxWidth: 640, width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12, color: '#8c8c8c' }}><BulbOutlined /><span style={{ fontSize: 13 }}>试试这些问题</span></div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  {SUGGEST_QUESTIONS.map((question) => (
                    <div key={question.value} onClick={() => handleSuggestClick(question.value)} style={{ padding: '12px 16px', borderRadius: 10, border: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`, background: isDark ? '#1f1f1f' : 'white', cursor: 'pointer', fontSize: 13, color: isDark ? '#e6e6e6' : '#595959', transition: 'all 0.2s', lineHeight: 1.5 }}>{question.label}</div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>
              {messages.map((message) => (<MessageBubble key={message.id} message={message} />))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div style={{ padding: '12px 24px 20px', background: isDark ? '#1f1f1f' : 'white', borderTop: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`, flexShrink: 0 }}>
          <div style={{ maxWidth: 800, margin: '0 auto' }}>
            {/* 智能推荐问题 */}
            <SmartSuggestions
              datasetId={selectedDataset}
              lastQuery={lastUserQuery}
              onSelect={handleSuggestClick}
              disabled={isStreaming}
            />
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
              <Input.TextArea value={inputValue} onChange={(e) => setInputValue(e.target.value)} onKeyDown={handleKeyDown} placeholder="输入数据分析问题，如：最近30天的销售趋势如何？" autoSize={{ minRows: 1, maxRows: 4 }} style={{ borderRadius: 12, padding: '10px 16px', fontSize: 14, resize: 'none' }} disabled={isStreaming} />
              <Button type="primary" icon={<SendOutlined />} onClick={handleSend} loading={isStreaming} style={{ height: 40, width: 40, borderRadius: 12, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }} />
            </div>
          </div>
        </div>
      </div>

      {hasSteps && showStepPanel && (
        <div style={{ width: 420, borderLeft: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`, background: isDark ? '#1f1f1f' : 'white', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
          <StepPanel steps={currentSteps} isLoading={isStreaming} showInSidebar />
        </div>
      )}

      <Modal title="上传数据文件" open={showUploadModal} onCancel={() => setShowUploadModal(false)} footer={null} width={600}>
        <FileUpload onUploadComplete={handleFileUploadComplete} />
      </Modal>

      {/* 导出对话弹窗 */}
      <ExportDialog
        visible={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        messages={messages}
        sessionTitle={currentSession?.title}
      />
    </div>
  )
}
