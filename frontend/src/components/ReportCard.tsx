import { useState } from 'react'
import { Card, Button, Space, Typography, Tag, Divider, Modal, message } from 'antd'
import {
  FileTextOutlined,
  DownloadOutlined,
  EyeOutlined,
  FilePptOutlined,
  FileExcelOutlined,
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography

interface ReportCardProps {
  title?: string
  summary?: string
  insights?: string[]
  reportHtml?: string
  reportMarkdown?: string
  excelPath?: string
  pptPath?: string
}

export default function ReportCard({
  title,
  summary,
  insights,
  reportHtml,
  reportMarkdown,
  excelPath,
  pptPath,
}: ReportCardProps) {
  const [previewVisible, setPreviewVisible] = useState(false)

  const handleDownload = (path: string | undefined, filename: string) => {
    if (!path) {
      message.warning('文件尚未生成')
      return
    }
    const link = document.createElement('a')
    link.href = `/exports/${path}`
    link.download = filename
    link.click()
  }

  return (
    <>
      <Card
        style={{
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          border: '1px solid #f0f0f0',
        }}
        styles={{ body: { padding: '16px 20px' } }}
      >
        {/* 报告标题 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <FileTextOutlined style={{ fontSize: 18, color: '#667eea' }} />
          <Text strong style={{ fontSize: 15 }}>
            {title || '数据分析报告'}
          </Text>
          <Tag color="purple" style={{ borderRadius: 10, fontSize: 11 }}>
            报告
          </Tag>
        </div>

        {/* 摘要 */}
        {summary && (
          <Paragraph
            style={{
              fontSize: 13,
              color: '#595959',
              lineHeight: 1.8,
              marginBottom: 12,
              background: '#fafafa',
              padding: '10px 14px',
              borderRadius: 8,
            }}
          >
            {summary}
          </Paragraph>
        )}

        {/* 关键洞察 */}
        {insights && insights.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Text strong style={{ fontSize: 13, color: '#262626' }}>
              📌 关键洞察
            </Text>
            <ul style={{ paddingLeft: 20, marginTop: 6, marginBottom: 0 }}>
              {insights.map((insight, index) => (
                <li
                  key={index}
                  style={{ fontSize: 13, color: '#595959', lineHeight: 1.8, marginBottom: 4 }}
                >
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        <Divider style={{ margin: '12px 0' }} />

        {/* 操作按钮 */}
        <Space wrap>
          {reportHtml && (
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => setPreviewVisible(true)}
              style={{ borderRadius: 6 }}
            >
              预览报告
            </Button>
          )}
          {reportHtml && (
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => {
                const blob = new Blob([reportHtml], { type: 'text/html;charset=utf-8;' })
                const url = URL.createObjectURL(blob)
                const link = document.createElement('a')
                link.href = url
                link.download = `${title || 'report'}.html`
                link.click()
                URL.revokeObjectURL(url)
              }}
              style={{ borderRadius: 6 }}
            >
              HTML
            </Button>
          )}
          {excelPath && (
            <Button
              size="small"
              icon={<FileExcelOutlined />}
              onClick={() => handleDownload(excelPath, `${title || 'report'}.xlsx`)}
              style={{ borderRadius: 6, color: '#52c41a', borderColor: '#52c41a' }}
            >
              Excel
            </Button>
          )}
          {pptPath && (
            <Button
              size="small"
              icon={<FilePptOutlined />}
              onClick={() => handleDownload(pptPath, `${title || 'report'}.pptx`)}
              style={{ borderRadius: 6, color: '#fa8c16', borderColor: '#fa8c16' }}
            >
              PPT
            </Button>
          )}
        </Space>
      </Card>

      {/* HTML 报告预览弹窗 */}
      <Modal
        title={title || '报告预览'}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={900}
        style={{ top: 20 }}
        bodyStyle={{ padding: 0, height: '80vh', overflow: 'auto' }}
      >
        {reportHtml && (
          <iframe
            srcDoc={reportHtml}
            style={{ width: '100%', height: '100%', border: 'none' }}
            title="report-preview"
          />
        )}
      </Modal>
    </>
  )
}
