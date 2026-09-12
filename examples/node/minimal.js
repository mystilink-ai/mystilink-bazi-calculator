'use strict';

const path = require('path');
const bazi = require(path.join(__dirname, '../../bindings/js'));

const result = bazi.calculate({ date: '1990-05-15', hour: 12 });
console.log('ganzhi:', result.bazi_ganzhi);

const dayun = bazi.dayun({ date: '1990-05-15', gender: 'male', count: 3 });
console.log('dayun count:', dayun.dayun_list.length);

const ln = bazi.liunian({ year: 2024, dayStem: result.pillars.day.stem });
console.log('liunian:', ln.ganzhi, ln.shishen || '');
