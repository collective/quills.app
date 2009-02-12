from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize

# Quills imports
from quills.core.interfaces import IBaseContent
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblog
from quills.app.utilities import recurseToInterface
from quills.app import QuillsAppMessageFactory as _

# Local imports
from base import BasePortletRenderer


PORTLET_TITLE = _(u"Weblog Authors")
PORTLET_DESC = _(u"This portlet lists weblog authors.")


class IWeblogAuthorsPortlet(IPortletDataProvider):

    show_location = schema.Bool(
        title=_(u'Show author location?'),
        description=_(u"If available, should the author's location be shown?"),
        required=True,
        default=True)

    show_portrait = schema.Bool(
        title=_(u'Show author portrait?'),
        description=_(u"If available, should the author's portrait be shown?"),
        required=True,
        default=True)

    show_description = schema.Bool(
        title=_(u'Show author description?'),
        description=_(u"If available, should the author's description be shown?"),
        required=True,
        default=True)


class Assignment(base.Assignment):

    implements(IWeblogAuthorsPortlet)

    def __init__(self,
                 show_location=True,
                 show_portrait=True,
                 show_description=True):
        self.show_location = show_location
        self.show_portrait = show_portrait
        self.show_description = show_description

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer):

    _template = ViewPageTemplateFile('authors.pt')

    @property
    def title(self):
        return PORTLET_TITLE
    
    @property
    def authors(self):
        weblog = self.getWeblog()
        return weblog.getAuthors()

    def getPortraitFor(self, author):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getPersonalPortrait(author.getId())

    def getInfoFor(self, author):
        mtool = getToolByName(self.context, 'portal_membership')
        info = mtool.getMemberInfo(author.getId())
        if info is None:
            info = { 'fullname'    : author.getId(),
                     'description' : '',
                     'location'    : '',
                     'language'    : '',
                     'home_page'   : '',
                     'username'    : author.getId(),
                   }
        if not info['fullname']:
            info['fullname'] = author.getId()
        if not info['username']:
            info['username'] = author.getId()
        return info
    
    def getAuthorURL(self, author_id):
        weblog = self.getWeblogContentObject()
        return "%s/authors/%s" % (weblog.absolute_url(), author_id)
    
    def getAuthorsURL(self):
        weblog = self.getWeblogContentObject()
        return "%s/authors" % weblog.absolute_url()


class AddForm(base.AddForm):
    form_fields = form.Fields(IWeblogAuthorsPortlet)
    label = _(u'add-portlet', default=u"Add ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self, data):
        return Assignment(show_location=data.get('show_location', True),
                          show_portrait=data.get('show_portrait', True),
                          show_description=data.get('show_description', True))


class EditForm(base.EditForm):
    form_fields = form.Fields(IWeblogAuthorsPortlet)
    label = _(u'edit-portlet', default=u"Edit ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC
