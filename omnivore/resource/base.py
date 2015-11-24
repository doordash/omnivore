from omnivore import client
from omnivore.resource import OmnivoreResource, OmnivoreLocationResource
from omnivore.resource.menu import Menu
from omnivore.util import (
    cached_property,
    get_embedded_object,
    has_embedded_objects
)


class Location(OmnivoreResource):

    @classmethod
    def all(cls):
        res = client.get(Location.list_url())
        locations = get_embedded_object(res, 'locations')
        return [Location(**l) for l in locations]

    def refresh_from(self, **kwargs):
        self.address = kwargs['address']
        self.name = kwargs['name']
        self.phone = kwargs['phone']
        self.website = kwargs['website']

    # Retrieving related objects

    @cached_property
    def discounts(self):
        res = client.get(Discount.list_url(self.id))
        discounts = get_embedded_object(res, 'discounts')
        return [Discount(self.id, **d) for d in discounts]

    @cached_property
    def employees(self):
        res = client.get(Employee.list_url(self.id))
        employees = get_embedded_object(res, 'employees')
        return [Employee(self.id, **e) for e in employees]

    @cached_property
    def menu(self):
        return Menu(self.id)

    @cached_property
    def order_types(self):
        res = client.get(OrderType.list_url(self.id))
        order_types = get_embedded_object(res, 'order_types')
        return [OrderType(self.id, **ot) for ot in order_types]

    @cached_property
    def revenue_centers(self):
        res = client.get(RevenueCenter.list_url(self.id))
        revenue_centers = get_embedded_object(res, 'revenue_centers')
        return [RevenueCenter(self.id, **rc) for rc in revenue_centers]

    @cached_property
    def tables(self):
        res = client.get(Table.list_url(self.id))
        tables = get_embedded_object(res, 'tables')
        return [Table(self.id, **t) for t in tables]

    @cached_property
    def tender_types(self):
        res = client.get(TenderType.list_url(self.id))
        tender_types = get_embedded_object(res, 'tender_types')
        return [TenderType(self.id, **tt) for tt in tender_types]

    @cached_property
    def tickets(self):
        res = client.get(Ticket.list_url(self.id))
        tickets = get_embedded_object(res, 'tickets')
        return [Ticket(self.id, **t) for t in tickets]

    def __unicode__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)


class Table(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        return super(Table, cls).list_url(location_id) + 'tables/'

    def refresh_from(self, **kwargs):
        self.available = kwargs['available']
        self.name = kwargs['name']
        self.number = kwargs['number']
        self.seats = kwargs['seats']

        if has_embedded_objects(kwargs):
            open_tickets = get_embedded_object(kwargs, 'open_tickets')
            self.open_tickets = [Ticket(self.location_id, **ticket)
                                 for ticket
                                 in open_tickets]

            revenue_center = get_embedded_object(kwargs, 'revenue_center')
            self.revenue_center = RevenueCenter(
                self.location_id,
                **revenue_center
            )


class Employee(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        return super(Employee, cls).list_url(location_id) + 'employees/'

    def refresh_from(self, **kwargs):
        self.check_name = kwargs['check_name']
        self.first_name = kwargs['first_name']
        self.last_name = kwargs['last_name']
        self.login = kwargs['login']


class OrderType(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        return super(OrderType, cls).list_url(location_id) + 'order_types/'

    def refresh_from(self, **kwargs):
        self.available = kwargs['available']
        self.name = kwargs['name']


class TenderType(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        return super(TenderType, cls).list_url(location_id) + 'tender_types/'

    def refresh_from(self, **kwargs):
        self.name = kwargs['name']


class RevenueCenter(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        base_url = super(RevenueCenter, cls).list_url(location_id)
        return base_url + 'revenue_centers/'

    def refresh_from(self, **kwargs):
        self.default = kwargs['default']
        self.name = kwargs['name']

        if has_embedded_objects(kwargs):
            open_tickets = get_embedded_object(kwargs, 'open_tickets')
            self.open_tickets = [Ticket(self.location_id, **ticket)
                                 for ticket
                                 in open_tickets]

            tables = get_embedded_object(kwargs, 'tables')
            self.tables = [Table(self.location_id, **t) for t in tables]


class Discount(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        return super(Discount, cls).list_url(location_id) + 'discounts/'

    def refresh_from(self, **kwargs):
        self.applies_to = kwargs['applies_to']
        self.available = kwargs['available']
        self.max_value = kwargs['max_value']
        self.min_ticket_total = kwargs['min_ticket_total']
        self.min_value = kwargs['min_value']
        self.name = kwargs['name']
        self.open = kwargs['open']
        self.type = kwargs['type']
        self.value = kwargs['value']


from omnivore.resource.ticket import Ticket  # noqa - avoid circular import
