// Games JavaScript
let currentGame = null;
let gameScore = 0;
let gameTimer = null;
let gameStartTime = null;
let gamePerformance = {
    accuracy: 0,
    avg_reaction_time: 0,
    completed: false,
    time_to_solve: 0,
    score: 0
};

function startGame(gameType) {
    currentGame = gameType;
    const modal = document.getElementById('gameModal');
    const gameArea = document.getElementById('gameArea');
    
    // Clear previous game
    gameArea.innerHTML = '';
    gameScore = 0;
    
    // Start performance tracking
    startGameTracking();
    
    // Show modal
    modal.style.display = 'block';
    
    // Initialize specific game
    switch(gameType) {
        case 'candy-crash':
            initCandyCrash();
            break;
        case 'lumosity':
            initLumosity();
            break;
        case 'subway-surfers':
            initSubwaySurfers();
            break;
        case 'funny-maze':
            initFunnyMaze();
            break;
        case 'breathing':
            initBreathingGame();
            break;
        case 'memory':
            initMemoryGame();
            break;
        case 'reaction':
            initReactionGame();
            break;
        case 'puzzle':
            initPuzzleGame();
            break;
    }
}

function closeGame() {
    const modal = document.getElementById('gameModal');
    modal.style.display = 'none';
    if (gameTimer) {
        clearInterval(gameTimer);
        gameTimer = null;
    }
    
    // Track game performance before closing
    if (currentGame && gameStartTime) {
        trackGamePerformance();
    }
    
    currentGame = null;
}

// Game Performance Tracking Functions
function startGameTracking() {
    gameStartTime = Date.now();
    gamePerformance = {
        accuracy: 0,
        avg_reaction_time: 0,
        completed: false,
        time_to_solve: 0,
        score: 0,
        reaction_times: []
    };
}

function trackReactionTime() {
    if (gamePerformance.reaction_times) {
        const reactionTime = Date.now() - gameStartTime;
        gamePerformance.reaction_times.push(reactionTime);
    }
}

function updateGameAccuracy(correct, total) {
    if (total > 0) {
        gamePerformance.accuracy = correct / total;
    }
}

function completeGame() {
    gamePerformance.completed = true;
    if (gameStartTime) {
        gamePerformance.time_to_solve = (Date.now() - gameStartTime) / 1000; // in seconds
    }
    
    // Calculate average reaction time
    if (gamePerformance.reaction_times && gamePerformance.reaction_times.length > 0) {
        gamePerformance.avg_reaction_time = gamePerformance.reaction_times.reduce((a, b) => a + b, 0) / gamePerformance.reaction_times.length;
    }
    
    gamePerformance.score = gameScore;
    
    // Track performance
    trackGamePerformance();
}

function trackGamePerformance() {
    if (!currentGame) return;
    
    const performanceData = {
        game_type: currentGame,
        performance_data: gamePerformance
    };
    
    // Send to server
    fetch('/api/game-performance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(performanceData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Game performance tracked successfully');
        } else {
            console.error('Error tracking game performance:', data.error);
        }
    })
    .catch(error => {
        console.error('Error tracking game performance:', error);
    });
}

// Enhanced game completion with mood assessment integration
function showGameCompletion() {
    const gameArea = document.getElementById('gameArea');
    const completionHTML = `
        <div class="text-center">
            <h3>🎉 Game Complete!</h3>
            <p>Score: ${gameScore}</p>
            <p>Accuracy: ${Math.round(gamePerformance.accuracy * 100)}%</p>
            <p>Time: ${Math.round(gamePerformance.time_to_solve)}s</p>
            <div class="mt-3">
                <button class="btn btn-primary me-2" onclick="takeMoodAssessment()">🧠 Take Mood Assessment</button>
                <button class="btn btn-secondary" onclick="closeGame()">Close</button>
            </div>
        </div>
    `;
    gameArea.innerHTML = completionHTML;
}

function takeMoodAssessment() {
    closeGame();
    // Redirect to mood assessment
    window.location.href = '/mood-assessment';
}

// Mental Health Games
function initBreathingGame() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center">
            <h3>🌬️ Breathing Exercise</h3>
            <p>Follow the circle to practice deep breathing</p>
            <div class="breathing-circle" id="breathingCircle" style="width: 200px; height: 200px; border-radius: 50%; background: linear-gradient(45deg, #667eea, #764ba2); margin: 20px auto; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.2rem; font-weight: bold; transition: all 4s ease-in-out;">
                Breathe In
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" onclick="startBreathingExercise()">Start Exercise</button>
                <button class="btn btn-secondary ms-2" onclick="completeGame()">Complete</button>
            </div>
        </div>
    `;
}

function startBreathingExercise() {
    const circle = document.getElementById('breathingCircle');
    let isInhaling = true;
    let cycle = 0;
    const maxCycles = 5;
    
    const breathingInterval = setInterval(() => {
        if (isInhaling) {
            circle.style.transform = 'scale(1.2)';
            circle.textContent = 'Breathe In';
            circle.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
        } else {
            circle.style.transform = 'scale(1)';
            circle.textContent = 'Breathe Out';
            circle.style.background = 'linear-gradient(45deg, #764ba2, #667eea)';
        }
        
        isInhaling = !isInhaling;
        
        if (!isInhaling) {
            cycle++;
            if (cycle >= maxCycles) {
                clearInterval(breathingInterval);
                gamePerformance.completed = true;
                gamePerformance.score = 100;
                showGameCompletion();
            }
        }
    }, 4000);
}

function initMemoryGame() {
    const gameArea = document.getElementById('gameArea');
    const cards = ['🧠', '💡', '🎯', '⭐', '🌟', '💫', '🔮', '🎪'];
    const shuffledCards = [...cards, ...cards].sort(() => Math.random() - 0.5);
    
    gameArea.innerHTML = `
        <div class="text-center">
            <h3>🧠 Memory Match</h3>
            <p>Match the pairs by clicking on cards</p>
            <div class="memory-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; max-width: 400px; margin: 20px auto;">
                ${shuffledCards.map((card, index) => `
                    <div class="memory-card" data-card="${card}" data-index="${index}" onclick="flipCard(this)" style="width: 80px; height: 80px; background: #6f42c1; color: white; display: flex; align-items: center; justify-content: center; font-size: 2rem; border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                        ?
                    </div>
                `).join('')}
            </div>
            <div class="mt-3">
                <p>Matches: <span id="matchCount">0</span>/8</p>
            </div>
        </div>
    `;
    
    window.memoryGame = {
        flippedCards: [],
        matches: 0,
        totalMatches: 8
    };
}

function flipCard(cardElement) {
    if (window.memoryGame.flippedCards.length >= 2) return;
    
    const card = cardElement.dataset.card;
    const index = cardElement.dataset.index;
    
    cardElement.textContent = card;
    cardElement.style.background = 'white';
    cardElement.style.color = '#6f42c1';
    
    window.memoryGame.flippedCards.push({ element: cardElement, card: card, index: index });
    
    if (window.memoryGame.flippedCards.length === 2) {
        setTimeout(() => {
            const [card1, card2] = window.memoryGame.flippedCards;
            
            if (card1.card === card2.card) {
                card1.element.style.background = '#28a745';
                card2.element.style.background = '#28a745';
                window.memoryGame.matches++;
                document.getElementById('matchCount').textContent = window.memoryGame.matches;
                
                if (window.memoryGame.matches === window.memoryGame.totalMatches) {
                    gamePerformance.completed = true;
                    gamePerformance.accuracy = 1;
                    gamePerformance.score = 100;
                    showGameCompletion();
                }
            } else {
                card1.element.textContent = '?';
                card2.element.textContent = '?';
                card1.element.style.background = '#6f42c1';
                card2.element.style.background = '#6f42c1';
                card1.element.style.color = 'white';
                card2.element.style.color = 'white';
            }
            
            window.memoryGame.flippedCards = [];
        }, 1000);
    }
}

function initReactionGame() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center">
            <h3>⚡ Reaction Time Test</h3>
            <p>Click the button as soon as it turns green!</p>
            <div class="reaction-area" style="margin: 40px 0;">
                <button id="reactionButton" class="btn btn-danger btn-lg" onclick="reactToButton()" style="width: 200px; height: 200px; border-radius: 50%; font-size: 1.5rem;">
                    Wait...
                </button>
            </div>
            <div class="mt-3">
                <p>Reaction Time: <span id="reactionTime">-</span>ms</p>
                <p>Average: <span id="avgReactionTime">-</span>ms</p>
                <p>Attempts: <span id="attemptCount">0</span>/5</p>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" onclick="startReactionTest()">Start Test</button>
            </div>
        </div>
    `;
    
    window.reactionGame = {
        attempts: 0,
        maxAttempts: 5,
        reactionTimes: [],
        waitingForClick: false
    };
}

function startReactionTest() {
    const button = document.getElementById('reactionButton');
    const attempts = window.reactionGame.attempts;
    
    if (attempts >= window.reactionGame.maxAttempts) {
        gamePerformance.completed = true;
        gamePerformance.avg_reaction_time = window.reactionGame.reactionTimes.reduce((a, b) => a + b, 0) / window.reactionGame.reactionTimes.length;
        gamePerformance.score = Math.max(0, 100 - gamePerformance.avg_reaction_time / 10);
        showGameCompletion();
        return;
    }
    
    button.textContent = 'Wait...';
    button.className = 'btn btn-danger btn-lg';
    button.disabled = true;
    window.reactionGame.waitingForClick = false;
    
    const randomDelay = Math.random() * 3000 + 1000; // 1-4 seconds
    
    setTimeout(() => {
        button.textContent = 'CLICK NOW!';
        button.className = 'btn btn-success btn-lg';
        button.disabled = false;
        window.reactionGame.waitingForClick = true;
        window.reactionGame.startTime = Date.now();
    }, randomDelay);
}

function reactToButton() {
    if (!window.reactionGame.waitingForClick) return;
    
    const reactionTime = Date.now() - window.reactionGame.startTime;
    window.reactionGame.reactionTimes.push(reactionTime);
    window.reactionGame.attempts++;
    
    document.getElementById('reactionTime').textContent = reactionTime;
    document.getElementById('attemptCount').textContent = window.reactionGame.attempts;
    
    const avgTime = window.reactionGame.reactionTimes.reduce((a, b) => a + b, 0) / window.reactionGame.reactionTimes.length;
    document.getElementById('avgReactionTime').textContent = Math.round(avgTime);
    
    setTimeout(() => startReactionTest(), 1000);
}

function initPuzzleGame() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center">
            <h3>🧩 Stress Relief Puzzle</h3>
            <p>Arrange the pieces to complete the puzzle</p>
            <div class="puzzle-container" style="margin: 20px auto; max-width: 300px;">
                <div class="puzzle-grid" id="puzzleGrid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; background: #333; padding: 10px; border-radius: 8px;">
                    <!-- Puzzle pieces will be generated here -->
                </div>
            </div>
            <div class="mt-3">
                <p>Moves: <span id="moveCount">0</span></p>
                <button class="btn btn-primary" onclick="generatePuzzle()">Generate Puzzle</button>
            </div>
        </div>
    `;
    
    window.puzzleGame = {
        moves: 0,
        solved: false
    };
}

function generatePuzzle() {
    const grid = document.getElementById('puzzleGrid');
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 0]; // 0 represents empty space
    const shuffled = [...numbers].sort(() => Math.random() - 0.5);
    
    grid.innerHTML = shuffled.map((num, index) => `
        <div class="puzzle-piece" data-value="${num}" data-index="${index}" onclick="movePiece(this)" style="width: 80px; height: 80px; background: ${num === 0 ? '#333' : '#6f42c1'}; color: white; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; border-radius: 4px; cursor: pointer; transition: all 0.3s ease;">
            ${num === 0 ? '' : num}
        </div>
    `).join('');
    
    window.puzzleGame.moves = 0;
    window.puzzleGame.solved = false;
    document.getElementById('moveCount').textContent = '0';
}

function movePiece(piece) {
    const value = parseInt(piece.dataset.value);
    if (value === 0) return;
    
    const index = parseInt(piece.dataset.index);
    const emptyIndex = findEmptyIndex();
    
    if (isAdjacent(index, emptyIndex)) {
        // Swap pieces
        const emptyPiece = document.querySelector(`[data-index="${emptyIndex}"]`);
        const tempValue = piece.dataset.value;
        const tempText = piece.textContent;
        
        piece.dataset.value = emptyPiece.dataset.value;
        piece.textContent = emptyPiece.textContent;
        piece.style.background = emptyPiece.style.background;
        
        emptyPiece.dataset.value = tempValue;
        emptyPiece.textContent = tempText;
        emptyPiece.style.background = tempValue === 0 ? '#333' : '#6f42c1';
        
        window.puzzleGame.moves++;
        document.getElementById('moveCount').textContent = window.puzzleGame.moves;
        
        if (checkPuzzleSolved()) {
            gamePerformance.completed = true;
            gamePerformance.time_to_solve = window.puzzleGame.moves;
            gamePerformance.score = Math.max(0, 100 - window.puzzleGame.moves);
            showGameCompletion();
        }
    }
}

function findEmptyIndex() {
    const emptyPiece = document.querySelector('[data-value="0"]');
    return parseInt(emptyPiece.dataset.index);
}

function isAdjacent(index1, index2) {
    const row1 = Math.floor(index1 / 3);
    const col1 = index1 % 3;
    const row2 = Math.floor(index2 / 3);
    const col2 = index2 % 3;
    
    return (Math.abs(row1 - row2) === 1 && col1 === col2) || 
           (Math.abs(col1 - col2) === 1 && row1 === row2);
}

function checkPuzzleSolved() {
    const pieces = document.querySelectorAll('.puzzle-piece');
    for (let i = 0; i < pieces.length - 1; i++) {
        if (parseInt(pieces[i].dataset.value) !== i + 1) {
            return false;
        }
    }
    return true;
}

// Candy Crash Game
function initCandyCrash() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center mb-3">
            <h3>🍭 Candy Crash</h3>
            <p>Click on candies to match 3 or more in a row!</p>
            <div>Score: <span id="score">0</span></div>
        </div>
        <div class="candy-game" id="candyGrid"></div>
        <div class="text-center mt-3">
            <button class="btn btn-primary" onclick="resetCandyGame()">Reset Game</button>
        </div>
    `;
    
    const grid = document.getElementById('candyGrid');
    const candies = ['🍭', '🍬', '🍫', '🍪', '🧁', '🍰'];
    
    // Create 8x8 grid
    for (let i = 0; i < 64; i++) {
        const cell = document.createElement('div');
        cell.className = 'candy-cell';
        cell.textContent = candies[Math.floor(Math.random() * candies.length)];
        cell.onclick = () => selectCandy(cell, i);
        grid.appendChild(cell);
    }
}

function selectCandy(cell, index) {
    cell.style.transform = 'scale(1.2)';
    cell.style.boxShadow = '0 0 10px #6f42c1';
    
    // Simple scoring
    gameScore += 10;
    document.getElementById('score').textContent = gameScore;
    
    // Reset after animation
    setTimeout(() => {
        cell.style.transform = 'scale(1)';
        cell.style.boxShadow = 'none';
        const candies = ['🍭', '🍬', '🍫', '🍪', '🧁', '🍰'];
        cell.textContent = candies[Math.floor(Math.random() * candies.length)];
    }, 300);
}

function resetCandyGame() {
    initCandyCrash();
}

// Lumosity Brain Training Game
function initLumosity() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center mb-3">
            <h3>🧠 Lumosity Brain Training</h3>
            <p>Memorize the pattern and click the cards in order!</p>
            <div>Level: <span id="level">1</span> | Score: <span id="score">0</span></div>
        </div>
        <div class="lumosity-game">
            <div class="memory-grid" id="memoryGrid"></div>
            <button class="btn btn-primary" onclick="startMemoryGame()">Start Game</button>
        </div>
    `;
}

function startMemoryGame() {
    const grid = document.getElementById('memoryGrid');
    grid.innerHTML = '';
    
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16];
    const shuffled = numbers.sort(() => Math.random() - 0.5);
    
    shuffled.forEach((num, index) => {
        const card = document.createElement('div');
        card.className = 'memory-card';
        card.textContent = num;
        card.onclick = () => flipCard(card, num);
        grid.appendChild(card);
    });
}

function flipCard(card, number) {
    if (card.classList.contains('flipped')) return;
    
    card.classList.add('flipped');
    gameScore += 5;
    document.getElementById('score').textContent = gameScore;
    
    // Check if all cards are flipped
    setTimeout(() => {
        const allFlipped = document.querySelectorAll('.memory-card.flipped').length;
        if (allFlipped === 16) {
            alert('Congratulations! You completed the memory game!');
        }
    }, 100);
}

// Subway Surfers Game
function initSubwaySurfers() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center mb-3">
            <h3>🏃‍♂️ Subway Surfers</h3>
            <p>Press SPACE to jump and avoid obstacles!</p>
            <div>Score: <span id="score">0</span> | Distance: <span id="distance">0</span>m</div>
        </div>
        <div class="subway-game" id="subwayGame">
            <div class="runner">🏃‍♂️</div>
        </div>
        <div class="text-center mt-3">
            <button class="btn btn-primary" onclick="startSubwayGame()">Start Running</button>
        </div>
    `;
}

function startSubwayGame() {
    const game = document.getElementById('subwayGame');
    const runner = game.querySelector('.runner');
    let isJumping = false;
    let distance = 0;
    
    // Jump on space key
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && !isJumping) {
            e.preventDefault();
            jump();
        }
    });
    
    function jump() {
        isJumping = true;
        runner.style.animation = 'none';
        runner.style.transform = 'translateY(-50px)';
        
        setTimeout(() => {
            runner.style.transform = 'translateY(0)';
            runner.style.animation = 'run 0.5s infinite';
            isJumping = false;
        }, 500);
    }
    
    // Create obstacles
    function createObstacle() {
        const obstacle = document.createElement('div');
        obstacle.className = 'obstacle';
        obstacle.textContent = '🚧';
        game.appendChild(obstacle);
        
        setTimeout(() => {
            if (obstacle.parentNode) {
                obstacle.remove();
            }
        }, 2000);
    }
    
    // Game loop
    gameTimer = setInterval(() => {
        distance += 1;
        gameScore += 1;
        document.getElementById('distance').textContent = distance;
        document.getElementById('score').textContent = gameScore;
        
        // Create obstacles randomly
        if (Math.random() < 0.3) {
            createObstacle();
        }
    }, 100);
}

// Funny Maze Game
function initFunnyMaze() {
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = `
        <div class="text-center mb-3">
            <h3>😄 Funny Maze</h3>
            <p>Use arrow keys to navigate to the goal!</p>
            <div>Moves: <span id="moves">0</span></div>
        </div>
        <div class="maze-game" id="mazeGrid"></div>
        <div class="text-center mt-3">
            <button class="btn btn-primary" onclick="resetMaze()">New Maze</button>
        </div>
    `;
    
    createMaze();
}

function createMaze() {
    const grid = document.getElementById('mazeGrid');
    grid.innerHTML = '';
    
    const maze = [
        [1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,1],
        [1,0,1,0,1,0,1,1,0,1],
        [1,0,1,0,0,0,0,1,0,1],
        [1,0,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,1,0,1],
        [1,1,1,0,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,1,2,1],
        [1,1,1,1,1,1,1,1,1,1]
    ];
    
    let playerPos = {x: 1, y: 1};
    let moves = 0;
    
    maze.forEach((row, y) => {
        row.forEach((cell, x) => {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'maze-cell';
            
            if (cell === 1) {
                cellDiv.classList.add('wall');
            } else if (cell === 2) {
                cellDiv.classList.add('goal');
                cellDiv.textContent = '🎯';
            } else if (x === playerPos.x && y === playerPos.y) {
                cellDiv.classList.add('player');
                cellDiv.textContent = '😄';
            }
            
            grid.appendChild(cellDiv);
        });
    });
    
    // Handle keyboard input
    document.addEventListener('keydown', (e) => {
        let newX = playerPos.x;
        let newY = playerPos.y;
        
        switch(e.key) {
            case 'ArrowUp':
                newY = Math.max(0, playerPos.y - 1);
                break;
            case 'ArrowDown':
                newY = Math.min(9, playerPos.y + 1);
                break;
            case 'ArrowLeft':
                newX = Math.max(0, playerPos.x - 1);
                break;
            case 'ArrowRight':
                newX = Math.min(9, playerPos.x + 1);
                break;
            default:
                return;
        }
        
        if (maze[newY][newX] !== 1) {
            playerPos.x = newX;
            playerPos.y = newY;
            moves++;
            document.getElementById('moves').textContent = moves;
            createMaze();
            
            if (maze[newY][newX] === 2) {
                alert(`Congratulations! You completed the maze in ${moves} moves!`);
            }
        }
    });
}

function resetMaze() {
    initFunnyMaze();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('gameModal');
    if (event.target === modal) {
        closeGame();
    }
}
