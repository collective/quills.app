from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quills.app.utilities import getArchiveURLFor
from quills.app.browser.baseview import BaseView
from quills.app import QuillsAppMessageFactory as _

from base import BasePortletRenderer

PORTLET_TITLE = _(u"Recent Comments")
PORTLET_DESC = _(u"This portlet lists recent weblog comments.")


class IRecentWeblogCommentsPortlet(IPortletDataProvider):
    max_comments = schema.Int(
        title=_(u'Maximum comments'),
        description=_(u"What's the maximum number of comments to list?"),
        required=True,
        default=5)


class Assignment(base.Assignment):
    implements(IRecentWeblogCommentsPortlet)

    def __init__(self, max_comments=5):
        self.max_comments = max_comments

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer, BaseView):
    _template = ViewPageTemplateFile('recentcomments.pt')

    @property
    def available(self):
        return len(self.getComments) > 0

    @property
    def title(self):
        return PORTLET_TITLE

    @property
    def getComments(self):
        weblog_content = self.getWeblogContentObject()
        if weblog_content is None:
            return []
        view = getMultiAdapter((weblog_content, self.request), name='manage_comments')
        return view.getComments()[:self.data.max_comments]

    def talkbackURL(self, item):
        # XXX This is (sadly) CMF-DiscussionItem-specific :(.
        comment = item.getObject()
        if not hasattr(comment, 'parentsInThread'):
            return comment.absolute_url()
        parent_comments = comment.parentsInThread()
        commented_object = parent_comments[0]
        weblog_content = self.getWeblogContentObject()
        base_url = getArchiveURLFor(commented_object, weblog_content)
        return '%s#%s' % (base_url, item.id)


class AddForm(base.AddForm):
    form_fields = form.Fields(IRecentWeblogCommentsPortlet)
    label = _(u'add-portlet', 
            default=u"Add ${portlet-name} Portlet", 
            mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self, data):
        return Assignment(max_comments=5)


class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentWeblogCommentsPortlet)
    label = _(u'edit-portlet', 
            default=u"Edit ${portlet-name} Portlet", 
            mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC


