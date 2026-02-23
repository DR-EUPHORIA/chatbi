/**
 * SSE 客户端工具 — 连接后端的流式对话接口
 */

export interface SSEEvent {
  type: string
  data: Record<string, unknown>
}

export type SSECallback = (event: SSEEvent) => void

export async function connectSSE(
  message: string,
  sessionId: string | null,
  datasetId: string | null,
  onEvent: SSECallback,
  onError: (error: Error) => void,
  onComplete: () => void,
): Promise<void> {
  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        dataset_id: datasetId,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Response body is not readable')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 解析 SSE 格式
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      let currentEvent = ''
      let currentData = ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          currentData = line.slice(6).trim()
        } else if (line === '' && currentEvent && currentData) {
          // 空行表示一个事件结束
          try {
            const parsedData = JSON.parse(currentData)
            onEvent({ type: currentEvent, data: parsedData })
          } catch {
            onEvent({ type: currentEvent, data: { raw: currentData } })
          }
          currentEvent = ''
          currentData = ''
        }
      }
    }

    onComplete()
  } catch (error) {
    onError(error instanceof Error ? error : new Error(String(error)))
  }
}
