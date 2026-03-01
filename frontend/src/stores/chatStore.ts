/**
 * 对话状态管理 — Zustand Store
 */

import { create } from 'zustand'

export interface StepInfo {
  id: string
  node: string
  status: string
  title: string
  detail: string
  data: Record<string, unknown>
  sequence: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  // Agent 执行结果
  steps?: StepInfo[]
  sql?: string
  sqlExplanation?: string
  sqlResult?: Record<string, unknown>[]
  sqlResultColumns?: string[]
  chartType?: string
  chartConfig?: Record<string, unknown>
  dashboardConfig?: Record<string, unknown>
  reportTitle?: string
  reportSummary?: string
  reportInsights?: string[]
  reportHtml?: string
  reportMarkdown?: string
  excelPath?: string
  pptPath?: string
  // 门控反馈
  gateFeedback?: string
  isClear?: boolean
  // 歧义澄清
  hasAmbiguity?: boolean
  clarifyOptions?: Array<{ label: string; value: string }>
  // 状态
  isLoading?: boolean
  error?: string
}

export interface ChatSession {
  sessionId: string
  title: string
  messages: ChatMessage[]
  datasetId: string | null
  createdAt: number
}

interface ChatStore {
  // 会话管理
  sessions: ChatSession[]
  currentSessionId: string | null
  // 操作
  createSession: () => string
  setCurrentSession: (sessionId: string) => void
  getCurrentSession: () => ChatSession | undefined
  deleteSession: (sessionId: string) => void
  renameSession: (sessionId: string, title: string) => void
  clearAllSessions: () => void
  addMessage: (message: ChatMessage) => void
  updateLastAssistantMessage: (updates: Partial<ChatMessage>) => void
  setDatasetId: (datasetId: string | null) => void
  // 加载状态
  isStreaming: boolean
  setIsStreaming: (streaming: boolean) => void
  // 上传的文件
  uploadedFileId: string | null
  setUploadedFileId: (fileId: string | null) => void
}

let sessionCounter = 0

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  currentSessionId: null,
  isStreaming: false,
  uploadedFileId: null,

  createSession: () => {
    sessionCounter += 1
    const sessionId = `session_${Date.now()}_${sessionCounter}`
    const newSession: ChatSession = {
      sessionId,
      title: '新对话',
      messages: [],
      datasetId: 'demo_ecommerce',
      createdAt: Date.now(),
    }
    set((state) => ({
      sessions: [newSession, ...state.sessions],
      currentSessionId: sessionId,
    }))
    return sessionId
  },

  setCurrentSession: (sessionId) => {
    set({ currentSessionId: sessionId })
  },

  getCurrentSession: () => {
    const { sessions, currentSessionId } = get()
    return sessions.find((s) => s.sessionId === currentSessionId)
  },

  deleteSession: (sessionId) => {
    set((state) => {
      const newSessions = state.sessions.filter((s) => s.sessionId !== sessionId)
      // 如果删除的是当前会话，切换到第一个会话或清空
      const newCurrentId = state.currentSessionId === sessionId
        ? (newSessions[0]?.sessionId || null)
        : state.currentSessionId
      return { sessions: newSessions, currentSessionId: newCurrentId }
    })
  },

  renameSession: (sessionId, title) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.sessionId === sessionId ? { ...session, title } : session
      ),
    }))
  },

  clearAllSessions: () => {
    set({ sessions: [], currentSessionId: null })
  },

  addMessage: (message) => {
    set((state) => {
      const sessions = state.sessions.map((session) => {
        if (session.sessionId === state.currentSessionId) {
          const updatedMessages = [...session.messages, message]
          // 用第一条用户消息作为会话标题
          const title = message.role === 'user' && session.messages.length === 0
            ? message.content.slice(0, 30)
            : session.title
          return { ...session, messages: updatedMessages, title }
        }
        return session
      })
      return { sessions }
    })
  },

  updateLastAssistantMessage: (updates) => {
    set((state) => {
      const sessions = state.sessions.map((session) => {
        if (session.sessionId === state.currentSessionId) {
          const messages = [...session.messages]
          // 找到最后一条 assistant 消息
          for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === 'assistant') {
              messages[i] = { ...messages[i], ...updates }
              break
            }
          }
          return { ...session, messages }
        }
        return session
      })
      return { sessions }
    })
  },

  setDatasetId: (datasetId) => {
    set((state) => {
      const sessions = state.sessions.map((session) => {
        if (session.sessionId === state.currentSessionId) {
          return { ...session, datasetId }
        }
        return session
      })
      return { sessions }
    })
  },

  setIsStreaming: (streaming) => {
    set({ isStreaming: streaming })
  },

  setUploadedFileId: (fileId) => {
    set({ uploadedFileId: fileId })
  },
}))
