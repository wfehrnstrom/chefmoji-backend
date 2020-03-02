from threading import Timer
from protocol_buffers.game_update_pb2 import OrderUpdate, OrderType

ORDER_TTL = 120

class Order:
    # @param OrderType type
    # @param integer expires_in: the length of time that the order takes to expire (become a failed order) in seconds
    # @param func on_expire: a callback to run on the expiration of the order
    def __init__(self, uid, type, on_expire, expires_in=None):
        self.uid = uid
        self.type = type
        self.on_expire = on_expire
        self.fulfilled = False
        if not expires_in:
            expires_in = self.type.expires_in()
        if on_expire:
            self.__expiration_timer = Timer(expires_in, on_expire)
        else:
            self.__expiration_timer = None

    def serialize(self, points=0):
        order_pb = OrderUpdate()
        order_pb.uid = self.uid
        order_pb.order_type = OrderType.Value(self.type.name) + 1
        # set to no-op right now. TODO: If need be, set.
        order_pb.registration_time = 0
        order_pb.fulfilled = self.fulfilled
        order_pb.points = points
        return order_pb.SerializeToString()

    def start_expiration_timer(self):
        if self.__expiration_timer:
            self.__expiration_timer.start()

    def cancel(self):
        if self.__expiration_timer:
            self.__expiration_timer.cancel()

class QueuedOrder(Order):
    def __init__(self, order, start_cb, starts_in=None, queue_imm=False):
        self.order = order
        start_cb()

    def on_start(self):
        self.order.start_expiration_timer()
        if self.start_cb is not None:
            self.start_cb()

    def queue(self):
        self.__start_timer.start()

