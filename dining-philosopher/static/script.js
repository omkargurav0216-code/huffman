document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const diningArea = document.getElementById('dining-area');
    const statusDisplay = document.getElementById('status-display');
    const statusText = document.getElementById('status-text');
    const totalMealsCount = document.getElementById('total-meals-count');
    const modeBadge = document.getElementById('mode-badge');
    const philosopherBars = document.getElementById('philosopher-bars');
    const phiCountSelect = document.getElementById('phi-count-select');
    const btnApplyCount = document.getElementById('btn-apply-count');
    
    // Control Buttons
    const btnStart = document.getElementById('btn-start');
    const btnPause = document.getElementById('btn-pause');
    const btnReset = document.getElementById('btn-reset');
    const btnDeadlock = document.getElementById('btn-deadlock');
    const btnPrevention = document.getElementById('btn-prevention');
    
    // Configuration
    const width = 450;
    const height = 450;
    const center = { x: width / 2, y: height / 2 };
    const tableRadius = 150; // Radius for positioning philosophers & forks
    
    // Vibrant colors matching the existing design for philosopher dots
    const dotColors = [
        '#818cf8', // P1
        '#f472b6', // P2
        '#34d399', // P3
        '#fb923c', // P4
        '#38bdf8', // P5
        '#a78bfa', // P6
        '#fb7185', // P7
        '#2dd4bf', // P8
        '#facc15', // P9
        '#c084fc', // P10
        '#f87171', // P11
        '#4ade80'  // P12
    ];
    
    // Create elements dynamically
    const philosopherNodes = [];
    const forkNodes = [];
    
    // Create statistics elements dynamically
    function initializeStatsElements(count) {
        philosopherBars.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const row = document.createElement('div');
            row.className = 'stat-row';
            row.innerHTML = `
                <div class="stat-info">
                    <span class="phi-dot" style="background-color: ${dotColors[i % dotColors.length]};"></span>
                    <span class="stat-name">P${i+1} (Philosopher${i+1})</span>
                    <span class="stat-val" id="meals-p${i}">0</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="bar-p${i}" style="width: 0%;"></div>
                </div>
            `;
            philosopherBars.appendChild(row);
        }
    }
    
    // Rebuild DOM elements for philosophers and forks
    function rebuildTableElements(count) {
        
        // Remove existing nodes from dining area
        philosopherNodes.forEach(node => node.remove());
        forkNodes.forEach(node => node.remove());
        
        // Remove existing bowls
        const existingBowls = diningArea.querySelectorAll('.bowl-node');
        existingBowls.forEach(node => node.remove());
        
        philosopherNodes.length = 0;
        forkNodes.length = 0;
        
        // 1. Create Philosopher Nodes & Bowls
        for (let i = 0; i < count; i++) {
            const angleDeg = i * (360 / count) - 90; // Rotate -90deg so P1 starts at the top
            const angleRad = (angleDeg * Math.PI) / 180;
            
            const x = center.x + tableRadius * Math.cos(angleRad);
            const y = center.y + tableRadius * Math.sin(angleRad);
            
            const node = document.createElement('div');
            node.className = 'philosopher-node state-thinking';
            node.id = `philosopher-${i}`;
            node.style.left = `${x}px`;
            node.style.top = `${y}px`;
            
            node.innerHTML = `
                <div class="phi-avatar"><i class="fa-solid fa-user-tie"></i></div>
                <div class="phi-id">P${i+1}</div>
                <div class="phi-name" style="font-size:0.55rem; opacity:0.85; max-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Philosopher${i+1}</div>
                <div class="phi-state-text" id="phi-state-${i}">Thinking</div>
            `;
            
            diningArea.appendChild(node);
            philosopherNodes.push(node);

            // Create Bowl Node
            const R_bowl = tableRadius - 60;
            const bx = center.x + R_bowl * Math.cos(angleRad);
            const by = center.y + R_bowl * Math.sin(angleRad);
            
            const bowlNode = document.createElement('div');
            bowlNode.className = 'bowl-node';
            bowlNode.style.left = `${bx}px`;
            bowlNode.style.top = `${by}px`;
            bowlNode.innerHTML = `<div class="bowl-inner"></div>`;
            diningArea.appendChild(bowlNode);
        }
        
        // 2. Create Fork Nodes
        for (let i = 0; i < count; i++) {
            // Place forks exactly between philosophers
            const angleDeg = i * (360 / count) + (180 / count) - 90;
            const angleRad = (angleDeg * Math.PI) / 180;
            
            const x = center.x + (tableRadius - 35) * Math.cos(angleRad); // Shift slightly inward toward center
            const y = center.y + (tableRadius - 35) * Math.sin(angleRad);
            
            const node = document.createElement('div');
            node.className = 'fork-node';
            node.id = `fork-${i}`;
            node.style.left = `${x}px`;
            node.style.top = `${y}px`;
            node.innerHTML = `<i class="fa-solid fa-utensils"></i>`;
            
            // Store default coordinates for animations
            node.dataset.defaultX = x;
            node.dataset.defaultY = y;
            node.dataset.defaultAngle = angleDeg;
            
            diningArea.appendChild(node);
            forkNodes.push(node);
        }
        
        // 3. Initialize Stats Elements
        initializeStatsElements(count);
        
    }
    
    // Draw initial table with default 5 philosophers
    rebuildTableElements(5);
    
    // API State Polling Loop
    let pollInterval = setInterval(fetchState, 500);
    
    async function fetchState() {
        try {
            const response = await fetch('/state');
            if (!response.ok) throw new Error('API disconnected');
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('Error fetching state:', error);
        }
    }
    
    function updateUI(state) {
        const N = state.philosophers.length;
        
        // Dynamic self-healing if client philosopher count differs from server count
        if (N !== philosopherNodes.length) {
            rebuildTableElements(N);
            phiCountSelect.value = N.toString();
            return;
        }
        
        // 1. Update Mode Badge
        if (state.deadlock) {
            modeBadge.innerText = 'DEADLOCK DETECTED';
            modeBadge.className = 'header-badge deadlock';
        } else if (state.prevention) {
            modeBadge.innerText = 'PREVENTION MODE ACTIVE';
            modeBadge.className = 'header-badge prevention';
        } else {
            modeBadge.innerText = 'NORMAL MODE';
            modeBadge.className = 'header-badge';
        }
        
        // 2. Update Status Display Panel
        statusDisplay.className = 'status-banner';
        if (state.deadlock) {
            statusDisplay.classList.add('status-deadlock');
            statusText.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> DEADLOCK DETECTED: Circular wait condition reached!';
        } else if (state.prevention && state.running) {
            statusDisplay.classList.add('status-prevention');
            statusText.innerHTML = `<i class="fa-solid fa-shield-halved"></i> Prevention Mode Active (Max ${N - 1} Eating)`;
        } else if (state.running) {
            statusDisplay.classList.add('status-running');
            statusText.innerHTML = '<i class="fa-solid fa-play"></i> Simulation Running';
        } else if (state.paused) {
            statusDisplay.classList.add('status-paused');
            statusText.innerHTML = '<i class="fa-solid fa-pause"></i> Simulation Paused';
        } else {
            statusDisplay.classList.add('status-inactive');
            statusText.innerHTML = '<i class="fa-solid fa-circle-dot"></i> Simulation Stopped / Ready';
        }
        
        // 3. Update Controls active button states
        if (state.prevention) {
            btnPrevention.classList.add('active');
            btnDeadlock.classList.remove('active');
        } else {
            btnPrevention.classList.remove('active');
        }
        
        if (state.deadlock) {
            btnDeadlock.classList.add('active');
            btnPrevention.classList.remove('active');
        } else {
            btnDeadlock.classList.remove('active');
        }
        
        // 4. Update Philosopher Nodes
        state.philosophers.forEach(phi => {
            const node = philosopherNodes[phi.id];
            if (!node) return;
            
            const stateText = document.getElementById(`phi-state-${phi.id}`);
            
            // Reset state classes
            node.className = 'philosopher-node';
            
            // Set current state styling & text
            let stateClass = 'state-thinking';
            let text = 'Thinking';
            
            if (phi.state === 'HUNGRY') {
                stateClass = 'state-hungry';
                text = 'Hungry';
            } else if (phi.state === 'EATING') {
                stateClass = 'state-eating';
                text = 'Eating';
            } else if (phi.state === 'DEADLOCK') {
                stateClass = 'state-deadlock';
                text = 'Deadlock';
            }
            
            node.classList.add(stateClass);
            if (stateText) stateText.innerText = text;
            
            // Update Statistic Table values
            const mealLabel = document.getElementById(`meals-p${phi.id}`);
            const mealBar = document.getElementById(`bar-p${phi.id}`);
            
            if (mealLabel) mealLabel.innerText = phi.meals_eaten;
            
            if (mealBar) {
                // Set bar width based on percentage of highest count or fixed scale
                const maxMeals = Math.max(...state.philosophers.map(p => p.meals_eaten), 1);
                const percentage = (phi.meals_eaten / maxMeals) * 100;
                mealBar.style.width = `${percentage}%`;
            }
        });
        
        // Update Total Meals Count
        totalMealsCount.innerText = state.total_meals;
        
        // 5. Update Fork Nodes (Colors & Physical Picking Animation)
        state.forks.forEach(fork => {
            const node = forkNodes[fork.id];
            if (!node) return;
            
            if (fork.held_by !== null) {
                node.classList.add('allocated');
                
                const holdingPhiId = fork.held_by;
                const phiAngleDeg = holdingPhiId * (360 / N) - 90;
                const phiAngleRad = (phiAngleDeg * Math.PI) / 180;
                
                // Determine if this fork is the holding philosopher's left fork or right fork
                const isLeftFork = (fork.id === holdingPhiId);
                
                const R_bowl = tableRadius - 38; // Bowl radius (112px from center)
                const perpOffset = 22; // Offset distance to the left or right of the bowl
                
                const cosTheta = Math.cos(phiAngleRad);
                const sinTheta = Math.sin(phiAngleRad);
                
                // Perpendicular vector components
                const perpX = -sinTheta;
                const perpY = cosTheta;
                
                let x, y;
                if (isLeftFork) {
                    // Left of the bowl: Bowl Position - perpOffset * perpVector
                    x = center.x + R_bowl * cosTheta - perpOffset * perpX;
                    y = center.y + R_bowl * sinTheta - perpOffset * perpY;
                } else {
                    // Right of the bowl: Bowl Position + perpOffset * perpVector
                    x = center.x + R_bowl * cosTheta + perpOffset * perpX;
                    y = center.y + R_bowl * sinTheta + perpOffset * perpY;
                }
                
                node.style.left = `${x}px`;
                node.style.top = `${y}px`;
            } else {
                node.classList.remove('allocated');
                // Return to default position
                node.style.left = `${node.dataset.defaultX}px`;
                node.style.top = `${node.dataset.defaultY}px`;
            }
        });
    }
    
    // Command functions sending requests to backend
    async function sendCommand(url) {
        try {
            const response = await fetch(url, { method: 'POST' });
            const data = await response.json();
            updateUI(data.state);
        } catch (error) {
            console.error(`Error sending command to ${url}:`, error);
        }
    }
    
    // Event Listeners for simulation controls
    btnStart.addEventListener('click', () => sendCommand('/start'));
    btnPause.addEventListener('click', () => sendCommand('/pause'));
    btnReset.addEventListener('click', () => sendCommand('/reset'));
    btnDeadlock.addEventListener('click', () => sendCommand('/deadlock'));
    btnPrevention.addEventListener('click', () => sendCommand('/prevention'));
    
    // Event Listener for applying philosopher count
    btnApplyCount.addEventListener('click', async () => {
        const count = parseInt(phiCountSelect.value);
        if (isNaN(count) || count < 2 || count > 12) {
            alert('Please select a valid philosopher count between 2 and 12.');
            return;
        }
        
        try {
            const response = await fetch('/set_count', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ count: count })
            });
            if (!response.ok) throw new Error('Failed to update philosopher count');
            
            const data = await response.json();
            clearInterval(pollInterval);
            rebuildTableElements(count);
            updateUI(data.state);
            pollInterval = setInterval(fetchState, 500);
        } catch (error) {
            console.error('Error applying philosopher count:', error);
            alert('Error updating philosopher count. Please try again.');
        }
    });
});
