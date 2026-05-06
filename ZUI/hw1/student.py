from blockworld import BlockWorld
from queue import PriorityQueue
from collections import defaultdict

class BlockWorldHeuristic(BlockWorld):
	def __init__(self, num_blocks=5, state=None):
		BlockWorld.__init__(self, num_blocks, state)

	def heuristic(self, goal):
		self_state = self.get_state()
		goal_state = goal.get_state()
		return 0.
	
	def henwas_heuristic(self, goal):
		self_state = self.get_state()
		goal_state = goal.get_state()
		sum_moves = 0

		for state in self_state:
			size = len(state) - 1
			flag = False  # turns True as soon as a foundation is broken
			
			# traverse from the ground to the top
			for i in range(size, -1, -1):
				block = state[i]
				
				if not flag:
					is_correctly_supported = False
					
					# find the block in the goal state
					for g_state in goal_state:
						if block in g_state:
							# height calculation
							curr_height = size - i
							goal_height = len(g_state) - g_state.index(block) - 1
							
							# It is only perfectly placed if the height matches AND
							# the entire slice of the stack from this block down to the ground matches.
							# (state[i:] gets the current block and everything below it)
							if curr_height == goal_height and state[i:] == g_state[g_state.index(block):]:
								is_correctly_supported = True
							break
					
					# If it's not supported correctly, the foundation is broken
					if not is_correctly_supported:
						flag = True 
						
				# if the flag was tripped by this block or any block below it, add to sum
				if flag:
					sum_moves += 1

		return sum_moves

class AStar():
	def reconstruct_path(self, path_dict, curr):
		action_list = []
		print(f'reconstructing path: {path_dict} | curr = {curr}')
				
		while curr in path_dict:
			parrent, action = path_dict[curr]
			action_list.append(action)
			curr = parrent
			
		action_list.reverse()
		return action_list

	def search(self, start, goal):
		curr = start
		gFnc = defaultdict(lambda: float('inf'))
		fFnc = defaultdict(lambda: float('inf'))
		path = dict()
		open = PriorityQueue()

		gFnc[curr] = 0
		fFnc[curr] = curr.henwas_heuristic(goal)
		open.put((fFnc[curr], curr))

		while not open.empty():
			fVal_curr, curr = open.get()
			# print(f"{fVal_curr} - {curr}")

			if curr == goal:
				return self.reconstruct_path(path, curr)

			for action, neighbor in curr.get_neighbors():
				gVal_neighbor = gFnc[curr] + 1 # gVal in this path we're now exploring
				if gVal_neighbor < gFnc[neighbor]: # new more efficient path to neighbor found
					path[neighbor] = (curr, action)
					# print(f"appending action {action}")
					gFnc[neighbor] = gVal_neighbor
					fFnc[neighbor] = neighbor.henwas_heuristic(goal) + gVal_neighbor

					open.put((fFnc[neighbor], neighbor))
		
		return None

if __name__ == '__main__':
	# Here you can test your algorithm. You can try different N values, e.g. 6, 7.
	N = 5

	start = BlockWorldHeuristic(N)
	goal = BlockWorldHeuristic(N)

	print("Searching for a path:")
	print(f"{start} -> {goal}")
	print()

	astar = AStar()
	path = astar.search(start, goal)

	if path is not None:
		print("Found a path:")
		print(path)

		print("\nHere's how it goes:")

		s = start.clone()
		print(s)

		for a in path:
			print(f"state: {s} | action: {a}")
			s.apply(a)
			print(s)

	else:
		print("No path exists.")

	print("Total expanded nodes:", BlockWorld.expanded)