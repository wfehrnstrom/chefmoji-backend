from enum import Enum, unique
from functools import reduce
import unittest
from utils import eprint

from game_update_pb2 import MapUpdate

UP_KEYS = ['w', 'ArrowUp']
LEFT_KEYS = ['a', 'ArrowLeft']
DOWN_KEYS = ['s', 'ArrowDown']
RIGHT_KEYS = ['d', 'ArrowRight']
KEYS = [UP_KEYS, LEFT_KEYS, DOWN_KEYS, RIGHT_KEYS]
MOVE_KEYS = []
for key_set in KEYS:
	MOVE_KEYS.extend(key_set)

class CellBase(Enum):
    WALL = 1
    FRIDGE = 2
    FLOOR = 3
    TABLE = 4
    SINK = 5
    STOVE = 6
    CUTTING_BOARD = 7
    TURNIN = 8
    SOURCE = 9

    def to_str(self):
	    reps = ['W', 'F', ' ', 'T', 'r', '0', 'K', '>', '@']
	    assert len(list(CellBase)) == len(reps)
	    return reps[self.value-1]

    def collidable(self):
	    return self.name != 'FLOOR'

# Entities are inherently movable
@unique
class EntityType(Enum):
	# Ingredients
	BREAD = 1
	SAUSAGE = 2
	CHEESE = 3
	TOMATO = 4
	LETTUCE = 5
	ONION = 6
	BACON = 7
	RAW_PATTY = 8
	MILK = 9
	EGG = 10
	FLOUR = 11
	BUTTER = 12
	BEEF = 13
	FISH = 14
	RICE = 15
	SOUP = 16
	PORK = 17
	NOODLES = 18
	FISH_CAKE = 19
	POTATO = 20
	CARROT = 21
	GARLIC = 22
	PINEAPPLE = 23
	ORANGE = 24
	MANGO = 25
	SUSHI = 26
	# Prepared Items

	# Player 
	PLAYER = 27
	# Misc
	PLATE = 28

	def to_str(self):
		reps = ['🍞', '🍖', '🧀', '🍅', '🥬', '🧅', '🥓', '🥩', '🥛', '🥚', '🌾', '🧈', '🐄', '🐟', '🍚', '🍲', '🐖', '🍝', '🍥', '🥔', '🥕', '🧄', '🍍', '🍊', '🥭', '🍣', '🤓', '🍽️']
		assert len(list(EntityType)) == len(reps)
		return reps[self.value-1]

class Entity:
	def __init__(self, uid, loc, type):
		self.uid = uid
		self.loc = loc
		self.type = type

	def to_str(self):
		return self.type.to_str()

	def placeable_on(self, cell):
		return (cell.base.value != CellBase.WALL.value or cell.entity is None)

class GameCell:
	def __init__(self, base, entity=None):
		self.base = base
		self.entity = entity
	
	def to_str(self):
		if self.entity is not None:
			return self.entity.to_str()
		return self.base.to_str()
	
	def collidable(self):
		print(self.base.name)
		if self.entity:
			print(self.entity.type)
		return self.base.collidable() or (self.entity is not None)

	def place(self, entity):
		if self.entity is not None:
			eprint("Overwrote existing entity.")
		self.entity = entity

class Player(Entity):
	def __init__(self, uid, loc, game, seq=1):
		self.id = uid
		self.inventory = None
		self.loc = loc
		self.type = EntityType.PLAYER
		if seq == 1:
			self.emoji = '😎'
		elif seq == 2:
			self.emoji = '🧠'

	def move(self, key):
		if key in UP_KEYS:
			return [self.loc[0], self.loc[1]-1]
		if key in DOWN_KEYS:
			return [self.loc[0], self.loc[1]+1]
		if key in LEFT_KEYS:
			return [self.loc[0]-1, self.loc[1]]
		if key in RIGHT_KEYS:
			return [self.loc[0]+1, self.loc[1]]
		return self.loc

def default_map(entities = []):
	game_map = [
		[GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(0, (2,1), EntityType.BUTTER)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(1, (4,1), EntityType.EGG)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.SINK), GameCell(CellBase.TABLE), GameCell(CellBase.STOVE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.CUTTING_BOARD), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(2, (6,2), EntityType.MILK)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(3, (8,2), EntityType.FLOUR)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(4, (1,3), EntityType.CARROT)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(5, (6,4), EntityType.CHEESE)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(6, (8,4), EntityType.RICE)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(7, (1,5), EntityType.LETTUCE)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TURNIN), GameCell(CellBase.TURNIN)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(8, (1, 7), EntityType.TOMATO)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(9, (6, 7), EntityType.RAW_PATTY)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(12, (8, 7), EntityType.BREAD)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(10, (6,9), EntityType.FISH)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(11, (8,9), EntityType.ONION)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(15, (4,10), EntityType.PORK)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity(203, (10,10),EntityType.POTATO)), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity(1001, (12, 10), EntityType.GARLIC)), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity(390, (15, 10), EntityType.PLATE)), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL)]
	]
	for ent in entities:
		game_map[ent.loc[1]][ent.loc[0]].entity = ent
	return game_map

class GameState(Enum):
	QUEUEING = 1
	PLAYING = 2
	PAUSED = 3
	FINISHED = 4

class Map:
	def __init__(self, entities=[]):
		self.map = default_map(entities)

	def in_bounds(self, loc):
		assert len(loc) == 2
		if len(self.map) == 0:
			return False
		return (loc[0] >= 0 and loc[0] < len(self.map[0])) and (loc[1] >= 0 and loc[1] < len(self.map))
	
	def smooth(self):
		if len(self.map) < 1:
			return True
		prev_len = len(self.map[0])
		for row in self.map[1:]:
			if len(row) != prev_len:
				return False
			prev_len = len(row)
		return True

	def closed(self):
		closed_entities = [CellBase.WALL, CellBase.TABLE, CellBase.FRIDGE, CellBase.CUTTING_BOARD, CellBase.STOVE, CellBase.TURNIN, CellBase.SINK]
		for x in range(0, len(self.map[0])):
			if self.map[0][x].base not in closed_entities or self.map[len(self.map)-1][x].base not in closed_entities:
				return False
		for y in range(0, len(self.map)):
			if self.map[y][0].base not in closed_entities or self.map[y][len(self.map[0])-1].base not in closed_entities:
				return False
		return True

	def valid(self):
		return self.smooth() and self.closed()

	def to_str(self):
		return [reduce(lambda c1, c2: c1 + c2, [cell.to_str() for cell in row]) for row in self.map]

	def debug(self):
		for row in self.to_str():
			print(row)

	def cell(self, x, y=None):
		# tuple format (x,y)
		if y is None:
			y = x[1]
			x = x[0]
		assert y >= 0 and y < len(self.map)
		assert x >= 0 and x < len(self.map[y])
		return self.map[y][x]

	def move_entity_from_to(self, frm, to):
		if frm == to:
			return
		cell = self.cell(frm)
		new_cell = self.cell(to)
		if cell.entity is None or cell is new_cell:
			raise ValueError
		elif cell.entity.placeable_on(new_cell):
			new_cell.place(cell.entity)
			cell.place(None)
			new_cell.entity.loc = to

class Game:
	def __init__(self, session_id, player_ids=[], entities=[], state = GameState.QUEUEING):
		self.state = GameState.QUEUEING
		# same as room identifier used by socket.io
		self.session_id = session_id
		self.__init_map(player_ids, entities)
		# items can be picked up with the 'e' key
		self.entities = {"players": self.players, "items": [], }
		self.points = 0
		self.order_queue = []
		assert self.map.valid()
		assert len(self.players) == 1
	
	def __init_map(self, player_ids, entities):
		i = 0
		starting_locs = [[2,6], [13,6]]
		self.players = dict()
		for p_id in player_ids:
			self.players[p_id] = Player(p_id, starting_locs[i], self)
			i += 1
		self.map = Map([ self.players[player_ids[0]] ])
		assert len(player_ids) <= 2

	def valid_player_update(self, player_id, key):
		player = self.players[player_id]
		if key in MOVE_KEYS:
			new_loc = player.move(key)
			print("New location: ")
			print(new_loc)
			return not self.map.cell(new_loc[0], new_loc[1]).collidable()
		elif key == 'e':
			# TODO: Implement Item pickup and drop
			return True
		else:
			return False

	def update(self, player_id, key):
		assert self.valid_player_update(player_id, key)
		if not self.in_play():
			# in this case, update is a no-op
			return
		player = self.players[player_id]
		# update player location
		self.map.move_entity_from_to(player.loc, player.move(key))

	def serialize_into_pb(self):
		pb = MapUpdate()
		for row in self.map.to_str():
			pb.map.append(row)
		for p in self.players.values():
			player = pb.players.add()
			player.id = p.id
			player.position.append(p.loc[0])
			player.position.append(p.loc[1])
			if p.inventory is not None:
				player.inventory = p.inventory
		return pb.SerializeToString()
		# TODO: Implement order serialization

	def play(self):
		self.state = GameState.PLAYING

	def in_play(self):
		return self.state is GameState.PLAYING

	def has_player(self, pid):
		return pid in self.players

class TestGameMethods(unittest.TestCase):
	def test_map(self):
		m = Map()
		for x in range(0, len(m.map[0])):
			for y in range(0, len(m.map)):
				self.assertTrue(m.in_bounds([x, y]))
		self.assertFalse(m.in_bounds([-1, 0]))
		self.assertFalse(m.in_bounds([0, -1]))
		self.assertFalse(m.in_bounds([len(m.map[0]), 0]))
		self.assertFalse(m.in_bounds([0, len(m.map)]))
		self.assertFalse(m.in_bounds([len(m.map[0]), len(m.map)]))
		self.assertTrue(m.closed())
		self.assertTrue(m.smooth())
		self.assertTrue(m.valid())
	
if __name__ == '__main__':
	unittest.main()
