class TriviaGame {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.questions = [];
    this.currentQuestion = 0;
    this.score = 0;
    this.answers = [];
    this.timeLeft = 20;
    this.timer = null;
    this.category = '';
    this.difficulty = '';
  }

  async init() {
    this.showSettings();
  }

  showSettings() {
    this.container.innerHTML = `
            <div class="trivia-settings">
                <h3 class="text-xl font-bold mb-4">Trivia Quiz Settings</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium mb-2">Category</label>
                        <select id="trivia-category" class="w-full px-4 py-2 bg-gray-700 rounded-lg">
                            <option value="">Any Category</option>
                            <option value="9">General Knowledge</option>
                            <option value="11">Film</option>
                            <option value="12">Music</option>
                            <option value="17">Science & Nature</option>
                            <option value="18">Computers</option>
                            <option value="21">Sports</option>
                            <option value="22">Geography</option>
                            <option value="23">History</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Difficulty</label>
                        <select id="trivia-difficulty" class="w-full px-4 py-2 bg-gray-700 rounded-lg">
                            <option value="">Any Difficulty</option>
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Number of Questions</label>
                        <select id="trivia-amount" class="w-full px-4 py-2 bg-gray-700 rounded-lg">
                            <option value="5">5 Questions</option>
                            <option value="10" selected>10 Questions</option>
                            <option value="15">15 Questions</option>
                        </select>
                    </div>
                    <button onclick="triviaGame.startGame()" class="w-full px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-bold text-lg">
                        Start Quiz
                    </button>
                </div>
            </div>
            <style>
                .trivia-settings { max-width: 500px; margin: 0 auto; }
            </style>
        `;
  }

  async startGame() {
    const category = document.getElementById('trivia-category').value;
    const difficulty = document.getElementById('trivia-difficulty').value;
    const amount = document.getElementById('trivia-amount').value;

    this.category = category;
    this.difficulty = difficulty;
    this.currentQuestion = 0;
    this.score = 0;
    this.answers = [];

    this.container.innerHTML = '<div class="text-center py-12"><div class="text-4xl mb-4">🎯</div><div class="text-xl">Loading questions...</div></div>';

    try {
      const response = await fetch(`/api/game/trivia?amount=${amount}&category=${category}&difficulty=${difficulty}`);
      const data = await response.json();

      if (data.questions && data.questions.length > 0) {
        this.questions = data.questions;
        this.showQuestion();
      } else {
        this.container.innerHTML = '<div class="text-center py-12"><div class="text-xl text-red-400">Failed to load questions. Please try again.</div><button onclick="triviaGame.showSettings()" class="mt-4 px-6 py-2 bg-blue-600 rounded-lg">Back</button></div>';
      }
    } catch (error) {
      console.error('Failed to load trivia:', error);
      this.container.innerHTML = '<div class="text-center py-12"><div class="text-xl text-red-400">Error loading questions.</div><button onclick="triviaGame.showSettings()" class="mt-4 px-6 py-2 bg-blue-600 rounded-lg">Back</button></div>';
    }
  }

  showQuestion() {
    if (this.currentQuestion >= this.questions.length) {
      this.showResults();
      return;
    }

    const q = this.questions[this.currentQuestion];
    const allAnswers = [...q.incorrect_answers, q.correct_answer].sort(() => Math.random() - 0.5);

    this.timeLeft = 20;
    this.startTimer();

    this.container.innerHTML = `
            <div class="trivia-question">
                <div class="flex justify-between items-center mb-6">
                    <div class="text-sm">
                        <span class="text-gray-400">Question ${this.currentQuestion + 1}/${this.questions.length}</span>
                        <span class="ml-4 text-blue-400">Score: ${this.score}</span>
                    </div>
                    <div class="text-sm">
                        <span class="px-3 py-1 rounded-full text-xs font-bold ${q.difficulty === 'easy' ? 'bg-green-600' :
        q.difficulty === 'medium' ? 'bg-yellow-600' : 'bg-red-600'
      }">${q.difficulty.toUpperCase()}</span>
                    </div>
                </div>
                
                <div class="mb-2 text-xs text-gray-400">${q.category}</div>
                <div class="mb-6 text-lg font-medium">${q.question}</div>
                
                <div class="mb-6">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-gray-400">Time Left</span>
                        <span class="text-sm font-bold" id="timer">${this.timeLeft}s</span>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div id="timer-bar" class="bg-blue-600 h-2 rounded-full transition-all duration-1000" style="width: 100%"></div>
                    </div>
                </div>

                <div class="space-y-3" id="answers">
                    ${allAnswers.map((answer, i) => `
                        <button 
                            onclick="triviaGame.selectAnswer('${answer.replace(/'/g, "\\'")}', '${q.correct_answer.replace(/'/g, "\\'")}')"
                            class="answer-btn w-full px-6 py-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-left transition-all"
                        >
                            ${answer}
                        </button>
                    `).join('')}
                </div>
            </div>
            <style>
                .trivia-question { max-width: 700px; margin: 0 auto; }
                .answer-btn.correct { background: #10B981 !important; }
                .answer-btn.wrong { background: #DC2626 !important; }
                .answer-btn:disabled { cursor: not-allowed; opacity: 0.7; }
            </style>
        `;
  }

  startTimer() {
    if (this.timer) clearInterval(this.timer);

    this.timer = setInterval(() => {
      this.timeLeft--;
      const timerEl = document.getElementById('timer');
      const timerBar = document.getElementById('timer-bar');

      if (timerEl) timerEl.textContent = `${this.timeLeft}s`;
      if (timerBar) {
        const percentage = (this.timeLeft / 20) * 100;
        timerBar.style.width = `${percentage}%`;

        if (this.timeLeft <= 5) {
          timerBar.classList.remove('bg-blue-600');
          timerBar.classList.add('bg-red-600');
        }
      }

      if (this.timeLeft <= 0) {
        clearInterval(this.timer);
        this.selectAnswer(null, this.questions[this.currentQuestion].correct_answer);
      }
    }, 1000);
  }

  selectAnswer(selected, correct) {
    clearInterval(this.timer);

    const buttons = document.querySelectorAll('.answer-btn');
    buttons.forEach(btn => {
      btn.disabled = true;
      if (btn.textContent.trim() === correct) {
        btn.classList.add('correct');
      } else if (btn.textContent.trim() === selected) {
        btn.classList.add('wrong');
      }
    });

    const isCorrect = selected === correct;
    if (isCorrect) {
      this.score += this.timeLeft > 0 ? Math.max(1, Math.floor(this.timeLeft / 2)) : 0;
    }

    this.answers.push({
      question: this.questions[this.currentQuestion].question,
      selected: selected || 'No answer',
      correct: correct,
      isCorrect: isCorrect
    });

    setTimeout(() => {
      this.currentQuestion++;
      this.showQuestion();
    }, 2000);
  }

  showResults() {
    const percentage = Math.round((this.answers.filter(a => a.isCorrect).length / this.answers.length) * 100);

    let emoji = '🎉';
    let message = 'Amazing!';
    if (percentage < 50) { emoji = '😅'; message = 'Keep practicing!'; }
    else if (percentage < 70) { emoji = '👍'; message = 'Good job!'; }
    else if (percentage < 90) { emoji = '🌟'; message = 'Excellent!'; }

    this.container.innerHTML = `
            <div class="trivia-results">
                <div class="text-center mb-8">
                    <div class="text-7xl mb-4">${emoji}</div>
                    <div class="text-3xl font-bold mb-2">${message}</div>
                    <div class="text-xl text-gray-400">You scored ${this.score} points!</div>
                    <div class="text-lg mt-2">
                        ${this.answers.filter(a => a.isCorrect).length}/${this.answers.length} correct (${percentage}%)
                    </div>
                </div>

                <div class="mb-6">
                    <h3 class="text-lg font-bold mb-3">Review Answers</h3>
                    <div class="space-y-3 max-h-96 overflow-y-auto">
                        ${this.answers.map((a, i) => `
                            <div class="p-4 rounded-lg ${a.isCorrect ? 'bg-green-900 bg-opacity-30 border border-green-600' : 'bg-red-900 bg-opacity-30 border border-red-600'}">
                                <div class="font-medium mb-2">${i + 1}. ${a.question}</div>
                                <div class="text-sm">
                                    <div class="text-gray-400">Your answer: <span class="${a.isCorrect ? 'text-green-400' : 'text-red-400'}">${a.selected}</span></div>
                                    ${!a.isCorrect ? `<div class="text-green-400">Correct: ${a.correct}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="flex gap-3">
                    <button onclick="triviaGame.startGame()" class="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-bold">
                        Play Again
                    </button>
                    <button onclick="triviaGame.showSettings()" class="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-bold">
                        New Settings
                    </button>
                </div>
            </div>
            <style>
                .trivia-results { max-width: 700px; margin: 0 auto; }
            </style>
        `;
  }
}

let triviaGame;
window.initTrivia = function (containerId) {
  triviaGame = new TriviaGame(containerId);
  triviaGame.init();
};