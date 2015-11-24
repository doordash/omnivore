from omnivore import client


class OmnivoreResource(object):

    @classmethod
    def list_url(cls):
        return client.build_url('locations/')

    @classmethod
    def retrieve_url(cls, instance_id):
        return cls.list_url() + instance_id + '/'

    @classmethod
    def get(cls, instance_id):
        res = client.get(cls.retrieve_url(instance_id))
        return cls(**res)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.refresh_from(**kwargs)

    def refresh(self):
        res = client.get(self.instance_url)
        return self.refresh_from(**res)

    def refresh_from(self, **kwargs):
        raise NotImplementedError

    @property
    def instance_url(self):
        return self.__class__.retrieve_url(self.id)

    def __unicode__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            self.id,
            self.location_id
        )

    def __str__(self):
        return unicode(self).encode('utf-8')


class OmnivoreLocationResource(OmnivoreResource):

    @classmethod
    def list_url(cls, location_id):
        return client.build_url('locations/') + location_id + '/'

    def __init__(self, location_id, **kwargs):
        self.location_id = location_id
        super(OmnivoreLocationResource, self).__init__(**kwargs)
