import { listModes } from '../services/modeService.js'

export function getModes(_req, res) {
  res.json({
    ok: true,
    data: listModes(),
  })
}
