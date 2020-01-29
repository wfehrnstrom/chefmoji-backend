from enum import Enum, unique
from functools import reduce
import unittest

from game_update_pb2 import MapUpdate

class CellBase(Enum):
    WALL = 1
    FRIDGE = 2
    FLOOR = 3
    TABLE = 4
    SINK = 5
    STOVE = 6
    CUTTING_BOARD = 7
    TURNIN = 8

    def to_str(self):
	    reps = ['W', 'F', ' ', 'T', 'r', '0', 'K', '>']
	    assert len(list(CellBase)) == len(reps)
	    return reps[self.value-1]

# Entities are inherently movable
@unique
class Entity(Enum):
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
		assert len(list(Entity)) == len(reps)
		return reps[self.value-1]

class GameCell:
	def __init__(self, base, entity_id=None):
		self.base = base
		self.entity = entity_id
	
	def to_str(self):
		if self.entity is not None:
			return self.entity.to_str()
		return self.base.to_str()


DEFAULT_MAP = [
		[GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity.BUTTER), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity.EGG), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.SINK), GameCell(CellBase.TABLE), GameCell(CellBase.STOVE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.CUTTING_BOARD), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity.MILK), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity.FLOUR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity.CARROT), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity.CHEESE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity.RICE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity.LETTUCE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TURNIN), GameCell(CellBase.TURNIN)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity.TOMATO), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity.RAW_PATTY), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity.BREAD), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity.FISH), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity.ONION), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity.PORK), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity.POTATO), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity.GARLIC), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity.PLATE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL)]
	]

class GameState(Enum):
	QUEUEING = 1
	STARTED = 2
	PAUSED = 3
	FINISHED = 4

class Map:
	def __init__(self):
		self.map = DEFAULT_MAP

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


class Player:
	def __init__(self, id, loc, game):
		self.id = id
		self.inventory = None
		assert game.map.in_bounds(loc)
		self.loc = loc

class IngredientCollection:
	pass

class Order:
	def __init__(self, output, ingredients):
		pass

class Game:
	def __init__(self, session_id, player_ids=[], entities=[]):
		self.state = GameState.QUEUEING
		# same as room identifier used by socket.io
		self.session_id = session_id
		self.players = dict()
		assert len(player_ids) <= 2
		starting_locs = [[3,6], [13,6]]
		i = 0
		for id in player_ids:
			self.players[id] = Player(id, starting_locs[i], self)
			i += 1
		# items can be picked up with the 'e' key
		self.entities = {"players": self.players, "items": [], }
		self.map = Map()
		assert self.map.valid()
		self.points = 0
		self.order_queue = []

	def serialize_into_pb(self):
		pb = MapUpdate()
		for row in self.map.to_str():
			pb.map.append(row)
		for p in self.players:
			player = pb.players.add()
			player.id = p.id
			player.position.append(p.loc[0])
			player.position.append(p.loc[1])
			if p.inventory is not None:
				player.inventory = p.inventory
		return pb.SerializeToString()
		# TODO: Implement order serialization

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
