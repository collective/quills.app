from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.app.portlets.browser.formhelper import NullAddForm
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneLocalesMessageFactory as _PLMF

# Quills imports
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblog
from quills.app.utilities import recurseToInterface
from quills.app.browser.baseview import BaseView
from quills.app import QuillsAppMessageFactory as _

# Local imports
from base import BasePortletRenderer


PORTLET_TITLE = _(u"Weblog Archive")
PORTLET_DESC = _(u"This portlet lists the archive of this weblog.")


class IWeblogArchivePortlet(IPortletDataProvider):
    """a portlet showing the archive of the current weblog"""


class Assignment(base.Assignment):

    implements(IWeblogArchivePortlet)

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer, BaseView):

    _template = ViewPageTemplateFile('archive.pt')
    
    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        self.data = data
        self._translation_service = getToolByName(self.context, 'translation_service')

    def getMonthName(self, month):
        """Returns the current month name as a Message."""
        msgid   = self._translation_service.month_msgid(month)
        english = self._translation_service.month_english(month)
        return _PLMF(msgid, default=english)

    @property
    def title(self):
        return PORTLET_TITLE

    @property
    def getSubArchives(self):
       weblog = self.getWeblog()
       return weblog.getSubArchives()


class AddForm(NullAddForm):
    form_fields = form.Fields(IWeblogArchivePortlet)
    label = _(u'add-portlet', default=u"Add ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IWeblogArchivePortlet)
    label = _(u'edit-portlet', default=u"Edit ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC
