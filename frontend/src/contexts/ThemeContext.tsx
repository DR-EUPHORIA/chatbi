/**
 * 主题上下文 - 支持深色/浅色主题切换
 */

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { ConfigProvider, theme as antdTheme } from 'antd'

type ThemeMode = 'light' | 'dark' | 'system'

interface ThemeContextType {
  themeMode: ThemeMode
  isDark: boolean
  setThemeMode: (mode: ThemeMode) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

// 主题色配置
const THEME_COLORS = {
  primary: '#667eea',
  primaryGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
}

// 浅色主题 token
const lightThemeToken = {
  colorPrimary: THEME_COLORS.primary,
  colorBgContainer: '#ffffff',
  colorBgLayout: '#f5f7fa',
  colorText: '#262626',
  colorTextSecondary: '#8c8c8c',
  borderRadius: 8,
}

// 深色主题 token
const darkThemeToken = {
  colorPrimary: THEME_COLORS.primary,
  colorBgContainer: '#1f1f1f',
  colorBgLayout: '#141414',
  colorText: '#e6e6e6',
  colorTextSecondary: '#8c8c8c',
  borderRadius: 8,
}

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem('chatbi-theme')
    return (saved as ThemeMode) || 'light'
  })

  const [systemDark, setSystemDark] = useState(() => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  // 监听系统主题变化
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => setSystemDark(e.matches)
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

  // 计算实际是否为深色模式
  const isDark = themeMode === 'dark' || (themeMode === 'system' && systemDark)

  // 保存主题设置
  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode)
    localStorage.setItem('chatbi-theme', mode)
  }

  // 切换主题
  const toggleTheme = () => {
    setThemeMode(isDark ? 'light' : 'dark')
  }

  // 更新 body 类名
  useEffect(() => {
    document.body.classList.toggle('dark-theme', isDark)
    document.body.style.colorScheme = isDark ? 'dark' : 'light'
  }, [isDark])

  return (
    <ThemeContext.Provider value={{ themeMode, isDark, setThemeMode, toggleTheme }}>
      <ConfigProvider
        theme={{
          algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
          token: isDark ? darkThemeToken : lightThemeToken,
          components: {
            Button: {
              primaryShadow: 'none',
            },
            Card: {
              borderRadiusLG: 12,
            },
            Input: {
              borderRadius: 8,
            },
            Select: {
              borderRadius: 8,
            },
          },
        }}
      >
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

// 主题切换按钮组件
import { Button, Tooltip, Dropdown, type MenuProps } from 'antd'
import { SunOutlined, MoonOutlined, DesktopOutlined } from '@ant-design/icons'

export function ThemeToggle() {
  const { themeMode, isDark, setThemeMode } = useTheme()

  const items: MenuProps['items'] = [
    {
      key: 'light',
      icon: <SunOutlined />,
      label: '浅色模式',
      onClick: () => setThemeMode('light'),
    },
    {
      key: 'dark',
      icon: <MoonOutlined />,
      label: '深色模式',
      onClick: () => setThemeMode('dark'),
    },
    {
      key: 'system',
      icon: <DesktopOutlined />,
      label: '跟随系统',
      onClick: () => setThemeMode('system'),
    },
  ]

  const currentIcon = themeMode === 'system' 
    ? <DesktopOutlined /> 
    : isDark 
      ? <MoonOutlined /> 
      : <SunOutlined />

  return (
    <Dropdown menu={{ items, selectedKeys: [themeMode] }} placement="bottomRight">
      <Tooltip title="切换主题">
        <Button
          type="text"
          icon={currentIcon}
          style={{ color: isDark ? '#e6e6e6' : '#595959' }}
        />
      </Tooltip>
    </Dropdown>
  )
}
