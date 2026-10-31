import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import '@fontsource-variable/inter'
import '@fontsource-variable/jetbrains-mono'
import '@fontsource-variable/space-grotesk'
import './index.css'
import App from './App.jsx'
import { ProgressProvider } from '@/features/progress/ProgressProvider.jsx'
import { PracticeProvider } from '@/features/practice/PracticeProvider.jsx'
import { ThemeProvider } from '@/features/theme/ThemeProvider.jsx'
import { createLocalStorageRepository } from '@/lib/progress/storage.js'
import { createPracticeRepository } from '@/lib/practice/storage.js'
import { PRACTICE_STORAGE_KEY, PROGRESS_STORAGE_KEY } from '@/config.js'

// Swap this repository for a database-backed one later; nothing else changes.
const progressRepository = createLocalStorageRepository(PROGRESS_STORAGE_KEY)
const practiceRepository = createPracticeRepository(PRACTICE_STORAGE_KEY)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <ProgressProvider repository={progressRepository}>
          <PracticeProvider repository={practiceRepository}>
            <App />
          </PracticeProvider>
        </ProgressProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
