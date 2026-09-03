import random
from collections import deque


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """
    A Simple Reflex Agent that acts purely based on current percepts
    using direct Condition-Action (if-then) rules without storing history.
    """
    def sense_and_act(self, percept: dict) -> str:
        # Rule 1: IF food_here THEN Stay (eat food)
        if percept.get('food_here', False) or percept.get('smells_food', False):
            return 'Stay'
        # Rule 2: IF wall_ahead THEN turn Right
        if percept.get('wall_ahead', False) or percept.get('hit_wall', False):
            return 'Right'
        # Rule 3: ELSE move forward (Up)
        return 'Up'


class ModelBasedAgent:
    """
    A Model-Based Reflex Agent that maintains internal state / memory
    to record history of percepts and actions, allowing it to detect loops and escape traps.
    """
    def __init__(self):
        self.actions_pool = ['Up', 'Right', 'Down', 'Left']
        self.action_index = 0
        self.last_percept = None
        self.last_action = None
        self.history = []  # Internal memory state tracking (percept, action) pairs

    def sense_and_act(self, percept: dict) -> str:
        # Step 1: Update internal state (Transition & Sensor Model)
        self.history.append({'percept': percept, 'last_action': self.last_action})

        # Step 2: Check condition-action rules querying internal memory state
        if percept.get('food_here', False) or percept.get('smells_food', False):
            action = 'Stay'
        elif percept.get('wall_ahead', False) or percept.get('hit_wall', False) or percept == self.last_percept:
            self.action_index = (self.action_index + 1) % len(self.actions_pool)
            action = self.actions_pool[self.action_index]
        else:
            action = self.actions_pool[self.action_index]

        # Step 3: Record state for next turn
        self.last_percept = dict(percept)
        self.last_action = action
        return action


class SearchAgent:
    """
    A Problem-Solving Search Agent that uses Breadth-First Search (BFS)
    to compute an optimal (shortest) sequence of actions offline.
    """
    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        """
        Performs Breadth-First Search (BFS) to find the shortest path from start_pos to goal_pos.

        :param start_pos: Tuple (x, y) starting coordinate
        :param goal_pos: Tuple (x, y) goal coordinate
        :param walls: List or set of (x, y) wall coordinates
        :param grid_size: Tuple (width, height) specifying grid boundaries
        :return: List of action strings (e.g., ['Up', 'Right', ...]) or None/[] if unreachable
        """
        width, height = grid_size
        walls_set = set(walls)

        if start_pos == goal_pos:
            return []

        moves = [
            (0, 1, 'Up'),
            (0, -1, 'Down'),
            (-1, 0, 'Left'),
            (1, 0, 'Right')
        ]

        queue = deque([(start_pos, [])])
        visited = {start_pos}

        while queue:
            (curr_x, curr_y), path = queue.popleft()

            if (curr_x, curr_y) == goal_pos:
                return path

            for dx, dy, action in moves:
                nx, ny = curr_x + dx, curr_y + dy
                next_pos = (nx, ny)

                if 0 <= nx < width and 0 <= ny < height and next_pos not in walls_set:
                    if next_pos not in visited:
                        visited.add(next_pos)
                        queue.append((next_pos, path + [action]))

        return None