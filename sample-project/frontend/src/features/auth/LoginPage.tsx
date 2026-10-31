import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import { showServerError } from '../../lib/forms'
import { meKey, useMe, type User } from './useMe'

const schema = z.object({
  email: z.email('Enter a valid email address'),
  password: z.string().min(1, 'Enter your password'),
})
type Values = z.infer<typeof schema>

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const client = useQueryClient()
  const me = useMe()
  const from = (location.state as { from?: string } | null)?.from ?? '/notes'

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })

  if (me.data) return <Navigate to={from} replace />

  async function onSubmit(values: Values) {
    try {
      const user = await api.post<User>('/auth/login', values)
      client.setQueryData(meKey, user)
      navigate(from, { replace: true })
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setError('root', { message: 'Email or password is wrong.' })
      } else {
        showServerError(e, setError)
      }
    }
  }

  return (
    <main className="auth">
      <h1>Sign in</h1>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        {errors.root && <p className="error" role="alert">{errors.root.message}</p>}

        <label htmlFor="email">Email</label>
        <input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined} {...register('email')} />
        {errors.email && <p className="error" id="email-error" role="alert">{errors.email.message}</p>}

        <label htmlFor="password">Password</label>
        <input id="password" type="password" autoComplete="current-password" aria-invalid={!!errors.password}
          aria-describedby={errors.password ? 'password-error' : undefined} {...register('password')} />
        {errors.password && <p className="error" id="password-error" role="alert">{errors.password.message}</p>}

        <button className="primary" disabled={isSubmitting}>{isSubmitting ? 'Signing in…' : 'Sign in'}</button>
      </form>
      <p>New here? <Link to="/register">Create an account</Link></p>
    </main>
  )
}
