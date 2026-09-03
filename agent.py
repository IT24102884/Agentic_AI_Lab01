# agent.py
from collections import deque
import heapq
import math
import random

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """A simple reflex agent using only current percepts and no memory."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Right'
        if percept.get('wall_ahead'):
            return 'Up'
        return 'Right'


class ModelBasedAgent:
    """A model-based agent that records percept history to avoid simple loops."""

    def __init__(self):
        self.visited_percepts = set()
        self.last_action = None
        self.last_percept = None

    def sense_and_act(self, percept: dict) -> str:
        current_state = (percept.get('wall_ahead'), percept.get('food_here'))

        if self.last_percept is not None and self.last_action is not None:
            self.visited_percepts.add((self.last_percept.get('wall_ahead'),
                                        self.last_percept.get('food_here'),
                                        self.last_action))

        if percept.get('food_here'):
            action = 'Right'
        elif percept.get('wall_ahead'):
            if (True, percept.get('food_here'), 'Left') in self.visited_percepts:
                action = 'Right'
            else:
                action = 'Left'
        else:
            if current_state in {(p[0], p[1]) for p in self.visited_percepts}:
                action = 'Up'
            else:
                action = 'Right'

        self.last_percept = percept.copy()
        self.last_action = action
        return action


class SearchAgent:
    """Search algorithms for planning paths through a static grid."""

    _MOVES = (
        ('Up', (0, 1)),
        ('Right', (1, 0)),
        ('Down', (0, -1)),
        ('Left', (-1, 0)),
    )

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        walls = {tuple(wall) for wall in walls}
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        heuristic = (self.euclidean_distance if heuristic_type == 'euclidean'
                     else self.manhattan_distance)
        reached_states = set()
        frontier = [(heuristic(start, goal), 0, start, [])]

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)
            if current_pos in reached_states:
                continue

            if current_pos == goal:
                return path_taken

            reached_states.add(current_pos)

            for next_pos, action in self._neighbors(current_pos, walls, grid_size):
                if next_pos not in reached_states:
                    new_g_cost = g_cost + 1
                    new_f_cost = new_g_cost + heuristic(next_pos, goal)
                    heapq.heappush(
                        frontier,
                        (new_f_cost, new_g_cost, next_pos, path_taken + [action])
                    )

        return None

    def _neighbors(self, position, walls, grid_size):
        width, height = grid_size
        x, y = position

        for action, (dx, dy) in self._MOVES:
            next_position = (x + dx, y + dy)
            if (0 <= next_position[0] < width and
                    0 <= next_position[1] < height and
                    next_position not in walls):
                yield next_position, action

    def sense_and_act(self, percept):
        if not self.plan:
            start_pos = tuple(percept['agent_pos'])
            food_positions = [tuple(food) for food in percept['all_food']]

            if not food_positions:
                return 'Stay'

            goal_pos = min(
                food_positions,
                key=lambda food: abs(food[0] - start_pos[0]) + abs(food[1] - start_pos[1])
            )
            search_methods = {
                'BFS': self.bfs_search,
                'DFS': self.dfs_search,
                'UCS': self.ucs_search,
                'AStar': self.astar_search,
            }
            search_method = search_methods.get(self.active_algo, self.bfs_search)
            self.plan = search_method(
                start_pos,
                goal_pos,
                percept['walls'],
                percept['grid_size']
            ) or []

        return self.plan.pop(0) if self.plan else 'Stay'

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = {tuple(wall) for wall in walls}
        reached = {tuple(start_pos)}
        frontier = deque([(tuple(start_pos), [])])

        while frontier:
            position, path = frontier.popleft()
            if position == tuple(goal_pos):
                return path

            for next_position, action in self._neighbors(position, walls, grid_size):
                if next_position not in reached:
                    reached.add(next_position)
                    frontier.append((next_position, path + [action]))

        return None

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = {tuple(wall) for wall in walls}
        reached = {tuple(start_pos)}
        frontier = [(tuple(start_pos), [])]

        while frontier:
            position, path = frontier.pop()
            if position == tuple(goal_pos):
                return path

            for next_position, action in self._neighbors(position, walls, grid_size):
                if next_position not in reached:
                    reached.add(next_position)
                    frontier.append((next_position, path + [action]))

        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = {tuple(wall) for wall in walls}
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        reached = set()
        frontier = [(0, 0, start, [])]
        queued = {start}
        entry_order = 1

        while frontier:
            cost, _, position, path = heapq.heappop(frontier)
            if position in reached:
                continue
            reached.add(position)

            if position == goal:
                return path

            for next_position, action in self._neighbors(position, walls, grid_size):
                if next_position not in queued:
                    queued.add(next_position)
                    heapq.heappush(
                        frontier,
                        (cost + 1, entry_order, next_position, path + [action])
                    )
                    entry_order += 1

        return None