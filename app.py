from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Read stop schedule data from CSV
stop_schedules = pd.read_csv('stop_schedule.csv')

# Function to process stop schedules based on start and end stops
def process_stop_schedules(start_stop, end_stop):
    start_buses = stop_schedules[stop_schedules['Stop'] == start_stop]['Departure Time'].tolist()
    end_buses = stop_schedules[stop_schedules['Stop'] == end_stop]['Departure Time'].tolist()
    
    bus_schedules = []
    for start_entry in start_buses:
        for end_entry in end_buses:
            start_times = start_entry.split(', ')
            end_times = end_entry.split(', ')
            for start_time in start_times:
                start_bus_id, start_arrival_time = start_time.split(': ')
                for end_time in end_times:
                    end_bus_id, end_arrival_time = end_time.split(': ')
                    if start_bus_id == end_bus_id:
                        bus_schedules.append({'Bus ID': start_bus_id, 'Arrival Time': start_arrival_time})
    return bus_schedules

@app.route('/filter_stops', methods=['GET'])
def filter_stops():
    query = request.args.get('query', '')
    filtered_stops = stop_schedules[stop_schedules['Stop'].str.contains(query, case=False, na=False)]['Stop'].unique().tolist()
    return jsonify(filtered_stops)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        start_stop = request.form['start_stop']
        end_stop = request.form['end_stop']
        
        bus_schedules = process_stop_schedules(start_stop, end_stop)
        
        return render_template('index.html', start_stop=start_stop, end_stop=end_stop, bus_schedules=bus_schedules)
    return render_template('index.html')

@app.route('/contributors')
def contributors():
    contributors_info = [
        {
            'name': 'Osama Mehram',
            'email': '215193@aack.au.edu.pk',
            'description': 'Osama Mehram is a dedicated contributor with a passion for coding.',
            'image_path': '/static/osama.jpg'  
        },
        {
            'name': 'Umar Shahzad',
            'email': '215160@aack.au.edu.pk',
            'description': 'Umar Shahzad is a talented developer who enjoys solving complex problems.',
            'image_path': '/static/umar.jpeg'  
        },
        {
            'name': 'Rumaisa Fatima',
            'email': '215150@aack.au.edu.pk',
            'description': 'Rumaisa Fatima is a creative individual with a flair for design and development.',
            'image_path': '/static/rumaisa.png'  
        }
    ]
    return render_template('a.html', contributors=contributors_info)

if __name__ == '__main__':
    app.run(debug=True)
