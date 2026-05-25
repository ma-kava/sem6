from blockworld import BlockWorldEnv
import random
import time

class QLearning():
	def __init__(self, env: BlockWorldEnv):
		self.env = env
		self.Q = {}

	def _get_q(self, state_key, action):
		return self.Q.get(state_key, {}).get(action, 0.0)

	def _set_q(self, state_key, action, value):
		if state_key not in self.Q:
			self.Q[state_key] = {}
		self.Q[state_key][action] = value

	def _max_q(self, state_key, actions):
		if not actions:
			return 0.0
		return max(self._get_q(state_key, a) for a in actions)

	def _state_key(self, s):
		return (s[0].get_state(), s[1].get_state())

	def _get_on_relations(self, conf):
		on = {}
		for stack in conf:
			on[stack[-1]] = 0
			for i in range(len(stack) - 1):
				on[stack[i]] = stack[i + 1]
		return on

	def _count_correct(self, current_conf, goal_conf):
		current_on = self._get_on_relations(current_conf)
		goal_on = self._get_on_relations(goal_conf)
		return sum(1 for b in current_on if current_on[b] == goal_on.get(b, -1))

	def _heuristic_action(self, s):
		current_state, goal_state = s[0], s[1]
		actions = current_state.get_actions()
		current_conf = current_state.get_state()
		goal_conf = goal_state.get_state()
		current_on = self._get_on_relations(current_conf)
		goal_on = self._get_on_relations(goal_conf)

		best_actions = []
		good_actions = []
		for (what, where) in actions:
			if goal_on.get(what) == where:
				if where == 0 or current_on.get(where) == goal_on.get(where):
					best_actions.append((what, where))
				else:
					good_actions.append((what, where))

		if best_actions: return random.choice(best_actions)
		if good_actions: return random.choice(good_actions)

		for (what, where) in actions:
			if where == 0 and current_on.get(what) != goal_on.get(what):
				return (what, where)

		return random.choice(actions)

	def train(self):
		alpha = 0.1
		gamma = 0.99
		num_episodes = 20000
		max_steps = 50
		epsilon_start = 1.0
		epsilon_end = 0.05
		epsilon_decay = epsilon_start - epsilon_end

		for episode in range(num_episodes):
			s, _ = self.env.reset()
			epsilon = max(epsilon_end, epsilon_start - epsilon_decay * episode / num_episodes)

			for step in range(max_steps):
				state_key = self._state_key(s)
				actions = s[0].get_actions()

				if random.random() < epsilon:
					if random.random() < 0.5:
						a = self._heuristic_action(s)
					else:
						a = random.choice(actions)
				else:
					best_q = self._get_q(state_key, actions[0])
					best_a = actions[0]
					for act in actions[1:]:
						q = self._get_q(state_key, act)
						if q > best_q:
							best_q = q
							best_a = act
					a = best_a

				s_, r, done, truncated, _ = self.env.step(a)

				before = self._count_correct(state_key[0], state_key[1])
				next_key = self._state_key(s_)
				after = self._count_correct(next_key[0], next_key[1])
				shaped_r = r + (after - before)

				next_actions = s_[0].get_actions()
				max_q_next = self._max_q(next_key, next_actions) if not done else 0.0

				old_q = self._get_q(state_key, a)
				new_q = old_q + alpha * (shaped_r + gamma * max_q_next - old_q)
				self._set_q(state_key, a, new_q)

				s = s_
				if done: break

	def act(self, s):
		state_key = self._state_key(s)
		actions = s[0].get_actions()

		if state_key in self.Q:
			best_q = self._get_q(state_key, actions[0])
			best_a = actions[0]
			for a in actions[1:]:
				q = self._get_q(state_key, a)
				if q > best_q:
					best_q = q
					best_a = a
			return best_a

		return self._heuristic_action(s)

if __name__ == '__main__':
	N = 4
	env = BlockWorldEnv(N)
	qlearning = QLearning(env)

	start = time.time()
	qlearning.train()
	print(f"Train time: {time.time() - start:.2f}s")

	test_env = BlockWorldEnv(N)
	test_problems = 1000
	solved = 0
	avg_steps = []

	for test_id in range(test_problems):
		s, _ = test_env.reset()
		done = False
		for step in range(50):
			a = qlearning.act(s)
			s_, r, done, truncated, _ = test_env.step(a)
			s = s_
			if done:
				solved += 1
				avg_steps.append(step + 1)
				break

	avg_steps = sum(avg_steps) / len(avg_steps) if avg_steps else float('inf')
	print(f"Solved {solved}/{test_problems} problems, with average number of steps {avg_steps}.")
