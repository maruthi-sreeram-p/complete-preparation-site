import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import '@fontsource-variable/inter'
import '@fontsource-variable/jetbrains-mono'
import '@fontsource-variable/space-grotesk'
import './index.css'
import App from './App.jsx'
import { ProgressProvider } from '@/features/progress/ProgressProvider.jsx'
import { ThemeProvider } from '@/features/theme/ThemeProvider.jsx'
import { createLocalStorageRepository } from '@/lib/progress/storage.js'
import { PROGRESS_STORAGE_KEY } from '@/config.js'

// Swap this repository for a database-backed one later; nothing else changes.
const progressRepository = createLocalStorageRepository(PROGRESS_STORAGE_KEY)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <ProgressProvider repository={progressRepository}>
          <App />
        </ProgressProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
