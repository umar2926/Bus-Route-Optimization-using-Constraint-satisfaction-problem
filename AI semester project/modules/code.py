import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta

# Read CSV files
routes = pd.read_csv('routes.csv')
stops = pd.read_csv('stops.csv')
bus_times = pd.read_csv('bus_times.csv')

# Constants
total_buses = 40
time_per_km = 1.75  # Time in minutes per kilometer

# Function to get stop distances for each route
def distance_of_stops():
    distance_of_stops = []
    for route in routes['route_num']:
        route_distances = stops[stops['route_num'] == route]['distance'].tolist()
        distance_of_stops.append(route_distances)
    return distance_of_stops

# Function to get the number of stops in each route
def stops_in_route():
    route_num = routes['route_num']
    num_of_stops = []
    for route in route_num:
        num_of_stops.append(len(stops[stops['route_num'] == route]))
    return num_of_stops

# Function to distribute buses
def distribute_buses():
    num_of_stops = stops_in_route()
    num_of_up_buses = []
    num_of_down_buses = []
    total_stops = sum(num_of_stops)
    for i in range(len(num_of_stops)):
        bus_count = round((num_of_stops[i] * total_buses) / total_stops)
        num_of_up_buses.append(math.ceil(bus_count / 2))
        num_of_down_buses.append(math.floor(bus_count / 2))
    return num_of_up_buses, num_of_down_buses

# Function to convert bus times to datetime objects
def convert_bus_times():
    bus_times['time'] = bus_times.apply(lambda row: datetime.strptime(f"{int(row['hours']):02d}:{int(row['minutes']):02d}", "%H:%M"), axis=1)
    return bus_times.sort_values(by='time')  

# Function to initialize bus schedules for all buses
def initialize_buses(sorted_bus_times):
    bus_schedules = {}
    bus_id = 1
    for i, row in sorted_bus_times.iterrows():
        route_id = (bus_id - 1) % len(routes) + 1
        terminal_start = stops[stops['route_num'] == route_id]['sub_routes'].iloc[0]
        departure_time = row['time']
        bus_schedules[bus_id] = {
            'route_id': route_id,
            'current_stop': terminal_start,
            'next_stop_idx': 1,
            'arrival_time': departure_time,
            'stops_visited': [(terminal_start, departure_time)]
        }
        bus_id += 1
        if bus_id > total_buses:
            break
    return bus_schedules

# Function to move buses to the next stop and record their times
def move_buses(bus_schedules):
    stop_schedules = {}
    moved_buses = []
    while True:
        buses_to_move = [bus_id for bus_id, bus_data in bus_schedules.items() if bus_data['arrival_time'] <= datetime(1900, 1, 1, 22, 0)] 
        if not buses_to_move:
            break

        # If it's the first departure time, move all buses simultaneously
        if min(bus_data['arrival_time'] for bus_data in bus_schedules.values()) == datetime(1900, 1, 1, 7, 0):
            buses_to_move = list(bus_schedules.keys())

        for bus_id in buses_to_move:
            bus_data = bus_schedules[bus_id]
            route_id = bus_data['route_id']
            next_stop_idx = bus_data['next_stop_idx']
            route_stops = stops[stops['route_num'] == route_id]['sub_routes'].tolist()

            if next_stop_idx >= len(route_stops):
                del bus_schedules[bus_id]
                continue

            next_stop = route_stops[next_stop_idx]

            next_stop_key = (route_id, next_stop)
            if next_stop_key in stop_schedules:
                conflicting_buses = stop_schedules[next_stop_key]
                for conflicting_bus in conflicting_buses:
                    if conflicting_bus['arrival_time'] == bus_data['arrival_time']:
                        bus_data['arrival_time'] += timedelta(minutes=5)
                        break

            if next_stop_key not in stop_schedules:
                stop_schedules[next_stop_key] = []
            stop_schedules[next_stop_key].append({'bus_id': bus_id, 'arrival_time': bus_data['arrival_time']})

            distance_to_next_stop = distance_of_stops()[route_id - 1][next_stop_idx] * time_per_km
            bus_data['arrival_time'] += timedelta(minutes=distance_to_next_stop)
            bus_data['current_stop'] = next_stop
            bus_data['next_stop_idx'] += 1
            bus_data['stops_visited'].append((next_stop, bus_data['arrival_time']))

    return stop_schedules, bus_schedules, moved_buses

# Main execution
sorted_bus_times = convert_bus_times()
bus_schedules = initialize_buses(sorted_bus_times)
stop_schedules, _, _ = move_buses(bus_schedules)

# Check if there are buses in the schedule
if bus_schedules:
    first_departure_time = min(bus['arrival_time'] for bus in bus_schedules.values())

    while bus_schedules and first_departure_time <= datetime(1900, 1, 1, 22, 0):
        buses_to_move = [bus_id for bus_id, bus_data in bus_schedules.items() if bus_data['arrival_time'] == first_departure_time]

        stop_schedules, _, _ = move_buses(bus_schedules)
        first_departure_time = min(bus['arrival_time'] for bus in bus_schedules.values())

        print("Buses moved for departure time:", first_departure_time)
else:
    print("No buses in the schedule.")

# Create DataFrame for stop schedules and save to CSV
stop_schedule_data = {'Route ID': [], 'Stop': [], 'Departure Time': []}
for stop_key, buses_info in stop_schedules.items():
    route_id, stop = stop_key
    stop_schedule_data['Route ID'].append(route_id)
    stop_schedule_data['Stop'].append(stop)
    stop_schedule_data['Departure Time'].append(', '.join([f"Bus {info['bus_id']}: {info['arrival_time'].strftime('%H:%M:%S')}" for info in buses_info]))

stop_schedule_df = pd.DataFrame(stop_schedule_data)
stop_schedule_df.to_csv('stop_schedule.csv', index=False)
print("Stop schedules saved to 'stop_schedule.csv'")
