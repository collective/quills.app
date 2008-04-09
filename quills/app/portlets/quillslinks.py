from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblog
from quills.app.utilities import recurseToInterface

# Local imports
from base import BasePortletRenderer


PORTLET_TITLE = u"Quills"
PORTLET_DESC = u"This portlet provides links to the various feeds of this instance."

class IQuillsLinksPortlet(IPortletDataProvider):
    """A weblog administration portlet.
    """


class Assignment(base.Assignment):
    implements(IQuillsLinksPortlet)

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(BasePortletRenderer, base.Renderer):

    _template = ViewPageTemplateFile('quillslinks.pt')

    @property
    def title(self):
        return _(PORTLET_TITLE)

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')


class AddForm(base.AddForm):
    form_fields = form.Fields(IQuillsLinksPortlet)
    label = _(u"Add %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IQuillsLinksPortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
