'''
Created on Apr 6, 2014

@author: benjamin

https://gist.github.com/kipanshi/3859962
'''

def refresh(instance):
    """Select and return instance from database.

    Usage:    ``instance = refresh(instance)``

    """
    return instance.__class__.objects.get(pk=instance.pk)


def update(instance, **data):
    """Update instance with data directly by using ``update()``
    skipping calling ``save()`` method.

    Usage:    ``instance = update(instance, some_field=some_value)``

    """
    instance.__class__.objects.filter(pk=instance.pk).update(**data)
    return refresh(instance)
