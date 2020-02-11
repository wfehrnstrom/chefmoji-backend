// source: game_update.proto
/**
 * @fileoverview
 * @enhanceable
 * @suppress {messageConventions} JS Compiler reports an error if a variable or
 *     field starts with 'MSG_' and isn't a translatable message.
 * @public
 */
// GENERATED CODE -- DO NOT EDIT!

goog.provide('proto.chefmoji.PlayerUpdate');

goog.require('jspb.BinaryReader');
goog.require('jspb.BinaryWriter');
goog.require('jspb.Message');

/**
 * Generated by JsPbCodeGenerator.
 * @param {Array=} opt_data Optional initial data array, typically from a
 * server response, or constructed directly in Javascript. The array is used
 * in place and becomes part of the constructed object. It is not cloned.
 * If no data is provided, the constructed object will be empty, but still
 * valid.
 * @extends {jspb.Message}
 * @constructor
 */
proto.chefmoji.PlayerUpdate = function(opt_data) {
  jspb.Message.initialize(this, opt_data, 0, -1, proto.chefmoji.PlayerUpdate.repeatedFields_, null);
};
goog.inherits(proto.chefmoji.PlayerUpdate, jspb.Message);
if (goog.DEBUG && !COMPILED) {
  /**
   * @public
   * @override
   */
  proto.chefmoji.PlayerUpdate.displayName = 'proto.chefmoji.PlayerUpdate';
}

/**
 * List of repeated fields within this message type.
 * @private {!Array<number>}
 * @const
 */
proto.chefmoji.PlayerUpdate.repeatedFields_ = [1];



if (jspb.Message.GENERATE_TO_OBJECT) {
/**
 * Creates an object representation of this proto.
 * Field names that are reserved in JavaScript and will be renamed to pb_name.
 * Optional fields that are not set will be set to undefined.
 * To access a reserved field use, foo.pb_<name>, eg, foo.pb_default.
 * For the list of reserved names please see:
 *     net/proto2/compiler/js/internal/generator.cc#kKeyword.
 * @param {boolean=} opt_includeInstance Deprecated. whether to include the
 *     JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @return {!Object}
 */
proto.chefmoji.PlayerUpdate.prototype.toObject = function(opt_includeInstance) {
  return proto.chefmoji.PlayerUpdate.toObject(opt_includeInstance, this);
};


/**
 * Static version of the {@see toObject} method.
 * @param {boolean|undefined} includeInstance Deprecated. Whether to include
 *     the JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @param {!proto.chefmoji.PlayerUpdate} msg The msg instance to transform.
 * @return {!Object}
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.chefmoji.PlayerUpdate.toObject = function(includeInstance, msg) {
  var f, obj = {
    positionList: (f = jspb.Message.getRepeatedField(msg, 1)) == null ? undefined : f,
    inventory: jspb.Message.getFieldWithDefault(msg, 2, ""),
    id: jspb.Message.getFieldWithDefault(msg, 3, "")
  };

  if (includeInstance) {
    obj.$jspbMessageInstance = msg;
  }
  return obj;
};
}


/**
 * Deserializes binary data (in protobuf wire format).
 * @param {jspb.ByteSource} bytes The bytes to deserialize.
 * @return {!proto.chefmoji.PlayerUpdate}
 */
proto.chefmoji.PlayerUpdate.deserializeBinary = function(bytes) {
  var reader = new jspb.BinaryReader(bytes);
  var msg = new proto.chefmoji.PlayerUpdate;
  return proto.chefmoji.PlayerUpdate.deserializeBinaryFromReader(msg, reader);
};


/**
 * Deserializes binary data (in protobuf wire format) from the
 * given reader into the given message object.
 * @param {!proto.chefmoji.PlayerUpdate} msg The message object to deserialize into.
 * @param {!jspb.BinaryReader} reader The BinaryReader to use.
 * @return {!proto.chefmoji.PlayerUpdate}
 */
proto.chefmoji.PlayerUpdate.deserializeBinaryFromReader = function(msg, reader) {
  while (reader.nextField()) {
    if (reader.isEndGroup()) {
      break;
    }
    var field = reader.getFieldNumber();
    switch (field) {
    case 1:
      var value = /** @type {!Array<number>} */ (reader.readPackedUint32());
      msg.setPositionList(value);
      break;
    case 2:
      var value = /** @type {string} */ (reader.readString());
      msg.setInventory(value);
      break;
    case 3:
      var value = /** @type {string} */ (reader.readString());
      msg.setId(value);
      break;
    default:
      reader.skipField();
      break;
    }
  }
  return msg;
};


/**
 * Serializes the message to binary data (in protobuf wire format).
 * @return {!Uint8Array}
 */
proto.chefmoji.PlayerUpdate.prototype.serializeBinary = function() {
  var writer = new jspb.BinaryWriter();
  proto.chefmoji.PlayerUpdate.serializeBinaryToWriter(this, writer);
  return writer.getResultBuffer();
};


/**
 * Serializes the given message to binary data (in protobuf wire
 * format), writing to the given BinaryWriter.
 * @param {!proto.chefmoji.PlayerUpdate} message
 * @param {!jspb.BinaryWriter} writer
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.chefmoji.PlayerUpdate.serializeBinaryToWriter = function(message, writer) {
  var f = undefined;
  f = message.getPositionList();
  if (f.length > 0) {
    writer.writePackedUint32(
      1,
      f
    );
  }
  f = message.getInventory();
  if (f.length > 0) {
    writer.writeString(
      2,
      f
    );
  }
  f = message.getId();
  if (f.length > 0) {
    writer.writeString(
      3,
      f
    );
  }
};


/**
 * repeated uint32 position = 1;
 * @return {!Array<number>}
 */
proto.chefmoji.PlayerUpdate.prototype.getPositionList = function() {
  return /** @type {!Array<number>} */ (jspb.Message.getRepeatedField(this, 1));
};


/**
 * @param {!Array<number>} value
 * @return {!proto.chefmoji.PlayerUpdate} returns this
 */
proto.chefmoji.PlayerUpdate.prototype.setPositionList = function(value) {
  return jspb.Message.setField(this, 1, value || []);
};


/**
 * @param {number} value
 * @param {number=} opt_index
 * @return {!proto.chefmoji.PlayerUpdate} returns this
 */
proto.chefmoji.PlayerUpdate.prototype.addPosition = function(value, opt_index) {
  return jspb.Message.addToRepeatedField(this, 1, value, opt_index);
};


/**
 * Clears the list making it empty but non-null.
 * @return {!proto.chefmoji.PlayerUpdate} returns this
 */
proto.chefmoji.PlayerUpdate.prototype.clearPositionList = function() {
  return this.setPositionList([]);
};


/**
 * optional string inventory = 2;
 * @return {string}
 */
proto.chefmoji.PlayerUpdate.prototype.getInventory = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 2, ""));
};


/**
 * @param {string} value
 * @return {!proto.chefmoji.PlayerUpdate} returns this
 */
proto.chefmoji.PlayerUpdate.prototype.setInventory = function(value) {
  return jspb.Message.setProto3StringField(this, 2, value);
};


/**
 * optional string id = 3;
 * @return {string}
 */
proto.chefmoji.PlayerUpdate.prototype.getId = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 3, ""));
};


/**
 * @param {string} value
 * @return {!proto.chefmoji.PlayerUpdate} returns this
 */
proto.chefmoji.PlayerUpdate.prototype.setId = function(value) {
  return jspb.Message.setProto3StringField(this, 3, value);
};


