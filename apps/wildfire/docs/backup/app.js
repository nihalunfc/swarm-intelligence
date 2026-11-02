document.addEventListener('DOMContentLoaded', () => {
    const btnStart = document.getElementById('btn-start');
    const btnReset = document.getElementById('btn-reset');
    const statusIndicator = document.getElementById('metric-status');
    const fireMetric = document.getElementById('metric-fire');
    
    // Setup Canvas
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    
    const resizeCanvas = () => {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const gridSize = 24; 
    let cellSize = canvas.width / gridSize;
    
    let isRunning = false;
    let grid = [];
    let drones = [];
    
    // Chart.js Setup for Live Telemetry
    const chartCtx = document.getElementById('telemetry-chart').getContext('2d');
    const telemetryChart = new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Active Fire Cells',
                data: [],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: '#1f2937' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { display: false } }
            }
        }
    });

    let timeStep = 0;

    function initGrid() {
        grid = Array(gridSize).fill().map(() => Array(gridSize).fill(0));
        // Ignite multiple center points to make it look organic
        grid[gridSize/2][gridSize/2] = 1;
        grid[gridSize/2 + 1][gridSize/2] = 1;
        grid[gridSize/2][gridSize/2 + 1] = 1;
        
        // Spawn 4 drones at corners
        drones = [
            { x: 1, y: 1 }, { x: gridSize-2, y: 1 },
            { x: 1, y: gridSize-2 }, { x: gridSize-2, y: gridSize-2 }
        ];
        
        timeStep = 0;
        telemetryChart.data.labels = [];
        telemetryChart.data.datasets[0].data = [];
        telemetryChart.update();
        
        drawGrid();
    }

    function drawGrid() {
        cellSize = canvas.width / gridSize; 
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        let fireCount = 0;
        
        // Draw Grid Elements with glow effects
        for (let y = 0; y < gridSize; y++) {
            for (let x = 0; x < gridSize; x++) {
                if (grid[y][x] === 1) { // FIRE
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = '#ef4444';
                    ctx.fillStyle = '#ef4444';
                    ctx.fillRect(x * cellSize + 1, y * cellSize + 1, cellSize - 2, cellSize - 2);
                    fireCount++;
                } else if (grid[y][x] === 2) { // EXTINGUISHED / RETARDANT
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = 'rgba(56, 189, 248, 0.4)'; // Blueish retardant
                    ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
                }
            }
        }
        ctx.shadowBlur = 0; // Reset shadow for drones

        // Update DOM Metrics
        fireMetric.innerText = fireCount;
        if (fireCount > 30) {
            statusIndicator.innerText = "CRITICAL SPREAD";
            statusIndicator.className = "danger";
        } else if (fireCount > 10) {
            statusIndicator.innerText = "ENGAGING FIRE";
            statusIndicator.className = "warning";
            statusIndicator.style.color = "#f59e0b";
        } else {
            statusIndicator.innerText = "CONTAINED";
            statusIndicator.className = "safe";
            statusIndicator.style.color = "";
        }

        // Draw Tactical Drones (Crosshairs)
        drones.forEach(drone => {
            const centerX = (drone.x * cellSize) + (cellSize/2);
            const centerY = (drone.y * cellSize) + (cellSize/2);
            
            ctx.strokeStyle = '#38bdf8'; // Light blue
            ctx.lineWidth = 2;
            
            // Draw Target Circle
            ctx.beginPath();
            ctx.arc(centerX, centerY, cellSize/2.5, 0, Math.PI * 2);
            ctx.stroke();
            
            // Draw Crosshair lines
            ctx.beginPath();
            ctx.moveTo(centerX, centerY - cellSize/1.5);
            ctx.lineTo(centerX, centerY + cellSize/1.5);
            ctx.moveTo(centerX - cellSize/1.5, centerY);
            ctx.lineTo(centerX + cellSize/1.5, centerY);
            ctx.stroke();
        });
        
        return fireCount;
    }

    function simulationLoop() {
        if (!isRunning) return;
        
        // 1. Organic Fire Spread
        let newGrid = JSON.parse(JSON.stringify(grid));
        for (let y = 1; y < gridSize-1; y++) {
            for (let x = 1; x < gridSize-1; x++) {
                if (grid[y][x] === 1) {
                    const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
                    dirs.forEach(d => {
                        // Wind blows slightly South-East (higher probability for positive dx/dy)
                        let prob = 0.08;
                        if (d[0] === 1 || d[1] === 1) prob = 0.15; 
                        
                        if (Math.random() < prob && newGrid[y+d[0]][x+d[1]] === 0) {
                            newGrid[y+d[0]][x+d[1]] = 1;
                        }
                    });
                }
            }
        }
        grid = newGrid;
        
        // 2. Swarm Logic (Seek & Destroy)
        drones.forEach(drone => {
            // Find nearest fire
            let nearestDist = Infinity;
            let targetX = drone.x;
            let targetY = drone.y;
            
            for (let y = 0; y < gridSize; y++) {
                for (let x = 0; x < gridSize; x++) {
                    if (grid[y][x] === 1) {
                        let dist = Math.abs(x - drone.x) + Math.abs(y - drone.y);
                        if (dist < nearestDist) {
                            nearestDist = dist;
                            targetX = x;
                            targetY = y;
                        }
                    }
                }
            }
            
            // Move one step towards target
            if (targetX > drone.x) drone.x++;
            else if (targetX < drone.x) drone.x--;
            
            if (targetY > drone.y) drone.y++;
            else if (targetY < drone.y) drone.y--;
            
            // Extinguish area of effect (3x3 drop)
            for(let dy=-1; dy<=1; dy++) {
                for(let dx=-1; dx<=1; dx++) {
                    let ny = drone.y + dy, nx = drone.x + dx;
                    if(ny>=0 && ny<gridSize && nx>=0 && nx<gridSize && grid[ny][nx] === 1) {
                        grid[ny][nx] = 2; // Drop retardant
                    }
                }
            }
        });

        let currentFire = drawGrid();
        
        // Update Chart
        timeStep++;
        telemetryChart.data.labels.push(timeStep);
        telemetryChart.data.datasets[0].data.push(currentFire);
        if(telemetryChart.data.labels.length > 50) {
            telemetryChart.data.labels.shift();
            telemetryChart.data.datasets[0].data.shift();
        }
        telemetryChart.update();

        setTimeout(simulationLoop, 200); // Faster tick rate for smoothness
    }

    btnStart.addEventListener('click', () => {
        if (!isRunning) {
            isRunning = true;
            btnStart.innerText = "Pause Swarm";
            simulationLoop();
        } else {
            isRunning = false;
            btnStart.innerText = "Deploy Swarm";
        }
    });

    btnReset.addEventListener('click', () => {
        isRunning = false;
        btnStart.innerText = "Deploy Swarm";
        initGrid();
    });
    
    // Mock Chatbot Interaction
    const btnSend = document.getElementById('btn-send');
    const inputField = document.getElementById('chat-input-field');
    const chatWindow = document.getElementById('chat-window');
    
    btnSend.addEventListener('click', () => {
        const text = inputField.value.trim();
        if(!text) return;
        
        // User Message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.innerHTML = `<strong>You:</strong> ${text}`;
        chatWindow.appendChild(userMsg);
        inputField.value = '';
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        // Mock Gemini Delay
        setTimeout(() => {
            const geminiMsg = document.createElement('div');
            geminiMsg.className = 'message gemini';
            geminiMsg.innerHTML = `<strong>Commander:</strong> Excellent question. In Phase 4, I will be hooked into the Google Gemini API to dynamically analyze the Swarm's Q-Table values and explain our real-time suppression strategy!`;
            chatWindow.appendChild(geminiMsg);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }, 800);
    });
    
    inputField.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') btnSend.click();
    });

    initGrid();
});
