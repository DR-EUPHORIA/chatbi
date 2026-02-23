import { useState } from 'react'
import { Button, Tooltip, Typography, message } from 'antd'
import { CopyOutlined, CheckOutlined } from '@ant-design/icons'

const { Text } = Typography

interface SqlBlockProps {
  sql: string
  explanation?: string
}

// SQL 关键词高亮
function highlightSql(sql: string): React.ReactNode[] {
  const keywords = [
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
    'ON', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL',
    'GROUP', 'BY', 'ORDER', 'ASC', 'DESC', 'HAVING', 'LIMIT', 'OFFSET',
    'AS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'CASE',
    'WHEN', 'THEN', 'ELSE', 'END', 'UNION', 'ALL', 'INSERT', 'INTO',
    'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'WITH',
  ]

  const parts = sql.split(/(\b\w+\b|'[^']*'|"[^"]*"|\d+\.?\d*)/g)

  return parts.map((part, index) => {
    const upperPart = part.toUpperCase()

    if (keywords.includes(upperPart)) {
      return (
        <span key={index} style={{ color: '#c678dd', fontWeight: 600 }}>
          {part}
        </span>
      )
    }

    // 字符串
    if (/^['"]/.test(part)) {
      return (
        <span key={index} style={{ color: '#98c379' }}>
          {part}
        </span>
      )
    }

    // 数字
    if (/^\d+\.?\d*$/.test(part)) {
      return (
        <span key={index} style={{ color: '#d19a66' }}>
          {part}
        </span>
      )
    }

    // 函数名（后面跟括号的词）
    if (/^\w+$/.test(part) && index + 1 < parts.length && parts[index + 1] === '(') {
      return (
        <span key={index} style={{ color: '#61afef' }}>
          {part}
        </span>
      )
    }

    return <span key={index}>{part}</span>
  })
}

export default function SqlBlock({ sql, explanation }: SqlBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql)
      setCopied(true)
      message.success('SQL 已复制')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      message.error('复制失败')
    }
  }

  return (
    <div style={{ borderRadius: 12, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
      {/* 头部 */}
      <div
        style={{
          background: '#282c34',
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f56' }} />
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ffbd2e' }} />
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#27c93f' }} />
          <Text style={{ color: '#abb2bf', fontSize: 12, marginLeft: 8 }}>SQL</Text>
        </div>
        <Tooltip title={copied ? '已复制' : '复制 SQL'}>
          <Button
            type="text"
            size="small"
            icon={copied ? <CheckOutlined style={{ color: '#52c41a' }} /> : <CopyOutlined style={{ color: '#abb2bf' }} />}
            onClick={handleCopy}
          />
        </Tooltip>
      </div>

      {/* 代码区 */}
      <div
        className="sql-block"
        style={{
          background: '#1e1e2e',
          padding: '16px',
          overflowX: 'auto',
          fontFamily: "'Fira Code', 'Consolas', 'Monaco', monospace",
          fontSize: 13,
          lineHeight: 1.7,
          color: '#e6e6e6',
          borderRadius: 0,
        }}
      >
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {highlightSql(sql)}
        </pre>
      </div>

      {/* SQL 解释 */}
      {explanation && (
        <div
          style={{
            background: '#f6f8fa',
            padding: '10px 16px',
            fontSize: 12,
            color: '#595959',
            lineHeight: 1.6,
            borderTop: '1px solid #f0f0f0',
          }}
        >
          💡 {explanation}
        </div>
      )}
    </div>
  )
}
