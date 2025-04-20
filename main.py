# run_tests.py

import json
import matplotlib.pyplot as plt
from scheduler import solve_sports_scheduling
import numpy as np
import random
import os

def load_test_cases(file_path):
    """
    Loads test cases from a JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found. Creating a default test cases file.")
        default_test_cases = [
            {
                "num_teams": 6,
                "strong": [1, 2],
                "medium": [3, 4],
                "weak": [5, 6]
            },
            {
                "num_teams": 8,
                "strong": [1, 2, 3],
                "medium": [4, 5],
                "weak": [6, 7, 8]
            }
        ]
        with open(file_path, 'w') as file:
            json.dump(default_test_cases, file, indent=4)
        return default_test_cases

def generate_random_test_case():
    """
    Generates a random test case for sports scheduling.
    """
    num_teams = random.randint(4, 10)  # Between 4 and 10 teams
    
    # Randomly divide teams into strong, medium, and weak categories
    teams = list(range(1, num_teams + 1))
    random.shuffle(teams)
    
    # Determine the number of teams in each category
    num_strong = max(1, num_teams // 3)
    num_medium = max(1, num_teams // 3)
    num_weak = num_teams - num_strong - num_medium
    
    strong_teams = teams[:num_strong]
    medium_teams = teams[num_strong:num_strong + num_medium]
    weak_teams = teams[num_strong + num_medium:]
    
    return {
        "num_teams": num_teams,
        "strong": strong_teams,
        "medium": medium_teams,
        "weak": weak_teams
    }

def generate_random_test_cases(num_cases=5):
    """
    Generates multiple random test cases.
    """
    return [generate_random_test_case() for _ in range(num_cases)]

def get_user_input_test_case():
    """
    Gets test case parameters from user input.
    """
    print("\n=== Create Your Own Test Case ===")
    
    while True:
        try:
            num_teams = int(input("Enter the number of teams (4-10): "))
            if 4 <= num_teams <= 10:
                break
            else:
                print("Number of teams must be between 4 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    teams = list(range(1, num_teams + 1))
    
    print(f"\nAvailable teams: {teams}")
    print("Assign teams to categories (strong, medium, weak).")
    
    strong_teams = []
    medium_teams = []
    weak_teams = []
    remaining_teams = teams.copy()
    
    # Get strong teams
    print("\nEnter strong teams (comma-separated, e.g., '1,3,5' or press Enter if none): ")
    strong_input = input().strip()
    if strong_input:
        strong_teams = [int(t) for t in strong_input.split(',') if t.strip().isdigit() and int(t) in remaining_teams]
        remaining_teams = [t for t in remaining_teams if t not in strong_teams]
    
    # Get medium teams
    print(f"\nRemaining teams: {remaining_teams}")
    print("Enter medium teams (comma-separated or press Enter if none): ")
    medium_input = input().strip()
    if medium_input:
        medium_teams = [int(t) for t in medium_input.split(',') if t.strip().isdigit() and int(t) in remaining_teams]
        remaining_teams = [t for t in remaining_teams if t not in medium_teams]
    
    # Assign remaining teams to weak
    weak_teams = remaining_teams
    
    print(f"\nTeam categories:")
    print(f"Strong teams: {strong_teams}")
    print(f"Medium teams: {medium_teams}")
    print(f"Weak teams: {weak_teams}")
    
    return {
        "num_teams": num_teams,
        "strong": strong_teams,
        "medium": medium_teams,
        "weak": weak_teams
    }

def solve_single_test_case(test_case):
    """
    Solves a single test case and returns results.
    """
    num_teams = test_case['num_teams']
    
    # Create the teams list and event list
    teams = list(range(1, num_teams + 1))
    events = [f"Match {i+1}" for i in range(num_teams // 2)]  # One match for each pair of teams
    
    # Create time slots
    time_slots = [f"Slot {i+1}" for i in range(num_teams)]
    
    # Costs are assigned arbitrarily
    costs = {event: 100 for event in events}
    
    # Team availability (all teams available for all time slots)
    team_availability = {f"Slot {i+1}": teams for i in range(len(time_slots))}
    
    # Event duration (each event has a duration of 1)
    event_duration = {event: 1 for event in events}
    
    # Solve the scheduling problem for this test case
    schedule, objective = solve_sports_scheduling(
        teams,
        events,
        time_slots,
        venue_capacity=2,  # Assuming a venue capacity of 2 teams
        costs=costs,
        team_availability=team_availability,
        event_duration=event_duration
    )
    
    # Initialize tracking dictionaries
    team_participation = {i: 0 for i in range(1, num_teams + 1)}
    event_distribution = {event: 0 for event in events}
    venue_utilization = {slot: 0 for slot in time_slots}
    
    # Update participation data
    for (team, event, time_slot), scheduled in schedule.items():
        if scheduled == 1:
            team_participation[team] += 1
            event_distribution[event] += 1
            venue_utilization[time_slot] += 1
    
    return {
        "test_case": test_case,
        "schedule": schedule,
        "objective": objective,
        "team_participation": team_participation,
        "event_distribution": event_distribution,
        "venue_utilization": venue_utilization
    }

def run_test_cases(test_cases):
    """
    Runs multiple test cases and returns results.
    """
    results = []
    
    # Initialize tracking dictionaries for all test cases
    max_team_num = max([tc['num_teams'] for tc in test_cases])
    team_participation = {i: 0 for i in range(1, max_team_num + 1)}
    
    max_events = max([tc['num_teams'] // 2 for tc in test_cases])
    event_distribution = {f"Match {i+1}": 0 for i in range(max_events)}
    
    max_slots = max([tc['num_teams'] for tc in test_cases])
    venue_utilization = {f"Slot {i+1}": 0 for i in range(max_slots)}
    
    for test_case in test_cases:
        result = solve_single_test_case(test_case)
        results.append(result)
        
        # Aggregate participation data for overall plotting
        for team, count in result["team_participation"].items():
            team_participation[team] += count
        
        for event, count in result["event_distribution"].items():
            event_distribution[event] += count
        
        for slot, count in result["venue_utilization"].items():
            venue_utilization[slot] += count
    
    return results, team_participation, event_distribution, venue_utilization

def evaluate_test_case(result):
    """
    Provides an evaluation for a test case based on the computed metrics.
    """
    test_case = result["test_case"]
    objective = result["objective"]
    team_participation = result["team_participation"]
    event_distribution = result["event_distribution"]
    venue_utilization = result["venue_utilization"]
    
    num_teams = test_case['num_teams']
    strong_teams = test_case['strong']
    medium_teams = test_case['medium']
    weak_teams = test_case['weak']
    
    print(f"\nEvaluating Test Case with {num_teams} Teams")
    print(f"Strong Teams: {strong_teams}, Medium Teams: {medium_teams}, Weak Teams: {weak_teams}")
    
    # Objective evaluation
    print(f"Total Objective Value (Cost): {objective}")
    if objective < 1000:
        print("Objective value is relatively low, indicating a good scheduling solution.")
    else:
        print("Objective value is high, indicating room for improvement in the scheduling optimization.")
    
    # Team participation evaluation
    max_participation = max(team_participation.values())
    max_team = max(team_participation, key=team_participation.get)
    print(f"Team Participation Distribution: {team_participation}")
    if max_participation <= 3:
        print("Team participation is well balanced, with no team overused.")
    else:
        print(f"Some teams are overused. Team {max_team} had the highest participation ({max_participation} times).")
    
    # Event distribution evaluation
    print(f"Event Distribution: {event_distribution}")
    events_overloaded = [event for event, count in event_distribution.items() if count > 2]
    if not events_overloaded:
        print("Events are well distributed across time slots.")
    else:
        print(f"The following events are overloaded: {events_overloaded}. Consider spreading them more evenly.")
    
    # Venue utilization evaluation
    print(f"Venue Utilization: {venue_utilization}")
    max_utilization = max(venue_utilization.values())
    max_slot = max(venue_utilization, key=venue_utilization.get)
    if max_utilization <= 2:
        print("Venue utilization is optimal, with each time slot efficiently used.")
    else:
        print(f"Some slots are underutilized or overutilized. Slot {max_slot} had the highest utilization ({max_utilization}).")

def plot_results(results, team_participation, event_distribution, venue_utilization):
    """
    Plots various metrics for evaluating the scheduling solution.
    """
    # Plot 1: Total cost (objective) vs. test cases
    objectives = [result["objective"] for result in results]
    test_case_labels = [f"Case {i+1}" for i in range(len(results))]
    
    plt.figure(figsize=(10, 6))
    plt.bar(test_case_labels, objectives, color='skyblue')
    plt.xlabel("Test Cases")
    plt.ylabel("Objective Value (Total Cost)")
    plt.title("Performance Evaluation of Sports Scheduling")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
    
    # Plot 2: Team participation distribution
    # Filter to only include teams that participated
    active_teams = {team: count for team, count in team_participation.items() if count > 0}
    teams = list(active_teams.keys())
    participations = list(active_teams.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(teams, participations, color='lightgreen')
    plt.xlabel("Team Number")
    plt.ylabel("Number of Participations")
    plt.title("Team Participation Distribution")
    plt.tight_layout()
    plt.show()
    
    # Plot 3: Event distribution across time slots
    # Filter to only include events that occurred
    active_events = {event: count for event, count in event_distribution.items() if count > 0}
    events = list(active_events.keys())
    event_counts = list(active_events.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(events, event_counts, color='salmon')
    plt.xlabel("Event")
    plt.ylabel("Number of Occurrences")
    plt.title("Event Distribution Across Time Slots")
    plt.tight_layout()
    plt.show()
    
    # Plot 4: Venue utilization across time slots
    # Filter to only include slots that were used
    active_slots = {slot: count for slot, count in venue_utilization.items() if count > 0}
    slots = list(active_slots.keys())
    slot_utilization = list(active_slots.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(slots, slot_utilization, color='lightcoral')
    plt.xlabel("Time Slot")
    plt.ylabel("Number of Events Scheduled")
    plt.title("Venue Utilization Across Time Slots")
    plt.tight_layout()
    plt.show()

def display_schedule(result):
    """
    Displays the schedule in a readable format.
    """
    schedule = result["schedule"]
    
    # Group by time slot
    slot_schedule = {}
    for (team, event, time_slot), scheduled in schedule.items():
        if scheduled == 1:
            if time_slot not in slot_schedule:
                slot_schedule[time_slot] = []
            slot_schedule[time_slot].append((team, event))
    
    print("\n=== Scheduled Events ===")
    for slot in sorted(slot_schedule.keys()):
        print(f"\n{slot}:")
        for team, event in slot_schedule[slot]:
            print(f"  Team {team} in {event}")

def main_menu():
    """
    Displays the main menu and handles user interaction.
    """
    while True:
        print("\n" + "="*50)
        print("SPORTS SCHEDULING OPTIMIZER - MAIN MENU")
        print("="*50)
        print("1. Run on randomly generated test cases and show analysis graphs")
        print("2. Run on a single random test case")
        print("3. Run on user input test case")
        print("4. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            num_cases = int(input("Enter the number of random test cases to generate (1-10): "))
            num_cases = min(max(1, num_cases), 10)  # Ensure between 1 and 10
            test_cases = generate_random_test_cases(num_cases)
            
            print(f"\nRunning {num_cases} random test cases...")
            results, team_participation, event_distribution, venue_utilization = run_test_cases(test_cases)
            
            for i, result in enumerate(results):
                print(f"\n--- Test Case {i+1} ---")
                evaluate_test_case(result)
                display_schedule(result)
            
            print("\nGenerating analysis graphs...")
            plot_results(results, team_participation, event_distribution, venue_utilization)
            
        elif choice == '2':
            test_case = generate_random_test_case()
            print("\nGenerated random test case:")
            print(f"Number of teams: {test_case['num_teams']}")
            print(f"Strong teams: {test_case['strong']}")
            print(f"Medium teams: {test_case['medium']}")
            print(f"Weak teams: {test_case['weak']}")
            
            print("\nSolving scheduling problem...")
            result = solve_single_test_case(test_case)
            
            evaluate_test_case(result)
            display_schedule(result)
            
            print("\nGenerating analysis graphs...")
            plot_results([result], 
                        result["team_participation"],
                        result["event_distribution"], 
                        result["venue_utilization"])
            
        elif choice == '3':
            test_case = get_user_input_test_case()
            
            print("\nSolving scheduling problem for your test case...")
            result = solve_single_test_case(test_case)
            
            evaluate_test_case(result)
            display_schedule(result)
            
            print("\nGenerating analysis graphs...")
            plot_results([result], 
                        result["team_participation"],
                        result["event_distribution"], 
                        result["venue_utilization"])
            
        elif choice == '4':
            print("\nExiting program. Thank you for using Sports Scheduling Optimizer!")
            break
            
        else:
            print("\nInvalid choice. Please enter a number between 1 and 4.")

# Main execution
if __name__ == "__main__":
    print("Welcome to Sports Scheduling Optimizer!")
    print("This program helps you create and analyze sports schedules.")
    
    # Check if scheduler module is available
    try:
        from scheduler import solve_sports_scheduling
        main_menu()
    except ImportError:
        print("\nError: The 'scheduler' module could not be imported.")
        print("Please ensure that 'scheduler.py' is in the same directory as this script.")
        print("This module should contain the 'solve_sports_scheduling' function.")