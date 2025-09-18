// Games JavaScript
let currentGame = null;
let gameScore = 0;
let gameTimer = null;

function startGame(gameType) {
    currentGame = gameType;
    const modal = document.getElementById('gameModal');
    const gameArea = document.getElementById('gameArea');
    
    // Clear previous game
    gameArea.innerHTML = '';
    gameScore = 0;
    
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
    }
}

function closeGame() {
    const modal = document.getElementById('gameModal');
    modal.style.display = 'none';
    if (gameTimer) {
        clearInterval(gameTimer);
        gameTimer = null;
    }
    currentGame = null;
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
