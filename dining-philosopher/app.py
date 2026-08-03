from flask import Flask, render_template, jsonify, request
from simulation import SimulationManager

app = Flask(__name__)
# Initialize the thread-safe SimulationManager
sim_manager = SimulationManager()

@app.route('/')
def index():
    """Serves the main visualization page."""
    return render_template('index.html')

@app.route('/state', methods=['GET'])
def get_state():
    """Returns the current state of philosophers and forks in JSON format."""
    return jsonify(sim_manager.get_state())

@app.route('/start', methods=['POST'])
def start_sim():
    """Starts or resumes the simulation."""
    sim_manager.start()
    return jsonify({'status': 'started', 'state': sim_manager.get_state()})

@app.route('/pause', methods=['POST'])
def pause_sim():
    """Pauses the simulation."""
    sim_manager.pause()
    return jsonify({'status': 'paused', 'state': sim_manager.get_state()})

@app.route('/reset', methods=['POST'])
def reset_sim():
    """Resets the simulation, clearing all states."""
    sim_manager.reset()
    return jsonify({'status': 'reset', 'state': sim_manager.get_state()})

@app.route('/deadlock', methods=['POST'])
def deadlock_demo():
    """Forces the simulation into a deadlock condition."""
    sim_manager.enable_deadlock_demo()
    return jsonify({'status': 'deadlock_demo', 'state': sim_manager.get_state()})

@app.route('/prevention', methods=['POST'])
def toggle_prevention():
    """Toggles the deadlock prevention mode."""
    is_prevention = sim_manager.toggle_prevention_mode()
    return jsonify({
        'status': 'prevention_toggled',
        'prevention': is_prevention,
        'state': sim_manager.get_state()
    })

@app.route('/set_count', methods=['POST'])
def set_count():
    """Sets the number of philosophers and forks dynamically."""
    data = request.get_json()
    if not data or 'count' not in data:
        return jsonify({'error': 'Missing count parameter'}), 400
    
    try:
        count = int(data['count'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid count, must be integer'}), 400
        
    if not (2 <= count <= 12):
        return jsonify({'error': 'Count must be between 2 and 12'}), 400
        
    success = sim_manager.set_philosopher_count(count)
    if success:
        return jsonify({'status': 'count_updated', 'count': count, 'state': sim_manager.get_state()})
    else:
        return jsonify({'error': 'Failed to update philosopher count'}), 500

if __name__ == '__main__':
    # Use debug=False to prevent double-execution of background threads via the reloader
    app.run(host='127.0.0.1', port=5000, debug=False)
