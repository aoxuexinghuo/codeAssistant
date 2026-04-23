import { routes } from './routes/index.js'

function setCorsHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
}

function createResponse(res) {
  // 这里把原生 Node 的 response 包一层，目的是让 controller 可以用更顺手的写法，
  // 例如 status().json()、setHeader()、write()，读起来会更接近常见后端框架。
  return {
    raw: res,
    status(code) {
      res.statusCode = code
      return this
    },
    setHeader(name, value) {
      setCorsHeaders(res)
      res.setHeader(name, value)
      return this
    },
    write(chunk) {
      res.write(chunk)
      return this
    },
    end(chunk) {
      res.end(chunk)
      return this
    },
    json(payload) {
      setCorsHeaders(res)
      res.setHeader('Content-Type', 'application/json; charset=utf-8')
      res.end(JSON.stringify(payload))
    },
  }
}

async function parseJson(req) {
  let raw = ''

  for await (const chunk of req) {
    raw += chunk
  }

  if (!raw) {
    return {}
  }

  try {
    return JSON.parse(raw)
  } catch {
    return {}
  }
}

function createRequest(req) {
  // 当前项目没有引入 Express 这类框架，所以这里只保留 controller 真正需要的最小能力：
  // method、url 和 json()。这样结构简单，也方便后面自己扩展。
  return {
    method: req.method,
    url: req.url,
    async json() {
      return parseJson(req)
    },
  }
}

export async function handleRequest(req, res) {
  setCorsHeaders(res)

  if (req.method === 'OPTIONS') {
    res.statusCode = 204
    res.end()
    return
  }

  const pathname = new URL(req.url, 'http://localhost').pathname
  const route = routes.find((item) => item.method === req.method && item.path === pathname)

  if (!route) {
    createResponse(res).status(404).json({
      ok: false,
      message: '接口不存在',
    })
    return
  }

  try {
    // 所有后端请求最后都会先走到这里，再根据 method + path 分发到具体 controller。
    await route.handler(createRequest(req), createResponse(res))
  } catch (error) {
    createResponse(res).status(500).json({
      ok: false,
      message: '服务内部错误',
      detail: error instanceof Error ? error.message : 'unknown error',
    })
  }
}
