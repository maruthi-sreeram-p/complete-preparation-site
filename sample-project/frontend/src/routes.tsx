import { Navigate, type RouteObject } from 'react-router'
import { Layout } from './components/Layout'
import { NotFoundPage } from './components/NotFoundPage'
import { LoginPage } from './features/auth/LoginPage'
import { RegisterPage } from './features/auth/RegisterPage'
import { RequireAuth } from './features/auth/RequireAuth'
import { NotesPage } from './features/notes/NotesPage'

// the editor is only needed once someone opens a note, so the router downloads it on demand
const noteForm = () => import('./features/notes/NoteFormPage').then((m) => ({ Component: m.NoteFormPage }))

export const routes: RouteObject[] = [
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <Layout />,
        children: [
          { index: true, element: <Navigate to="/notes" replace /> },
          { path: 'notes', element: <NotesPage /> },
          { path: 'notes/new', lazy: noteForm },
          { path: 'notes/:id', lazy: noteForm },
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]
