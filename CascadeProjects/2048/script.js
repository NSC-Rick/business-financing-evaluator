class Game2048 {
    constructor() {
        this.size = 4;
        this.startTiles = 2;
        this.grid = [];
        this.score = 0;
        this.best = localStorage.getItem('best2048') || 0;
        this.won = false;
        this.over = false;
        this.keepPlaying = false;
        
        this.tileContainer = document.getElementById('tile-container');
        this.scoreElement = document.getElementById('score');
        this.bestElement = document.getElementById('best');
        this.messageContainer = document.getElementById('game-message');
        
        this.setup();
        this.addEventListeners();
    }
    
    setup() {
        this.grid = this.emptyGrid();
        this.score = 0;
        this.won = false;
        this.over = false;
        this.keepPlaying = false;
        
        this.addStartTiles();
        this.updateDisplay();
        this.hideMessage();
    }
    
    emptyGrid() {
        const cells = [];
        for (let x = 0; x < this.size; x++) {
            const row = cells[x] = [];
            for (let y = 0; y < this.size; y++) {
                row.push(null);
            }
        }
        return cells;
    }
    
    addStartTiles() {
        for (let i = 0; i < this.startTiles; i++) {
            this.addRandomTile();
        }
    }
    
    addRandomTile() {
        if (this.availableCells().length > 0) {
            const value = Math.random() < 0.9 ? 2 : 4;
            const cell = this.randomAvailableCell();
            this.grid[cell.x][cell.y] = {
                value: value,
                mergedFrom: null,
                previousPosition: null
            };
        }
    }
    
    availableCells() {
        const cells = [];
        for (let x = 0; x < this.size; x++) {
            for (let y = 0; y < this.size; y++) {
                if (!this.grid[x][y]) {
                    cells.push({ x: x, y: y });
                }
            }
        }
        return cells;
    }
    
    randomAvailableCell() {
        const cells = this.availableCells();
        if (cells.length) {
            return cells[Math.floor(Math.random() * cells.length)];
        }
    }
    
    move(direction) {
        if (this.isGameTerminated()) return;
        
        let cell, tile;
        const vector = this.getVector(direction);
        const traversals = this.buildTraversals(vector);
        let moved = false;
        
        this.prepareTiles();
        
        traversals.x.forEach(x => {
            traversals.y.forEach(y => {
                cell = { x: x, y: y };
                tile = this.grid[x][y];
                
                if (tile) {
                    const positions = this.findFarthestPosition(cell, vector);
                    const next = this.grid[positions.next.x][positions.next.y];
                    
                    if (next && next.value === tile.value && !next.mergedFrom) {
                        const merged = {
                            value: tile.value * 2,
                            mergedFrom: [tile, next],
                            previousPosition: cell
                        };
                        
                        merged.mergedFrom.forEach(t => {
                            t.previousPosition = {
                                x: t.x === positions.next.x ? cell.x : t.x,
                                y: t.y === positions.next.y ? cell.y : t.y
                            };
                        });
                        
                        this.grid[x][y] = merged;
                        this.grid[positions.next.x][positions.next.y] = null;
                        
                        tile.x = positions.next.x;
                        tile.y = positions.next.y;
                        
                        this.score += merged.value;
                        
                        if (merged.value === 2048 && !this.won) {
                            this.won = true;
                        }
                        
                        moved = true;
                    } else {
                        const positions = this.findFarthestPosition(cell, vector);
                        if (positions.farthest.x !== cell.x || positions.farthest.y !== cell.y) {
                            this.grid[positions.farthest.x][positions.farthest.y] = tile;
                            this.grid[x][y] = null;
                            
                            tile.previousPosition = cell;
                            tile.x = positions.farthest.x;
                            tile.y = positions.farthest.y;
                            
                            moved = true;
                        }
                    }
                }
            });
        });
        
        if (moved) {
            this.addRandomTile();
            if (!this.movesAvailable()) {
                this.over = true;
            }
            
            this.updateDisplay();
        }
    }
    
    getVector(direction) {
        const map = {
            0: { x: 0,  y: -1 }, // up
            1: { x: 1,  y: 0 },  // right
            2: { x: 0,  y: 1 },  // down
            3: { x: -1, y: 0 }   // left
        };
        return map[direction];
    }
    
    buildTraversals(vector) {
        const traversals = { x: [], y: [] };
        
        for (let pos = 0; pos < this.size; pos++) {
            traversals.x.push(pos);
            traversals.y.push(pos);
        }
        
        if (vector.x === 1) traversals.x = traversals.x.reverse();
        if (vector.y === 1) traversals.y = traversals.y.reverse();
        
        return traversals;
    }
    
    findFarthestPosition(cell, vector) {
        let previous;
        
        do {
            previous = cell;
            cell = { x: previous.x + vector.x, y: previous.y + vector.y };
        } while (this.withinBounds(cell) && this.cellAvailable(cell));
        
        return {
            farthest: previous,
            next: this.withinBounds(cell) ? cell : null
        };
    }
    
    withinBounds(position) {
        return position.x >= 0 && position.x < this.size &&
               position.y >= 0 && position.y < this.size;
    }
    
    cellAvailable(cell) {
        return !this.cellOccupied(cell);
    }
    
    cellOccupied(cell) {
        return !!this.grid[cell.x][cell.y];
    }
    
    prepareTiles() {
        for (let x = 0; x < this.size; x++) {
            for (let y = 0; y < this.size; y++) {
                if (this.grid[x][y]) {
                    this.grid[x][y].mergedFrom = null;
                    this.grid[x][y].previousPosition = null;
                }
            }
        }
    }
    
    movesAvailable() {
        return this.availableCells().length > 0 || this.tileMatchesAvailable();
    }
    
    tileMatchesAvailable() {
        for (let x = 0; x < this.size; x++) {
            for (let y = 0; y < this.size; y++) {
                const tile = this.grid[x][y];
                if (tile) {
                    for (let direction = 0; direction < 4; direction++) {
                        const vector = this.getVector(direction);
                        const cell = { x: x + vector.x, y: y + vector.y };
                        
                        if (this.withinBounds(cell)) {
                            const other = this.grid[cell.x][cell.y];
                            if (other && other.value === tile.value) {
                                return true;
                            }
                        }
                    }
                }
            }
        }
        return false;
    }
    
    isGameTerminated() {
        return this.over || (this.won && !this.keepPlaying);
    }
    
    updateDisplay() {
        this.clearContainer(this.tileContainer);
        
        for (let x = 0; x < this.size; x++) {
            for (let y = 0; y < this.size; y++) {
                if (this.grid[x][y]) {
                    this.addTile(this.grid[x][y]);
                }
            }
        }
        
        this.updateScore();
        
        if (this.won && !this.keepPlaying) {
            this.showMessage('You win!', 'game-won');
        } else if (this.over) {
            this.showMessage('Game over!', 'game-over');
        }
    }
    
    addTile(tile) {
        const wrapper = document.createElement('div');
        const inner = document.createElement('div');
        const position = this.positionClass({ x: tile.x, y: tile.y });
        const classes = ['tile', 'tile-' + tile.value];
        
        if (tile.value > 2048) classes.push('tile-super');
        
        inner.classList.add('tile-inner');
        inner.textContent = tile.value;
        
        wrapper.classList.add(...classes);
        wrapper.classList.add(position);
        wrapper.appendChild(inner);
        
        this.tileContainer.appendChild(wrapper);
        
        if (tile.previousPosition) {
            window.requestAnimationFrame(() => {
                classes.push('tile-' + this.positionClass(tile.previousPosition));
                wrapper.classList.add(...classes);
            });
        }
        
        if (tile.mergedFrom) {
            classes.push('tile-merged');
            wrapper.classList.add(...classes);
        }
    }
    
    positionClass(position) {
        return 'tile-position-' + position.x + '-' + position.y;
    }
    
    updateScore() {
        this.scoreElement.textContent = this.score;
        
        if (this.score > this.best) {
            this.best = this.score;
            this.bestElement.textContent = this.best;
            localStorage.setItem('best2048', this.best);
        }
    }
    
    showMessage(text, className) {
        this.messageContainer.classList.add(className);
        this.messageContainer.querySelector('p').textContent = text;
        this.messageContainer.style.display = 'block';
    }
    
    hideMessage() {
        this.messageContainer.classList.remove('game-won', 'game-over');
        this.messageContainer.style.display = 'none';
    }
    
    clearContainer(container) {
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
    }
    
    restart() {
        this.setup();
    }
    
    addEventListeners() {
        // Keyboard controls
        document.addEventListener('keydown', (event) => {
            const mapped = {
                38: 0, // up
                39: 1, // right
                40: 2, // down
                37: 3  // left
            };
            
            if (mapped[event.which] !== undefined) {
                event.preventDefault();
                this.move(mapped[event.which]);
            }
        });
        
        // Touch controls
        let touchStartX, touchStartY;
        
        this.tileContainer.addEventListener('touchstart', (event) => {
            if (event.touches.length > 0) {
                touchStartX = event.touches[0].clientX;
                touchStartY = event.touches[0].clientY;
                event.preventDefault();
            }
        });
        
        this.tileContainer.addEventListener('touchmove', (event) => {
            if (event.touches.length > 0) {
                event.preventDefault();
            }
        });
        
        this.tileContainer.addEventListener('touchend', (event) => {
            if (event.changedTouches.length > 0) {
                const touchEndX = event.changedTouches[0].clientX;
                const touchEndY = event.changedTouches[0].clientY;
                
                const dx = touchEndX - touchStartX;
                const dy = touchEndY - touchStartY;
                
                const absDx = Math.abs(dx);
                const absDy = Math.abs(dy);
                
                if (Math.max(absDx, absDy) > 10) {
                    if (absDx > absDy) {
                        this.move(dx > 0 ? 1 : 3); // right : left
                    } else {
                        this.move(dy > 0 ? 2 : 0); // down : up
                    }
                }
                
                event.preventDefault();
            }
        });
    }
}

// Initialize the game
const game = new Game2048();
