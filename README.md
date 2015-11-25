# Omnivore Python library [![Circle CI](https://circleci.com/gh/chillbear/omnivore.svg?style=svg&circle-token=631d18f785e1a482771a2223e3fad866703fc856)](https://circleci.com/gh/chillbear/omnivore)

## Installation

```bash
pip install git+ssh://git@github.com/chillbear/omnivore.git@master
```

To install from source, run

```bash
git clone https://github.com/chillbear/omnivore.git
cd omnivore
python setup.py install
```

## Documentation

Please see the [Omnivore API Documentation](https://panel.omnivore.io/docs/api/) for the most up-to-date API documentation.

### Usage

Getting and interacting with locations:

```python
import omnivore

locations = omnivore.Location.all()
location = locations[0]

# print location.discounts
# print location.employees
# print location.order_types
# print location.revenue_centers
# print location.tables
# print location.tender_types
# print location.tickets
```

Properties are cached on each model instance. To refresh, do `location = Location.get(location.id)`. (TODO: allow properties to be refreshed manually)

Objects embedded in API responses are added as properties on each model instance. To refresh, do `locations.refresh()`.

Interacting with tickets:

```python
employee_id = 'xxx'
order_type_id = 'xxx'
revenue_center_id = 'xxx'
table_id = 'xxx'
guest_count = 1
name = 'Test Ticket'
auto_send = True

ticket = location.open_ticket(
    employee_id,
    order_type_id,
    revenue_center_id,
    table_id,
    guest_count,
    name,
    auto_send
)
print ticket
# ticket.void()

tip = ticket.totals['total'] * .2
print ticket.pay('3rd_party', ticket.totals['due'], tip, tender_type='xxx, payment_source='doordash')
# {
#     "amount_paid": 100,
#     "accepted": True,
#     "ticket_closed": True,
#     "balance_remaining": 0,
#     "type": "3rd_party"
# }
```

Interacting with menus:

```python
menu = location.menu

categories = menu.categories
items = menu.items
modifiers = menu.modifiers

# TODO: display modifiers and modifier groups
```

## Development

We use virtualenv. Install with `[sudo] pip install virtualenv`, initialize with `virtualenv venv`, and activate with `source venv/bin/activate`.

Install the development requirements with `pip install -r requirements/dev.txt`

### Testing

To run the test suite, run `py.test` from the project root.

### Linting

We enforce linting on the code with flake8. Run with `flake8 omnivore` from the project root.

### TODOs

- create method for Discount
- allow refresh of cached properties
- ModifierGroup::option
- TicketItemModifier::modifier
- remove has_embedded_objects for things like nested ticket
  resources where they will never show up as an embedded object
- price_levels
- allow addition of multiple TicketItems
- tests
