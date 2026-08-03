# Dining Philosophers Problem Visualization

A premium, production-quality interactive visualization tool designed to demonstrate the **Dining Philosophers Problem**, a classic operating systems synchronization challenge. The application uses a Flask (Python) backend to simulate philosophers as concurrent threads competing for shared resources (forks), and a modern HTML5/CSS3/Vanilla JavaScript frontend to present real-time state changes and animations.

This project is tailored specifically for academic curriculum requirements (such as 4th-semester Operating Systems mini-projects) to explain concurrency, synchronization, deadlocks, and deadlock prevention.

---

## 🌟 Features

- **Circular Dining Table Visualization**: 5 philosophers and 5 forks arranged dynamically in a circular table using clean math-based HTML/CSS positioning.
- **Micro-Animations**: Custom animations representing the state transitions:
  - **Thinking**: Slow breathing/pulsing blue glow.
  - **Hungry**: Fast shaking yellow avatar indicating demand.
  - **Eating**: Enlarged emerald-green avatar with pulsating center.
  - **Deadlock**: Crimson-red shaking avatars showing a locked state.
- **Physical Fork Pickups**: Forks physically move towards the philosopher holding them when allocated.
- **Three Simulation Modes**:
  1. **Normal Mode**: Deadlock-free continuous execution where philosophers think, get hungry, eat, and release forks.
  2. **Deadlock Demo**: Artificially forces a deadlock condition using thread synchronization barriers. All philosophers acquire their left fork at once and block waiting for their right fork indefinitely, triggering a "DEADLOCK DETECTED" visual state.
  3. **Deadlock Prevention**: Restricts the maximum number of concurrent dining attempts to 4 using a semaphore mechanism (`MAX_ALLOWED = 4`). This breaks the circular wait condition, ensuring deadlock never occurs.
- **Live Statistics Panel**: Tracks individual meals eaten per philosopher and total meals served with dynamic bar charts.
- **Controls & Status Panels**: Complete control suite (Start, Pause, Reset, Deadlock Demo, Prevention Mode) communicating asynchronously (no page refreshes).

---

## 💻 Technology Stack

- **Backend**: Python 3, Flask, standard library `threading` (`threading.Thread`, `threading.Lock`, `threading.Semaphore`, `threading.Barrier`).
- **Frontend**: HTML5 semantic tags, Vanilla CSS3 (Custom Variables, Flexbox, Keyframes), Vanilla JavaScript (ES6, Fetch API, DOM manipulation).

---

## 📁 Folder Structure

```text
DiningPhilosophers/
│
├── app.py                  # Flask web server, API routes, and static file mapping
├── simulation.py           # Core simulation logic (Philosopher thread, locks, and SimulationManager)
├── requirements.txt        # Flask dependency specification
├── README.md               # Project documentation and study guide
│
├── templates/
│   └── index.html          # Dashboard page template
│
└── static/
    ├── style.css           # Custom stylesheets and responsive layout
    └── script.js           # Polls state and updates UI components dynamically
```

---

## 🚀 Setup & Run Instructions

### Prerequisites
- Python 3.8 or higher installed on your computer.

### Step 1: Clone or Navigate to the Directory
Ensure you are in the root directory where `app.py` is located.

```bash
cd DiningPhilosophers
```

### Step 2: Install Dependencies
Install the required packages using pip:

```bash
pip install -r requirements.txt
```

### Step 3: Run the Server
Launch the Flask development server:

```bash
python app.py
```

### Step 4: Access the Dashboard
Open your web browser and navigate to:

```text
http://localhost:5000
```

---

## 🔌 API Endpoints

- **`GET /`**: Serves the primary web dashboard.
- **`GET /state`**: Returns a JSON representation of the current simulation state.
  - **Sample Response**:
    ```json
    {
      "philosophers": [
        {"id": 0, "state": "THINKING", "meals_eaten": 3},
        {"id": 1, "state": "HUNGRY", "meals_eaten": 2},
        {"id": 2, "state": "EATING", "meals_eaten": 3},
        {"id": 3, "state": "THINKING", "meals_eaten": 2},
        {"id": 4, "state": "THINKING", "meals_eaten": 1}
      ],
      "forks": [
        {"id": 0, "held_by": null},
        {"id": 1, "held_by": 2},
        {"id": 2, "held_by": 2},
        {"id": 3, "held_by": null},
        {"id": 4, "held_by": null}
      ],
      "deadlock": false,
      "prevention": false,
      "running": true,
      "total_meals": 11
    }
    ```
- **`POST /start`**: Starts or resumes the philosopher threads.
- **`POST /pause`**: Pauses the state updates of all threads.
- **`POST /reset`**: Stops all threads, releases all locks, and clears all counters.
- **`POST /deadlock`**: Toggles simulation into Deadlock Demonstration mode.
- **`POST /prevention`**: Toggles Deadlock Prevention mode.

---

## 🎓 Operating Systems Concepts Used

1. **Synchronization**: Coordinating the execution of multiple concurrent threads that share a common address space and access resources. We coordinate the 5 philosopher threads to share 5 forks safely.
2. **Critical Section**: The section of code where a thread accesses a shared resource (eating while holding two forks). Only one philosopher can enter the critical section for a specific pair of forks at any time.
3. **Mutex / Locks**: Mutual Exclusion is enforced using `threading.Lock()` representing each fork. Only the thread that successfully acquires the lock can hold the fork and proceed.
4. **Deadlock**: A state in which a set of threads are blocked because each thread is holding a resource and waiting for another resource held by some other thread.
5. **Deadlock Prevention**: Methods to design resource allocation protocols such that at least one of the four necessary conditions for deadlock is broken. Here, we break the **Circular Wait** condition by limiting the maximum concurrent eaters to 4.

---

## ❓ Viva Questions and Answers

### Q1: What is synchronization?
**A:** Synchronization is a mechanism that coordinates the execution of concurrent threads or processes to ensure they do not access shared resources (like memory, variables, or hardware) simultaneously in an uncontrolled manner. Proper synchronization avoids race conditions and ensures data consistency.

### Q2: What is a critical section?
**A:** A critical section is a segment of code in a concurrent program that accesses shared resources (like variables, files, or ports) and must not be executed by more than one thread/process at a time. The entry and exit to critical sections are managed using synchronization primitives like Mutexes.

### Q3: Why does deadlock occur in the Dining Philosophers Problem?
**A:** Deadlock occurs when each of the 5 philosophers picks up their left fork (each philosopher holds 1 fork). At this point, all 5 forks are held. When they try to pick up their right fork, they find it is already held by their right-hand neighbor. They will all wait indefinitely for their neighbor to release the fork, resulting in a deadlock.

### Q4: What are the four conditions of deadlock?
**A:** According to Coffman's conditions, a deadlock can occur if and only if all four conditions hold simultaneously:
1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode (only one philosopher can hold a fork).
2. **Hold and Wait**: A process must hold at least one resource and wait for additional resources held by other processes (philosopher holds left fork, waits for right fork).
3. **No Preemption**: Resources cannot be forcibly taken from a process holding them (a philosopher's fork cannot be stolen by another).
4. **Circular Wait**: A closed loop of processes exists where each process holds resources needed by the next (P0 waits for P1's fork, P1 waits for P2's fork... P4 waits for P0's fork).

### Q5: How does prevention mode work in this simulation?
**A:** Prevention mode works by limiting the number of philosophers allowed to sit at the table or attempt fork acquisition simultaneously to 4 (using a Semaphore with `MAX_ALLOWED = 4`). Since there are 5 forks and at most 4 philosophers trying to acquire them, at least one philosopher is guaranteed to acquire two forks, eat, and release them, thereby breaking the **Circular Wait** condition.

---

## 🔮 Future Enhancements

- **Deadlock Detection & Recovery**: Instead of just preventing deadlock, let deadlock happen, detect it, and automatically preempt one of the forks to break the cycle.
- **Dining Philosophers with Chandy-Misra Algorithm**: Implement a completely distributed state machine that uses clean, message-passing token systems instead of locks.
- **Custom Speed Controls**: Add sliders to adjust the thinking and eating speed ranges in real time.

---

## 📸 Screenshots

*(Placeholder: Add your project screenshots here to visually showcase the circular dining table and active states).*
