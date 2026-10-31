import { setupServer } from 'msw/node'

/** Tests add handlers with server.use(...). Nothing is handled by default. */
export const server = setupServer()
