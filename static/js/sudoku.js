class Sudoku {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.puzzle = [];
        this.solution = [];
        this.userGrid = [];
        this.selectedCell = null;
        this.difficulty = 'medium';
    }

    async init() {
        await this.loadPuzzle();
        this.render();
    }

    async loadPuzzle() {
        try {
            const response = await fetch(`/api/game/sudoku?difficulty=${this.difficulty}`);
            const data = await response.json();
            this.puzzle = data.puzzle;
            this.solution = data.solution;
            this.userGrid = this.puzzle.map(row => [...row]);
        } catch (error) {
            console.error('Failed to load puzzle:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="sudoku-container">
                <div class="sudoku-header mb-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-bold">Sudoku</h3>
                        <p class="text-sm text-gray-400">Fill in the grid with numbers 1-9</p>
                    </div>
                    <div class="flex gap-2">
                        <select id="sudoku-difficulty" class="px-3 py-1 bg-gray-700 rounded text-sm">
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                        </select>
                        <button onclick="sudokuGame.checkSolution()" class="px-4 py-1 bg-blue-600 rounded text-sm hover:bg-blue-700">Check</button>
                        <button onclick="sudokuGame.newGame()" class="px-4 py-1 bg-purple-600 rounded text-sm hover:bg-purple-700">New Game</button>
                    </div>
                </div>
                <div class="sudoku-grid" id="sudoku-grid"></div>
                <div class="number-pad mt-4 flex justify-center gap-2">
                    ${[1,2,3,4,5,6,7,8,9].map(num => `
                        <button onclick="sudokuGame.enterNumber(${num})" class="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 font-bold">${num}</button>
                    `).join('')}
                    <button onclick="sudokuGame.clearCell()" class="px-4 py-2 bg-red-600 rounded hover:bg-red-700 font-bold">Clear</button>
                </div>
            </div>
            <style>
                .sudoku-grid {
                    display: grid;
                    grid-template-columns: repeat(9, 1fr);
                    gap: 1px;
                    background: #4B5563;
                    border: 3px solid #4B5563;
                    width: fit-content;
                    margin: 0 auto;
                }
                .sudoku-cell {
                    aspect-ratio: 1;
                    width: 45px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #374151;
                    color: white;
                    font-weight: bold;
                    font-size: 20px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .sudoku-cell:hover { background: #4B5563; }
                .sudoku-cell.selected { background: #3B82F6; }
                .sudoku-cell.given { background: #1F2937; color: #9CA3AF; cursor: not-allowed; }
                .sudoku-cell.error { background: #DC2626; }
                .sudoku-cell.correct { background: #10B981; }
                
                /* 3x3 box borders */
                .sudoku-cell:nth-child(3n) { border-right: 3px solid #4B5563; }
                .sudoku-cell:nth-child(n+19):nth-child(-n+27),
                .sudoku-cell:nth-child(n+46):nth-child(-n+54) { border-bottom: 3px solid #4B5563; }
            </style>
        `;

        const gridContainer = document.getElementById('sudoku-grid');
        this.userGrid.forEach((row, i) => {
            row.forEach((num, j) => {
                const cell = document.createElement('div');
                cell.className = 'sudoku-cell';
                if (this.puzzle[i][j] !== 0) {
                    cell.classList.add('given');
                }
                cell.textContent = num !== 0 ? num : '';
                cell.dataset.row = i;
                cell.dataset.col = j;
                
                cell.addEventListener('click', () => {
                    if (this.puzzle[i][j] === 0) {
                        this.selectCell(i, j);
                    }
                });
                
                gridContainer.appendChild(cell);
            });
        });

        document.getElementById('sudoku-difficulty').value = this.difficulty;
        document.getElementById('sudoku-difficulty').addEventListener('change', (e) => {
            this.difficulty = e.target.value;
            this.newGame();
        });

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            if (this.selectedCell && e.key >= '1' && e.key <= '9') {
                this.enterNumber(parseInt(e.key));
            } else if (this.selectedCell && (e.key === 'Backspace' || e.key === 'Delete')) {
                this.clearCell();
            }
        });
    }

    selectCell(row, col) {
        document.querySelectorAll('.sudoku-cell').forEach(cell => {
            cell.classList.remove('selected');
        });
        
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        if (cell && !cell.classList.contains('given')) {
            cell.classList.add('selected');
            this.selectedCell = {row, col};
        }
    }

    enterNumber(num) {
        if (!this.selectedCell) return;
        
        const {row, col} = this.selectedCell;
        if (this.puzzle[row][col] !== 0) return; // Can't change given numbers
        
        this.userGrid[row][col] = num;
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        if (cell) {
            cell.textContent = num;
            cell.classList.remove('error', 'correct');
        }
    }

    clearCell() {
        if (!this.selectedCell) return;
        
        const {row, col} = this.selectedCell;
        if (this.puzzle[row][col] !== 0) return; // Can't clear given numbers
        
        this.userGrid[row][col] = 0;
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        if (cell) {
            cell.textContent = '';
            cell.classList.remove('error', 'correct');
        }
    }

    checkSolution() {
        let allCorrect = true;
        let hasEmpty = false;

        document.querySelectorAll('.sudoku-cell').forEach(cell => {
            cell.classList.remove('error', 'correct');
        });

        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (this.puzzle[i][j] === 0) {
                    const cell = document.querySelector(`[data-row="${i}"][data-col="${j}"]`);
                    if (this.userGrid[i][j] === 0) {
                        hasEmpty = true;
                    } else if (this.userGrid[i][j] !== this.solution[i][j]) {
                        cell.classList.add('error');
                        allCorrect = false;
                    } else {
                        cell.classList.add('correct');
                    }
                }
            }
        }

        if (hasEmpty) {
            alert('Please fill in all cells first!');
        } else if (allCorrect) {
            setTimeout(() => {
                alert('🎉 Congratulations! You solved the puzzle correctly!');
            }, 300);
        } else {
            alert('Some cells are incorrect. They are marked in red.');
        }
    }

    async newGame() {
        await this.loadPuzzle();
        this.selectedCell = null;
        this.render();
    }
}

// Initialize global instance
let sudokuGame;
window.initSudoku = function(containerId) {
    sudokuGame = new Sudoku(containerId);
    sudokuGame.init();
};
