from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.app.portlets.browser.formhelper import NullAddForm
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblog
from quills.app.utilities import recurseToInterface
from quills.app import QuillsAppMessageFactory as _

# Local imports
from base import BasePortletRenderer


PORTLET_TITLE = _(u"Quills")
PORTLET_DESC = _(u"This portlet provides links to the various feeds of this instance.")

class IQuillsLinksPortlet(IPortletDataProvider):
    """A weblog administration portlet.
    """


class Assignment(base.Assignment):
    implements(IQuillsLinksPortlet)

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer):

    _template = ViewPageTemplateFile('quillslinks.pt')

    @property
    def title(self):
        return PORTLET_TITLE

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')


class AddForm(NullAddForm):
    form_fields = form.Fields(IQuillsLinksPortlet)
    label = _(u'add-portlet', default=u"Add ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IQuillsLinksPortlet)
    label = _(u'edit-portlet', default=u"Edit ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = _(PORTLET_DESC)
