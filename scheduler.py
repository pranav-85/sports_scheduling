# scheduler.py

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

def solve_sports_scheduling(teams, events, time_slots, venue_capacity, costs, team_availability, event_duration):
    """
    Solves the sports scheduling problem using linear programming.

    Parameters:
    - teams (list): List of teams participating in the event.
    - events (list): List of sports events to schedule.
    - time_slots (list): Available time slots.
    - venue_capacity (int): Maximum number of teams that can play in the venue.
    - costs (list): List of costs for each team or event.
    - team_availability (dict): Availability of teams for each time slot.
    - event_duration (dict): Duration of each event.

    Returns:
    - schedule (dict): The optimal schedule of events and teams.
    - objective (float): The objective value (e.g., minimized cost, maximized matchups).
    """
    
    # Define the LP problem
    model = LpProblem(name="sports-scheduling", sense=LpMaximize)

    # Create decision variables: which team plays in which event at what time
    schedule_vars = {
        (team, event, time_slot): LpVariable(f"schedule_{team}_{event}_{time_slot}", cat="Binary")
        for team in teams for event in events for time_slot in time_slots
    }

    # Ensure each team is assigned to one event per time slot
    for team in teams:
        for time_slot in time_slots:
            model += lpSum(schedule_vars[(team, event, time_slot)] for event in events) == 1, f"team_{team}_time_slot_{time_slot}"

    # Ensure each event happens at one time slot with enough teams
    for event in events:
        for time_slot in time_slots:
            model += lpSum(schedule_vars[(team, event, time_slot)] for team in teams) <= venue_capacity, f"event_{event}_time_slot_{time_slot}"

    # Constraints for team availability
    for team in teams:
        for time_slot in time_slots:
            if team not in team_availability[time_slot]:
                for event in events:
                    model += schedule_vars[(team, event, time_slot)] == 0, f"team_{team}_not_available_{time_slot}"

    # Objective: Minimize cost or maximize the number of matches played
    model += lpSum(costs[event] * schedule_vars[(team, event, time_slot)] for team in teams for event in events for time_slot in time_slots), "Total_Cost"

    # Solve the problem
    model.solve()

    # Prepare result
    schedule = {
        (team, event, time_slot): schedule_vars[(team, event, time_slot)].value()
        for team in teams for event in events for time_slot in time_slots if schedule_vars[(team, event, time_slot)].value() == 1
    }
    objective = value(model.objective)

    return schedule, objective
