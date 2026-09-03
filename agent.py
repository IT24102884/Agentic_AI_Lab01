# agent.py
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    def __init__(self):
        self.actions = ['Up', 'Down', 'Left', 'Right']
        self.plan = []
        self.active_algo = 'BFS'

    def get_neighbors(self, state, grid_size, walls):
        x, y = state
        possible_moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]
        neighbors = []
        width, height = grid_size
        walls_set = set(walls)

        for action, position in possible_moves:
            nx, ny = position

            # Check grid boundaries
            if nx < 0 or nx >= width:
                continue

            if ny < 0 or ny >= height:
                continue

            # Check walls
            if position in walls_set:
                continue

            neighbors.append((position, action))

        return neighbors

    def bfs_search(self, start, goal, grid_size, walls):
        frontier = deque()
        frontier.append((start, []))
        reached = {start}

        while frontier:
            current, path = frontier.popleft()

            if current == goal:
                return path

            for neighbor, action in self.get_neighbors(current, grid_size, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    new_path = path + [action]
                    frontier.append((neighbor, new_path))

        return []

    def dfs_search(self, start, goal, grid_size, walls):
        frontier = []
        frontier.append((start, []))
        reached = {start}

        while frontier:
            current, path = frontier.pop()

            if current == goal:
                return path

            for neighbor, action in self.get_neighbors(current, grid_size, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    new_path = path + [action]
                    frontier.append((neighbor, new_path))

        return []

    def ucs_search(self, start, goal, grid_size, walls):
        frontier = []
        counter = 0
        heapq.heappush(frontier, (0, counter, start, []))
        reached = {}

        while frontier:
            cost, _, current, path = heapq.heappop(frontier)

            if current in reached and reached[current] <= cost:
                continue

            reached[current] = cost

            if current == goal:
                return path

            for neighbor, action in self.get_neighbors(current, grid_size, walls):
                new_cost = cost + 1
                new_path = path + [action]

                if neighbor not in reached or new_cost < reached[neighbor]:
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, neighbor, new_path))

        return []

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            agent_pos = tuple(percept['agent_pos'])
            all_food = percept['all_food']
            grid_size = percept['grid_size']
            walls = tuple(percept['walls'])

            if not all_food:
                return random.choice(self.actions)

            # Find the closest food (using Manhattan distance as a simple heuristic)
            def manhattan(p1, p2):
                return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

            closest_food = min(all_food, key=lambda f: manhattan(agent_pos, f))

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, grid_size, walls)
            
            if not self.plan:
                return random.choice(self.actions)

        return self.plan.pop(0)

