import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { api, ApiError } from './api'

describe('api client', () => {
  it('returns parsed JSON', async () => {
    server.use(http.get('/api/ping', () => HttpResponse.json({ ok: true })))
    expect(await api.get('/ping')).toEqual({ ok: true })
  })

  it('treats 204 as no content', async () => {
    server.use(http.delete('/api/notes/1', () => new HttpResponse(null, { status: 204 })))
    expect(await api.del('/notes/1')).toBeUndefined()
  })

  it('throws an ApiError with the server problem and field errors', async () => {
    server.use(http.post('/api/notes', () =>
      HttpResponse.json({ title: 'Validation failed', detail: 'Some fields are invalid.', errors: { title: 'Required' } }, { status: 400 })))

    const error = await api.post('/notes', {}).catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(400)
    expect((error as ApiError).message).toBe('Some fields are invalid.')
    expect((error as ApiError).fieldErrors).toEqual({ title: 'Required' })
  })

  it('copes with an error that is not JSON', async () => {
    server.use(http.get('/api/boom', () => new HttpResponse('<html>bad gateway</html>', { status: 502 })))

    const error = await api.get('/boom').catch((e: unknown) => e)

    expect((error as ApiError).status).toBe(502)
    expect((error as ApiError).message).toBe('Request failed (502)')
    expect((error as ApiError).fieldErrors).toEqual({})
  })

  it('reports an unreachable server as status 0, with a friendly message', async () => {
    server.use(http.get('/api/down', () => HttpResponse.error()))

    const error = await api.get('/down').catch((e: unknown) => e)

    expect((error as ApiError).status).toBe(0)
    expect((error as ApiError).message).toMatch(/cannot reach the server/i)
  })

  it('sends JSON with the right header, and none on a GET', async () => {
    let seen: { type: string | null; body: unknown } | undefined
    server.use(
      http.post('/api/echo', async ({ request }) => {
        seen = { type: request.headers.get('content-type'), body: await request.json() }
        return HttpResponse.json({})
      }),
      http.get('/api/plain', ({ request }) => HttpResponse.json({ type: request.headers.get('content-type') })),
    )

    await api.post('/echo', { a: 1 })
    expect(seen).toEqual({ type: 'application/json', body: { a: 1 } })
    expect(await api.get('/plain')).toEqual({ type: null })
  })
})
