const COLS = 9;
const ROWS = 9;
const W = COLS + 2; // boundary padding
const H = ROWS + 2;
const SIZE = W * H;
const MINE_COUNT = 10;
const NEIGHBORS = [-W - 1, -W, -W + 1, -1, 1, W - 1, W, W + 1];

const cells = new Array(SIZE);
const counts = new Int8Array(SIZE);
const flagged = new Uint8Array(SIZE);
const mined = new Uint8Array(SIZE);
const revealed = new Uint8Array(SIZE);

let firstClick = true;
let flaggedCount = 0;
let gameOver = false;
let revealedCount = 0;
let seconds = 0;
let timer = null;

const board = document.getElementById('board');
const messageEl = document.getElementById('message');
const mineCountEl = document.getElementById('mineCount');
const resetBtn = document.getElementById('reset');
const timerEl = document.getElementById('timer');

const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

function idx(r, c) { return r * W + c; }

function placeMines(firstIdx) {
  const forbidden = new Set([firstIdx]);
  for (const d of NEIGHBORS) forbidden.add(firstIdx + d);
  const pool = [];
  for (let r = 1; r <= ROWS; r++)
    for (let c = 1; c <= COLS; c++) {
      const i = idx(r, c);
      if (!forbidden.has(i)) pool.push(i);
    }
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  for (let k = 0; k < MINE_COUNT; k++) mined[pool[k]] = 1;
  for (let r = 1; r <= ROWS; r++)
    for (let c = 1; c <= COLS; c++) {
      const i = idx(r, c);
      if (mined[i]) continue;
      let n = 0;
      for (const d of NEIGHBORS) if (mined[i + d]) n++;
      counts[i] = n;
    }
}

// left-click: show number or mine; right-click: show/remove flag
function updateCell(i) {
  const el = cells[i];
  if (!el) return;
  el.classList.toggle('revealed', revealed[i]);
  el.classList.toggle('flagged', flagged[i]);
  if (revealed[i]) {
    el.textContent = mined[i] ? '💥' : (counts[i] ? String(counts[i]) : '');
    el.dataset.n = counts[i];
  } else {
    el.textContent = flagged[i] ? '🚩' : '';
    el.dataset.n = '';
  }
}

// false if on boundary padding
function withinBoard(i) {
  const r = Math.floor(i / W);
  const c = i % W;
  if (r < 1 || r > ROWS || c < 1 || c > COLS) {
    return false;
  } else {
    return true;
  }
}

function reveal(i) {
  if (gameOver || flagged[i] || revealed[i]) return;
  if (mined[i]) { lose(); return; }

  if (!withinBoard(i)) return;
  const newly = [i];
  revealed[i] = 1;
  revealedCount++;
  if (counts[i] === 0) {
    const stack = [i];
    while (stack.length) {
      const cur = stack.pop();
      for (const d of NEIGHBORS) {
        const j = cur + d;
        if (!withinBoard(j)) continue;
        if (revealed[j] || flagged[j] || mined[j]) continue;
        revealed[j] = 1;
        revealedCount++;
        newly.push(j);
        if (counts[j] === 0) stack.push(j);
      }
    }
  }
  for (const k of newly) updateCell(k);
  checkWin();
}

// clicking a revealed numbered cell with right number of flagged neighbors reveals unflagged neighbors
function chord(i) {
  if (gameOver || !revealed[i] || flagged[i]) return;
  const n = counts[i];
  if (n === 0) return;
  let f = 0;
  for (const d of NEIGHBORS) {
    if (flagged[i + d]) f++;
  }
  if (f !== n) return;
  for (const d of NEIGHBORS) {
    const j = i + d;
    if (flagged[j]) continue;
    reveal(j);
  }
}

function flag(i) {
  if (gameOver || revealed[i]) return;
  flagged[i] = !flagged[i];
  flaggedCount += flagged[i] ? 1 : -1;
  updateCell(i);
  updateMineCount();
}

function updateMineCount() {
  mineCountEl.textContent = 'Mines: ' + Math.max(0, MINE_COUNT - flaggedCount);
}

function lose() {
  gameOver = true;
  stopTimer();
  messageEl.textContent = '💥 Boom!';
  messageEl.classList.add('lost');
  for (let r = 1; r <= ROWS; r++)
    for (let c = 1; c <= COLS; c++) {
      const i = idx(r, c);
      if (mined[i] && !revealed[i]) {
        revealed[i] = 1;
        updateCell(i);
      }
    }
}

function checkWin() {
  if (revealedCount !== COLS * ROWS - MINE_COUNT) return;
  stopTimer();
  for (let r = 1; r <= ROWS; r++)
    for (let c = 1; c <= COLS; c++) {
      const i = idx(r, c);
      if (mined[i] && !flagged[i]) {
        flag(i)
      }
    }
  gameOver = true;
  messageEl.textContent = '🎉 You win!';
  messageEl.classList.add('won');
}

function onAction(i, action) {
  if (gameOver) return;
  if (action === 'reveal') {
    if (flagged[i]) return;
    if (firstClick) {
      placeMines(i);
      firstClick = false;
      startTimer();
    }
    if (revealed[i]) chord(i);
    else reveal(i);
  } else {
    if (revealed[i]) return;
    flag(i);
  }
}

function startTimer() {
  seconds = 0;
  timer = setInterval(() => {
    seconds++;
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    timerEl.textContent = m + ':' + s;
  }, 1000);
}

function stopTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function newGame() {
  counts.fill(0);
  revealed.fill(0);
  flagged.fill(0);
  mined.fill(0);
  firstClick = true;
  gameOver = false;
  revealedCount = 0;
  flaggedCount = 0;
  stopTimer();
  seconds = 0;
  timerEl.textContent = '0:00';
  updateMineCount();
  messageEl.textContent = '';
  messageEl.classList.remove('lost', 'won');
  for (let r = 1; r <= ROWS; r++)
    for (let c = 1; c <= COLS; c++)
      updateCell(idx(r, c));
}

// Double-tap flags; a single tap reveals (matching desktop left/right click).
// The first tap schedules a reveal; a second tap within the window cancels it
// and flags instead. This matters because flag() rejects already-revealed
// cells, so the reveal must not have happened yet when the flag runs.
function attachTouch(el, i) {
  let pending = null;   // scheduled reveal timer
  let moved = false;
  let start = null;
  el.addEventListener('touchstart', (e) => {
    // non-passive: must preventDefault() to kill the browser's double-tap zoom
    e.preventDefault();
    start = [e.touches[0].clientX, e.touches[0].clientY];
    moved = false;
  }, { passive: false });
  el.addEventListener('touchmove', (e) => {
    if (!start) return;
    const dx = e.touches[0].clientX - start[0];
    const dy = e.touches[0].clientY - start[1];
    if (dx * dx + dy * dy > 25) {
      moved = true;
      if (pending) { clearTimeout(pending); pending = null; }
    }
  }, { passive: true });
  el.addEventListener('touchend', () => {
    start = null;
    if (moved) return; // a scroll, not a tap
    if (pending) {
      // second tap: cancel the pending reveal, flag instead
      clearTimeout(pending);
      pending = null;
      onAction(i, 'flag');
      return;
    }
    // first tap: schedule a reveal; a quick follow-up cancels it and flags
    pending = setTimeout(() => { pending = null; onAction(i, 'reveal'); }, 250);
  }, { passive: true });
  el.addEventListener('touchcancel', () => { if (pending) { clearTimeout(pending); pending = null; } start = null; });
}

function buildBoard() {
  board.innerHTML = '';
  board.style.gridTemplateColumns = `repeat(${COLS}, 1fr)`;
  for (let r = 1; r <= ROWS; r++)
    for (let c = 1; c <= COLS; c++) {
      const i = idx(r, c);
      const el = document.createElement('button');
      el.className = 'cell';
      el.type = 'button';
      el.dataset.i = i;
      if (!isTouch) {
        el.addEventListener('click', () => onAction(i, 'reveal'));
        el.addEventListener('contextmenu', (e) => {
          e.preventDefault();
          onAction(i, 'flag');
        });
      } else {
        attachTouch(el, i);
      }
      cells[i] = el;
      board.appendChild(el);
    }
}

resetBtn.addEventListener('click', newGame);
document.addEventListener('keydown', (e) => {
  if (e.key === 'r' || e.key === 'R') newGame();
});

buildBoard();
newGame();