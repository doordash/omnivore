from __future__ import unicode_literals
from omnivore import client
from omnivore.resource import PrintableResource
from omnivore.resource.base import OmnivoreLocationResource
from omnivore.util import (
    cached_property,
    get_embedded_object,
    has_embedded_objects
)


class OmnivoreMenuResource(OmnivoreLocationResource):

    @classmethod
    def list_url(cls, location_id):
        base_url = super(OmnivoreMenuResource, cls).list_url(location_id)
        return base_url + 'menu/'


class OmnivoreMenuItemResource(OmnivoreMenuResource):

    @classmethod
    def list_url(cls, location_id, item_id):
        base_url = super(OmnivoreMenuItemResource, cls).list_url(location_id)
        return base_url + 'items/' + item_id + '/'

    @classmethod
    def retrieve_url(cls, location_id, item_id, instance_id):
        return cls.list_url(location_id, item_id) + instance_id + '/'

    def __init__(self, location_id, item_id, **kwargs):
        self.item_id = item_id
        super(OmnivoreMenuItemResource, self).__init__(location_id, **kwargs)

    @property
    def instance_url(self):
        return self.__class__.retrieve_url(
            self.location_id,
            self.item_id,
            self.id
        )


class Menu(PrintableResource):

    def __init__(self, location_id):
        self.location_id = location_id

    # Retrieving related objects

    @cached_property
    def categories(self):
        res = client.get(Category.list_url(self.location_id))
        categories = get_embedded_object(res, 'categories')
        return [Category(self.location_id, **c) for c in categories]

    @cached_property
    def items(self):
        res = client.get(MenuItem.list_url(self.location_id))
        menu_items = get_embedded_object(res, 'menu_items')
        return [MenuItem(self.location_id, **mi) for mi in menu_items]

    @cached_property
    def modifiers(self):
        res = client.get(Modifier.list_url(self.location_id))
        modifiers = get_embedded_object(res, 'modifiers')
        return [Modifier(self.location_id, **m) for m in modifiers]

    def __unicode__(self):
        return '<Omnivore::{} {}>'.format(
            self.__class__.__name__,
            self.location_id
        )


class Category(OmnivoreMenuResource):

    @classmethod
    def list_url(cls, location_id):
        return super(Category, cls).list_url(location_id) + 'categories/'

    def refresh_from(self, **kwargs):
        self.name = kwargs['name']


class MenuItem(OmnivoreMenuResource):

    @classmethod
    def list_url(cls, location_id):
        return super(MenuItem, cls).list_url(location_id) + 'items/'

    def refresh_from(self, **kwargs):
        self.name = kwargs['name']
        self.price_per_unit = kwargs['price_per_unit']
        self.in_stock = kwargs['in_stock']
        option_sets = get_embedded_object(kwargs, 'option_sets')
        self.modifier_groups_count = len(option_sets)

    # Retrieving related objects

    @cached_property
    def modifier_groups(self):
        res = client.get(ModifierGroup.list_url(self.location_id, self.id))
        groups = get_embedded_object(res, 'modifier_groups')
        return [
            ModifierGroup(self.location_id, self.id, **mg)
            for mg
            in groups
        ]


class Modifier(OmnivoreMenuResource):

    @classmethod
    def list_url(cls, location_id):
        return super(Modifier, cls).list_url(location_id) + 'modifiers/'

    def refresh_from(self, **kwargs):
        self.name = kwargs['name']
        self.price_per_unit = kwargs['price_per_unit']

    def to_ticket_modifier(self, quantity, price_level=None, comment=None):
        data = {
            'modifier': self.id,
            'quantity': quantity
        }

        if price_level:
            data['price_level'] = price_level

        if comment:
            data['comment'] = comment

        return data


class ModifierGroup(OmnivoreMenuItemResource):

    @classmethod
    def list_url(cls, location_id, item_id):
        base_url = super(ModifierGroup, cls).list_url(location_id, item_id)
        return base_url + 'modifier_groups/'

    def refresh_from(self, **kwargs):
        self.name = kwargs['name']
        self.minimum = kwargs['minimum']
        self.maximum = kwargs['maximum']
        self.required = kwargs['required']

        if has_embedded_objects(kwargs):
            options = get_embedded_object(kwargs, 'options')
            self.options = [Modifier(self.location_id, **m) for m in options]
