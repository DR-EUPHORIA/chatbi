import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'
import DemoPage from './pages/DemoPage'
import { ThemeProvider } from './contexts/ThemeContext'

const { Sider, Content } = Layout

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout style={{ minHeight: '100vh' }}>
          <Sider
            width={64}
            style={{
              background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
              position: 'fixed',
              left: 0,
              top: 0,
              bottom: 0,
              zIndex: 100,
            }}
          >
            <Sidebar />
          </Sider>
          <Layout style={{ marginLeft: 64 }}>
            <Content style={{ minHeight: '100vh' }}>
              <Routes>
                <Route path="/" element={<ChatPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/demo" element={<DemoPage />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
