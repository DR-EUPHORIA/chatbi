import { useNavigate, useLocation } from 'react-router-dom'
import { Tooltip } from 'antd'
import {
  MessageOutlined,
  DashboardOutlined,
  AppstoreOutlined,
  SettingOutlined,
} from '@ant-design/icons'

const menuItems = [
  { key: '/', icon: <MessageOutlined />, label: '对话' },
  { key: '/dashboard', icon: <DashboardOutlined />, label: '大屏' },
  { key: '/demo', icon: <AppstoreOutlined />, label: 'Demo' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', paddingTop: 16 }}>
      {/* Logo */}
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 10,
          background: 'rgba(255,255,255,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 32,
          cursor: 'pointer',
          fontSize: 18,
          fontWeight: 700,
          color: 'white',
        }}
        onClick={() => navigate('/')}
      >
        CB
      </div>

      {/* 导航菜单 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.key
          return (
            <Tooltip key={item.key} title={item.label} placement="right">
              <div
                onClick={() => navigate(item.key)}
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  fontSize: 18,
                  color: 'white',
                  background: isActive ? 'rgba(255,255,255,0.25)' : 'transparent',
                  transition: 'background 0.2s',
                }}
              >
                {item.icon}
              </div>
            </Tooltip>
          )
        })}
      </div>

      {/* 底部设置 */}
      <div style={{ paddingBottom: 16 }}>
        <Tooltip title="设置" placement="right">
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              fontSize: 18,
              color: 'rgba(255,255,255,0.7)',
            }}
          >
            <SettingOutlined />
          </div>
        </Tooltip>
      </div>
    </div>
  )
}
