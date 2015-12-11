from __future__ import unicode_literals
from omnivore import client, error
from omnivore.resource import OmnivoreLocationResource
from omnivore.resource.base import (
    Employee,
    Discount,
    OrderType,
    RevenueCenter,
    Table
)
from omnivore.resource.menu import MenuItem, Modifier
from omnivore.util import (
    cached_property,
    get_embedded_object,
    has_embedded_objects
)


class OmnivoreTicketResource(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id, ticket_id):
        base_url = super(OmnivoreTicketResource, cls).list_url(location_id)
        return base_url + 'tickets/' + ticket_id + '/'

    @classmethod
    def retrieve_url(cls, location_id, ticket_id, instance_id):
        return cls.list_url(location_id, ticket_id) + instance_id + '/'

    def __init__(self, location_id, ticket_id, **kwargs):
        self.ticket_id = ticket_id
        super(OmnivoreTicketResource, self).__init__(location_id, **kwargs)

    @property
    def instance_url(self):
        return self.__class__.retrieve_url(
            self.location_id,
            self.ticket_id,
            self.id
        )


class OmnivoreTicketItemResource(OmnivoreTicketResource):

    @classmethod
    def list_url(cls, location_id, ticket_id, item_id):
        base_url = super(OmnivoreTicketItemResource, cls).list_url(
            location_id,
            ticket_id
        )
        return base_url + 'items/' + item_id + '/'

    @classmethod
    def retrieve_url(cls, location_id, ticket_id, item_id, instance_id):
        base_url = cls.list_url(location_id, ticket_id, item_id)
        return base_url + instance_id + '/'

    def __init__(self, location_id, ticket_id, item_id, **kwargs):
        self.item_id = item_id
        super(OmnivoreTicketItemResource, self).__init__(
            location_id,
            ticket_id,
            **kwargs
        )

    @property
    def instance_url(self):
        return self.__class__.retrieve_url(
            self.location_id,
            self.ticket_id,
            self.item_id,
            self.id
        )


class Ticket(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        return super(Ticket, cls).list_url(location_id) + 'tickets/'

    @classmethod
    def open(cls, location_id, employee_id, order_type_id, revenue_center_id,
             table_id, guest_count=None, name=None, auto_send=None):
        data = {
            'employee': employee_id,
            'order_type': order_type_id,
            'revenue_center': revenue_center_id,
            'table': table_id
        }

        if guest_count:
            data['guest_count'] = guest_count

        if name:
            data['name'] = name

        if auto_send:
            data['auto_send'] = auto_send

        res = client.post(cls.list_url(location_id), data)

        return cls(location_id, **res)

    def refresh_from(self, **kwargs):
        self.auto_send = kwargs['auto_send']
        self.closed_at = kwargs['closed_at']
        self.guest_count = kwargs['guest_count']
        self.name = kwargs['name']
        self.open = kwargs['open']
        self.opened_at = kwargs['opened_at']
        self.ticket_number = kwargs['ticket_number']
        self.totals = kwargs['totals']

        if has_embedded_objects(kwargs):
            employee = get_embedded_object(kwargs, 'employee')
            self.employee = Employee(self.location_id, **employee)

            discounts = get_embedded_object(kwargs, 'discounts')
            self.discounts = [
                TicketDiscount(self.location_id, **discount)
                for discount
                in discounts
            ]

            ticket_items = get_embedded_object(kwargs, 'items')
            self.items = [
                TicketItem(self.location_id, self.id, **ti)
                for ti
                in ticket_items
            ]

            order_type = get_embedded_object(kwargs, 'order_type')
            self.order_type = OrderType(self.location_id, **order_type)

            payments = get_embedded_object(kwargs, 'payments')
            self.payments = [
                Payment(self.location_id, self.id, **p)
                for p
                in payments
            ]

            revenue_center = get_embedded_object(kwargs, 'revenue_center')
            self.revenue_center = RevenueCenter(
                self.location_id,
                **revenue_center
            )

            table = get_embedded_object(kwargs, 'table')
            self.table = Table(self.location_id, **table)

            voided_items = get_embedded_object(kwargs, 'voided_items')
            self.voided_items = [
                MenuItem(self.location_id, **item)
                for item
                in voided_items
            ]

    def void(self):
        res = client.post(self.instance_url, {'void': True})
        self.refresh_from(**res)

    def add_item(self, menu_item, quantity,
                 price_level=None, comment=None,
                 modifiers=None, discounts=None):
        data = {
            'menu_item': menu_item.id,
            'quantity': quantity
        }

        if price_level:
            price_level_ids = [pl.id for pl in menu_item.price_levels]
            if price_level not in price_level_ids:
                raise error.APIError(
                    'Unknown price level for item {}'.format(menu_item.id)
                )

            data['price_level'] = price_level

        if comment:
            if not isinstance(comment, str):
                raise error.APIError('Comment must be an ascii string')
            if len(comment) > 20:
                raise error.APIError('Max comment length is 20 characters')

            data['comment'] = comment

        if modifiers:
            data['modifiers'] = modifiers

        if discounts:
            data['discounts'] = discounts

        res = client.post(
            TicketItem.list_url(self.location_id, self.id),
            data
        )

        self.refresh_from(**res)

    # TODO: allow addition of multiple TicketItems

    def void_item(self, ticket_item):
        res = client.delete(ticket_item.retrieve_url)
        self.refresh_from(**res)

    def pay(self, type, amount, tip, **kwargs):
        if type not in Payment.types:
            msg = 'Unknown payment type: \'{}\'. Allowed types: {}'.format(
                type,
                Payment.types
            )
            raise error.APIError(msg)

        if type == '3rd_party':
            if 'tender_type' not in kwargs or 'payment_source' not in kwargs:
                msg = 'Missing tender_type or payment_source for payment'
                raise error.APIError(msg)
        else:
            if 'card_info' not in kwargs:
                # TODO: verify required card_info fields
                raise error.APIError('Missing card_info for payment')

        data = dict(type=type, amount=amount, tip=tip, **kwargs)

        res = client.post(Payment.list_url(self.location_id, self.id), data)

        self.refresh_from(**res.pop('ticket'))
        return res

    # Retrieving related objects

    @cached_property
    def payments(self):
        res = client.get(Payment.list_url(self.location_id, self.id))
        payments = get_embedded_object(res, 'payments')
        return [Payment(self.location_id, **p) for p in payments]


class TicketDiscount(OmnivoreTicketResource):

    # TODO: apply

    @classmethod
    def list_url(cls, location_id, ticket_id):
        base_url = super(TicketDiscount, cls).list_url(location_id, ticket_id)
        return base_url + 'discounts/'

    def refresh_from(self, **kwargs):
        self.comment = kwargs['comment']
        self.name = kwargs['name']
        self.value = kwargs['value']

        if has_embedded_objects(kwargs):
            discount = get_embedded_object(kwargs, 'discount')
            self.discount = Discount(self.location_id, **discount)


class TicketItem(OmnivoreTicketResource):

    @classmethod
    def list_url(cls, location_id, ticket_id):
        base_url = super(TicketItem, cls).list_url(location_id, ticket_id)
        return base_url + 'items/'

    def refresh_from(self, **kwargs):
        self.comment = kwargs['comment']
        self.name = kwargs['name']
        self.price_per_unit = kwargs['price_per_unit']
        self.quantity = kwargs['quantity']
        self.sent = kwargs['sent']

        if has_embedded_objects(kwargs):
            menu_item = get_embedded_object(kwargs, 'menu_item')
            self.menu_item = MenuItem(self.location_id, **menu_item)

            modifiers = get_embedded_object(kwargs, 'modifiers')
            self.modifiers = [
                TicketItemModifier(
                    self.location_id,
                    self.ticket_id,
                    self.id,
                    **modifier
                )
                for modifier
                in modifiers
            ]


class TicketItemModifier(OmnivoreTicketItemResource):

    @classmethod
    def list_url(cls, location_id, ticket_id, item_id):
        base_url = super(TicketItemModifier, cls).list_url(
            location_id,
            ticket_id,
            item_id
        )
        return base_url + 'modifiers/'

    def refresh_from(self, **kwargs):
        self.comment = kwargs['comment']
        self.name = kwargs['name']
        self.price_per_unit = kwargs['price_per_unit']
        self.quantity = kwargs['quantity']

        if has_embedded_objects(kwargs):
            modifier = get_embedded_object(kwargs, 'menu_modifier')
            self.modifier = Modifier(self.location_id, **modifier)


class TicketItemDiscount(OmnivoreTicketItemResource):

    @classmethod
    def list_url(cls, location_id, ticket_id, item_id):
        base_url = super(TicketItemDiscount, cls).list_url(
            location_id,
            ticket_id,
            item_id
        )
        return base_url + 'discounts/'

    def refresh_from(self, **kwargs):
        self.comment = kwargs['comment']
        self.name = kwargs['name']
        self.value = kwargs['value']

        if has_embedded_objects(kwargs):
            discount = get_embedded_object(kwargs, 'discount')
            self.discount = Discount(self.location_id, **discount)


class Payment(OmnivoreTicketResource):

    types = ['card_not_present', 'card_present', '3rd_party', 'gift_card']

    @classmethod
    def list_url(cls, location_id, ticket_id):
        base_url = super(Payment, cls).list_url(location_id, ticket_id)
        return base_url + 'payments/'

    def refresh_from(self, **kwargs):
        self.type = kwargs['type']
        self.amount = kwargs['amount']
        self.tip = kwargs['tip']
