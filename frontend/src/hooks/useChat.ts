/**
 * 对话 Hook — 封装 SSE 连接和消息管理，支持多轮对话上下文
 */

import { useCallback, useMemo } from 'react'
import { useChatStore, type ChatMessage, type StepInfo } from '../stores/chatStore'
import { connectSSE, type SSEEvent } from '../utils/sse'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function normalizeStep(
  rawStep: unknown,
  fallbackNode: string,
  sequence: number,
): StepInfo {
  const step = isRecord(rawStep) ? rawStep : {}
  const nodeValue = step.node ?? step.node_name
  const node = typeof nodeValue === 'string' && nodeValue.trim()
    ? nodeValue
    : (fallbackNode || 'unknown')

  const status = typeof step.status === 'string' && step.status.trim()
    ? step.status
    : 'pending'

  const title = typeof step.title === 'string' && step.title.trim()
    ? step.title
    : node

  const detail = typeof step.detail === 'string'
    ? step.detail
    : ''

  const data = isRecord(step.data) ? step.data : {}
  const rawId = step.id
  const id = typeof rawId === 'string' && rawId.trim()
    ? rawId
    : `${node}_${sequence}`

  return {
    id,
    node,
    status,
    title,
    detail,
    data,
    sequence,
  }
}

// 构建对话上下文，用于多轮对话
function buildConversationContext(messages: ChatMessage[], maxTurns: number = 5): string {
  // 获取最近的 N 轮对话
  const recentMessages = messages.slice(-maxTurns * 2)
  
  if (recentMessages.length === 0) return ''
  
  const contextParts: string[] = []
  
  for (const msg of recentMessages) {
    if (msg.role === 'user') {
      contextParts.push(`用户: ${msg.content}`)
    } else if (msg.role === 'assistant' && msg.content) {
      // 只取回答的前 200 字符作为上下文
      const summary = msg.content.length > 200 
        ? msg.content.slice(0, 200) + '...'
        : msg.content
      contextParts.push(`助手: ${summary}`)
    }
  }
  
  return contextParts.join('\n')
}

// 检测是否是追问类型的问题
function isFollowUpQuestion(content: string): boolean {
  const followUpPatterns = [
    /^(那|那么|所以|因此|另外|还有|再|继续)/,
    /^(上个月|上周|去年|昨天|前天)/,
    /^(按|用|换成|改成|拆分|细分)/,
    /(呢|吗|怎么样|如何|是什么)\?*$/,
    /^(为什么|什么原因|怎么回事)/,
    /^(它|这个|这些|那个|那些)/,
  ]
  
  return followUpPatterns.some(pattern => pattern.test(content.trim()))
}

export function useChat() {
  const {
    sessions,
    currentSessionId,
    isStreaming,
    createSession,
    setCurrentSession,
    getCurrentSession,
    addMessage,
    updateLastAssistantMessage,
    setIsStreaming,
  } = useChatStore()

  const currentSession = getCurrentSession()
  const messages = currentSession?.messages || []

  // 获取最后一条用户查询（用于智能推荐）
  const lastUserQuery = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        return messages[i].content
      }
    }
    return undefined
  }, [messages])

  // 获取最后一条助手回复的结果
  const lastAssistantResult = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'assistant' && !messages[i].isLoading) {
        return {
          content: messages[i].content,
          sql: messages[i].sql,
          chartConfig: messages[i].chartConfig,
        }
      }
    }
    return undefined
  }, [messages])

  const sendMessage = useCallback(async (content: string) => {
    if (isStreaming || !content.trim()) return

    // 如果没有当前会话，创建一个
    let sessionId = currentSessionId
    if (!sessionId) {
      sessionId = createSession()
    }

    const session = useChatStore.getState().sessions.find(s => s.sessionId === sessionId)
    const datasetId = session?.datasetId || 'demo_ecommerce'
    const currentMessages = session?.messages || []

    // 检测是否是追问，如果是则构建上下文
    const isFollowUp = isFollowUpQuestion(content)
    let enhancedContent = content
    
    if (isFollowUp && currentMessages.length > 0) {
      const context = buildConversationContext(currentMessages)
      if (context) {
        // 将上下文信息附加到消息中（后端可以解析）
        enhancedContent = `[对话上下文]\n${context}\n\n[当前问题]\n${content}`
      }
    }

    // 添加用户消息（显示原始内容，不显示上下文）
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}_user`,
      role: 'user',
      content,
      timestamp: Date.now(),
    }
    addMessage(userMessage)

    // 添加 assistant 占位消息
    const assistantMessage: ChatMessage = {
      id: `msg_${Date.now()}_assistant`,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      isLoading: true,
      steps: [],
    }
    addMessage(assistantMessage)

    setIsStreaming(true)

    const collectedSteps: StepInfo[] = []
    let finalState: Record<string, unknown> = {}
    let stepSequence = 0

    await connectSSE(
      content,
      sessionId,
      datasetId,
      // onEvent
      (event: SSEEvent) => {
        const eventData = event.data

        if (event.type === 'step') {
          const stepData = eventData as Record<string, unknown>
          const stateSnapshot = (stepData.state_snapshot || {}) as Record<string, unknown>
          const fallbackNode = typeof stepData.node === 'string' ? stepData.node : 'unknown'

          // 收集步骤信息
          if (stepData.steps && Array.isArray(stepData.steps)) {
            for (const rawStep of stepData.steps) {
              stepSequence += 1
              collectedSteps.push(normalizeStep(rawStep, fallbackNode, stepSequence))
            }
          }

          finalState = { ...finalState, ...stateSnapshot }

          // 实时更新 assistant 消息
          updateLastAssistantMessage({
            steps: [...collectedSteps],
            isLoading: true,
          })
        }

        if (event.type === 'done') {
          finalState = { ...finalState, ...(eventData as Record<string, unknown>) }
        }

        if (event.type === 'error') {
          updateLastAssistantMessage({
            isLoading: false,
            error: String((eventData as Record<string, unknown>).error || '未知错误'),
          })
        }
      },
      // onError
      (error: Error) => {
        updateLastAssistantMessage({
          isLoading: false,
          error: error.message,
          content: `抱歉，发生了错误：${error.message}`,
        })
        setIsStreaming(false)
      },
      // onComplete
      () => {
        // 用最终状态更新消息
        updateLastAssistantMessage({
          isLoading: false,
          content: (finalState.final_answer as string) || '',
          steps: collectedSteps,
          sql: (finalState.generated_sql as string) || undefined,
          sqlExplanation: (finalState.sql_explanation as string) || undefined,
          sqlResult: (finalState.sql_result as Record<string, unknown>[]) || undefined,
          sqlResultColumns: (finalState.sql_result_columns as string[]) || undefined,
          chartType: (finalState.chart_type as string) || undefined,
          chartConfig: (finalState.chart_config as Record<string, unknown>) || undefined,
          dashboardConfig: (finalState.dashboard_config as Record<string, unknown>) || undefined,
          reportTitle: (finalState.report_title as string) || undefined,
          reportSummary: (finalState.report_summary as string) || undefined,
          reportInsights: (finalState.report_insights as string[]) || undefined,
          reportHtml: (finalState.report_html as string) || undefined,
          reportMarkdown: (finalState.report_markdown as string) || undefined,
          excelPath: (finalState.excel_path as string) || undefined,
          pptPath: (finalState.ppt_path as string) || undefined,
          gateFeedback: (finalState.gate_feedback as string) || undefined,
          isClear: finalState.is_clear as boolean | undefined,
          hasAmbiguity: finalState.has_ambiguity as boolean | undefined,
          clarifyOptions: (finalState.clarify_options as Array<{ label: string; value: string }>) || undefined,
          error: (finalState.error as string) || undefined,
        })
        setIsStreaming(false)
      },
    )
  }, [isStreaming, currentSessionId, createSession, addMessage, updateLastAssistantMessage, setIsStreaming])

  // 重新发送最后一条消息（重试功能）
  const retryLastMessage = useCallback(() => {
    if (isStreaming || messages.length < 2) return
    
    // 找到最后一条用户消息
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        sendMessage(messages[i].content)
        break
      }
    }
  }, [isStreaming, messages, sendMessage])

  return {
    sessions,
    currentSessionId,
    currentSession,
    messages,
    isStreaming,
    sendMessage,
    createSession,
    setCurrentSession,
    // 新增
    lastUserQuery,
    lastAssistantResult,
    retryLastMessage,
  }
}
