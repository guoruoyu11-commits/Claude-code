import { MACHINE_SPRITES, COST_SPRITE } from '../data/sprite_manifest.js'

// 生成机体缩略图在雪碧图中的定位样式（配合 global.css 的 .sprite-cell）。
// 机体不在雪碧图（缺图/未生成）时返回 null，组件走文字降级。
export function machineSpriteStyle(machine) {
  if (!machine.img) return null
  const num = machine.img.match(/(\d+)\.png/)?.[1]
  const sheet = MACHINE_SPRITES[machine.cost]
  const cell = num && sheet?.cells[num]
  if (!cell) return null
  return {
    backgroundImage: `url(${sheet.url})`,
    '--cols': sheet.cols,
    '--rows': sheet.rows,
    '--col': cell[0],
    '--row': cell[1],
  }
}

// cost 筛选图标雪碧图定位样式，key 为 '3000' / '3000_off' 等
export function costSpriteStyle(key) {
  const cell = COST_SPRITE.cells[key]
  if (!cell) return null
  return {
    backgroundImage: `url(${COST_SPRITE.url})`,
    '--cols': COST_SPRITE.cols,
    '--rows': COST_SPRITE.rows,
    '--col': cell[0],
    '--row': cell[1],
  }
}
