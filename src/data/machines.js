/**
 * EXVS.2 Infinite Boost machine data.
 * img: leave empty string for now — set to the actual URL from exvsdb.com
 *      e.g. 'https://exvsdb.com/exvs2ib/images/nu_gundam.webp'
 * When img is empty or fails to load, MachineCard shows a cost-coloured gradient fallback.
 */
export const MACHINES = [
  // ══════════ 3000 COST ══════════
  // S
  { id: 'nu-gundam',              name: 'νガンダム',                    short: 'νG',   cost: 3000, tier: 'S',  img: '' },
  { id: 'strike-freedom',         name: 'ストライクフリーダムガンダム',     short: 'SF',   cost: 3000, tier: 'S',  img: '' },
  { id: 'unicorn',                name: 'ユニコーンガンダム',              short: 'UC',   cost: 3000, tier: 'S',  img: '' },
  { id: 'oo-raiser',              name: 'ダブルオーライザー',              short: '00R',  cost: 3000, tier: 'S',  img: '' },
  { id: 'mighty-sf',              name: 'マイティストライクフリーダムガンダム', short: 'MSF', cost: 3000, tier: 'S',  img: '' },
  // A+
  { id: 'hi-nu',                  name: 'Hi-νガンダム',                  short: 'HiN',  cost: 3000, tier: 'A+', img: '' },
  { id: 'sazabi',                 name: 'サザビー',                       short: 'Szb',  cost: 3000, tier: 'A+', img: '' },
  { id: 'sinanju',                name: 'シナンジュ',                     short: 'Snj',  cost: 3000, tier: 'A+', img: '' },
  { id: 'turn-a',                 name: '∀ガンダム',                      short: '∀G',   cost: 3000, tier: 'A+', img: '' },
  { id: 'wing-zero-ew',           name: 'ウイングガンダムゼロ EW版',        short: 'WZ',   cost: 3000, tier: 'A+', img: '' },
  { id: 'oo-qant',                name: 'ダブルオークアンタ',               short: '00Q',  cost: 3000, tier: 'A+', img: '' },
  { id: 'barbatos-lupus-rex',     name: 'ガンダムバルバトスルプスレクス',     short: 'BLR',  cost: 3000, tier: 'A+', img: '' },
  { id: 'zz-gundam',              name: 'ZZガンダム',                      short: 'ZZ',   cost: 3000, tier: 'A+', img: '' },
  // A
  { id: 'fazz',                   name: 'フルアーマーZZガンダム',           short: 'FAZZ', cost: 3000, tier: 'A',  img: '' },
  { id: 'epyon',                  name: 'ガンダムエピオン',                 short: 'Ep',   cost: 3000, tier: 'A',  img: '' },
  { id: 'deathscythe-hell-ew',    name: 'ガンダムデスサイズヘル EW版',       short: 'DS',   cost: 3000, tier: 'A',  img: '' },
  { id: 'heavy-arms-ew',          name: 'ガンダムヘビーアームズ改 EW版',     short: 'HA',   cost: 3000, tier: 'A',  img: '' },
  { id: 'altron-ew',              name: 'アルトロンガンダム EW版',           short: 'Alt',  cost: 3000, tier: 'A',  img: '' },
  { id: 'sandrock-ew',            name: 'ガンダムサンドロック改 EW版',        short: 'SR',   cost: 3000, tier: 'A',  img: '' },
  { id: 'seravee',                name: 'セラヴィーガンダム',               short: 'Ser',  cost: 3000, tier: 'A',  img: '' },
  // B+
  { id: 'turn-x',                 name: 'ターンX',                         short: 'TX',   cost: 3000, tier: 'B+', img: '' },
  { id: 'qubeley',                name: 'キュベレイ',                       short: 'Qub',  cost: 3000, tier: 'B+', img: '' },
  { id: 'crossbone-fullcloth',    name: 'クロスボーンガンダムX1フルクロス',   short: 'FCr',  cost: 3000, tier: 'B+', img: '' },
  // B
  { id: 'v2',                     name: 'V2ガンダム',                       short: 'V2',   cost: 3000, tier: 'B',  img: '' },
  { id: 'perfect',                name: 'パーフェクトガンダム',              short: 'PG',   cost: 3000, tier: 'B',  img: '' },
  { id: 'xi',                     name: 'ΞガンダムXi',                     short: 'Ξ',    cost: 3000, tier: 'B',  img: '' },
  // C
  { id: 'gp03',                   name: 'ガンダム試作3号機 デンドロビウム',   short: 'GP03', cost: 3000, tier: 'C',  img: '' },

  // ══════════ 2500 COST ══════════
  // S
  { id: 'destiny',                name: 'デスティニーガンダム',              short: 'Dst',  cost: 2500, tier: 'S',  img: '' },
  { id: 'freedom',                name: 'フリーダムガンダム',               short: 'Frd',  cost: 2500, tier: 'S',  img: '' },
  // A+
  { id: 'reborns',                name: 'リボーンズガンダム',               short: 'Rb',   cost: 2500, tier: 'A+', img: '' },
  { id: 'providence',             name: 'プロビデンスガンダム',              short: 'Prv',  cost: 2500, tier: 'A+', img: '' },
  { id: 'z-gundam',               name: 'Zガンダム',                        short: 'ZG',   cost: 2500, tier: 'A+', img: '' },
  { id: 'akatsuki',               name: 'アカツキガンダム',                  short: 'Akt',  cost: 2500, tier: 'A+', img: '' },
  { id: 'crossbone-x1-kai',       name: 'クロスボーンガンダムX1改',          short: 'X1改', cost: 2500, tier: 'A+', img: '' },
  // A
  { id: 'justice',                name: 'ジャスティスガンダム',              short: 'Jst',  cost: 2500, tier: 'A',  img: '' },
  { id: 'arche',                  name: 'アーチェガンダム',                  short: 'Arc',  cost: 2500, tier: 'A',  img: '' },
  { id: 'kimaris-vidar',          name: 'ガンダムキマリスヴィダール',          short: 'KV',   cost: 2500, tier: 'A',  img: '' },
  { id: 'barbatos-lupus',         name: 'ガンダムバルバトスルプス',           short: 'BL',   cost: 2500, tier: 'A',  img: '' },
  { id: 'penelope',               name: 'ペーネロペー',                      short: 'Pen',  cost: 2500, tier: 'A',  img: '' },
  // B+
  { id: 'f91',                    name: 'ガンダムF91',                       short: 'F91',  cost: 2500, tier: 'B+', img: '' },
  { id: 'crossbone-x2-kai',       name: 'クロスボーンガンダムX2改',          short: 'X2改', cost: 2500, tier: 'B+', img: '' },
  // B
  { id: 'flauros',                name: 'ガンダムフラウロス',                 short: 'Flr',  cost: 2500, tier: 'B',  img: '' },
  { id: 'gelgoog-char',           name: '高機動型ゲルググ（シャア機）',        short: 'ShrG', cost: 2500, tier: 'B',  img: '' },
  // C
  { id: 'gp02',                   name: 'ガンダム試作2号機 サイサリス',       short: 'GP02', cost: 2500, tier: 'C',  img: '' },

  // ══════════ 2000 COST ══════════
  // S
  { id: 'exia',                   name: 'ガンダムエクシア',                  short: 'Ex',   cost: 2000, tier: 'S',  img: '' },
  { id: 'strike',                 name: 'ストライクガンダム',                short: 'Str',  cost: 2000, tier: 'S',  img: '' },
  // A+
  { id: 'wing',                   name: 'ウイングガンダム',                  short: 'W',    cost: 2000, tier: 'A+', img: '' },
  { id: 'nadleeh',                name: 'ガンダムナドレ',                    short: 'Nd',   cost: 2000, tier: 'A+', img: '' },
  { id: 'virtue',                 name: 'ガンダムヴァーチェ',                short: 'Vr',   cost: 2000, tier: 'A+', img: '' },
  { id: 'arios',                  name: 'アリオスガンダム',                  short: 'Ars',  cost: 2000, tier: 'A+', img: '' },
  { id: 'cherudim',               name: 'ケルディムガンダム',                short: 'Chr',  cost: 2000, tier: 'A+', img: '' },
  // A
  { id: 'blitz',                  name: 'ブリッツガンダム',                  short: 'Blt',  cost: 2000, tier: 'A',  img: '' },
  { id: 'duel',                   name: 'デュエルガンダム',                  short: 'Dl',   cost: 2000, tier: 'A',  img: '' },
  { id: 'buster',                 name: 'バスターガンダム',                  short: 'Bus',  cost: 2000, tier: 'A',  img: '' },
  { id: 'double-x',               name: 'ガンダムダブルエックス',             short: 'DX',   cost: 2000, tier: 'A',  img: '' },
  { id: 'kimaris',                name: 'ガンダムキマリス',                   short: 'Kim',  cost: 2000, tier: 'A',  img: '' },
  { id: 'gusion-rebake',          name: 'ガンダムグシオンリベイクフルシティ', short: 'GRFC', cost: 2000, tier: 'A',  img: '' },
  // B+
  { id: 'gundam-x',               name: 'ガンダムエックス',                  short: 'GX',   cost: 2000, tier: 'B+', img: '' },
  { id: 'mk2',                    name: 'ガンダムMk-Ⅱ',                     short: 'Mk2',  cost: 2000, tier: 'B+', img: '' },
  { id: 'age1',                   name: 'ガンダムAGE-1',                     short: 'AGE1', cost: 2000, tier: 'B+', img: '' },
  // B
  { id: 'g-archer',               name: 'Gアーチャー',                       short: 'GA',   cost: 2000, tier: 'B',  img: '' },
  { id: 'gp01',                   name: 'ガンダム試作1号機フルバーニアン',    short: 'GP01', cost: 2000, tier: 'B',  img: '' },
  // C
  { id: 'rx78',                   name: 'ガンダム（RX-78-2）',               short: 'RX78', cost: 2000, tier: 'C',  img: '' },

  // ══════════ 1500 COST ══════════
  // S
  { id: 'gelgoog-m',              name: 'ゲルググM（シーマ機）',              short: 'GgM',  cost: 1500, tier: 'S',  img: '' },
  // A+
  { id: 'gouf',                   name: 'グフ',                              short: 'Gf',   cost: 1500, tier: 'A+', img: '' },
  { id: 'rick-dom',               name: 'リック・ドム',                       short: 'RD',   cost: 1500, tier: 'A+', img: '' },
  { id: 'hygog',                  name: 'ハイゴッグ',                         short: 'HyG',  cost: 1500, tier: 'A+', img: '' },
  // A
  { id: 'gelgoog',                name: 'ゲルググ',                           short: 'Gg',   cost: 1500, tier: 'A',  img: '' },
  { id: 'zgok',                   name: 'ズゴック',                           short: 'Zg',   cost: 1500, tier: 'A',  img: '' },
  { id: 'gm-sniper2',             name: 'ジム・スナイパーII',                 short: 'GSn',  cost: 1500, tier: 'A',  img: '' },
  { id: 'guncannon',              name: 'ガンキャノン',                       short: 'GC',   cost: 1500, tier: 'A',  img: '' },
  // B+
  { id: 'zaku2-kai',              name: 'ザクII改',                           short: 'ZkK',  cost: 1500, tier: 'B+', img: '' },
  { id: 'acguy',                  name: 'アッガイ',                           short: 'Agg',  cost: 1500, tier: 'B+', img: '' },
  // B
  { id: 'gm',                     name: 'ジム',                              short: 'Gm',   cost: 1500, tier: 'B',  img: '' },
  { id: 'zaku2-char',             name: 'ザクII（シャア専用）',               short: 'SZk',  cost: 1500, tier: 'B',  img: '' },
  // C
  { id: 'guntank',                name: 'ガンタンク',                         short: 'GT',   cost: 1500, tier: 'C',  img: '' },
]

export const TIERS = ['S', 'A+', 'A', 'B+', 'B', 'C']

export const TIER_META = {
  'S':  { label: 'S',  sub: '最強', cls: 's'     },
  'A+': { label: 'A+', sub: '',     cls: 'aplus'  },
  'A':  { label: 'A',  sub: '',     cls: 'a'      },
  'B+': { label: 'B+', sub: '',     cls: 'bplus'  },
  'B':  { label: 'B',  sub: '',     cls: 'b'      },
  'C':  { label: 'C',  sub: '要強化', cls: 'c'    },
}
