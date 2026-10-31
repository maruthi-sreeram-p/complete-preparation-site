import { screen, waitFor, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../../test/server'
import { note, pageOf, renderApp, signedIn } from '../../test/render'

describe('notes list', () => {
  beforeEach(() => signedIn())

  it('shows loading, then the notes, newest first as the server sent them', async () => {
    server.use(http.get('/api/notes', async () => {
      await new Promise((r) => setTimeout(r, 30))
      return HttpResponse.json(pageOf([note(2, { title: 'Second' }), note(1, { title: 'First' })]))
    }))
    renderApp('/notes')

    expect(await screen.findByText('Loading notes…')).toBeInTheDocument()
    const items = await screen.findAllByRole('listitem')
    expect(items.map((li) => within(li).getByRole('link').textContent)).toEqual(['Second', 'First'])
    expect(screen.queryByText('Loading notes…')).not.toBeInTheDocument()
  })

  it('invites you to create the first note when there are none', async () => {
    server.use(http.get('/api/notes', () => HttpResponse.json(pageOf([]))))
    renderApp('/notes')

    expect(await screen.findByText(/no notes yet/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'New note' })).toHaveAttribute('href', '/notes/new')
  })

  it('shows an error with a working retry', async () => {
    let calls = 0
    server.use(http.get('/api/notes', () => {
      calls++
      return calls === 1 ? new HttpResponse(null, { status: 500 }) : HttpResponse.json(pageOf([note(1)]))
    }))
    const { user } = renderApp('/notes')

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not load your notes/i)
    await user.click(screen.getByRole('button', { name: 'Try again' }))

    expect(await screen.findByRole('link', { name: 'Note 1' })).toBeInTheDocument()
  })

  it('searches after typing pauses, and keeps the search in the URL', async () => {
    const requested: string[] = []
    server.use(http.get('/api/notes', ({ request }) => {
      const q = new URL(request.url).searchParams.get('q') ?? ''
      requested.push(q)
      return HttpResponse.json(q ? pageOf([note(7, { title: 'Java notes' })]) : pageOf([note(1), note(2)]))
    }))
    const { user, router } = renderApp('/notes')
    await screen.findByRole('link', { name: 'Note 1' })

    await user.type(screen.getByLabelText('Search notes'), 'java')

    expect(await screen.findByRole('link', { name: 'Java notes' })).toBeInTheDocument()
    expect(router.state.location.search).toBe('?q=java')
    // one request for the empty search, one for "java": nothing for "j", "ja" or "jav"
    expect(requested).toEqual(['', 'java'])
  })

  it('opens straight onto a shared search link', async () => {
    server.use(http.get('/api/notes', ({ request }) => {
      const q = new URL(request.url).searchParams.get('q')
      return HttpResponse.json(pageOf([note(7, { title: `Results for ${q}` })]))
    }))
    renderApp('/notes?q=spring')

    expect(await screen.findByRole('link', { name: 'Results for spring' })).toBeInTheDocument()
    expect(screen.getByLabelText('Search notes')).toHaveValue('spring')
  })

  it('says when a search finds nothing', async () => {
    server.use(http.get('/api/notes', () => HttpResponse.json(pageOf([]))))
    renderApp('/notes?q=zzz')

    expect(await screen.findByText(/no notes match/i)).toHaveTextContent('zzz')
  })

  it('pages forward and back, and ignores a nonsense page in the URL', async () => {
    const pages: number[] = []
    server.use(http.get('/api/notes', ({ request }) => {
      const page = Number(new URL(request.url).searchParams.get('page'))
      pages.push(page)
      return HttpResponse.json(pageOf([note(page + 1, { title: `On page ${page + 1}` })], 3, page))
    }))
    const { user, router } = renderApp('/notes?page=abc')

    expect(await screen.findByText('On page 1')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Previous' })).toBeDisabled()

    await user.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByText('On page 2')).toBeInTheDocument()
    expect(router.state.location.search).toBe('?page=1')
    expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByText('On page 3')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled()

    await user.click(screen.getByRole('button', { name: 'Previous' }))
    expect(await screen.findByText('On page 2')).toBeInTheDocument()
    expect(pages[0]).toBe(0)
  })

  it('hides the pager when everything fits on one page', async () => {
    server.use(http.get('/api/notes', () => HttpResponse.json(pageOf([note(1)], 1))))
    renderApp('/notes')

    await screen.findByRole('link', { name: 'Note 1' })
    expect(screen.queryByRole('navigation', { name: 'Pagination' })).not.toBeInTheDocument()
  })
})

describe('deleting a note', () => {
  beforeEach(() => signedIn())

  it('asks first, and only deletes after confirmation', async () => {
    let listed = [note(1, { title: 'Keep me' }), note(2, { title: 'Remove me' })]
    const deleted: string[] = []
    server.use(
      http.get('/api/notes', () => HttpResponse.json(pageOf(listed))),
      http.delete('/api/notes/:id', ({ params }) => {
        deleted.push(String(params.id))
        listed = listed.filter((n) => String(n.id) !== params.id)
        return new HttpResponse(null, { status: 204 })
      }),
    )
    const { user } = renderApp('/notes')

    await user.click(await screen.findByRole('button', { name: 'Delete Remove me' }))
    expect(deleted).toEqual([])                                   // nothing yet: this was only the first click
    await user.click(screen.getByRole('button', { name: 'Keep it' }))
    expect(screen.getByRole('button', { name: 'Delete Remove me' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Delete Remove me' }))
    await user.click(screen.getByRole('button', { name: 'Yes, delete' }))

    await waitFor(() => expect(screen.queryByRole('link', { name: 'Remove me' })).not.toBeInTheDocument())
    expect(deleted).toEqual(['2'])
    expect(screen.getByRole('link', { name: 'Keep me' })).toBeInTheDocument()
  })

  it('says so when the delete fails, and leaves the note in the list', async () => {
    server.use(
      http.get('/api/notes', () => HttpResponse.json(pageOf([note(1, { title: 'Stubborn' })]))),
      http.delete('/api/notes/1', () => new HttpResponse(null, { status: 500 })),
    )
    const { user } = renderApp('/notes')

    await user.click(await screen.findByRole('button', { name: 'Delete Stubborn' }))
    await user.click(screen.getByRole('button', { name: 'Yes, delete' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not delete/i)
    expect(screen.getByRole('link', { name: 'Stubborn' })).toBeInTheDocument()
  })
})
