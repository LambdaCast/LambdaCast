'''
Created on Apr 5, 2014

@author: benjamin
'''

from django.utils.translation import ugettext_lazy as _

LICENSE_CHOICES = (
    ("None", _(u"No License")),
    ("CC0", _(u"Public Domain/CC0")),
    ("CC-BY", _(u"CreativeCommons - Attribution")),
    ("CC-BY-NC", _(u"CreativeCommons - Attribution - NonCommercial")),
    ("CC-BY-NC-ND", _(u"CreativeCommons - Attribution - NonCommercial - NoDerivs")),
    ("CC-BY-ND", _(u"CreativeCommons - Attribution - NoDerivs")),
)

LICENSE_URLS = {'None': "",
                'CC0': _(u"https://creativecommons.org/publicdomain/zero/1.0/"),
                'CC-BY': _(u"http://creativecommons.org/licenses/by/3.0/"),
                'CC-BY-NC': _(u"http://creativecommons.org/licenses/by-nc/3.0/"),
                'CC-BY-NC-ND': _(u"http://creativecommons.org/licenses/by-nc-nd/3.0/"),
                'CC-BY-ND': _(u"http://creativecommons.org/licenses/by-nd/3.0/")
}