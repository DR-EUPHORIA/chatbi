/**
 * 历史会话侧边栏组件
 */

import { useState } from 'react'
import { Typography, Button, Tooltip, Input, Popconfirm, Empty } from 'antd'
import {
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import { useChatStore, type ChatSession } from '../stores/chatStore'

const { Text } = Typography

interface SessionSidebarProps {
  collapsed?: boolean
}

export default function SessionSidebar({ collapsed = false }: SessionSidebarProps) {
  const {
    sessions,
    currentSessionId,
    createSession,
    setCurrentSession,
    deleteSession,
    renameSession,
  } = useChatStore()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [searchText, setSearchText] = useState('')

  const handleCreateSession = () => {
    createSession()
  }

  const handleSelectSession = (sessionId: string) => {
    if (editingId) return
    setCurrentSession(sessionId)
  }

  const handleStartEdit = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingId(session.sessionId)
    setEditTitle(session.title)
  }

  const handleSaveEdit = (sessionId: string) => {
    if (editTitle.trim()) {
      renameSession(sessionId, editTitle.trim())
    }
    setEditingId(null)
    setEditTitle('')
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const handleDelete = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    deleteSession(sessionId)
  }

  // 过滤会话
  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchText.toLowerCase()) ||
    session.messages.some(m => m.content.toLowerCase().includes(searchText.toLowerCase()))
  )

  // 按日期分组
  const groupedSessions = groupSessionsByDate(filteredSessions)

  if (collapsed) {
    return null
  }

  return (
    <div
      style={{
        width: 280,
        height: '100%',
        background: 'white',
        borderRight: '1px solid #f0f0f0',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* 头部 */}
      <div
        style={{
          padding: '16px',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreateSession}
          block
          style={{
            height: 40,
            borderRadius: 8,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
          }}
        >
          新建对话
        </Button>

        {/* 搜索框 */}
        <Input
          placeholder="搜索对话..."
          prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ marginTop: 12, borderRadius: 8 }}
        />
      </div>

      {/* 会话列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px 12px' }}>
        {filteredSessions.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={searchText ? '没有找到匹配的对话' : '暂无对话'}
            style={{ marginTop: 60 }}
          />
        ) : (
          Object.entries(groupedSessions).map(([group, groupSessions]) => (
            <div key={group} style={{ marginBottom: 16 }}>
              <Text
                type="secondary"
                style={{ fontSize: 12, padding: '4px 8px', display: 'block' }}
              >
                {group}
              </Text>
              {groupSessions.map((session) => (
                <div
                  key={session.sessionId}
                  onClick={() => handleSelectSession(session.sessionId)}
                  style={{
                    padding: '10px 12px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    marginBottom: 4,
                    background: session.sessionId === currentSessionId ? '#667eea10' : 'transparent',
                    border: session.sessionId === currentSessionId ? '1px solid #667eea30' : '1px solid transparent',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    if (session.sessionId !== currentSessionId) {
                      e.currentTarget.style.background = '#f5f5f5'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (session.sessionId !== currentSessionId) {
                      e.currentTarget.style.background = 'transparent'
                    }
                  }}
                >
                  {editingId === session.sessionId ? (
                    <div style={{ display: 'flex', gap: 4 }}>
                      <Input
                        size="small"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onPressEnter={() => handleSaveEdit(session.sessionId)}
                        autoFocus
                        style={{ flex: 1 }}
                      />
                      <Button
                        size="small"
                        type="text"
                        icon={<CheckOutlined style={{ color: '#52c41a' }} />}
                        onClick={() => handleSaveEdit(session.sessionId)}
                      />
                      <Button
                        size="small"
                        type="text"
                        icon={<CloseOutlined />}
                        onClick={handleCancelEdit}
                      />
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <MessageOutlined style={{ color: '#8c8c8c', flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <Text
                          ellipsis
                          style={{
                            fontSize: 13,
                            color: session.sessionId === currentSessionId ? '#667eea' : '#262626',
                            fontWeight: session.sessionId === currentSessionId ? 500 : 400,
                            display: 'block',
                          }}
                        >
                          {session.title || '新对话'}
                        </Text>
                        <Text
                          type="secondary"
                          style={{ fontSize: 11 }}
                        >
                          {session.messages.length} 条消息
                        </Text>
                      </div>
                      <div
                        className="session-actions"
                        style={{
                          display: 'flex',
                          gap: 2,
                          opacity: 0,
                          transition: 'opacity 0.2s',
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.opacity = '1' }}
                        onMouseLeave={(e) => { e.currentTarget.style.opacity = '0' }}
                      >
                        <Tooltip title="重命名">
                          <Button
                            size="small"
                            type="text"
                            icon={<EditOutlined style={{ fontSize: 12 }} />}
                            onClick={(e) => handleStartEdit(session, e)}
                          />
                        </Tooltip>
                        <Popconfirm
                          title="确定删除这个对话吗？"
                          onConfirm={(e) => handleDelete(session.sessionId, e as React.MouseEvent)}
                          okText="删除"
                          cancelText="取消"
                          placement="right"
                        >
                          <Tooltip title="删除">
                            <Button
                              size="small"
                              type="text"
                              icon={<DeleteOutlined style={{ fontSize: 12, color: '#ff4d4f' }} />}
                              onClick={(e) => e.stopPropagation()}
                            />
                          </Tooltip>
                        </Popconfirm>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))
        )}
      </div>

      {/* 底部信息 */}
      <div
        style={{
          padding: '12px 16px',
          borderTop: '1px solid #f0f0f0',
          fontSize: 11,
          color: '#bfbfbf',
          textAlign: 'center',
        }}
      >
        共 {sessions.length} 个对话
      </div>
    </div>
  )
}

// 按日期分组会话
function groupSessionsByDate(sessions: ChatSession[]): Record<string, ChatSession[]> {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const yesterday = today - 24 * 60 * 60 * 1000
  const lastWeek = today - 7 * 24 * 60 * 60 * 1000

  const groups: Record<string, ChatSession[]> = {}

  sessions.forEach((session) => {
    const createdAt = session.createdAt
    let group: string

    if (createdAt >= today) {
      group = '今天'
    } else if (createdAt >= yesterday) {
      group = '昨天'
    } else if (createdAt >= lastWeek) {
      group = '最近7天'
    } else {
      group = '更早'
    }

    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(session)
  })

  return groups
}
