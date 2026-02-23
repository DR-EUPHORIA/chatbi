/**
 * 文件上传组件
 */

import { useState } from 'react'
import { Upload, Button, Modal, Typography, Progress, message, Tag, Space } from 'antd'
import {
  UploadOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileTextOutlined,
  FileImageOutlined,
  DeleteOutlined,
  CheckCircleFilled,
  LoadingOutlined,
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'

const { Text, Paragraph } = Typography

interface FileUploadProps {
  onUploadComplete?: (fileInfo: UploadedFileInfo) => void
  maxSize?: number // MB
  accept?: string
}

export interface UploadedFileInfo {
  fileId: string
  fileName: string
  fileType: string
  fileSize: number
  uploadedAt: number
  previewData?: Record<string, unknown>[]
  columns?: string[]
}

const FILE_TYPE_ICONS: Record<string, React.ReactNode> = {
  xlsx: <FileExcelOutlined style={{ color: '#52c41a', fontSize: 24 }} />,
  xls: <FileExcelOutlined style={{ color: '#52c41a', fontSize: 24 }} />,
  csv: <FileTextOutlined style={{ color: '#1890ff', fontSize: 24 }} />,
  pdf: <FilePdfOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />,
  png: <FileImageOutlined style={{ color: '#722ed1', fontSize: 24 }} />,
  jpg: <FileImageOutlined style={{ color: '#722ed1', fontSize: 24 }} />,
  jpeg: <FileImageOutlined style={{ color: '#722ed1', fontSize: 24 }} />,
}

export default function FileUpload({
  onUploadComplete,
  maxSize = 10,
  accept = '.xlsx,.xls,.csv,.pdf,.png,.jpg,.jpeg',
}: FileUploadProps) {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<UploadedFileInfo | null>(null)

  const handleUpload = async (file: File) => {
    // 检查文件大小
    if (file.size > maxSize * 1024 * 1024) {
      message.error(`文件大小不能超过 ${maxSize}MB`)
      return false
    }

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/files/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('上传失败')
      }

      const result = await response.json()

      const fileInfo: UploadedFileInfo = {
        fileId: result.file_id,
        fileName: file.name,
        fileType: file.name.split('.').pop() || '',
        fileSize: file.size,
        uploadedAt: Date.now(),
        previewData: result.preview_data,
        columns: result.columns,
      }

      setUploadedFile(fileInfo)
      onUploadComplete?.(fileInfo)
      message.success('文件上传成功')
      setPreviewVisible(true)
    } catch (error) {
      message.error('文件上传失败，请重试')
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }

    return false
  }

  const uploadProps: UploadProps = {
    accept,
    fileList,
    beforeUpload: handleUpload,
    onChange: ({ fileList }) => setFileList(fileList),
    showUploadList: false,
    maxCount: 1,
  }

  const getFileIcon = (fileType: string) => {
    return FILE_TYPE_ICONS[fileType.toLowerCase()] || <FileTextOutlined style={{ fontSize: 24 }} />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <>
      <Upload.Dragger
        {...uploadProps}
        style={{
          padding: '20px',
          borderRadius: 12,
          border: '2px dashed #d9d9d9',
          background: '#fafafa',
        }}
      >
        {uploading ? (
          <div style={{ padding: '20px 0' }}>
            <LoadingOutlined style={{ fontSize: 32, color: '#667eea' }} />
            <p style={{ marginTop: 16, color: '#8c8c8c' }}>正在上传...</p>
            <Progress percent={50} status="active" style={{ maxWidth: 200, margin: '0 auto' }} />
          </div>
        ) : uploadedFile ? (
          <div style={{ padding: '10px 0' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
              {getFileIcon(uploadedFile.fileType)}
              <div style={{ textAlign: 'left' }}>
                <Text strong style={{ display: 'block' }}>{uploadedFile.fileName}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatFileSize(uploadedFile.fileSize)}
                </Text>
              </div>
              <CheckCircleFilled style={{ color: '#52c41a', fontSize: 18 }} />
            </div>
            <Space style={{ marginTop: 12 }}>
              <Button size="small" onClick={() => setPreviewVisible(true)}>
                预览数据
              </Button>
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => {
                  e.stopPropagation()
                  setUploadedFile(null)
                  setFileList([])
                }}
              >
                移除
              </Button>
            </Space>
          </div>
        ) : (
          <div style={{ padding: '20px 0' }}>
            <p className="ant-upload-drag-icon">
              <UploadOutlined style={{ fontSize: 32, color: '#667eea' }} />
            </p>
            <p className="ant-upload-text" style={{ fontSize: 14, color: '#262626' }}>
              点击或拖拽文件到此处上传
            </p>
            <p className="ant-upload-hint" style={{ fontSize: 12, color: '#8c8c8c' }}>
              支持 Excel、CSV、PDF、图片等格式，最大 {maxSize}MB
            </p>
            <Space style={{ marginTop: 12 }}>
              <Tag color="green">Excel</Tag>
              <Tag color="blue">CSV</Tag>
              <Tag color="red">PDF</Tag>
              <Tag color="purple">图片</Tag>
            </Space>
          </div>
        )}
      </Upload.Dragger>

      {/* 数据预览弹窗 */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {uploadedFile && getFileIcon(uploadedFile.fileType)}
            <span>{uploadedFile?.fileName}</span>
          </div>
        }
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>,
          <Button
            key="analyze"
            type="primary"
            onClick={() => {
              setPreviewVisible(false)
              message.info('已选择此文件进行分析')
            }}
          >
            使用此文件分析
          </Button>,
        ]}
        width={800}
      >
        {uploadedFile?.previewData && uploadedFile.previewData.length > 0 ? (
          <div style={{ overflow: 'auto' }}>
            <Paragraph type="secondary" style={{ marginBottom: 12 }}>
              数据预览（前 5 行）
            </Paragraph>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: 13,
              }}
            >
              <thead>
                <tr>
                  {uploadedFile.columns?.map((col) => (
                    <th
                      key={col}
                      style={{
                        padding: '8px 12px',
                        background: '#fafafa',
                        border: '1px solid #f0f0f0',
                        textAlign: 'left',
                        fontWeight: 600,
                      }}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {uploadedFile.previewData.slice(0, 5).map((row, index) => (
                  <tr key={index}>
                    {uploadedFile.columns?.map((col) => (
                      <td
                        key={col}
                        style={{
                          padding: '8px 12px',
                          border: '1px solid #f0f0f0',
                        }}
                      >
                        {String(row[col] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
              共 {uploadedFile.previewData.length} 行数据
            </Text>
          </div>
        ) : (
          <Empty description="暂无预览数据" />
        )}
      </Modal>
    </>
  )
}

// 空状态组件
function Empty({ description }: { description: string }) {
  return (
    <div style={{ textAlign: 'center', padding: '40px 0', color: '#bfbfbf' }}>
      <FileTextOutlined style={{ fontSize: 48, marginBottom: 16 }} />
      <div>{description}</div>
    </div>
  )
}
