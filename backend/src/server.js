import { createServer } from 'node:http'
import { handleRequest } from './app.js'
import { env } from './config/env.js'

const server = createServer(handleRequest)

server.listen(env.port, () => {
  console.log(`Backend running at http://localhost:${env.port}`)
})
