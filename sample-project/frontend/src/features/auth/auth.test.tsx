import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../../test/server'
import { asha, pageOf, renderApp, signedIn, signedOut } from '../../test/render'

describe('signing in', () => {
  it('sends a signed-out visitor to the sign-in page, and back afterwards', async () => {
    signedOut()
    server.use(
      http.post('/api/auth/login', () => HttpResponse.json(asha)),
      http.get('/api/notes', () => HttpResponse.json(pageOf([]))),
    )
    const { user, router } = renderApp('/notes?q=java')

    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/login')

    // from now on, the server knows who this is
    signedIn()
    await user.type(screen.getByLabelText('Email'), 'asha@example.com')
    await user.type(screen.getByLabelText('Password'), 'correct-horse')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(await screen.findByRole('heading', { name: 'Your notes' })).toBeInTheDocument()
    expect(router.state.location.search).toBe('?q=java')   // the page they originally asked for
  })

  it('shows field errors without calling the server', async () => {
    signedOut()
    let calls = 0
    server.use(http.post('/api/auth/login', () => { calls++; return HttpResponse.json(asha) }))
    const { user } = renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), 'not-an-email')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(await screen.findByText('Enter a valid email address')).toBeInTheDocument()
    expect(screen.getByText('Enter your password')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInvalid()
    expect(calls).toBe(0)
  })

  it('says only that the email or password is wrong', async () => {
    signedOut()
    server.use(http.post('/api/auth/login', () =>
      HttpResponse.json({ title: 'Sign-in failed', detail: 'Email or password is wrong.' }, { status: 401 })))
    const { user } = renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), 'asha@example.com')
    await user.type(screen.getByLabelText('Password'), 'wrong')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Email or password is wrong.')
    expect(screen.getByLabelText('Email')).toHaveValue('asha@example.com')   // their typing is kept
  })

  it('disables the button while signing in, so a double click cannot send twice', async () => {
    signedOut()
    let calls = 0
    server.use(http.post('/api/auth/login', async () => {
      calls++
      await new Promise((r) => setTimeout(r, 80))
      return HttpResponse.json(asha)
    }))
    const { user } = renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), 'asha@example.com')
    await user.type(screen.getByLabelText('Password'), 'correct-horse')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))
    expect(await screen.findByRole('button', { name: 'Signing in…' })).toBeDisabled()
    await waitFor(() => expect(calls).toBe(1))
  })

  it('skips the sign-in page for someone who is already signed in', async () => {
    signedIn()
    server.use(http.get('/api/notes', () => HttpResponse.json(pageOf([]))))
    const { router } = renderApp('/login')

    await waitFor(() => expect(router.state.location.pathname).toBe('/notes'))
  })
})

describe('registering', () => {
  it('checks that the passwords match before asking the server', async () => {
    signedOut()
    const { user } = renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'new@example.com')
    await user.type(screen.getByLabelText('Password'), 'long-enough-1')
    await user.type(screen.getByLabelText('Confirm password'), 'different-2')
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    expect(await screen.findByText('Passwords do not match')).toBeInTheDocument()
  })

  it('puts a duplicate-email error from the server next to the email field', async () => {
    signedOut()
    server.use(http.post('/api/auth/register', () =>
      HttpResponse.json({ title: 'Email taken', detail: 'That email is already registered.', errors: { email: 'That email is already registered' } }, { status: 409 })))
    const { user } = renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'asha@example.com')
    await user.type(screen.getByLabelText('Password'), 'long-enough-1')
    await user.type(screen.getByLabelText('Confirm password'), 'long-enough-1')
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    expect(await screen.findByText('That email is already registered')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveAccessibleDescription('That email is already registered')
  })

  it('sends the email and password, but never the confirmation', async () => {
    signedOut()
    let body: unknown
    server.use(
      http.post('/api/auth/register', async ({ request }) => { body = await request.json(); return HttpResponse.json(asha, { status: 201 }) }),
      http.get('/api/notes', () => HttpResponse.json(pageOf([]))),
    )
    const { user, router } = renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'new@example.com')
    await user.type(screen.getByLabelText('Password'), 'long-enough-1')
    await user.type(screen.getByLabelText('Confirm password'), 'long-enough-1')
    signedIn()
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/notes'))
    expect(body).toEqual({ email: 'new@example.com', password: 'long-enough-1' })
  })
})

describe('session handling', () => {
  it('signs out: calls the server, clears cached data and shows the sign-in page', async () => {
    signedIn()
    let loggedOut = false
    server.use(
      http.get('/api/notes', () => HttpResponse.json(pageOf([]))),
      http.post('/api/auth/logout', () => { loggedOut = true; return new HttpResponse(null, { status: 204 }) }),
    )
    const { user, client } = renderApp('/notes')

    await user.click(await screen.findByRole('button', { name: 'Sign out' }))

    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(loggedOut).toBe(true)
    expect(client.getQueryCache().findAll({ queryKey: ['notes'] })).toHaveLength(0)
  })

  it('sends the user to sign in when the token expires while the page is open', async () => {
    signedIn()
    server.use(http.get('/api/notes', () => HttpResponse.json({ title: 'Unauthorized' }, { status: 401 })))
    const { router } = renderApp('/notes')

    await waitFor(() => expect(router.state.location.pathname).toBe('/login'))
  })

  it('offers a retry when the server cannot be reached at all', async () => {
    server.use(http.get('/api/me', () => HttpResponse.error()))
    renderApp('/notes')

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not reach the server/i)
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
  })
})
