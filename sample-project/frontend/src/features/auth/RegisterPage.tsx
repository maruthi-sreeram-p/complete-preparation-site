import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useNavigate } from 'react-router'
import { z } from 'zod'
import { api } from '../../lib/api'
import { showServerError } from '../../lib/forms'
import { meKey, useMe, type User } from './useMe'

const schema = z
  .object({
    email: z.email('Enter a valid email address'),
    password: z.string().min(8, 'Use at least 8 characters').max(72, 'Use at most 72 characters'),
    confirm: z.string(),
  })
  .refine((v) => v.password === v.confirm, { message: 'Passwords do not match', path: ['confirm'] })
type Values = z.infer<typeof schema>

export function RegisterPage() {
  const navigate = useNavigate()
  const client = useQueryClient()
  const me = useMe()

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })

  if (me.data) return <Navigate to="/notes" replace />

  async function onSubmit({ email, password }: Values) {
    try {
      const user = await api.post<User>('/auth/register', { email, password })
      client.setQueryData(meKey, user)
      navigate('/notes', { replace: true })
    } catch (e) {
      showServerError(e, setError)   // a duplicate email lands on the email field
    }
  }

  return (
    <main className="auth">
      <h1>Create an account</h1>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        {errors.root && <p className="error" role="alert">{errors.root.message}</p>}

        <label htmlFor="email">Email</label>
        <input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined} {...register('email')} />
        {errors.email && <p className="error" id="email-error" role="alert">{errors.email.message}</p>}

        <label htmlFor="password">Password</label>
        <input id="password" type="password" autoComplete="new-password" aria-invalid={!!errors.password}
          aria-describedby={errors.password ? 'password-error' : 'password-hint'} {...register('password')} />
        <p className="hint" id="password-hint">At least 8 characters.</p>
        {errors.password && <p className="error" id="password-error" role="alert">{errors.password.message}</p>}

        <label htmlFor="confirm">Confirm password</label>
        <input id="confirm" type="password" autoComplete="new-password" aria-invalid={!!errors.confirm}
          aria-describedby={errors.confirm ? 'confirm-error' : undefined} {...register('confirm')} />
        {errors.confirm && <p className="error" id="confirm-error" role="alert">{errors.confirm.message}</p>}

        <button className="primary" disabled={isSubmitting}>{isSubmitting ? 'Creating…' : 'Create account'}</button>
      </form>
      <p>Already have an account? <Link to="/login">Sign in</Link></p>
    </main>
  )
}
