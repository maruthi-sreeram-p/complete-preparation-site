import { Route, Routes } from 'react-router-dom'
import AppShell from '@/components/layout/AppShell.jsx'
import NotFound from '@/components/layout/NotFound.jsx'
import RoadmapScope from '@/features/roadmap/RoadmapScope.jsx'
import DashboardPage from '@/features/dashboard/DashboardPage.jsx'
import RoadmapPage from '@/features/roadmap/RoadmapPage.jsx'
import TopicPage from '@/features/topic/TopicPage.jsx'
import HomePage from '@/features/home/HomePage.jsx'
import PracticePage from '@/features/practice/PracticePage.jsx'
import CopyrightPage from '@/features/legal/CopyrightPage.jsx'
import PrivacyPage from '@/features/legal/PrivacyPage.jsx'
import TermsPage from '@/features/legal/TermsPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomePage />} />
        <Route path="r/:roadmapId" element={<RoadmapScope />}>
          <Route index element={<DashboardPage />} />
          <Route path="roadmap" element={<RoadmapPage />} />
          <Route path="topics/:topicId" element={<TopicPage />} />
        </Route>
        <Route path="practice" element={<PracticePage />} />
        <Route path="practice/:subjectId" element={<PracticePage />} />
        <Route path="privacy" element={<PrivacyPage />} />
        <Route path="terms" element={<TermsPage />} />
        <Route path="copyright" element={<CopyrightPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
