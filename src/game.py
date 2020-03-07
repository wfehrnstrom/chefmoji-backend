from enum import Enum, unique
from functools import reduce, partial
import unittest
from utils import eprint
from order import Order, QueuedOrder, ORDER_TTL
from threading import Timer, Thread, Event
import random
import time
import json
from collections import Counter
from protocol_buffers.game_update_pb2 import MapUpdate, MapRow, PlayerUpdate, StationUpdate, InventoryUpdate, OrderType

UP_KEYS = ['w', 'ArrowUp']
LEFT_KEYS = ['a', 'ArrowLeft']
DOWN_KEYS = ['s', 'ArrowDown']
RIGHT_KEYS = ['d', 'ArrowRight']
KEYS = [UP_KEYS, LEFT_KEYS, DOWN_KEYS, RIGHT_KEYS]
MOVE_KEYS = []
for key_set in KEYS:
	MOVE_KEYS.extend(key_set)

@unique
class CellBase(Enum):
    WALL = 1
    FRIDGE = 2
    FLOOR = 3
    TABLE = 4
    TRASH = 5
    STOVE = 6
    CUTTING_BOARD = 7
    TURNIN = 8
    PLATE = 9

    def to_str(self):
	    reps = ['W', 'F', 'G', 'T', 'T🗑️', 'T♨️', 'T🔪', 'T➡️', 'T🍽️']
	    assert len(list(CellBase)) == len(reps)
	    return reps[self.value-1]
		
    def is_station(self):
	    reps = [False, False, False, False, True, True, True, True, True]
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
	HOT_WATER = 26
	# Prepared Items

	# Player 
	PLAYER = 27

	def to_str(self):
		reps = ['🍞', '🍖', '🧀', '🍅', '🥬', '🧅', '🥓', '🥩', '🥛', '🥚', '🌾', '🧈', '🐄', '🐟', '🍚', '🍲', '🐖', '🍝', '🍥', '🥔', '🥕', '🧄', '🍍', '🍊', '🥭', '🍵', '🤓']
		assert len(list(EntityType)) == len(reps)
		return reps[self.value-1]
	
	def needs_to_be_chopped(self):
		reps = [False, False, False, True, True, True, False, False, False, False, False, False, True, True, False, False, True, False, False, True, True, True, True, True, True, False, False]
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
			return self.base.to_str() + self.entity.to_str()
		return self.base.to_str()
	
	def collidable(self):
		return self.base.collidable() or (self.entity is not None)

	def place(self, entity):
		if self.entity is not None and entity is not None:
			eprint("Overwrote existing entity.")
		self.entity = entity

class Inventory:
	def __init__(self, item=None, plated=False, cooked=False, chopped=False):
		self.item = item
		self.plated = plated
		self.cooked = cooked
		self.chopped = chopped
	
	def is_choppable(self):
		if isinstance(self.item, EntityType):			
			return self.item.needs_to_be_chopped()
		return False
			

class Player(Entity):
	def __init__(self, uid, loc, game, seq):
		self.id = uid
		self.inventory = Inventory()
		self.loc = loc
		self.type = EntityType.PLAYER
		self.seq = seq

	def to_str(self):
		reps = ['😎', '🧠']
		return reps[self.seq]

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
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(0, (2,1), EntityType.BUTTER)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(1, (4,1), EntityType.EGG)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity(56, (11,2), EntityType.HOT_WATER)), GameCell(CellBase.TABLE), GameCell(CellBase.STOVE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.CUTTING_BOARD), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(2, (6,2), EntityType.MILK)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(3, (8,2), EntityType.FLOUR)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(4, (1,3), EntityType.CARROT)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(3, (8,3), EntityType.NOODLES)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(5, (6,4), EntityType.CHEESE)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(6, (8,4), EntityType.RICE)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(7, (1,5), EntityType.LETTUCE)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TURNIN), GameCell(CellBase.TURNIN)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(8, (1, 7), EntityType.TOMATO)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(9, (6, 7), EntityType.RAW_PATTY)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(12, (8, 7), EntityType.BREAD)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE, Entity(151, (1,9), EntityType.FISH_CAKE)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FRIDGE, Entity(10, (6,9), EntityType.FISH)), GameCell(CellBase.WALL), GameCell(CellBase.TABLE, Entity(11, (8,9), EntityType.ONION)), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.FLOOR), GameCell(CellBase.TRASH), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(151, (2,10), EntityType.SAUSAGE)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE, Entity(15, (4,10), EntityType.PORK)), GameCell(CellBase.FRIDGE), GameCell(CellBase.FRIDGE), GameCell(CellBase.WALL), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity(203, (10,10),EntityType.POTATO)), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE, Entity(1001, (12, 10), EntityType.GARLIC)), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.PLATE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.TABLE), GameCell(CellBase.WALL)],
		[GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL), GameCell(CellBase.WALL)]
	]
	for ent in entities:
		game_map = add_entity_to_default_map(game_map, ent)
	return game_map

def add_entity_to_default_map(map, entity):
	map[entity.loc[1]][entity.loc[0]].entity = entity
	return map


@unique
class GameState(Enum):
	QUEUEING = 1
	PLAYING = 2
	PAUSED = 3
	FINISHED = 4

class Map:
	def __init__(self, players=[]):
		self.map = default_map(players)

	def remove_entity(self, loc=None):
		if self.in_bounds(loc):	
			self.map[loc[1]][loc[0]].entity = None
		
	def add_entity(self, entity, loc=None):
		if loc is None:
			loc = entity.loc
			if loc is None:
				eprint("Entity unable to be added because no location was specified.")
				return
		elif (self.entity_at(loc)):
			eprint("Entity would overwrite existing entity. Refusing to add.")
			return
		add_entity_to_default_map(self.map, entity)

	def entity_at(self, loc):
		c = self.cell(loc)
		return c and c.entity is not None

	def in_bounds(self, loc):
		if not loc or len(loc) != 2 or not self.map or len(self.map) == 0: 
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
		closed_entities = [CellBase.WALL, CellBase.TABLE, CellBase.FRIDGE, CellBase.CUTTING_BOARD, CellBase.STOVE, CellBase.TURNIN, CellBase.TRASH]
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
		row_arr = []
		for row in self.map:
			pb_row = MapRow()
			for cell in row:
				pb_row.cells.append(cell.to_str())
			row_arr.append(pb_row)
		return row_arr
		#return [reduce(lambda pb_row, cell: pb_row.cells.append(cell.to_str()), [cell for cell in row]) for row in self.map]

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

class OrderTimer():
   def __init__(self, t, hFunction):
      self.t = t
      self.hFunction = hFunction
      self.thread = Timer(self.t, self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t, self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

class Stove:
	def __init__(self, game_id, slots=[]):
		self.slots = []
		self.game_id = game_id

	def add_item(self, item):
		if isinstance(item.item, EntityType) and len(self.slots) < 6:
			self.slots.append(item)
			return True
		else:
			return False

	def clear(self, sio):
		self.slots = []
		sio.emit('stove-update', self.serialize(), room=self.game_id)

	def check_valid(self, player, sio):
		for item in list(OrderItem):
			if item.needs_to_be_cooked():
				temp = item.get_recipe()
				for ingred in self.slots:
					try:
						if ingred.chopped == ingred.item.needs_to_be_chopped():
							temp.remove(ingred.item)
						else:
							print('INGREDIENT NEEDS TO BE CHOPPED. Slots cleared')
							self.clear(sio)
							return False
					except ValueError:
						if not temp:
							print('DID NOT FIND MATCH: too many ingredients in slots')
							self.clear(sio)
							return False
						break
				if not temp:
					print('Found match!')
					player.inventory = Inventory(item, False, True, False)
					self.clear(sio)
					return True
		print('DID NOT FIND MATCH: no matching recipe')
		self.clear(sio)		
		return False


	def serialize(self):
		pb = StationUpdate()
		for i in self.slots:
			slot = InventoryUpdate()
			slot.item = i.item.to_str()
			slot.cooked = i.cooked
			slot.plated = i.plated
			slot.chopped = i.chopped
			pb.slots.append(slot)
		return pb.SerializeToString()

class PlatingStation:
	def __init__(self, game_id, slots=[]):
		self.slots = []
		self.game_id = game_id

	def add_item(self, item):
		if len(self.slots) < 6:
			if item.plated:
				return False
			self.slots.append(item)
			return True
		else:
			return False
	
	def clear(self, sio):
		self.slots = []
		sio.emit('plating-update', self.serialize(), room=self.game_id)

	#TODO: add 'needs_to_be_chopped() for OrderItem so this doesn't break
	def check_valid(self, player, sio):
		if len(self.slots) == 1:
			if isinstance(self.slots[0].item, OrderItem):
				print('Found match!')
				player.inventory = Inventory(self.slots[0].item, True, self.slots[0].cooked, False)
				self.clear(sio)
				return True
		for item in list(OrderItem):
			if not item.needs_to_be_cooked():
				temp = item.get_recipe()
				for ingred in self.slots:
					if isinstance(ingred, OrderItem):
						print('ORDERITEM FOUND WITH INVALID INGREDIENTS. Slots cleared')
						return False
					try:
						if ingred.chopped == ingred.item.needs_to_be_chopped():
							temp.remove(ingred.item)
						else:
							print('INGREDIENT NEEDS TO BE CHOPPED. Slots cleared')
							self.clear(sio)
							return False
					except ValueError:
						if not temp:
							print('DID NOT FIND MATCH: too many ingredients in slots')
							self.clear(sio)
							return False
						break
				if not temp:
					print('Found match!')
					player.inventory = Inventory(item, True, player.inventory.cooked, False)
					self.clear(sio)
					return True
		print('DID NOT FIND MATCH: no matching recipe')
		self.clear(sio)		
		return False

	def serialize(self):
		pb = StationUpdate()
		for i in self.slots:
			slot = InventoryUpdate()
			slot.item = i.item.to_str()
			slot.cooked = i.cooked
			slot.plated = i.plated
			slot.chopped = i.chopped
			pb.slots.append(slot)
		return pb.SerializeToString()	

class Game:
	def __init__(self, sio, session_id, player_ids=[], entities=[], orders=[], state = GameState.QUEUEING):
		self.sio = sio
		self.state = state
		# same as room identifier used by socket.io
		self.session_id = session_id
		self.__init_map(player_ids, entities)
		self.points = 0
		self.orders = []
		self.stove = Stove(session_id)
		self.plating_station = PlatingStation(session_id)

	def start_orders(self):
		self.generateOrder()
		self.order_timer = OrderTimer(60, self.generateOrder)
		self.order_timer.start()

	def send_cookbook(self):
		cookbook = self.generateCookbook()
		self.sio.emit('recipes', self.serialize_into_pb(), room=self.session_id)
	
	def generateOrder(self):
		item = random.choice(list(OrderItem))
		base_order = Order(len(self.orders) + 1, item, on_expire=None)
		self.orders.append(QueuedOrder(base_order, partial(self.send_order, self.sio, base_order), 3))

	def clear_orders(self):
		for queued_order in self.orders:
			queued_order.order.cancel()
		self.orders = []

	def clear_and_stop_orders(self):
		self.clear_orders()
		if self.order_timer:
			self.order_timer.cancel()

	def finish(self):
		if self.state == GameState.PLAYING:
			self.clear_and_stop_orders()
		self.state = GameState.FINISHED

	def remove_player(self, player_id):
		if player_id in self.players:
			loc = self.players[player_id].loc
			self.map.remove_entity(loc)
			del self.players[player_id]
			if len(self.players) == 0:
				self.finish()

	def __init_map(self, player_ids, entities):
		i = 0
		self.starting_locs = [[2,6], [13,6]]
		self.players = dict()
		for p_id in player_ids:
			print('attempting to create game with player', i+1)
			self.players[p_id] = Player(p_id, self.starting_locs[i], self, i)
			i += 1
			if i > 1:
				break
		self.map = Map(self.players.values())
		assert len(player_ids) <= 2

	def send_order(self, sio, order):
		print("-------------ORDER SENT OUT--------------")
		print("---name---")
		print(order.type.name)
		serialized = order.serialize()
		print(serialized)
		sio.emit('order', serialized, room=self.session_id)

	def handle_station(self, base, player_id):
		player = self.players[player_id]
		if base is CellBase.TRASH:
			player.inventory = Inventory()
			return True
		elif base is CellBase.CUTTING_BOARD:
			if player.inventory.is_choppable():
				player.inventory.chopped = True
				return True
			return False
		elif base is CellBase.STOVE:
			if self.stove.add_item(player.inventory):
				player.inventory = Inventory()
				self.sio.emit('stove-update', self.stove.serialize(), room=self.session_id)
				return True
			else:
				return False
		elif base is CellBase.PLATE:
			if self.plating_station.add_item(player.inventory):
				player.inventory = Inventory()
				self.sio.emit('plating-update', self.plating_station.serialize(), room=self.session_id)
				return True
			else:
				return False
		elif base is CellBase.TURNIN:
			return self.turnin(base, player)

	def turnin(self, base, player):
		if base == CellBase.TURNIN:
			if player.inventory.plated:
				if isinstance(player.inventory.item, OrderItem):
					for queued_order in self.orders:
						if not queued_order.order.fulfilled:
							converted = OrderType.Value(queued_order.order.type.name) + 1
							if converted == player.inventory.item.value:
								if player.inventory.cooked == OrderItem(converted).needs_to_be_cooked():
									player.inventory = Inventory()
									queued_order.order.fulfilled = True
									self.points += OrderItem(converted).get_points()
									print("Point update:", self.points)
									self.sio.emit('order', queued_order.order.serialize(self.points), room=self.session_id)
									return True

	def handle_assemble(self, base, player_id):
		player = self.players[player_id]
		if base == CellBase.STOVE:
			return self.stove.check_valid(player, self.sio)
		elif base == CellBase.PLATE:
			return self.plating_station.check_valid(player, self.sio)
		
	def add_player(self, player_id):
		if player_id not in self.players and len(self.players) < 2:
			old_num_players = len(self.players)
			self.players[player_id] = Player(player_id, self.starting_locs[old_num_players], self, old_num_players)
			self.map.add_entity(self.players[player_id])
			return True
		return False

	def valid_player_update(self, player_id, key):
		player = self.players[player_id]
		if key in MOVE_KEYS:
			new_loc = player.move(key)
			return not self.map.cell(new_loc[0], new_loc[1]).collidable()
		elif key == 'e':
			search = [-1, 1]
			for s in search:
				if self.map.cell(player.loc[0], player.loc[1] + s).base.is_station():
					return self.handle_station(self.map.cell(player.loc[0], player.loc[1] + s).base, player_id)
				elif self.map.cell(player.loc[0] + s, player.loc[1]).base.is_station():
					return self.handle_station(self.map.cell(player.loc[0] + s, player.loc[1]).base, player_id)
				elif self.map.cell(player.loc[0], player.loc[1] + s).entity is not None:
					if player.inventory.item is None:
						player.inventory.item = self.map.cell(player.loc[0], player.loc[1] + s).entity.type
						print("Inventory update:", player.inventory.item.to_str())
						return True
				elif self.map.cell(player.loc[0] + s, player.loc[1]).entity is not None:
					if player.inventory.item is None:
						player.inventory.item = self.map.cell(player.loc[0] + s, player.loc[1]).entity.type
						print("Inventory update:", player.inventory.item.to_str())
						return True
		elif key == 'q':
			search = [-1, 1]
			for s in search:
				if self.map.cell(player.loc[0], player.loc[1] + s).base in [CellBase.STOVE, CellBase.PLATE]:
					return self.handle_assemble(self.map.cell(player.loc[0], player.loc[1] + s).base, player_id)
				elif self.map.cell(player.loc[0] + s, player.loc[1]).base in [CellBase.STOVE, CellBase.PLATE]:
					return self.handle_assemble(self.map.cell(player.loc[0] + s, player.loc[1]).base, player_id)
		else:
			return False

	def update(self, player_id, key):
		if not self.in_play():
			# in this case, update is a no-op
			return
		player = self.players[player_id]
		# update player location
		self.map.move_entity_from_to(player.loc, player.move(key))

	def play(self):
		self.state = GameState.PLAYING
		self.start_orders()
		
		# for order in self.orders:
		# 	order.queue()

	def in_play(self):
		return self.state is GameState.PLAYING

	def has_player(self, pid):
		return pid in self.players

	def serialize_into_pb(self):
		pb = MapUpdate()
		for row in self.map.to_str():
			pb.map.append(row)
		for p in self.players.values():
			player = pb.players.add()
			player.id = p.id
			player.emoji = p.to_str()
			player.position.append(p.loc[0])
			player.position.append(p.loc[1])
			if p.inventory.item is not None:
				player.inventory.item = p.inventory.item.to_str()
				player.inventory.cooked = p.inventory.cooked
				player.inventory.plated = p.inventory.plated
				player.inventory.chopped = p.inventory.chopped

		return pb.SerializeToString()
		# TODO: Implement order serialization
	
	def generateCookbook(self):
		cookbook = {}
		for item in list(OrderItem):
			item_details = {}
			item_details['name'] = item.name
			item_details['emoji'] = item.to_str()
			item_details['difficulty'] = item.get_difficulty()
			item_details['ingredients'] = []
			for ingredient in item.get_recipe():
				item_details['ingredients'].append({ 'emoji' : ingredient.to_str(), 'chopped' : ingredient.needs_to_be_chopped()})
			item_details['cooked'] = item.needs_to_be_cooked()
			cookbook[item.to_str()] = item_details
		return cookbook
@unique
class OrderItem(Enum):
	# easy
	HOT_DOG = 1
	PIZZA = 2
	WAFFLES = 3
	SUSHI = 4
	EGGS = 5

	# medium
	GYRO = 6
	PANCAKES = 7
	RAMEN = 8
	STEW = 9

	# hard
	BENTO_BOX = 10
	TACO = 11
	SANDWICH = 12
	HAMBURGER = 13
	BURRITO = 14
	CURRY_RICE = 15

	def get_difficulty(self):
		if self.value in [1, 2, 3, 4, 5]:
			return 1
		if self.value in [6, 7, 8, 9]:
			return 2
		if self.value in [10, 11, 12, 13, 14, 15]:
			return 3
		
	def get_points(self):
		if self.get_difficulty() == 1:
			return 15
		if self.get_difficulty() == 2:
			return 20
		if self.get_difficulty() == 3:
			return 30

	# amount of time before order expires in seconds
	def expires_in(self):
		return ORDER_TTL

	def to_str(self):
		reps = ['🌭', '🍕', '🧇', '🍣', '🍳', '🥙', '🥞', '🍜', '🍲', '🍱', '🌮', '🥪', '🍔', '🌯', '🍛']
		assert len(list(OrderItem)) == len(reps)
		return reps[self.value-1]

	def get_recipe(self):
		recipes = [
			[EntityType.BREAD, EntityType.SAUSAGE], # hot dog
			[EntityType.BREAD, EntityType.CHEESE, EntityType.TOMATO], # pizza
			[EntityType.MILK, EntityType.EGG, EntityType.FLOUR], # waffles
			[EntityType.FISH, EntityType.RICE], # sushi
			[EntityType.EGG, EntityType.EGG, EntityType.EGG], # eggs
			[EntityType.BREAD, EntityType.CHEESE, EntityType.LETTUCE, EntityType.TOMATO], # gyro
			[EntityType.MILK, EntityType.EGG, EntityType.BUTTER, EntityType.FLOUR], # pancakes
			[EntityType.HOT_WATER, EntityType.PORK, EntityType.NOODLES, EntityType.FISH_CAKE], # ramen
			[EntityType.HOT_WATER, EntityType.POTATO, EntityType.LETTUCE, EntityType.CARROT], # stew
			[EntityType.RICE, EntityType.FISH, EntityType.POTATO, EntityType.LETTUCE, EntityType.FISH_CAKE], # bento box
			[EntityType.BREAD, EntityType.CHEESE, EntityType.RAW_PATTY, EntityType.LETTUCE, EntityType.ONION], # taco
			[EntityType.BREAD, EntityType.CHEESE, EntityType.PORK, EntityType.LETTUCE, EntityType.TOMATO], # sandwich
			[EntityType.BREAD, EntityType.CHEESE, EntityType.RAW_PATTY, EntityType.LETTUCE, EntityType.TOMATO, EntityType.ONION], # hamburger
			[EntityType.BREAD, EntityType.CHEESE, EntityType.RAW_PATTY, EntityType.LETTUCE, EntityType.ONION], # burrito
			[EntityType.RICE, EntityType.ONION, EntityType.GARLIC, EntityType.HOT_WATER, EntityType.CARROT] # curry rice
		]
		assert len(list(OrderItem)) == len(recipes)
		return recipes[self.value-1]
	def needs_to_be_chopped(self):
		return False

	def needs_to_be_cooked(self):
		#reps = ['🌭', '🍕', '🧇', '🍣', '🍳', '🥙', '🥞', '🍜', '🍲', '🍱', '🌮', '🥪', '🍔', '🌯', '🍛']
		reps = [True, True, True, False, True, False, True, True, True, False, False, False, True, True, True]
		assert len(list(OrderItem)) == len(reps)
		return reps[self.value-1]

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
