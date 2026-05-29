import ox
from ox import Board
import random, time
import numpy as np
import math

class Node:
	def __init__(self, board, parent, c=1.414):
		self.board = board
		self.parent = parent
		self.visits = 0
		self.wins = 0
		self.children = None
		self.c = c # exploration constant

	def get_children(self):
		if self.board.is_terminal():
			return []

		# expansion
		if self.children is None:
			ch = []
			for a in self.board.get_actions():
				b = self.board.clone()
				b.apply_action(a)
				n = Node(b, self, self.c) 
				ch.append((a, n))
			self.children = ch

		return self.children

	def get_child(self, action):
		if self.children is None: 
			return None

		for a, n in self.children:
			if a == action:
				return n
		return None		 

	def is_fully_expanded(self):
		if self.children is None:
			return False
		
		for action, child in self.children:
			if child.visits == 0:
				return False
				
		return True
	
class MCTS:
	def __init__(self, root: Node, play_as: int, time_limit: float):
		self.root = root
		self.play_as = play_as
		self.time_limit = time_limit

	def _ucb1(self, child_tuple):
		action, node = child_tuple
        
		if node.visits == 0:
			return float('inf')

		if node.parent is None or node.parent.visits == 0:
			return 0

		exploitation = node.wins / node.visits
		exploration = node.c * math.sqrt(math.log(node.parent.visits) / node.visits)

		return exploitation + exploration

	def search(self):
		t = time.time()
		
		while (time.time() - t) < self.time_limit:
			leaf = self._select(self.root)
			child = self._expand(leaf)
			winner_id = self._rollout(child)
			self._backpropagate(child, winner_id)
			
		best_action = None
		max_visits = -1
		
		for action, child in self.root.get_children():
			if child.visits > max_visits:
				max_visits = child.visits
				best_action = action
				
		return best_action

	def _select(self, node: Node):
		curr = node
		while curr.is_fully_expanded() and not curr.board.is_terminal():	
			best_child_tuple = max(curr.get_children(), key=self._ucb1)
			curr = best_child_tuple[1]

		return curr

	def _expand(self, node: Node):
		if node.board.is_terminal():
			return node

		children = node.get_children()
		for a, ch in children:
			if ch.visits == 0:
				return ch
				
		return node

	def _rollout(self, node: Node):
		board = node.board.clone()
		
		while not board.is_terminal():
			actions = board.get_actions()
			board.apply_action(random.choice(list(actions)))
			
		return board.get_rewards()

	def _backpropagate(self, node, rewards):
		curr = node
		while curr is not None:
			curr.visits += 1
			
			if curr.parent is not None:
				player_who_moved = curr.parent.board.current_player()
				raw_reward = rewards[player_who_moved]
				normalized_reward = (raw_reward + 1.0) / 2.0
				curr.wins += normalized_reward
					
			curr = curr.parent

class MCTSBot:
    """Enhanced MCTS bot that reuses the search tree between moves."""
    def __init__(self, play_as: int, time_limit: float):
        self.play_as = play_as
        self.time_limit = time_limit * 0.95
        self.root = None

    def play_action(self, board):
        # Try to reuse the existing tree by finding the subtree
        # matching the current board (after opponent's move)
        reused = False
        if self.root is not None and self.root.children is not None:
            for action, child in self.root.children:
                if str(child.board) == str(board):
                    self.root = child
                    self.root.parent = None
                    reused = True
                    break

        if not reused:
            self.root = Node(board.clone(), parent=None)

        self.alg = MCTS(self.root, self.play_as, self.time_limit)
        action = self.alg.search()

        # Descend to the chosen child so we can reuse the subtree next turn
        child_node = self.root.get_child(action)
        if child_node is not None:
            self.root = child_node
            self.root.parent = None
        else:
            self.root = None

        return action

class MCTSBot2:
    """Simple MCTS bot that rebuilds the tree from scratch every move."""
    def __init__(self, play_as: int, time_limit: float):
        self.play_as = play_as
        self.time_limit = time_limit * 0.95

    def play_action(self, board):
        root_node = Node(board.clone(), parent=None)
        self.alg = MCTS(root_node, self.play_as, self.time_limit)
        action = self.alg.search()

        return action

if __name__ == '__main__':
	board = ox.Board(8)  # 8x8
	bots = [MCTSBot(0, 0.1), MCTSBot(1, 1.0)]

	# try your bot against itself
	while not board.is_terminal():
		current_player = board.current_player()
		current_player_mark = ox.MARKS_AS_CHAR[ ox.PLAYER_TO_MARK[current_player] ]

		current_bot = bots[current_player]
		a = current_bot.play_action(board)
		board.apply_action(a)

		print(f"{current_player_mark}: {a} -> \n{board}\n")