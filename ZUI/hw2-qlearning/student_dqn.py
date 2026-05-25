
import numpy as np
import os
import json
import random
import torch

from dataclasses import dataclass
from argparse import ArgumentParser
from itertools import count
from typing import Iterable,Tuple


from blockworld import BlockWorldEnv
from dqn_networks import DQNNetwork
from replay_buffer import ReplayBuffer


#Arguments to control which experiment will be run. Do not modify these!
parser = ArgumentParser()
parser.add_argument("--num_blocks", type=int, default=5, help="How many blocks to allow in our BlockWorld instance.")
parser.add_argument("--model_restore_path", type=str, default="checkpoints", help="Path from where to restore a stored model. Used only for DQN")
parser.add_argument("--restore_episode", type=int, default=-1, help="An episode of the stored model to restore. If <=0, the model is trained from scratch. Used only for DQN")
parser.add_argument("--no_train", action='store_true', help="If this flag is supplied, no training is performed and the model is run as is.")
parser.add_argument("--test_problems", type=int, default=1000, help="How many problems to test the learner on.")


@dataclass
class DQNConfig:
    #Do not delete these! But you can play with the values.
    #PRNG seed, to get consistent results.
    seed: int = 42
    #Minibatch size
    batch_size: int = 128
    #Network parameters
    hidden_features: int = 256
    #Every C steps reset target network: Q_hat = Q
    target_update_freq: int = 1000
    #Overall learning rate
    lr: float = 3e-4
    #Replay buffer parameters
    replay_capacity: int = 50000
    #A prioritized replay trick. Since our
    # environment normally has sparse rewards (only positive reward for correct solution).
    # it is quite hard task for the network to learn. We maintain a separate buffer
    # for the terminal steps, which actually give us our reward.
    # This ratio defines the fraction of the size of the
    # terminal-only buffer w.r.t. the normal buffer.
    # For details, look at the ReplayBuffer implementation.
    replay_terminal_ratio: float = 0.1
    #How many environment episodes to run
    num_episodes: int = 1000
    #How often to checkpoint the model. It will be saved at the interval of episodes defined by this.
    save_interval: int = 100
    # --- Custom parameters ---
    #Discount factor
    gamma: float = 0.99
    # epsilon-greedy parameters
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay_episodes: int = 4000
    # Max steps per training episode
    max_steps: int = 500

class DQN():
	# don't modify the methods' signatures!
  def __init__(self, env: BlockWorldEnv, config: DQNConfig, N: int):
    """Class handling the Deep Q-learning algorithm, for better scaling than
    tabular version in BlockWorld.

    Args:
        env (BlockWorldEnv): The BlockWorldEnvironment
        config (DQNConfig): Configuration containing all parameters required by DQN
        N (int): Number of blocks in the blockworld. We need this to determine action space size.
    """
    self.num_blocks = N
    self.env = env
    self.config = config
    #If interested you can try training on GPU too, but it requires a compatible torch installation.
    self.device = torch.device('cpu')
    self.config = config
    self.env = env

    self.steps_done = 0
    self.episodes = 0

    self.memory = ReplayBuffer(config.replay_capacity, config.replay_terminal_ratio)

    #Fix the random seed, for reproducibility
    self.rng = np.random.default_rng(config.seed)
    torch.manual_seed(config.seed)

    #For the neural network, we require a fixed
    # size input/output.
    # State representation: for each block (1..N), one-hot encode what it stands on.
    # "stands on" can be: ground (0) or any of the N blocks => N+1 categories.
    # encode both state and goal => 2 * N * (N+1)
    self.state_dim = 2 * N * (N + 1)
    #For actions, we can move every element at any other element (except itself)
    # and ground. That means N actions for each element, however not all
    # of them will always be legal. We will have to employ legal action masking
    self.n_actions = N * N

    self.q_net = DQNNetwork(self.state_dim, self.n_actions, config.hidden_features)
    self.target_net = DQNNetwork(self.state_dim, self.n_actions, config.hidden_features)
    self.target_net.load_state_dict(self.q_net.state_dict())

    # A standard Mean squared error loss.
    self.criterion = torch.nn.MSELoss()

    #Recommended to use the Adam optimizer.
    self.optimizer = torch.optim.Adam(self.q_net.parameters(), self.config.lr)

  def _get_on_relations(self, block_world_state):
    """Extract 'stands on' relations from a BlockWorldStochastic state.

    Returns a dict: block -> what_it_stands_on (0 for ground)
    """
    on = {}
    for stack in block_world_state.state:
      for i, block in enumerate(stack):
        if i == len(stack) - 1:
          # bottom of stack, stands on ground
          on[int(block)] = 0
        else:
          # stands on the block below it in the stack
          on[int(block)] = int(stack[i + 1])
    return on

  def _encode_world(self, block_world_state):
    """One-hot encode the 'stands on' relations for a single world state.

    Returns a tensor of size N * (N+1)
    """
    N = self.num_blocks
    encoding = torch.zeros(N * (N + 1))
    on = self._get_on_relations(block_world_state)
    for block in range(1, N + 1):
      stands_on = on.get(block, 0)
      # Index: (block-1) * (N+1) + stands_on
      idx = (block - 1) * (N + 1) + stands_on
      encoding[idx] = 1.0
    return encoding

  def train(self):
    config = self.config
    for i_episode in range(config.num_episodes):
      raw_state, info = self.env.reset()

      #This is how to pre-compute tensors and add a batch dimension of 1
      state = self.state_to_tensor(raw_state).unsqueeze(0)
      #Our legal action mask
      mask = self.create_legal_mask(raw_state[0].get_actions()).unsqueeze(0)

      # Compute epsilon for this episode
      frac = min(1.0, self.episodes / max(1, config.epsilon_decay_episodes))
      epsilon = config.epsilon_start + (config.epsilon_end - config.epsilon_start) * frac

      for t in count():
        # Select action with epsilon-greedy
        action_tuple = self._select_action(raw_state, state, mask, epsilon)

        raw_next_state, reward, terminated, truncated, _ = self.env.step(action_tuple)
        #This is how to convert to a torch tensor.
        reward_tensor = torch.tensor([reward], device=self.device, dtype=torch.float)
        #Add reward shaping term
        reward_shaping = self.compute_reward_shaping(raw_state, raw_next_state)
        reward_tensor += reward_shaping

        # Convert action to network index for storage
        action_idx = self._action_to_index(action_tuple)
        action_tensor = torch.tensor([[action_idx]], device=self.device, dtype=torch.long)

        if terminated:
            next_state = None
            next_mask = None
        else:
            # Pre-compute next state tensors
            next_state = self.state_to_tensor(raw_next_state).unsqueeze(0)
            next_mask = self.create_legal_mask(raw_next_state[0].get_actions()).unsqueeze(0)

        # Store transition in replay buffer
        self.memory.push(state, mask, action_tensor, next_state, next_mask, reward_tensor)

        state = next_state
        raw_state = raw_next_state
        mask = next_mask
        self.steps_done += 1

        #optimize network
        self._optimize()

        # Every C steps reset target network: Q_hat = Q
        if self.steps_done % config.target_update_freq == 0:
          self.target_net.load_state_dict(self.q_net.state_dict())

        if terminated or t >= config.max_steps:
            self.episodes += 1
            print(f"Finished episode {self.episodes}. Performed {t + 1} steps. Epsilon: {epsilon:.3f}")
            if config.save_interval > 0 and self.episodes % config.save_interval == 0:
                save_model(self, self.episodes)
            break

    print('Complete')

  def _action_to_index(self, action_tuple):
    """Convert (what, where) action to flat network index."""
    what, where = action_tuple
    row_offset = (what - 1) * self.num_blocks
    col_offset = where - int(where > what)
    return row_offset + col_offset

  def _select_action(self, raw_state, state_tensor, mask_tensor, epsilon):
    """Epsilon-greedy action selection."""
    if self.rng.random() < epsilon:
      return random.choice(raw_state[0].get_actions())
    else:
      with torch.no_grad():
        q_values = self.q_net(state_tensor, mask_tensor)
        action_idx = q_values.argmax(dim=1).item()
      return self.network_action_to_action(action_idx)

  def _optimize(self):
    """Perform one step of DQN optimization."""
    config = self.config
    if len(self.memory) < config.batch_size:
      return

    transitions = self.memory.sample(config.batch_size, self.rng)

    # Separate terminal and non-terminal transitions
    non_terminal_mask = torch.tensor(
      [t.next_state is not None for t in transitions],
      device=self.device, dtype=torch.bool
    )

    state_batch = torch.cat([t.state for t in transitions])
    mask_batch = torch.cat([t.mask for t in transitions])
    action_batch = torch.cat([t.action for t in transitions])
    reward_batch = torch.cat([t.reward for t in transitions])

    # crrent Q-vals for chosen actions
    current_q = self.q_net(state_batch, mask_batch).gather(1, action_batch)

    # Compute target Q-vals
    next_q = torch.zeros(config.batch_size, device=self.device)
    if non_terminal_mask.any():
      non_terminal_next_states = torch.cat([t.next_state for t in transitions if t.next_state is not None])
      non_terminal_next_masks = torch.cat([t.next_mask for t in transitions if t.next_mask is not None])
      with torch.no_grad():
        next_q[non_terminal_mask] = self.target_net(
          non_terminal_next_states, non_terminal_next_masks
        ).max(1).values

    # Bellman target
    target_q = reward_batch + config.gamma * next_q

    # Compute loss
    loss = self.criterion(current_q.squeeze(), target_q)

    # Optimize
    self.optimizer.zero_grad()
    loss.backward()
    self.optimizer.step()

  def state_to_tensor(self, state) ->torch.Tensor:
    """Convert a state of the BlockWorld environment into a flat tensor.

    Args:
        state (_type_): The state tuple provided by the BlockWorld

    Returns:
        torch.Tensor: A torch suitable flat representation of the state.
    """
    # Encode both the current state and goal as one-hot "stands on" vectors
    current_encoding = self._encode_world(state[0])
    goal_encoding = self._encode_world(state[1])
    state_tensor = torch.cat([current_encoding, goal_encoding])
    return state_tensor

  def create_legal_mask(self, actions: Iterable) ->torch.Tensor:
    """Create a mask of legal actions in the given state,
    to be represented as just a binary vector, like the
    network expects it.

    Args:
        actions (Iterable): An iterable of (where, what) actions
        as returned by the environment

    Returns:
        torch.Tensor: The binary vector as torch Tensor.
    """
    all_actions = np.zeros(self.n_actions)
    for (what, where) in actions:
      row_offset = (what - 1) * self.num_blocks
      #Compensate for the fact, that we
      # cannot move a block upon itself.
      # So, blocks with a higher
      # number than our block will have index one higher
      # in the action map than we want it to
      col_offset = where - int(where > what)
      all_actions[row_offset + col_offset] = 1
    return torch.tensor(all_actions, dtype=torch.bool)

  def compute_reward_shaping(self, state, next_state) -> float:
    """Computes the reward shaping when moving from state to next_state
    This serves to help the DQN drive the search to promising space,
    as just the standard spare reward of -0.1 or 10 makes the task much harder.

    Args:
        state: The current environment state
        next_state: The environment state we transitioned to.

    Returns:
        float: The reward shaping component, that will be added up to the original reward.
    """
    # count how many blocks sit on the correct block/ground (matching goal)
    before = self._count_correct(state[0], state[1])
    after = self._count_correct(next_state[0], next_state[1])
    # +1 for each newly correct placement, -1 for each broken one
    return float(after - before)

  def _count_correct(self, current_state, goal_state):
    """Count blocks whose 'on' relation matches the goal."""
    current_on = self._get_on_relations(current_state)
    goal_on = self._get_on_relations(goal_state)
    return sum(1 for b in range(1, self.num_blocks + 1)
               if current_on.get(b, -1) == goal_on.get(b, -2))

  def network_action_to_action(self, network_action: np.ndarray) ->Tuple[int, int]:
    """Convert action index returned by the network Q-values back to the
    environment (what, where) tuple

    Args:
        network_action (torch.Tensor| np.ndarray): Index of the chosen action

    Returns:
        Tuple[int, int]: A (what, where) tuple, as provided by the environment
    """
    network_action = int(network_action)
    #Blocks are 1 indexed, so add 1
    what = (network_action // self.num_blocks) + 1
    where = network_action % self.num_blocks
    #Moving a block upon itself is illegal,
    # so if the where index is >= our what index
    # we must add 1 to get the correct block
    where += (where >= what)
    return (what, where)

  def act(self, state):
    """Return an action to play in a given state (greedy, no exploration)."""
    state_tensor = self.state_to_tensor(state).unsqueeze(0)
    mask = self.create_legal_mask(state[0].get_actions()).unsqueeze(0)
    with torch.no_grad():
      q_values = self.q_net(state_tensor, mask)
      action_idx = q_values.argmax(dim=1).item()
    return self.network_action_to_action(action_idx)



def load_model(model_dir: str, N: int) -> 'DQN':
		"""Restore a model from a directory containing config.json, q_net.pt and target_net.pt."""
		# Load config from JSON (safe, no pickle)
		with open(os.path.join(model_dir, "config.json"), 'r') as f:
			config_dict = json.load(f)
		config = DQNConfig(**config_dict)

		env = BlockWorldEnv(N)
		model = DQN(env, config, N)

		model.q_net.load_state_dict(
				torch.load(os.path.join(model_dir, "q_net.pt"), weights_only=True,
											map_location=model.device))
		model.target_net.load_state_dict(
				torch.load(os.path.join(model_dir, "target_net.pt"), weights_only=True,
											map_location=model.device))
		print(f"Loaded weights from '{model_dir}/'")
		return model

def save_model(model: DQN, episode: int, save_dir: str = "checkpoints") -> None:
		"""Save policy and target network weights to disk."""
		os.makedirs(save_dir, exist_ok=True)
		#Save the static information, config and environment.
		# Save only once, if it does not exist yet
		config_path = os.path.join(save_dir, f"config.json")
		env_path = os.path.join(save_dir, f"env_spec.pt")
		if not os.path.exists(config_path):
				# Save config as JSON (safe format, no pickle needed)
				with open(config_path, 'w') as f:
					json.dump(vars(model.config), f, indent=2)
		if not os.path.exists(env_path):
				torch.save(model.num_blocks, env_path)
		#Save the rng states
		torch.save((model.rng.bit_generator.state, torch.get_rng_state()), os.path.join(save_dir, f"rng_states_ep{episode}.pt"))
		#Save the replay buffer state, optional.
		#torch.save(model.memory.getstate(), os.path.join(save_dir, f"replay_buffer_ep{episode}.pt"))
		#Save the weights
		torch.save(model.q_net.state_dict(),
								os.path.join(save_dir, f"q_net_ep{episode}.pt"))
		torch.save(model.target_net.state_dict(),
								os.path.join(save_dir, f"target_net_ep{episode}.pt"))
		print(f"Saved weights at episode {episode} to '{save_dir}/'")


def nn_learner_setup(N: int, model_dir: str = None):
	env = BlockWorldEnv(N)
	if model_dir:
		learner = load_model(model_dir, N)
	else:
		config = DQNConfig()
		learner = DQN(env, config, N)
	return learner

if __name__ == '__main__':

	args = parser.parse_args()
	if args.restore_episode > 0 and args.model_restore_path:
		qlearning = nn_learner_setup(args.num_blocks, args.model_restore_path)
	else:
		qlearning = nn_learner_setup(args.num_blocks)

	# Train
	if not args.no_train:
		qlearning.train()

	# Evaluate
	test_env = BlockWorldEnv(args.num_blocks)

	test_problems = args.test_problems
	solved = 0
	avg_steps = []

	for test_id in range(test_problems):
		s, _ = test_env.reset()
		done = False

		print(f"\nProblem {test_id}:")
		print(f"{s[0]} -> {s[1]}")

		for step in range(50): 	# max 50 steps per problem
			a = qlearning.act(s)
			print(f"{a}: {s[0]}")
			s_, r, done, truncated, _ = test_env.step(a)


			s = s_

			if done:
				solved += 1
				avg_steps.append(step + 1)
				break

	avg_steps = sum(avg_steps) / len(avg_steps) if avg_steps else float('inf')
	print(f"Solved {solved}/{test_problems} problems, with average number of steps {avg_steps}.")
