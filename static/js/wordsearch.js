class WordSearch {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.grid = [];
        this.words = [];
        this.foundWords = new Set();
        this.selectedCells = [];
        this.isSelecting = false;
        this.theme = 'general';
        this.size = 12;
    }

    async init() {
        await this.loadPuzzle();
        this.render();
    }

    async loadPuzzle() {
        try {
            const response = await fetch(`/api/game/wordsearch?theme=${this.theme}&size=${this.size}`);
            const data = await response.json();
            this.grid = data.grid;
            this.words = data.words;
            this.foundWords = new Set();
        } catch (error) {
            console.error('Failed to load puzzle:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="word-search-container">
                <div class="word-search-header mb-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-bold">Find the Words</h3>
                        <p class="text-sm text-gray-400">${this.foundWords.size} / ${this.words.length} found</p>
                    </div>
                    <div class="flex gap-2">
                        <select id="ws-theme" class="px-3 py-1 bg-gray-700 rounded text-sm">
                            <option value="general">General</option>
                            <option value="animals">Animals</option>
                            <option value="food">Food & Drinks</option>
                            <option value="travel">Travel</option>
                            <option value="tech">Technology</option>
                            <option value="nature">Nature</option>
                            <option value="music">Music</option>
                            <option value="sports">Sports</option>
                            <option value="movies">Movies</option>
                            <option value="space">Space</option>
                            <option value="christmas">Christmas</option>
                        </select>
                        <button onclick="wordSearchGame.newGame()" class="px-4 py-1 bg-purple-600 rounded text-sm hover:bg-purple-700">New Game</button>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div class="word-search-grid" id="ws-grid"></div>
                    <div class="word-list">
                        <h4 class="font-bold mb-2 text-sm">Words to Find:</h4>
                        <div class="space-y-1">
                            ${this.words.map(word => `
                                <div class="word-item ${this.foundWords.has(word) ? 'found' : ''}" data-word="${word}">
                                    ${this.foundWords.has(word) ? '✓' : '•'} ${word}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
            <style>
                .word-search-grid {
                    display: grid;
                    grid-template-columns: repeat(${this.size}, 1fr);
                    gap: 2px;
                    user-select: none;
                }
                .ws-cell {
                    aspect-ratio: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #374151;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    cursor: pointer;
                    border-radius: 4px;
                    transition: all 0.2s;
                }
                .ws-cell:hover { background: #4B5563; }
                .ws-cell.selected { background: #3B82F6; }
                .ws-cell.found { background: #10B981; color: white; }
                .word-item { padding: 4px 8px; font-size: 14px; border-radius: 4px; }
                .word-item.found { color: #10B981; text-decoration: line-through; }
            </style>
        `;

        const gridContainer = document.getElementById('ws-grid');
        this.grid.forEach((row, i) => {
            row.forEach((letter, j) => {
                const cell = document.createElement('div');
                cell.className = 'ws-cell';
                cell.textContent = letter;
                cell.dataset.row = i;
                cell.dataset.col = j;

                cell.addEventListener('mousedown', () => this.startSelection(i, j));
                cell.addEventListener('mouseenter', () => this.continueSelection(i, j));
                cell.addEventListener('mouseup', () => this.endSelection());

                gridContainer.appendChild(cell);
            });
        });

        document.getElementById('ws-theme').value = this.theme;
        document.getElementById('ws-theme').addEventListener('change', (e) => {
            this.theme = e.target.value;
            this.newGame();
        });
    }

    startSelection(row, col) {
        this.isSelecting = true;
        this.selectedCells = [{ row, col }];
        this.highlightSelection();
    }

    continueSelection(row, col) {
        if (!this.isSelecting) return;

        const last = this.selectedCells[this.selectedCells.length - 1];
        if (last.row === row && last.col === col) return;

        // Only allow straight lines
        if (this.selectedCells.length === 1) {
            this.selectedCells.push({ row, col });
        } else {
            const first = this.selectedCells[0];
            const dx = Math.sign(row - first.row);
            const dy = Math.sign(col - first.col);

            this.selectedCells = [{ row: first.row, col: first.col }];
            let r = first.row, c = first.col;

            while (r !== row || c !== col) {
                r += dx;
                c += dy;
                if (r < 0 || r >= this.size || c < 0 || c >= this.size) break;
                this.selectedCells.push({ row: r, col: c });
            }
        }

        this.highlightSelection();
    }

    endSelection() {
        if (!this.isSelecting) return;
        this.isSelecting = false;

        const word = this.selectedCells.map(({ row, col }) => this.grid[row][col]).join('');
        const reverseWord = word.split('').reverse().join('');

        if (this.words.includes(word) && !this.foundWords.has(word)) {
            this.foundWords.add(word);
            this.markAsFound();
            this.checkWin();
        } else if (this.words.includes(reverseWord) && !this.foundWords.has(reverseWord)) {
            this.foundWords.add(reverseWord);
            this.markAsFound();
            this.checkWin();
        } else {
            this.clearSelection();
        }
    }

    highlightSelection() {
        document.querySelectorAll('.ws-cell').forEach(cell => {
            cell.classList.remove('selected');
        });

        this.selectedCells.forEach(({ row, col }) => {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (cell) cell.classList.add('selected');
        });
    }

    markAsFound() {
        this.selectedCells.forEach(({ row, col }) => {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (cell) {
                cell.classList.remove('selected');
                cell.classList.add('found');
            }
        });
        this.render();
    }

    clearSelection() {
        document.querySelectorAll('.ws-cell.selected').forEach(cell => {
            cell.classList.remove('selected');
        });
        this.selectedCells = [];
    }

    checkWin() {
        if (this.foundWords.size === this.words.length) {
            setTimeout(() => {
                alert('🎉 Congratulations! You found all the words!');
            }, 300);
        }
    }

    async newGame() {
        await this.loadPuzzle();
        this.render();
    }
}

// Initialize global instance
let wordSearchGame;
window.initWordSearch = function (containerId) {
    wordSearchGame = new WordSearch(containerId);
    wordSearchGame.init();
};
