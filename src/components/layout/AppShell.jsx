import { Outlet, matchPath, useLocation } from 'react-router-dom'
import Footer from './Footer.jsx'
import Header from './Header.jsx'

export default function AppShell() {
  const { pathname } = useLocation()
  // the roadmap canvas fills the screen exactly; a footer under it would add a page scrollbar
  const fullScreen = Boolean(matchPath('/r/:roadmapId/roadmap', pathname))

  return (
    <div className="flex min-h-dvh flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      {!fullScreen && <Footer />}
    </div>
  )
}
