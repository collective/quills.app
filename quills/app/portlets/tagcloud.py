from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.app.portlets.browser.formhelper import NullAddForm
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quills.app import QuillsAppMessageFactory as _
from base import BasePortletRenderer

PORTLET_TITLE = _(u"Tag Cloud")
PORTLET_DESC = _(u"This portlet displays a tag cloud.")


class ITagCloudPortlet(IPortletDataProvider):
    """A tag cloud portlet.
    """

class Assignment(base.Assignment):
    implements(ITagCloudPortlet)

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer):
    _template = ViewPageTemplateFile('tagcloud.pt')

    @property
    def title(self):
        return PORTLET_TITLE
    
    def getCloud(self):
        weblog = self.getWeblog()
        if weblog == []:
            return []
        # Get a list of topics, sorted alphabetically
        topics = weblog.getTopics()
        if not topics:
            return []
        # Create a list of entries for each topic
        topic_size = []
        for topic in topics:
            topic_size.append(len(topic))
        # Find the Min and Max number entries
        min_topic_size = min(topic_size)
        max_topic_size = max(topic_size)
        # Make sure size_topic_size is never 0, or we get ZeroDivisionError later
        size_topic_size = max_topic_size - min_topic_size + 0.0 or 1
        # Create a list to return tuples containing the:
        #    - topic object
        #    - relative weight of the topic, 0.0 to 1.0
        #    - number of entries for that topic, since we already calculated it.
        # Skip topics that have no entries.
        result = []
        for topic, number_of_entries in zip(topics, topic_size):
            if number_of_entries > 0:
                # Normalize the result
                rel = ( (number_of_entries - min_topic_size ) / size_topic_size )
                # Add the result
                cloud_dict = {'topic'               :   topic,
                              'rank'                :   rel,
                              'size'                :   int(rel*10),
                              'number_of_entries'   :   number_of_entries}
                result.append(cloud_dict)
        # Done...
        return result
    
    def getTopicsURL(self):
        weblog = self.getWeblog()
        if weblog == []:
            return ''
        # XXX This feels very hacky!
        if getattr(weblog, 'absolute_url', None):
           url = weblog.absolute_url()
        else:
            # The `weblog' object must be an adapter, so we'll use its context
            # to get hold of the url.
            url = weblog.context.absolute_url()
        return "%s/topics" % url


class AddForm(NullAddForm):
    form_fields = form.Fields(ITagCloudPortlet)
    label = _(u'add-portlet', 
            default=u"Add ${portlet-name} Portlet", 
            mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(ITagCloudPortlet)
    label = _(u'edit-portlet', 
            default=u"Edit ${portlet-name} Portlet", 
            mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

