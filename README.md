# Omnivore Python library

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
# TODO: open/void tickets
# TODO: payments
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
