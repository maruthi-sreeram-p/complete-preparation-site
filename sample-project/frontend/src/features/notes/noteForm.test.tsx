import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../../test/server'
import { note, pageOf, renderApp, signedIn } from '../../test/render'

const listStub = () => http.get('/api/notes', () => HttpResponse.json(pageOf([])))

describe('creating a note', () => {
  beforeEach(() => signedIn())

  it('checks the title in the browser before sending anything', async () => {
    let calls = 0
    server.use(listStub(), http.post('/api/notes', () => { calls++; return HttpResponse.json(note(1), { status: 201 }) }))
    const { user } = renderApp('/notes/new')

    await user.type(await screen.findByLabelText('Title'), '   ')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    expect(await screen.findByText('Give the note a title')).toBeInTheDocument()
    expect(screen.getByLabelText('Title')).toHaveFocus()          // focus goes to the first problem
    expect(calls).toBe(0)
  })

  it('sends what was typed, trimmed, without a version, then returns to the list', async () => {
    let body: unknown
    server.use(
      listStub(),
      http.post('/api/notes', async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(note(5), { status: 201 })
      }),
    )
    const { user, router } = renderApp('/notes/new')

    await user.type(await screen.findByLabelText('Title'), '  Groceries ')
    await user.type(screen.getByLabelText('Text'), 'milk and eggs')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/notes'))
    expect(body).toEqual({ title: 'Groceries', body: 'milk and eggs' })
  })

  it('puts server-side validation messages next to their fields and keeps the input', async () => {
    server.use(http.post('/api/notes', () =>
      HttpResponse.json({ title: 'Validation failed', errors: { title: 'Title is too long for the server' } }, { status: 400 })))
    const { user } = renderApp('/notes/new')

    await user.type(await screen.findByLabelText('Title'), 'Something')
    await user.type(screen.getByLabelText('Text'), 'my long text')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    expect(await screen.findByText('Title is too long for the server')).toBeInTheDocument()
    expect(screen.getByLabelText('Text')).toHaveValue('my long text')
  })

  it('shows a general message when the server is unreachable', async () => {
    server.use(http.post('/api/notes', () => HttpResponse.error()))
    const { user } = renderApp('/notes/new')

    await user.type(await screen.findByLabelText('Title'), 'Something')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/cannot reach the server/i)
    expect(screen.getByLabelText('Title')).toHaveValue('Something')
  })

  it('rejects a text that is over the limit', async () => {
    const { user } = renderApp('/notes/new')
    await user.type(await screen.findByLabelText('Title'), 'Long one')
    await user.click(screen.getByLabelText('Text'))
    await user.paste('x'.repeat(5001))
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    expect(await screen.findByText('Keep the note under 5,000 characters')).toBeInTheDocument()
  })
})

describe('editing a note', () => {
  beforeEach(() => signedIn())

  it('loads the note into the form, and only enables saving after a change', async () => {
    server.use(listStub(), http.get('/api/notes/3', () => HttpResponse.json(note(3, { title: 'Existing', body: 'Old text', version: 4 }))))
    const { user } = renderApp('/notes/3')

    expect(await screen.findByLabelText('Title')).toHaveValue('Existing')
    expect(screen.getByLabelText('Text')).toHaveValue('Old text')
    expect(screen.getByRole('button', { name: 'Save note' })).toBeDisabled()

    await user.type(screen.getByLabelText('Text'), ' plus more')
    expect(screen.getByRole('button', { name: 'Save note' })).toBeEnabled()
  })

  it('sends the version it loaded, so the server can detect a clash', async () => {
    let body: unknown
    server.use(
      listStub(),
      http.get('/api/notes/3', () => HttpResponse.json(note(3, { version: 4 }))),
      http.put('/api/notes/3', async ({ request }) => { body = await request.json(); return HttpResponse.json(note(3, { version: 5 })) }),
    )
    const { user, router } = renderApp('/notes/3')

    await user.type(await screen.findByLabelText('Text'), '!')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/notes'))
    expect(body).toEqual({ title: 'Note 3', body: 'Body 3!', version: 4 })
  })

  it('explains an edit conflict, and loads the latest version on request', async () => {
    let served = note(3, { title: 'My version', version: 1 })
    server.use(
      listStub(),
      http.get('/api/notes/3', () => HttpResponse.json(served)),
      http.put('/api/notes/3', () => {
        served = note(3, { title: 'Their version', version: 2 })        // someone saved first
        return HttpResponse.json({ title: 'Edit conflict', detail: 'Someone else changed this note. Reload it to see the latest version.' }, { status: 409 })
      }),
    )
    const { user } = renderApp('/notes/3')

    await user.type(await screen.findByLabelText('Text'), ' my edit')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/someone else changed this note/i)
    await user.click(screen.getByRole('button', { name: /load the latest version/i }))

    await waitFor(() => expect(screen.getByLabelText('Title')).toHaveValue('Their version'))
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows "not found" for a note that is missing or belongs to someone else', async () => {
    server.use(http.get('/api/notes/99', () => HttpResponse.json({ title: 'Not found' }, { status: 404 })))
    renderApp('/notes/99')

    expect(await screen.findByRole('heading', { name: 'Note not found' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Back to your notes' })).toHaveAttribute('href', '/notes')
  })

  it('does not even ask the server about an id that is not a number', async () => {
    renderApp('/notes/abc')
    expect(await screen.findByRole('heading', { name: 'Note not found' })).toBeInTheDocument()
  })

  it('says when the note was deleted while it was being edited', async () => {
    server.use(
      listStub(),
      http.get('/api/notes/3', () => HttpResponse.json(note(3))),
      http.put('/api/notes/3', () => HttpResponse.json({ title: 'Not found' }, { status: 404 })),
    )
    const { user } = renderApp('/notes/3')

    await user.type(await screen.findByLabelText('Title'), ' x')
    await user.click(screen.getByRole('button', { name: 'Save note' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/deleted in the meantime/i)
  })
})
