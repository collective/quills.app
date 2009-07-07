Test the syndication capabilities of Quills via fatsyndication.

Issue ##205 — topic filtered feed show all posts
------------------------------------------------



    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> entry = self.weblog.addEntry(title="Issue #205 Post 1",
    ...                             id="issue205a",
    ...                             topics=['Issue205Tag1'],
    ...                             excerpt="None", text="None")
    >>> entry.publish() 
    >>> entry = self.weblog.addEntry(title="Issue #205 Post 2",
    ...                             id="issue205b",
    ...                             topics=['Issue205Tag2'],
    ...                             excerpt="None", text="None")
    >>> entry.publish() 

    >>> from quills.core.interfaces import ITopicContainer
    >>> ITopicContainer.providedBy(self.weblog)
    True

Quills defines a Topic object for filtering by criteria like keywords
and authors. We now fetch the Topic by which we tagged the first post.

    >>> tag1 = self.weblog.getTopicById('Issue205Tag1')
    >>> tag1.getKeywords()
    ['Issue205Tag1']

It should be only one entry, and it should be the first one.
    
    >>> postsByTag1 = tag1.getEntries()
    >>> len(postsByTag1)
    1

    >>> postsByTag1[0].getId()
    'issue205a'

    >>> postsByTag1[0].getTitle()
    'Issue #205 Post 1'

Now the same for the second entry.

    >>> tag2 = self.weblog.getTopicById('Issue205Tag2')
    >>> tag2.getKeywords()
    ['Issue205Tag2']

    >>> postsByTag2 = tag2.getEntries()
    >>> len(postsByTag2)
    1

    >>> postsByTag2[0].getId()
    'issue205b'

    >>> postsByTag2[0].getTitle()
    'Issue #205 Post 2'

Now create a feed for the first tag and read it. Basesyndication
defines two methods for reading the entries, one sorted, the other
unsorted. We test them both.

    >>> from Products.basesyndication.interfaces import IFeed, IFeedSource
    >>> feed = IFeed(tag1)

First unsorted.

    >>> entries = feed.getFeedEntries()
    
    >>> len(entries)
    1

    >>> entries[0].getTags()
    ('Issue205Tag1',)
    
    >>> entries[0].getTitle()
    'Issue #205 Post 1'

Then sorted.    

    >>> entries = feed.getSortedFeedEntries()
    
    >>> len(entries)
    1

    >>> entries[0].getTags()
    ('Issue205Tag1',)
    
    >>> entries[0].getTitle()
    'Issue #205 Post 1'

Basesyndication also defines the notion of a feed-source that provides
feed entries. This time with only one method for that.

    >>> feed = IFeedSource(tag1)
    >>> entries = feed.getFeedEntries()
    
    >>> len(entries)
    1

    >>> entries[0].getTags()
    ('Issue205Tag1',)
    
    >>> entries[0].getTitle()
    'Issue #205 Post 1'

Topics can be set up for multiple keywords. They then match only posts
tagged by each keyword (logical and). 

But first we need a third post with tagged by two keywords.

    >>> entry = self.weblog.addEntry(title="Issue #205 Post 3",
    ...                             id="issue205c",
    ...                             topics=['Issue205Tag1',
    ...                                     'Issue205Tag2'],
    ...                             excerpt="None", text="None")
    >>> entry.publish() 

Unfortunately, the basesyndication API defines no way for creating
multiple keyword topics. We have to resort to the actual implementation.

    >>> from quills.app.topic import Topic
    >>> tag1tag2 = Topic(keywords=['Issue205Tag1', 'Issue205Tag2'])
    >>> tag1tag2 = tag1tag2.__of__(self.portal['weblog'])
    
    
    >>> tag1tag2.getKeywords()
    ['Issue205Tag1', 'Issue205Tag2']

    >>> postsByTag1Tag2 = tag1tag2.getEntries()
    >>> len(postsByTag1Tag2)
    1

    >>> postsByTag1Tag2[0].getId()
    'issue205c'
    
The feed test as above.

    >>> feed = IFeed(tag1tag2)
    >>> entries = feed.getFeedEntries()  
    >>> len(entries)
    1

    >>> entries[0].getTags()
    ('Issue205Tag1', 'Issue205Tag2')
    
    >>> entries[0].getTitle()
    'Issue #205 Post 3'

Then sorted.    

    >>> entries = feed.getSortedFeedEntries()
    
    >>> len(entries)
    1

    >>> entries[0].getTags()
    ('Issue205Tag1', 'Issue205Tag2')
    
    >>> entries[0].getTitle()
    'Issue #205 Post 3'
