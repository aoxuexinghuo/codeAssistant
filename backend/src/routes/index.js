import { createReply, createReplyStream } from '../controllers/assistantController.js'
import { createHistory, getHistory, removeHistory } from '../controllers/historyController.js'
import { getModes } from '../controllers/modeController.js'

export const routes = [
  {
    method: 'GET',
    path: '/api/health',
    handler: (_req, res) =>
      res.json({
        ok: true,
        data: {
          service: 'programming-assistant-backend',
        },
      }),
  },
  {
    method: 'GET',
    path: '/api/modes',
    handler: getModes,
  },
  {
    method: 'POST',
    path: '/api/assistant/reply',
    handler: createReply,
  },
  {
    method: 'POST',
    path: '/api/assistant/reply-stream',
    handler: createReplyStream,
  },
  {
    method: 'GET',
    path: '/api/history',
    handler: getHistory,
  },
  {
    method: 'POST',
    path: '/api/history',
    handler: createHistory,
  },
  {
    method: 'DELETE',
    path: '/api/history',
    handler: removeHistory,
  },
]
