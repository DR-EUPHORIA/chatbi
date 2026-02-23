import { Avatar, Typography, Alert } from 'antd'
import { UserOutlined, RobotOutlined } from '@ant-design/icons'
import type { ChatMessage } from '../stores/chatStore'
import { useChat } from '../hooks/useChat'
import StepPanel from './StepPanel'
import SqlBlock from './SqlBlock'
import DataTable from './DataTable'
import ChartCard from './ChartCard'
import ReportCard from './ReportCard'
import ClarifyOptions from './ClarifyOptions'
import QuickActions from './QuickActions'

const { Paragraph } = Typography

interface MessageBubbleProps {
  message: ChatMessage
}

interface ClarifyOption {
  label: string
  value: string
  description?: string
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const { sendMessage, isStreaming, retryLastMessage } = useChat()
  const isUser = message.role === 'user'

  const handleClarifySelect = (option: ClarifyOption) => {
    if (isStreaming) return
    sendMessage(option.value)
  }

  const handleRetry = () => {
    if (isStreaming) return
    retryLastMessage()
  }

  return (
    <div
      className="message-enter"
      style={{
        display: 'flex',
        gap: 12,
        marginBottom: 24,
        flexDirection: isUser ? 'row-reverse' : 'row',
      }}
    >
      {/* 头像 */}
      <Avatar
        size={36}
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{
          flexShrink: 0,
          background: isUser
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'linear-gradient(135deg, #5AD8A6 0%, #36CFC9 100%)',
        }}
      />

      {/* 消息内容 */}
      <div style={{ maxWidth: '85%', minWidth: 0 }}>
        {isUser ? (
          /* 用户消息 */
          <div
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '10px 16px',
              borderRadius: '16px 4px 16px 16px',
              fontSize: 14,
              lineHeight: 1.6,
              wordBreak: 'break-word',
            }}
          >
            {message.content}
          </div>
        ) : (
          /* Assistant 消息 */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* 加载状态 */}
            {message.isLoading && (
              <div
                style={{
                  background: 'white',
                  padding: '12px 16px',
                  borderRadius: '4px 16px 16px 16px',
                  fontSize: 14,
                  color: '#8c8c8c',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                }}
              >
                <span className="step-running">正在分析中...</span>
              </div>
            )}

            {/* 错误信息 */}
            {message.error && (
              <Alert
                type="error"
                message="执行出错"
                description={message.error}
                showIcon
                style={{ borderRadius: 12 }}
              />
            )}

            {/* 执行步骤面板 */}
            {message.steps && message.steps.length > 0 && (
              <StepPanel steps={message.steps} isLoading={message.isLoading} />
            )}

            {/* 门控反馈 */}
            {message.gateFeedback && message.isClear === false && (
              <Alert
                type="warning"
                message="需要更多信息"
                description={message.gateFeedback}
                showIcon
                style={{ borderRadius: 12 }}
              />
            )}

            {/* 歧义澄清选项 */}
            {message.hasAmbiguity && message.clarifyOptions && message.clarifyOptions.length > 0 && (
              <ClarifyOptions
                question={message.gateFeedback}
                options={message.clarifyOptions}
                onSelect={handleClarifySelect}
                disabled={isStreaming}
              />
            )}

            {/* SQL 代码块 */}
            {message.sql && (
              <SqlBlock sql={message.sql} explanation={message.sqlExplanation} />
            )}

            {/* 数据表格 */}
            {message.sqlResult && message.sqlResult.length > 0 && (
              <DataTable
                data={message.sqlResult}
                columns={message.sqlResultColumns}
              />
            )}

            {/* 图表 */}
            {message.chartConfig && (
              <ChartCard
                chartType={message.chartType || 'bar'}
                chartConfig={message.chartConfig}
              />
            )}

            {/* 报告 */}
            {(message.reportTitle || message.reportSummary) && (
              <ReportCard
                title={message.reportTitle}
                summary={message.reportSummary}
                insights={message.reportInsights}
                reportHtml={message.reportHtml}
                reportMarkdown={message.reportMarkdown}
                excelPath={message.excelPath}
                pptPath={message.pptPath}
              />
            )}

            {/* 文本回答 */}
            {message.content && !message.isLoading && (
              <div
                style={{
                  background: 'white',
                  padding: '12px 16px',
                  borderRadius: '4px 16px 16px 16px',
                  fontSize: 14,
                  lineHeight: 1.8,
                  boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                  wordBreak: 'break-word',
                }}
              >
                <Paragraph
                  style={{ marginBottom: 0, whiteSpace: 'pre-wrap' }}
                >
                  {message.content}
                </Paragraph>
              </div>
            )}

            {/* 快捷操作按钮 */}
            {!message.isLoading && (message.content || message.sql || message.chartConfig) && (
              <div style={{ marginTop: 4 }}>
                <QuickActions
                  content={message.content}
                  sql={message.sql}
                  chartConfig={message.chartConfig}
                  onRetry={handleRetry}
                  disabled={isStreaming}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
