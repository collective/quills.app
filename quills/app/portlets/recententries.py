from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Quills imports
from quills.core.interfaces import IWeblogLocator
from quills.app.browser.baseview import BaseView
from quills.app import QuillsAppMessageFactory as _

# Local imports
from base import BasePortletRenderer


PORTLET_TITLE = _(u"Recent Entries")
PORTLET_DESC = _(u"This portlet lists recent weblog entries.")


class IRecentWeblogEntriesPortlet(IPortletDataProvider):

    max_entries = schema.Int(
        title=_(u'Maximum entries'),
        description=_(u"What's the maximum number of entries to list?"),
        required=True,
        default=5)


class Assignment(base.Assignment):

    implements(IRecentWeblogEntriesPortlet)

    def __init__(self, max_entries=5):
        self.max_entries = max_entries

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer, BaseView):

    _template = ViewPageTemplateFile('recententries.pt')

    @property
    def title(self):
        return PORTLET_TITLE

    @property
    def getEntries(self):
        weblog = self.getWeblog()
        return weblog.getEntries(maximum=self.data.max_entries)


class AddForm(base.AddForm):
    form_fields = form.Fields(IRecentWeblogEntriesPortlet)
    label = _(u'add-portlet', default=u"Add ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self, data):
        return Assignment(max_entries=5)


class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentWeblogEntriesPortlet)
    label = _(u'edit-portlet', default=u"Edit ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC
