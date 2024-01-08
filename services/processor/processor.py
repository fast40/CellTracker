from cell_tracker import experiments
from cell_tracker import tracker
import time

while True:
    for experiment_id, _, _ in experiments.get(exclude_completed=True, exclude_errors=True):
        experiment_directory_path = experiments.get_experiment_directory_path(experiment_id)

        csv_path = experiment_directory_path / 'results.csv'
        visualization_path = experiment_directory_path / 'visualization.png'

        tracker.process(experiment_id, csv_path, visualization_path)
    
    print('iteration done')
    
    time.sleep(5)
