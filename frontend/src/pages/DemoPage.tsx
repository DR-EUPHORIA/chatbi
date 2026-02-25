import { useState } from 'react'
import { Card, Typography, Tag, Space, Button, Descriptions, Table, message } from 'antd'
import {
  DatabaseOutlined,
  TableOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography

// Demo 数据集信息
const DEMO_DATASET = {
  name: '电商销售数据（Demo）',
  description: '包含订单、商品、品类、用户等电商核心数据，约 10 万条模拟数据。数据库类型为 SQLite，已预置在项目中。',
  tables: [
    {
      name: 'orders',
      description: '订单表 — 核心业务表',
      rowCount: '~100,000',
      columns: [
        { name: 'order_id', type: 'INTEGER', desc: '订单ID（主键）' },
        { name: 'user_id', type: 'INTEGER', desc: '用户ID（外键）' },
        { name: 'product_id', type: 'INTEGER', desc: '商品ID（外键）' },
        { name: 'order_date', type: 'TEXT', desc: '下单日期' },
        { name: 'quantity', type: 'INTEGER', desc: '购买数量' },
        { name: 'unit_price', type: 'REAL', desc: '单价' },
        { name: 'total_amount', type: 'REAL', desc: '订单总金额' },
        { name: 'profit', type: 'REAL', desc: '利润' },
        { name: 'status', type: 'TEXT', desc: '订单状态（paid/shipped/delivered/refunded）' },
        { name: 'payment_method', type: 'TEXT', desc: '支付方式' },
        { name: 'region', type: 'TEXT', desc: '地区' },
      ],
    },
    {
      name: 'products',
      description: '商品表',
      rowCount: '20',
      columns: [
        { name: 'product_id', type: 'INTEGER', desc: '商品ID（主键）' },
        { name: 'product_name', type: 'TEXT', desc: '商品名称' },
        { name: 'category_id', type: 'INTEGER', desc: '品类ID（外键）' },
        { name: 'price', type: 'REAL', desc: '标价' },
        { name: 'cost', type: 'REAL', desc: '成本' },
        { name: 'stock', type: 'INTEGER', desc: '库存' },
      ],
    },
    {
      name: 'categories',
      description: '品类表',
      rowCount: '14',
      columns: [
        { name: 'category_id', type: 'INTEGER', desc: '品类ID（主键）' },
        { name: 'category_name', type: 'TEXT', desc: '品类名称' },
        { name: 'parent_category', type: 'TEXT', desc: '父品类' },
      ],
    },
    {
      name: 'users',
      description: '用户表',
      rowCount: '5,000',
      columns: [
        { name: 'user_id', type: 'INTEGER', desc: '用户ID（主键）' },
        { name: 'username', type: 'TEXT', desc: '用户名' },
        { name: 'gender', type: 'TEXT', desc: '性别' },
        { name: 'age', type: 'INTEGER', desc: '年龄' },
        { name: 'city', type: 'TEXT', desc: '城市' },
        { name: 'region', type: 'TEXT', desc: '地区' },
        { name: 'register_date', type: 'TEXT', desc: '注册日期' },
      ],
    },
  ],
}

export default function DemoPage() {
  const [expandedTable, setExpandedTable] = useState<string | null>('orders')
  const [initializing, setInitializing] = useState(false)

  const handleInitDb = async () => {
    setInitializing(true)
    try {
      const response = await fetch('/api/dataset/init-demo', { method: 'POST' })
      if (response.ok) {
        message.success('Demo 数据库初始化成功！')
      } else {
        message.error('初始化失败，请查看后端日志')
      }
    } catch {
      message.error('请求失败，请确认后端服务已启动')
    } finally {
      setInitializing(false)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 1000, margin: '0 auto' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 8 }}>
          <DatabaseOutlined style={{ marginRight: 8, color: '#667eea' }} />
          Demo 数据集
        </Title>
        <Paragraph type="secondary">
          ChatBI Mini 预置了一套电商模拟数据，你可以直接在对话页面中使用自然语言查询这些数据。
        </Paragraph>
      </div>

      {/* 数据集概览 */}
      <Card
        style={{ borderRadius: 12, marginBottom: 24 }}
        styles={{ body: { padding: '20px 24px' } }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <Text strong style={{ fontSize: 16 }}>{DEMO_DATASET.name}</Text>
              <Tag color="purple">Demo</Tag>
              <Tag color="blue">SQLite</Tag>
            </div>
            <Paragraph type="secondary" style={{ marginBottom: 0, maxWidth: 600 }}>
              {DEMO_DATASET.description}
            </Paragraph>
          </div>
          <Button
            type="primary"
            icon={initializing ? <ReloadOutlined spin /> : <PlayCircleOutlined />}
            onClick={handleInitDb}
            loading={initializing}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: 8,
            }}
          >
            {initializing ? '初始化中...' : '初始化数据库'}
          </Button>
        </div>
      </Card>

      {/* 表结构详情 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {DEMO_DATASET.tables.map((table) => (
          <Card
            key={table.name}
            style={{
              borderRadius: 12,
              border: expandedTable === table.name ? '1px solid #667eea' : '1px solid #f0f0f0',
              cursor: 'pointer',
            }}
            styles={{ body: { padding: 0 } }}
          >
            {/* 表头 */}
            <div
              onClick={() => setExpandedTable(expandedTable === table.name ? null : table.name)}
              style={{
                padding: '14px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: expandedTable === table.name ? '1px solid #f5f5f5' : 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <TableOutlined style={{ color: '#667eea' }} />
                <Text strong style={{ fontFamily: 'monospace' }}>{table.name}</Text>
                <Text type="secondary" style={{ fontSize: 13 }}>— {table.description}</Text>
              </div>
              <Tag style={{ borderRadius: 10 }}>~{table.rowCount} 行</Tag>
            </div>

            {/* 字段列表 */}
            {expandedTable === table.name && (
              <div style={{ padding: '0 4px 4px' }}>
                <Table
                  dataSource={table.columns}
                  rowKey="name"
                  size="small"
                  pagination={false}
                  columns={[
                    {
                      title: '字段名',
                      dataIndex: 'name',
                      key: 'name',
                      width: 160,
                      render: (name: string) => (
                        <Text code style={{ fontSize: 12 }}>{name}</Text>
                      ),
                    },
                    {
                      title: '类型',
                      dataIndex: 'type',
                      key: 'type',
                      width: 100,
                      render: (type: string) => (
                        <Tag color="blue" style={{ borderRadius: 6, fontSize: 11 }}>{type}</Tag>
                      ),
                    },
                    {
                      title: '说明',
                      dataIndex: 'desc',
                      key: 'desc',
                      render: (desc: string) => (
                        <Text type="secondary" style={{ fontSize: 13 }}>{desc}</Text>
                      ),
                    },
                  ]}
                />
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  )
}
