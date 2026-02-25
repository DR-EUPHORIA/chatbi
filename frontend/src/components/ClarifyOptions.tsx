/**
 * 歧义澄清选项组件
 */

import { Typography, Button, Space, Card, Tag } from 'antd'
import { QuestionCircleOutlined, CheckOutlined } from '@ant-design/icons'

const { Text, Paragraph } = Typography

interface ClarifyOption {
  label: string
  value: string
  description?: string
}

interface ClarifyOptionsProps {
  question?: string
  options: ClarifyOption[]
  onSelect: (option: ClarifyOption) => void
  disabled?: boolean
}

export default function ClarifyOptions({
  question,
  options,
  onSelect,
  disabled = false,
}: ClarifyOptionsProps) {
  if (!options || options.length === 0) {
    return null
  }

  return (
    <Card
      style={{
        borderRadius: 12,
        border: '1px solid #ffd666',
        background: '#fffbe6',
      }}
      styles={{ body: { padding: '16px 20px' } }}
    >
      {/* 标题 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <QuestionCircleOutlined style={{ color: '#faad14', fontSize: 18 }} />
        <Text strong style={{ fontSize: 14, color: '#614700' }}>
          需要澄清
        </Text>
        <Tag color="warning" style={{ borderRadius: 10, fontSize: 11 }}>
          请选择
        </Tag>
      </div>

      {/* 问题描述 */}
      {question && (
        <Paragraph
          style={{
            fontSize: 13,
            color: '#614700',
            marginBottom: 16,
            lineHeight: 1.6,
          }}
        >
          {question}
        </Paragraph>
      )}

      {/* 选项列表 */}
      <Space direction="vertical" style={{ width: '100%' }} size={8}>
        {options.map((option, index) => (
          <Button
            key={option.value}
            block
            disabled={disabled}
            onClick={() => onSelect(option)}
            style={{
              height: 'auto',
              padding: '12px 16px',
              borderRadius: 8,
              textAlign: 'left',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 12,
              border: '1px solid #f0f0f0',
              background: 'white',
            }}
          >
            <div
              style={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 12,
                fontWeight: 600,
                flexShrink: 0,
              }}
            >
              {index + 1}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Text strong style={{ display: 'block', fontSize: 13 }}>
                {option.label}
              </Text>
              {option.description && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {option.description}
                </Text>
              )}
            </div>
          </Button>
        ))}
      </Space>

      {/* 提示 */}
      <Text
        type="secondary"
        style={{
          fontSize: 11,
          display: 'block',
          marginTop: 12,
          textAlign: 'center',
        }}
      >
        点击选项继续分析，或输入更详细的问题
      </Text>
    </Card>
  )
}

// 已选择的澄清结果展示
interface ClarifyResultProps {
  selectedOption: ClarifyOption
}

export function ClarifyResult({ selectedOption }: ClarifyResultProps) {
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '6px 12px',
        background: '#f6ffed',
        border: '1px solid #b7eb8f',
        borderRadius: 8,
        fontSize: 13,
      }}
    >
      <CheckOutlined style={{ color: '#52c41a' }} />
      <Text style={{ color: '#389e0d' }}>
        已选择：{selectedOption.label}
      </Text>
    </div>
  )
}
