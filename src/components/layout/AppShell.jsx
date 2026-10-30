import { Outlet } from 'react-router-dom'
import Header from './Header.jsx'

export default function AppShell() {
  return (
    <div className="min-h-dvh">
      <Header />
      <main>
        <Outlet />
      </main>
    </div>
  )
}
