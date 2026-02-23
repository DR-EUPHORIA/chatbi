import { Table, Button, Tooltip, message, Typography } from 'antd'
import { DownloadOutlined } from '@ant-design/icons'

const { Text } = Typography

interface DataTableProps {
  data: Record<string, unknown>[]
  columns?: string[]
}

export default function DataTable({ data, columns }: DataTableProps) {
  if (!data || data.length === 0) return null

  // 自动推断列
  const columnKeys = columns || Object.keys(data[0])

  const tableColumns = columnKeys.map((key) => ({
    title: key,
    dataIndex: key,
    key,
    ellipsis: true,
    render: (value: unknown) => {
      if (value === null || value === undefined) {
        return <Text type="secondary" italic>NULL</Text>
      }
      if (typeof value === 'number') {
        // 格式化数字
        return Number.isInteger(value)
          ? value.toLocaleString()
          : value.toLocaleString(undefined, { maximumFractionDigits: 2 })
      }
      return String(value)
    },
  }))

  const handleDownloadCsv = () => {
    try {
      const header = columnKeys.join(',')
      const rows = data.map((row) =>
        columnKeys.map((key) => {
          const val = row[key]
          if (val === null || val === undefined) return ''
          const strVal = String(val)
          // 如果包含逗号或引号，用引号包裹
          if (strVal.includes(',') || strVal.includes('"') || strVal.includes('\n')) {
            return `"${strVal.replace(/"/g, '""')}"`
          }
          return strVal
        }).join(',')
      )
      const csvContent = [header, ...rows].join('\n')
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `query_result_${Date.now()}.csv`
      link.click()
      URL.revokeObjectURL(url)
      message.success('CSV 已下载')
    } catch {
      message.error('下载失败')
    }
  }

  return (
    <div className="chart-card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* 表头 */}
      <div
        style={{
          padding: '10px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f5f5f5',
        }}
      >
        <Text style={{ fontSize: 13, color: '#595959' }}>
          查询结果 · {data.length} 条记录
        </Text>
        <Tooltip title="下载 CSV">
          <Button
            type="text"
            size="small"
            icon={<DownloadOutlined />}
            onClick={handleDownloadCsv}
          />
        </Tooltip>
      </div>

      {/* 表格 */}
      <Table
        dataSource={data.map((row, index) => ({ ...row, _key: index }))}
        columns={tableColumns}
        rowKey="_key"
        size="small"
        pagination={data.length > 10 ? { pageSize: 10, size: 'small' } : false}
        scroll={{ x: 'max-content' }}
        style={{ fontSize: 13 }}
      />
    </div>
  )
}
