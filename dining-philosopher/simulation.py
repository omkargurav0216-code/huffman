import threading
import time
import random

# Philosopher States
THINKING = 'THINKING'
HUNGRY = 'HUNGRY'
EATING = 'EATING'
DEADLOCK = 'DEADLOCK'

class Fork:
    """Represents a fork in the dining philosophers problem."""
    def __init__(self, fork_id):
        self.id = fork_id
        self.lock = threading.Lock()
        self._held_by = None  # Philosopher ID or None
        self.lock_held = threading.Lock()

    @property
    def held_by(self):
        with self.lock_held:
            return self._held_by

    @held_by.setter
    def held_by(self, value):
        with self.lock_held:
            self._held_by = value

class Philosopher(threading.Thread):
    """Represents a single philosopher thread."""
    def __init__(self, phi_id, manager):
        super().__init__()
        self.id = phi_id
        self.manager = manager
        self._state = THINKING
        self._meals_eaten = 0
        self.daemon = True
        self.left_fork_idx = self.id
        self.right_fork_idx = (self.id + 1) % self.manager.phi_count
        self.running = True
        self.has_semaphore = False

    @property
    def state(self):
        with self.manager.state_lock:
            return self._state

    @state.setter
    def state(self, value):
        with self.manager.state_lock:
            self._state = value

    @property
    def meals_eaten(self):
        with self.manager.state_lock:
            return self._meals_eaten

    @meals_eaten.setter
    def meals_eaten(self, value):
        with self.manager.state_lock:
            self._meals_eaten = value

    def run(self):
        while self.running:
            # Check pause/resume state
            self.manager.check_paused(self.id)
            if not self.running:
                break

            # 1. THINKING
            self.state = THINKING
            self.manager.sleep_interactive(self, random.uniform(2.0, 4.0))

            if not self.running:
                break
            self.manager.check_paused(self.id)

            # 2. HUNGRY
            self.state = HUNGRY
            
            # Attempt to acquire forks
            acquired = self.manager.acquire_forks(self)
            if not acquired:
                continue

            if not self.running:
                self.manager.release_forks(self)
                break
            self.manager.check_paused(self.id)

            # 3. EATING
            self.state = EATING
            self.manager.sleep_interactive(self, random.uniform(2.0, 3.5))

            # 4. RELEASE FORKS & INCREMENT MEALS (if not stopped/reset during eating)
            self.manager.release_forks(self)

            if self.running:
                self.meals_eaten += 1
                self.manager.increment_total_meals()

            if not self.running:
                break
            self.manager.check_paused(self.id)

class SimulationManager:
    """Manages the lifecycle, threads, and parameters of the simulation."""
    def __init__(self, phi_count=5):
        # Use RLock for reentrancy to allow properties to query states thread-safely
        self.state_lock = threading.RLock()
        self.phi_count = phi_count
        self.forks = [Fork(i) for i in range(phi_count)]
        self.philosophers = []
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start unpaused
        
        self.dining_semaphore = threading.Semaphore(phi_count - 1)
        self.deadlock_barrier = threading.Barrier(phi_count)
        
        # State indicators
        self.is_running = False
        self.is_paused = False  # Track paused state explicitly
        self.prevention_mode = False
        self.deadlock_demo = False
        self.deadlock_detected = False
        self.total_meals = 0

    def set_philosopher_count(self, count):
        """Updates the philosopher count and resets the simulation cleanly."""
        if not (2 <= count <= 12):
            return False
        self.stop_and_clean_threads()
        with self.state_lock:
            self.phi_count = count
            self.forks = [Fork(i) for i in range(count)]
            self.dining_semaphore = threading.Semaphore(count - 1)
            self.deadlock_barrier = threading.Barrier(count)
            self.total_meals = 0
            self.prevention_mode = False
            self.deadlock_demo = False
            self.deadlock_detected = False
            self.is_running = False
            self.is_paused = False
        return True

    def start(self):
        """Starts or resumes the simulation."""
        with self.state_lock:
            if not self.is_running:
                self.is_running = True
                self.is_paused = False
                self.pause_event.set()
                if not self.philosophers:
                    self.deadlock_detected = False
                    self.philosophers = [Philosopher(i, self) for i in range(self.phi_count)]
                    for p in self.philosophers:
                        p.start()
            else:
                # Resume if currently paused
                if self.is_paused:
                    self.is_paused = False
                    self.pause_event.set()

    def pause(self):
        """Pauses the simulation."""
        with self.state_lock:
            if self.is_running and not self.is_paused:
                self.is_paused = True
                self.pause_event.clear()

    def reset(self):
        """Resets the simulation state and recreates threads."""
        self.stop_and_clean_threads()
        with self.state_lock:
            self.total_meals = 0
            self.prevention_mode = False
            self.deadlock_demo = False
            self.deadlock_detected = False
            self.is_running = False
            self.is_paused = False

    def enable_deadlock_demo(self):
        """Triggers the deadlock demonstration."""
        self.stop_and_clean_threads()
        with self.state_lock:
            self.deadlock_demo = True
            self.prevention_mode = False
            self.deadlock_detected = False
            self.is_running = True
            self.is_paused = False
            self.pause_event.set()
            
            # Recreate barrier specifically for active threads
            self.deadlock_barrier = threading.Barrier(self.phi_count)
            self.philosophers = [Philosopher(i, self) for i in range(self.phi_count)]
            for p in self.philosophers:
                p.start()

    def toggle_prevention_mode(self):
        """Toggles deadlock prevention mode."""
        with self.state_lock:
            current_running = self.is_running
            current_paused = self.is_paused
            self.prevention_mode = not self.prevention_mode
            self.deadlock_demo = False
            self.deadlock_detected = False

        self.stop_and_clean_threads()
        
        with self.state_lock:
            self.is_running = current_running
            self.is_paused = current_paused
            
            if self.is_running:
                if self.is_paused:
                    self.pause_event.clear()
                else:
                    self.pause_event.set()
                self.philosophers = [Philosopher(i, self) for i in range(self.phi_count)]
                for p in self.philosophers:
                    p.start()
            return self.prevention_mode

    def stop_and_clean_threads(self):
        """Signals stop, waits for joins outside the state lock, then recreates state."""
        # 1. Signal stop to all philosopher threads
        with self.state_lock:
            for p in self.philosophers:
                p.running = False
            
            self.pause_event.set()  # Unblock anyone waiting on pause
            
            # Abort barrier to unblock threads waiting on it
            try:
                self.deadlock_barrier.abort()
            except Exception:
                pass

        # 2. Join the threads cleanly outside the lock to prevent deadlock
        for p in self.philosophers:
            p.join(timeout=1.0)
            
        # 3. Recreate forks, synchronization primitives, and simulation state under lock
        with self.state_lock:
            self.forks = [Fork(i) for i in range(self.phi_count)]
            self.dining_semaphore = threading.Semaphore(self.phi_count - 1)
            self.deadlock_barrier = threading.Barrier(self.phi_count)
            self.philosophers = []

    def check_paused(self, phi_id):
        """Called by threads to check if they should block due to pause."""
        self.pause_event.wait()

    def sleep_interactive(self, philosopher, duration):
        """Allows threads to sleep in small chunks so they stay highly responsive to pause/stop/reset."""
        elapsed = 0.0
        step = 0.1
        while elapsed < duration:
            if not philosopher.running:
                break
            self.check_paused(philosopher.id)
            time.sleep(step)
            elapsed += step

    def increment_total_meals(self):
        """Thread-safe increment of total meals."""
        with self.state_lock:
            self.total_meals += 1

    def acquire_forks(self, philosopher):
        """Handles fork acquisition depending on the active simulation mode."""
        phi_id = philosopher.id
        left_fork = self.forks[philosopher.left_fork_idx]
        right_fork = self.forks[philosopher.right_fork_idx]

        if self.prevention_mode:
            # 1. Acquire the semaphore (MAX_ALLOWED = N - 1)
            acquired_sem = False
            while not acquired_sem:
                if not philosopher.running or not self.prevention_mode:
                    return False
                self.check_paused(phi_id)
                acquired_sem = self.dining_semaphore.acquire(timeout=0.1)
            
            philosopher.has_semaphore = True

            # 2. Acquire left fork
            left_acquired = False
            while not left_acquired:
                if not philosopher.running or not self.prevention_mode:
                    self.release_forks(philosopher)
                    return False
                self.check_paused(phi_id)
                left_acquired = left_fork.lock.acquire(timeout=0.1)
                
            left_fork.held_by = phi_id

            # 3. Acquire right fork
            right_acquired = False
            while not right_acquired:
                if not philosopher.running or not self.prevention_mode:
                    self.release_forks(philosopher)
                    return False
                self.check_paused(phi_id)
                right_acquired = right_fork.lock.acquire(timeout=0.1)

            right_fork.held_by = phi_id
            return True

        elif self.deadlock_demo:
            # 1. Acquire left fork
            left_acquired = False
            while not left_acquired:
                if not philosopher.running or not self.deadlock_demo:
                    return False
                self.check_paused(phi_id)
                left_acquired = left_fork.lock.acquire(timeout=0.1)

            left_fork.held_by = phi_id

            # 2. Synchronize all philosophers at the barrier to guarantee they all hold their left fork
            try:
                self.deadlock_barrier.wait()
            except threading.BrokenBarrierError:
                # Cleanup if barrier gets broken (e.g. on reset)
                left_fork.held_by = None
                try:
                    left_fork.lock.release()
                except RuntimeError:
                    pass
                return False

            # 3. Attempt right fork acquisition. This will block forever because neighbor holds it.
            # We use timeout loop so that threads can still be aborted/joined when resetting.
            right_acquired = False
            while not right_acquired:
                if not philosopher.running or not self.deadlock_demo:
                    left_fork.held_by = None
                    try:
                        left_fork.lock.release()
                    except RuntimeError:
                        pass
                    return False
                self.check_paused(phi_id)
                right_acquired = right_fork.lock.acquire(timeout=0.1)

            right_fork.held_by = phi_id
            return True

        else:
            # Normal Mode: Deadlock-free resource ordering (lower index first)
            first_idx = min(philosopher.left_fork_idx, philosopher.right_fork_idx)
            second_idx = max(philosopher.left_fork_idx, philosopher.right_fork_idx)
            first_fork = self.forks[first_idx]
            second_fork = self.forks[second_idx]

            # Acquire first fork (lower index)
            first_acquired = False
            while not first_acquired:
                if not philosopher.running or self.deadlock_demo or self.prevention_mode:
                    return False
                self.check_paused(phi_id)
                first_acquired = first_fork.lock.acquire(timeout=0.1)

            first_fork.held_by = phi_id

            # Acquire second fork (higher index)
            second_acquired = False
            while not second_acquired:
                if not philosopher.running or self.deadlock_demo or self.prevention_mode:
                    # Release first fork and return
                    first_fork.held_by = None
                    try:
                        first_fork.lock.release()
                    except RuntimeError:
                        pass
                    return False
                self.check_paused(phi_id)
                second_acquired = second_fork.lock.acquire(timeout=0.1)

            second_fork.held_by = phi_id
            return True

    def release_forks(self, philosopher):
        """Releases the locks held by a philosopher and releases any semaphore."""
        left_fork = self.forks[philosopher.left_fork_idx]
        right_fork = self.forks[philosopher.right_fork_idx]

        # Release right fork
        if right_fork.held_by == philosopher.id:
            right_fork.held_by = None
            try:
                right_fork.lock.release()
            except RuntimeError:
                pass

        # Release left fork
        if left_fork.held_by == philosopher.id:
            left_fork.held_by = None
            try:
                left_fork.lock.release()
            except RuntimeError:
                pass

        # Release semaphore if it was acquired
        if philosopher.has_semaphore:
            philosopher.has_semaphore = False
            try:
                self.dining_semaphore.release()
            except ValueError:
                pass

    def check_deadlock(self):
        """Detects whether the simulation has entered a deadlock state."""
        if self.deadlock_detected:
            return True

        if self.deadlock_demo and len(self.philosophers) == self.phi_count:
            # Deadlock occurs if all philosophers are HUNGRY and all forks are held
            all_hungry = all(p.state in [HUNGRY, DEADLOCK] for p in self.philosophers)
            all_forks_held = all(f.held_by is not None for f in self.forks)
            
            if all_hungry and all_forks_held:
                self.deadlock_detected = True
                # Set all philosophers to DEADLOCK state for visual feedback
                for p in self.philosophers:
                    p.state = DEADLOCK
                return True
                
        return False

    def get_state(self):
        """Returns the JSON-compatible representation of the simulation state."""
        with self.state_lock:
            # Check deadlock status dynamically before building state
            deadlock_active = self.check_deadlock()
            
            philosophers_data = []
            for p in self.philosophers:
                philosophers_data.append({
                    'id': p.id,
                    'state': p.state,
                    'meals_eaten': p.meals_eaten
                })
            
            # If simulation hasn't started, fill in default states
            if not self.philosophers:
                philosophers_data = [{'id': i, 'state': THINKING, 'meals_eaten': 0} for i in range(self.phi_count)]
                
            forks_data = []
            for f in self.forks:
                forks_data.append({
                    'id': f.id,
                    'held_by': f.held_by
                })

            return {
                'philosophers': philosophers_data,
                'forks': forks_data,
                'deadlock': deadlock_active,
                'prevention': self.prevention_mode,
                'running': self.is_running and not self.is_paused,
                'paused': self.is_paused,
                'total_meals': self.total_meals
            }
