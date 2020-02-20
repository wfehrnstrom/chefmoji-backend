# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: game_update.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='game_update.proto',
  package='chefmoji',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x11game_update.proto\x12\x08\x63hefmoji\"\x17\n\x06MapRow\x12\r\n\x05\x63\x65lls\x18\x01 \x03(\t\"y\n\tMapUpdate\x12\x1d\n\x03map\x18\x01 \x03(\x0b\x32\x10.chefmoji.MapRow\x12\'\n\x07players\x18\x02 \x03(\x0b\x32\x16.chefmoji.PlayerUpdate\x12$\n\x05order\x18\x03 \x03(\x0b\x32\x15.chefmoji.OrderUpdate\"Z\n\x0cPlayerUpdate\x12\x10\n\x08position\x18\x01 \x03(\r\x12,\n\tinventory\x18\x02 \x01(\x0b\x32\x19.chefmoji.InventoryUpdate\x12\n\n\x02id\x18\x03 \x01(\t\"P\n\x0fInventoryUpdate\x12\x0c\n\x04item\x18\x01 \x01(\t\x12\x0e\n\x06plated\x18\x02 \x01(\x08\x12\x0e\n\x06\x63ooked\x18\x03 \x01(\x08\x12\x0f\n\x07\x63hopped\x18\x04 \x01(\x08\"q\n\x0bOrderUpdate\x12\x0b\n\x03uid\x18\x01 \x01(\r\x12\x19\n\x11registration_time\x18\x02 \x01(\r\x12\'\n\norder_type\x18\x03 \x01(\x0e\x32\x13.chefmoji.OrderType\x12\x11\n\tfulfilled\x18\x04 \x01(\x08*\xc5\x01\n\tOrderType\x12\x0b\n\x07HOT_DOG\x10\x00\x12\t\n\x05PIZZA\x10\x01\x12\x0b\n\x07WAFFLES\x10\x02\x12\t\n\x05SUSHI\x10\x03\x12\x08\n\x04\x45GGS\x10\x04\x12\x08\n\x04GYRO\x10\x05\x12\x0c\n\x08PANCAKES\x10\x06\x12\t\n\x05RAMEN\x10\x07\x12\x08\n\x04STEW\x10\x08\x12\r\n\tBENTO_BOX\x10\t\x12\x08\n\x04TACO\x10\n\x12\x0c\n\x08SANDWICH\x10\x0b\x12\r\n\tHAMBURGER\x10\x0c\x12\x0b\n\x07\x42URRITO\x10\r\x12\x0e\n\nCURRY_RICE\x10\x0e\x62\x06proto3'
)

_ORDERTYPE = _descriptor.EnumDescriptor(
  name='OrderType',
  full_name='chefmoji.OrderType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='HOT_DOG', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PIZZA', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WAFFLES', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUSHI', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EGGS', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GYRO', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PANCAKES', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RAMEN', index=7, number=7,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STEW', index=8, number=8,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BENTO_BOX', index=9, number=9,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TACO', index=10, number=10,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SANDWICH', index=11, number=11,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HAMBURGER', index=12, number=12,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BURRITO', index=13, number=13,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CURRY_RICE', index=14, number=14,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=469,
  serialized_end=666,
)
_sym_db.RegisterEnumDescriptor(_ORDERTYPE)

OrderType = enum_type_wrapper.EnumTypeWrapper(_ORDERTYPE)
HOT_DOG = 0
PIZZA = 1
WAFFLES = 2
SUSHI = 3
EGGS = 4
GYRO = 5
PANCAKES = 6
RAMEN = 7
STEW = 8
BENTO_BOX = 9
TACO = 10
SANDWICH = 11
HAMBURGER = 12
BURRITO = 13
CURRY_RICE = 14



_MAPROW = _descriptor.Descriptor(
  name='MapRow',
  full_name='chefmoji.MapRow',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cells', full_name='chefmoji.MapRow.cells', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=31,
  serialized_end=54,
)


_MAPUPDATE = _descriptor.Descriptor(
  name='MapUpdate',
  full_name='chefmoji.MapUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='map', full_name='chefmoji.MapUpdate.map', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='players', full_name='chefmoji.MapUpdate.players', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='order', full_name='chefmoji.MapUpdate.order', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=56,
  serialized_end=177,
)


_PLAYERUPDATE = _descriptor.Descriptor(
  name='PlayerUpdate',
  full_name='chefmoji.PlayerUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='position', full_name='chefmoji.PlayerUpdate.position', index=0,
      number=1, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='inventory', full_name='chefmoji.PlayerUpdate.inventory', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='chefmoji.PlayerUpdate.id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=179,
  serialized_end=269,
)


_INVENTORYUPDATE = _descriptor.Descriptor(
  name='InventoryUpdate',
  full_name='chefmoji.InventoryUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='item', full_name='chefmoji.InventoryUpdate.item', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='plated', full_name='chefmoji.InventoryUpdate.plated', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cooked', full_name='chefmoji.InventoryUpdate.cooked', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='chopped', full_name='chefmoji.InventoryUpdate.chopped', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=271,
  serialized_end=351,
)


_ORDERUPDATE = _descriptor.Descriptor(
  name='OrderUpdate',
  full_name='chefmoji.OrderUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uid', full_name='chefmoji.OrderUpdate.uid', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='registration_time', full_name='chefmoji.OrderUpdate.registration_time', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='order_type', full_name='chefmoji.OrderUpdate.order_type', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fulfilled', full_name='chefmoji.OrderUpdate.fulfilled', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=353,
  serialized_end=466,
)

_MAPUPDATE.fields_by_name['map'].message_type = _MAPROW
_MAPUPDATE.fields_by_name['players'].message_type = _PLAYERUPDATE
_MAPUPDATE.fields_by_name['order'].message_type = _ORDERUPDATE
_PLAYERUPDATE.fields_by_name['inventory'].message_type = _INVENTORYUPDATE
_ORDERUPDATE.fields_by_name['order_type'].enum_type = _ORDERTYPE
DESCRIPTOR.message_types_by_name['MapRow'] = _MAPROW
DESCRIPTOR.message_types_by_name['MapUpdate'] = _MAPUPDATE
DESCRIPTOR.message_types_by_name['PlayerUpdate'] = _PLAYERUPDATE
DESCRIPTOR.message_types_by_name['InventoryUpdate'] = _INVENTORYUPDATE
DESCRIPTOR.message_types_by_name['OrderUpdate'] = _ORDERUPDATE
DESCRIPTOR.enum_types_by_name['OrderType'] = _ORDERTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

MapRow = _reflection.GeneratedProtocolMessageType('MapRow', (_message.Message,), {
  'DESCRIPTOR' : _MAPROW,
  '__module__' : 'game_update_pb2'
  # @@protoc_insertion_point(class_scope:chefmoji.MapRow)
  })
_sym_db.RegisterMessage(MapRow)

MapUpdate = _reflection.GeneratedProtocolMessageType('MapUpdate', (_message.Message,), {
  'DESCRIPTOR' : _MAPUPDATE,
  '__module__' : 'game_update_pb2'
  # @@protoc_insertion_point(class_scope:chefmoji.MapUpdate)
  })
_sym_db.RegisterMessage(MapUpdate)

PlayerUpdate = _reflection.GeneratedProtocolMessageType('PlayerUpdate', (_message.Message,), {
  'DESCRIPTOR' : _PLAYERUPDATE,
  '__module__' : 'game_update_pb2'
  # @@protoc_insertion_point(class_scope:chefmoji.PlayerUpdate)
  })
_sym_db.RegisterMessage(PlayerUpdate)

InventoryUpdate = _reflection.GeneratedProtocolMessageType('InventoryUpdate', (_message.Message,), {
  'DESCRIPTOR' : _INVENTORYUPDATE,
  '__module__' : 'game_update_pb2'
  # @@protoc_insertion_point(class_scope:chefmoji.InventoryUpdate)
  })
_sym_db.RegisterMessage(InventoryUpdate)

OrderUpdate = _reflection.GeneratedProtocolMessageType('OrderUpdate', (_message.Message,), {
  'DESCRIPTOR' : _ORDERUPDATE,
  '__module__' : 'game_update_pb2'
  # @@protoc_insertion_point(class_scope:chefmoji.OrderUpdate)
  })
_sym_db.RegisterMessage(OrderUpdate)


# @@protoc_insertion_point(module_scope)
