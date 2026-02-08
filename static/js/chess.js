class ChessGame {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.game = null;
    this.board = null;
    this.playerColor = 'white';
    this.gameOver = false;
  }

  async init() {
    // Load chess.js library
    if (typeof Chess === 'undefined') {
      await this.loadScript('https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js');
    }

    // Load chessboard.js library
    if (typeof Chessboard === 'undefined') {
      await this.loadScript('https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js');
      await this.loadCSS('https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css');
    }

    this.game = new Chess();
    this.renderGame();
  }

  loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  loadCSS(href) {
    return new Promise((resolve) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.onload = resolve;
      document.head.appendChild(link);
    });
  }

  renderGame() {
    this.container.innerHTML = `
            <div class="chess-container">
                <div class="flex justify-between items-center mb-4">
                    <div>
                        <h3 class="text-xl font-bold">Chess</h3>
                        <p class="text-sm text-gray-400" id="game-status">White to move</p>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="chessGame.flipBoard()" class="px-4 py-2 bg-gray-700 rounded-lg text-sm hover:bg-gray-600">
                            Flip Board
                        </button>
                        <button onclick="chessGame.newGame()" class="px-4 py-2 bg-purple-600 rounded-lg text-sm hover:bg-purple-700">
                            New Game
                        </button>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div class="lg:col-span-2">
                        <div id="chess-board" style="width: 100%; max-width: 500px; margin: 0 auto;"></div>
                    </div>
                    
                    <div class="space-y-4">
                        <div class="bg-gray-700 rounded-lg p-4">
                            <h4 class="font-bold mb-2 text-sm">Captured Pieces</h4>
                            <div class="space-y-2">
                                <div>
                                    <div class="text-xs text-gray-400">White</div>
                                    <div id="captured-white" class="text-2xl min-h-[32px]"></div>
                                </div>
                                <div>
                                    <div class="text-xs text-gray-400">Black</div>
                                    <div id="captured-black" class="text-2xl min-h-[32px]"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-gray-700 rounded-lg p-4">
                            <h4 class="font-bold mb-2 text-sm">Move History</h4>
                            <div id="move-history" class="text-sm space-y-1 max-h-64 overflow-y-auto"></div>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                .chess-container { max-width: 900px; margin: 0 auto; }
            </style>
        `;

    const config = {
      draggable: true,
      position: 'start',
      onDragStart: (source, piece) => this.onDragStart(source, piece),
      onDrop: (source, target) => this.onDrop(source, target),
      onSnapEnd: () => this.onSnapEnd(),
      pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
    };

    this.board = Chessboard('chess-board', config);
    this.updateStatus();
  }

  onDragStart(source, piece) {
    if (this.gameOver) return false;
    if (this.game.game_over()) return false;
    if ((this.game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (this.game.turn() === 'b' && piece.search(/^w/) !== -1)) {
      return false;
    }
  }

  onDrop(source, target) {
    const move = this.game.move({
      from: source,
      to: target,
      promotion: 'q'
    });

    if (move === null) return 'snapback';

    this.updateCaptured();
    this.updateMoveHistory();
    this.updateStatus();
  }

  onSnapEnd() {
    this.board.position(this.game.fen());
  }

  updateStatus() {
    const status = document.getElementById('game-status');
    if (!status) return;

    let statusText = '';
    const turn = this.game.turn() === 'w' ? 'White' : 'Black';

    if (this.game.in_checkmate()) {
      statusText = `Checkmate! ${turn === 'White' ? 'Black' : 'White'} wins!`;
      this.gameOver = true;
    } else if (this.game.in_draw()) {
      statusText = 'Draw!';
      this.gameOver = true;
    } else if (this.game.in_stalemate()) {
      statusText = 'Stalemate!';
      this.gameOver = true;
    } else if (this.game.in_threefold_repetition()) {
      statusText = 'Draw by repetition';
      this.gameOver = true;
    } else if (this.game.insufficient_material()) {
      statusText = 'Draw by insufficient material';
      this.gameOver = true;
    } else if (this.game.in_check()) {
      statusText = `${turn} in check`;
    } else {
      statusText = `${turn} to move`;
    }

    status.textContent = statusText;
  }

  updateCaptured() {
    const history = this.game.history({ verbose: true });
    const captured = { w: [], b: [] };

    history.forEach(move => {
      if (move.captured) {
        captured[move.color === 'w' ? 'b' : 'w'].push(move.captured);
      }
    });

    const pieceSymbols = {
      p: '♟', n: '♞', b: '♝', r: '♜', q: '♛', k: '♚'
    };

    const whiteEl = document.getElementById('captured-white');
    const blackEl = document.getElementById('captured-black');

    if (whiteEl) {
      whiteEl.textContent = captured.b.map(p => pieceSymbols[p]).join(' ') || '—';
    }
    if (blackEl) {
      blackEl.textContent = captured.w.map(p => pieceSymbols[p]).join(' ') || '—';
    }
  }

  updateMoveHistory() {
    const history = this.game.history({ verbose: true });
    const historyEl = document.getElementById('move-history');
    if (!historyEl) return;

    const moves = [];
    for (let i = 0; i < history.length; i += 2) {
      const moveNum = Math.floor(i / 2) + 1;
      const white = history[i].san;
      const black = history[i + 1] ? history[i + 1].san : '';
      moves.push(`<div class="text-gray-300"><span class="text-gray-500">${moveNum}.</span> ${white} ${black}</div>`);
    }

    historyEl.innerHTML = moves.join('');
    historyEl.scrollTop = historyEl.scrollHeight;
  }

  flipBoard() {
    this.board.flip();
  }

  newGame() {
    if (this.game.history().length > 0 && !confirm('Start a new game?')) {
      return;
    }

    this.game.reset();
    this.board.start();
    this.gameOver = false;

    document.getElementById('captured-white').textContent = '—';
    document.getElementById('captured-black').textContent = '—';
    document.getElementById('move-history').innerHTML = '';

    this.updateStatus();
  }
}

let chessGame;
window.initChess = function (containerId) {
  chessGame = new ChessGame(containerId);
  chessGame.init();
};