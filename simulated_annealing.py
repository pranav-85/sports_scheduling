import numpy as np
import random
import math
import copy

class SportsScheduler:
    def __init__(self, num_teams=18, teams_strength=None, costs=None):
        self.num_teams = num_teams
        self.num_rounds = num_teams - 1
        
        # Define team strengths if not provided
        if teams_strength is None:
            # Default strength classification from the paper
            # 5 strong teams, 6 medium teams, 7 weak teams
            self.teams_strength = ['S'] * 5 + ['M'] * 6 + ['W'] * 7
        else:
            self.teams_strength = teams_strength
            
        # Define cost parameters
        # Format: (strong-strong, strong-medium, medium-strong, medium-medium)
        if costs is None:
            self.costs = {
                'S': (16, 4, 4, 2),    # Costs for strong teams
                'M': (32, 8, 8, 4),    # Costs for medium teams
                'W': (48, 12, 12, 6)   # Costs for weak teams
            }
        else:
            self.costs = costs
        
        # Initialize the schedule
        self.schedule = self.initialize_schedule()
        
    def initialize_schedule(self):
        """Create an initial valid round-robin tournament schedule."""
        # Fixed implementation to ensure correct schedule generation
        n = self.num_teams
        is_odd = n % 2 == 1
        
        if is_odd:
            n += 1  # Add a dummy team if odd
            
        # Initialize teams
        teams = list(range(n))
        
        # Generate rounds
        schedule = []
        for round_num in range(n - 1):
            round_matches = []
            for i in range(n // 2):
                home_team = teams[i]
                away_team = teams[n - 1 - i]
                
                # Skip matches involving dummy team (if added)
                if home_team < self.num_teams and away_team < self.num_teams:
                    round_matches.append((home_team, away_team))
            
            schedule.append(round_matches)
            
            # Rotate teams: keep first team fixed, rotate the rest
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]
        
        # Print initial schedule to debug
        print("Initial schedule created:")
        for r, round_matches in enumerate(schedule):
            print(f"Round {r+1}: {round_matches}")
        
        return schedule
    
    def get_opponent(self, team, round_matches):
        """Find the opponent of a team in a round."""
        for match in round_matches:
            if team in match:
                return match[0] if match[1] == team else match[1]
        return None  # Team doesn't play in this round
        
    def evaluate_cost(self, schedule):
        """Calculate the cost of the schedule."""
        total_cost = 0
        
        # For each team
        for team in range(self.num_teams):
            team_strength = self.teams_strength[team]
            
            # Check consecutive rounds
            for r in range(len(schedule) - 1):
                # Find opponent in current round
                current_opponent = self.get_opponent(team, schedule[r])
                
                # Find opponent in next round
                next_opponent = self.get_opponent(team, schedule[r + 1])
                
                # Skip if team doesn't play in either round (shouldn't happen in valid schedule)
                if current_opponent is None or next_opponent is None:
                    continue
                
                # Get strengths of opponents
                current_opp_strength = self.teams_strength[current_opponent]
                next_opp_strength = self.teams_strength[next_opponent]
                
                # Apply costs based on consecutive opponent patterns
                if current_opp_strength == 'S' and next_opp_strength == 'S':
                    # Strong vs Strong then Strong
                    if team_strength == 'S':
                        total_cost += self.costs['S'][0]
                    elif team_strength == 'M':
                        total_cost += self.costs['M'][0]
                    else:  # Weak team
                        total_cost += self.costs['W'][0]
                        
                elif current_opp_strength == 'S' and next_opp_strength == 'M':
                    # Strong vs Strong then Medium
                    if team_strength == 'S':
                        total_cost += self.costs['S'][1]
                    elif team_strength == 'M':
                        total_cost += self.costs['M'][1]
                    else:  # Weak team
                        total_cost += self.costs['W'][1]
                        
                elif current_opp_strength == 'M' and next_opp_strength == 'S':
                    # Strong vs Medium then Strong
                    if team_strength == 'S':
                        total_cost += self.costs['S'][2]
                    elif team_strength == 'M':
                        total_cost += self.costs['M'][2]
                    else:  # Weak team
                        total_cost += self.costs['W'][2]
                        
                elif current_opp_strength == 'M' and next_opp_strength == 'M':
                    # Strong vs Medium then Medium
                    if team_strength == 'S':
                        total_cost += self.costs['S'][3]
                    elif team_strength == 'M':
                        total_cost += self.costs['M'][3]
                    else:  # Weak team
                        total_cost += self.costs['W'][3]
                
        return total_cost
    
    def is_valid_schedule(self, schedule):
        """Check if a schedule is valid and print diagnostics."""
        # Print schedule being validated
        # print("Validating schedule:")
        # for r, round_matches in enumerate(schedule):
        #     print(f"Round {r+1}: {round_matches}")
        
        # Each team should play exactly once in each round
        for r in range(len(schedule)):
            teams_in_round = []
            for match in schedule[r]:
                teams_in_round.extend(match)
            
            # Count occurrences of each team in the round
            team_count = {}
            for team in teams_in_round:
                if team < self.num_teams:  # Skip dummy team if any
                    team_count[team] = team_count.get(team, 0) + 1
            
            # Each team should appear exactly once
            for team in range(self.num_teams):
                if team_count.get(team, 0) != 1:
                    print(f"Validation failed: Team {team} appears {team_count.get(team, 0)} times in round {r+1}")
                    return False
        
        # Each pair of teams should play exactly once
        played_matches = set()
        for r in range(len(schedule)):
            for match in schedule[r]:
                # Sort the match to ensure consistency
                sorted_match = tuple(sorted(match))
                if sorted_match in played_matches:
                    print(f"Validation failed: Match {sorted_match} played more than once")
                    return False
                played_matches.add(sorted_match)
        
        # Check that all required matches are scheduled
        total_matches = self.num_teams * (self.num_teams - 1) // 2
        if len(played_matches) != total_matches:
            print(f"Validation failed: Expected {total_matches} matches, found {len(played_matches)}")
            return False
        
        # print("Schedule is valid!")
        return True
    
    def generate_neighbor(self, schedule):
        """Generate a neighbor solution by swapping matches between rounds."""
        # Make a deep copy to avoid changing the original
        new_schedule = copy.deepcopy(schedule)
        
        # Try different neighborhood operations
        operation = random.choice([1, 2])
        
        if operation == 1:
            # Swap two matches between different rounds
            max_attempts = 20  # Limit attempts to find valid swap
            
            for _ in range(max_attempts):
                # Select two different rounds
                round1_idx = random.randint(0, len(new_schedule) - 1)
                round2_idx = random.randint(0, len(new_schedule) - 1)
                while round1_idx == round2_idx:
                    round2_idx = random.randint(0, len(new_schedule) - 1)
                
                # Select one match from each round
                match1_idx = random.randint(0, len(new_schedule[round1_idx]) - 1)
                match2_idx = random.randint(0, len(new_schedule[round2_idx]) - 1)
                
                match1 = new_schedule[round1_idx][match1_idx]
                match2 = new_schedule[round2_idx][match2_idx]
                
                # Check if swap would create duplicate teams in a round
                teams_in_round1 = set()
                teams_in_round2 = set()
                
                for idx, match in enumerate(new_schedule[round1_idx]):
                    if idx != match1_idx:
                        teams_in_round1.add(match[0])
                        teams_in_round1.add(match[1])
                
                for idx, match in enumerate(new_schedule[round2_idx]):
                    if idx != match2_idx:
                        teams_in_round2.add(match[0])
                        teams_in_round2.add(match[1])
                
                # Check if swap would create conflicts
                if (match2[0] in teams_in_round1 or match2[1] in teams_in_round1 or
                    match1[0] in teams_in_round2 or match1[1] in teams_in_round2):
                    continue  # Try again
                
                # Perform the swap
                new_schedule[round1_idx][match1_idx] = match2
                new_schedule[round2_idx][match2_idx] = match1
                break
        
        elif operation == 2:
            # Swap home/away status within the same match
            round_idx = random.randint(0, len(new_schedule) - 1)
            match_idx = random.randint(0, len(new_schedule[round_idx]) - 1)
            
            match = new_schedule[round_idx][match_idx]
            new_schedule[round_idx][match_idx] = (match[1], match[0])
        
        return new_schedule
    
    def simulated_annealing(self, initial_temp=1000, cooling_rate=0.95, iterations=100):
        """Apply simulated annealing to find a good schedule."""
        current_schedule = self.schedule
        
        # Verify initial schedule is valid
        print("Checking if initial schedule is valid...")
        if not self.is_valid_schedule(current_schedule):
            print("Warning: Initial schedule is not valid!")
            # Generate a new valid schedule
            self.schedule = self.initialize_schedule()
            current_schedule = self.schedule
            if not self.is_valid_schedule(current_schedule):
                print("Still cannot generate a valid schedule. Exiting.")
                return None, None
        
        current_cost = self.evaluate_cost(current_schedule)
        print(f"Initial schedule cost: {current_cost}")
        
        best_schedule = copy.deepcopy(current_schedule)
        best_cost = current_cost
        
        temp = initial_temp
        
        for i in range(iterations):
            # Generate a neighbor solution
            neighbor_schedule = self.generate_neighbor(current_schedule)
            
            # Check if still valid
            if not self.is_valid_schedule(neighbor_schedule):
                print(f"Warning: Generated an invalid neighbor at iteration {i}")
                continue
                
            neighbor_cost = self.evaluate_cost(neighbor_schedule)
            
            # Decide whether to accept the neighbor
            if neighbor_cost < current_cost:
                # Accept better solution
                current_schedule = neighbor_schedule
                current_cost = neighbor_cost
                
                # Update best solution if needed
                if current_cost < best_cost:
                    best_schedule = copy.deepcopy(current_schedule)
                    best_cost = current_cost
                    print(f"Iteration {i}: Found new best solution with cost {best_cost}")
            else:
                # Accept worse solution with a probability
                delta = neighbor_cost - current_cost
                probability = math.exp(-delta / temp)
                
                if random.random() < probability:
                    current_schedule = neighbor_schedule
                    current_cost = neighbor_cost
            
            # Cool down the temperature
            temp *= cooling_rate
            
            # Print progress periodically
            if (i+1) % 100 == 0:
                print(f"Iteration {i+1}: Current cost = {current_cost}, Best cost = {best_cost}, Temperature = {temp:.2f}")
        
        # Final validation
        print("Final validation of best schedule:")
        if not self.is_valid_schedule(best_schedule):
            print("Warning: Best schedule is not valid!")
        
        self.schedule = best_schedule
        return best_schedule, best_cost

# Function to test basic schedule generation
def test_schedule_generation(num_teams=18):
    print(f"Testing schedule generation with {num_teams} teams")
    
    # Create a scheduler
    scheduler = SportsScheduler(num_teams=num_teams)
    
    # Validate the initial schedule
    valid = scheduler.is_valid_schedule(scheduler.schedule)
    
    if valid:
        print(f"Successfully generated a valid schedule for {num_teams} teams!")
        # Print the initial schedule cost
        cost = scheduler.evaluate_cost(scheduler.schedule)
        print(f"Initial schedule cost: {cost}")
    else:
        print(f"Failed to generate a valid schedule for {num_teams} teams.")
    
    return scheduler

# Test with different numbers of teams
if __name__ == "__main__":
    # Test with the default 18 teams
    # print("=== Testing with 18 teams ===")
    # scheduler18 = test_schedule_generation(18)
    
    # # Test with an odd number of teams
    # print("\n=== Testing with 15 teams ===")
    # scheduler15 = test_schedule_generation(15)
    
    # Test with a small number of teams
    print("\n=== Testing with 6 teams ===")
    scheduler6 = test_schedule_generation(6)
    
    # Run a small optimization to verify the entire process
    print("\n=== Running simplified optimization with 8 teams ===")
    scheduler8 = SportsScheduler(num_teams=8, teams_strength=['S']*3 + ['M']*2 + ['W']*3)
    schedule, cost = scheduler8.simulated_annealing(initial_temp=500, cooling_rate=0.9, iterations=200)
    
    if schedule:
        print(f"Optimization successful! Final cost: {cost}")
    else:
        print("Optimization failed.")