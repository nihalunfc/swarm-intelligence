document.addEventListener('DOMContentLoaded', () => {
    // Initialize Leaflet Satellite Map (Niagara Falls coordinates)
    const map = L.map('satellite-map', {
        zoomControl: false,
        attributionControl: false,
        dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false
    }).setView([43.0896, -79.0849], 15);

    // Free Esri World Imagery (No API Key required!)
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19
    }).addTo(map);

    const btnStart = document.getElementById('btn-start');
    const btnReset = document.getElementById('btn-reset');
    const statusIndicator = document.getElementById('metric-status');
    const fireMetric = document.getElementById('metric-fire');
    
    // Setup Canvas
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    
    // Use the classic, highly-reliable rendering from V1
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
        // Ignite a larger central cluster to guarantee aggressive spread
        grid[gridSize/2][gridSize/2] = 1;
        grid[gridSize/2 + 1][gridSize/2] = 1;
        grid[gridSize/2][gridSize/2 + 1] = 1;
        grid[gridSize/2 - 1][gridSize/2 - 1] = 1;
        
        // Spawn 12 drones in a tactical cluster at the "Base" (Top-Left)
        drones = [];
        for (let i = 0; i < 12; i++) {
            drones.push({ x: Math.floor(Math.random() * 3), y: Math.floor(Math.random() * 3) });
        }
        
        document.getElementById('metric-drones').innerText = drones.length;
        
        timeStep = 0;
        telemetryChart.data.labels = [];
        telemetryChart.data.datasets[0].data = [];
        telemetryChart.update();
        
        drawGrid();
    }

    function drawGrid() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let fireCount = 0;
        
        // Classic, reliable grid rendering
        for (let y = 0; y < gridSize; y++) {
            for (let x = 0; x < gridSize; x++) {
                if (grid[y][x] === 1) { // FIRE
                    ctx.fillStyle = 'rgba(239, 68, 68, 0.8)'; 
                    ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
                    fireCount++;
                } else if (grid[y][x] === 2) { // EXTINGUISHED
                    ctx.fillStyle = 'rgba(51, 65, 85, 0.6)'; 
                    ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
                }
            }
        }

        // Update DOM Metrics
        fireMetric.innerText = fireCount;
        
        // Mathematical Scaler for Real-World Scenarios
        // Assume 1 cell = 1 Hectare. 
        // A standard firefighting drone (e.g., DJI Agras T40) carries ~40 Liters.
        // Assume 1 Hectare of active fire requires ~600 Liters (15 drone payloads) to suppress.
        let realDronesNeeded = fireCount * 15;
        document.getElementById('metric-real-drones').innerText = realDronesNeeded;

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

        // Classic Drone Rendering (Blue Circles)
        ctx.fillStyle = '#3b82f6'; 
        drones.forEach(drone => {
            ctx.beginPath();
            ctx.arc((drone.x * cellSize) + (cellSize/2), (drone.y * cellSize) + (cellSize/2), cellSize/3, 0, Math.PI * 2);
            ctx.fill();
        });
        
        return fireCount;
    }

    function simulationLoop() {
        if (!isRunning) return;
        
        // 1. Organic Fire Spread (Aggressive)
        let newGrid = JSON.parse(JSON.stringify(grid));
        for (let y = 1; y < gridSize-1; y++) {
            for (let x = 1; x < gridSize-1; x++) {
                if (grid[y][x] === 1) {
                    const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
                    dirs.forEach(d => {
                        // Wind blows South-East heavily
                        let prob = 0.15;
                        if (d[0] === 1 || d[1] === 1) prob = 0.35; 
                        
                        if (Math.random() < prob && newGrid[y+d[0]][x+d[1]] === 0) {
                            newGrid[y+d[0]][x+d[1]] = 1;
                        }
                    });
                }
            }
        }
        grid = newGrid;
        
        // 2. Swarm Logic (Seek & Destroy)
        // Drones only move on even timeSteps, making them slower than the fire!
        if (timeStep % 2 === 0) {
            drones.forEach(drone => {
                // Find nearest fire
                let nearestDist = Infinity;
                let targetX = drone.x;
                let targetY = drone.y;
                
                for (let y = 0; y < gridSize; y++) {
                    for (let x = 0; x < gridSize; x++) {
                        if (grid[y][x] === 1) {
                            // DECENTRALIZED COORDINATION: 
                            // Add slight random noise to the distance heuristic so the swarm 
                            // divides and conquers the fire front instead of clumping on one cell
                            let dist = Math.abs(x - drone.x) + Math.abs(y - drone.y) + (Math.random() * 8);
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
                
                // Extinguish strictly the single cell the drone is on top of (1x1 area)
                if(grid[drone.y][drone.x] === 1) {
                    grid[drone.y][drone.x] = 2; // Drop retardant
                }
            });
        }

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

        setTimeout(simulationLoop, 400); // Slower tick rate (400ms) for better viewing
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
    
    // Phase 4: Gemini API Integration
    const btnSend = document.getElementById('btn-send');
    const inputField = document.getElementById('chat-input-field');
    const chatWindow = document.getElementById('chat-window');
    const apiKeyField = document.getElementById('gemini-api-key');
    
    btnSend.addEventListener('click', async () => {
        const text = inputField.value.trim();
        const apiKey = apiKeyField.value.trim();
        if(!text) return;
        
        // Render User Message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.innerHTML = `<strong>You:</strong> ${text}`;
        chatWindow.appendChild(userMsg);
        inputField.value = '';
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        if (!apiKey) {
            const sysMsg = document.createElement('div');
            sysMsg.className = 'message system';
            sysMsg.innerHTML = `<strong>System:</strong> API Key missing. Please enter your Gemini API Key at the top to activate the Swarm Commander.`;
            chatWindow.appendChild(sysMsg);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            return;
        }

        // Add loading indicator
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'message system';
        loadingMsg.innerHTML = `<strong>System:</strong> Connecting to Gemini Neural Link...`;
        chatWindow.appendChild(loadingMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        // Prepare Live Context for Gemini (Explainable AI)
        const currentFireCount = document.getElementById('metric-fire').innerText;
        const systemPrompt = `You are the WARL Swarm Commander AI. You oversee a decentralized swarm of autonomous drones fighting a wildfire. Current live status: ${currentFireCount} active fire cells. There are 3 Drones active. The wind is currently blowing aggressively South-East. Answer the user's question briefly (1-2 short paragraphs) and act in character as a highly advanced, analytical AI commander explaining the swarm's tactical Reinforcement Learning decisions. User says: ${text}`;

        try {
            // 1. Dynamically discover available models for this specific API key (Bypasses region/project naming differences)
            const modelListResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
            const modelListData = await modelListResponse.json();
            
            if (modelListData.error) throw new Error("Model Discovery Failed: " + modelListData.error.message);
            
            // 2. Find any valid Gemini model that supports text generation
            let targetModel = "models/gemini-1.5-flash"; // Fallback
            if (modelListData.models) {
                const validModels = modelListData.models.filter(m => 
                    m.supportedGenerationMethods && 
                    m.supportedGenerationMethods.includes("generateContent") &&
                    m.name.includes("gemini")
                );
                
                if (validModels.length === 0) {
                    throw new Error("No Gemini models supporting text generation were found on your Google Cloud account/region.");
                }
                
                // Prefer flash if available, otherwise take the first available one
                const flashModel = validModels.find(m => m.name.includes("1.5-flash"));
                targetModel = flashModel ? flashModel.name : validModels[0].name;
            }

            // 3. Call the dynamically discovered model
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/${targetModel}:generateContent?key=${apiKey}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: systemPrompt }] }]
                })
            });

            const data = await response.json();
            loadingMsg.remove(); // Safely remove loading indicator

            if (data.error) throw new Error(data.error.message);
            if (!data.candidates || data.candidates.length === 0) throw new Error("Gemini returned an empty response (possible safety filter).");

            const replyText = data.candidates[0].content.parts[0].text;
            
            const geminiMsg = document.createElement('div');
            geminiMsg.className = 'message gemini';
            // Convert simple markdown ** to HTML strong
            let formattedReply = replyText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            geminiMsg.innerHTML = `<strong>Commander:</strong> ${formattedReply}`;
            chatWindow.appendChild(geminiMsg);
        } catch (error) {
            loadingMsg.remove(); // Safely remove loading indicator if it still exists
            const errorMsg = document.createElement('div');
            errorMsg.className = 'message system';
            errorMsg.style.color = '#ef4444';
            errorMsg.innerHTML = `<strong>Error:</strong> Failed to connect to Gemini API. (${error.message})`;
            chatWindow.appendChild(errorMsg);
        }
        
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
    
    inputField.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') btnSend.click();
    });

    initGrid();
});
