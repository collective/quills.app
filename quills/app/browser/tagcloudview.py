# Zope imports
from zope.interface import implements
from Products.Five import BrowserView

# Plone imports
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.browser.interfaces import ITagCloudView
#from quills.app.utilities import WeblogFinder


class TagCloudView(BrowserView):
    """A view to help in rendering tag clouds.
    """

    implements(ITagCloudView)

    def getCloud(self, weblog=None):
        if weblog is None:
            # Get the parent weblog
            weblog = self.getParentWeblog(self.context)
        # Get a list of topics, sorted alphabetically
        topics = weblog.getCategories()
        if not topics:
            return []
        # Create a list of entries for each topic
        topic_size = []
        for topic in topics:
            topic_size.append(  len(topic) )
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
                rel = ( (number_of_entries - min_topic_size ) /
                        size_topic_size )
                # Add the result
                result.append( [topic, rel, number_of_entries] )
        # Done...
        return result

    def getClouds(self):
        result=[]
        # Get all the Weblogs in the instance
        catalog = getToolByName(self.context, 'portal_catalog')
        weblogs = catalog.searchResults(sort_on='id', meta_type='Weblog')
        # For each blog, get the cloud. If something in the cloud, add to result
        for weblog in weblogs:
            weblog = weblog.getObject()
            cloud = self.getCloud(weblog)
            if cloud:
                result.append({"weblog": weblog, "cloud": cloud})
        return result
