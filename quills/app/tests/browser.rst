Quills browser tests
====================

Here we klick ourselves through a Quills instance and check that everything is in order. First some boilerplate to get our browser up and running:

    >>> self.setRoles(("Contributor",))
    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = False
    >>> entry = self.weblog.addEntry("Blog entry",
    ...                              "Just for testing",
    ...                              "Nothing to see.",
    ...                              ['fishslapping'],
    ...                              id="entry")
    >>> from quills.core.interfaces import IWeblogEntry
    >>> IWeblogEntry.providedBy(entry)
    True

    >>> entry.publish()
    >>> browser.open('http://nohost/plone/weblog/')

portlets
********

Viewing the blog we should get a few portlets. authors, recent entries and the tag cloud:

    >>> browser.contents
    '...<dl class="portlet portletWeblogAuthors"...'

    >>> browser.contents
    '...<dl class="portlet portletRecentEntries"...'

    >>> browser.contents
    '...<dl class="portlet portletWeblogArchive"...'

    >>> browser.contents
    '...<dl class="portlet portletTagCloud"...
     ...<a...href="http://nohost/plone/weblog/topics/fishslapping"...
     ...title="1 entries">fishslapping</a>...'

And since we're authenticated as Contributor, we also get the admin portlet:

    >>> browser.contents
    '...<dl class="portlet portletWeblogAdmin"...'

And last but not least, the Quills portlet:

    >>> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'


feed links
**********

When viewing a blog, there should be links to its feeds. We expect atom, rss 2.0 and rdf 1.0 and 1.1:

    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/atom+xml"...
     ...title="Atom feed"...
     ...http://nohost/plone/weblog/atom.xml...'

    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/rss+xml"...
     ...title="RSS 2.0 feed"...
     ...http://nohost/plone/weblog/rss.xml...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed11.rdf...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed.rdf...'

the same links should also be present when viewing an entry, but note, we only
guarantee this when an weblog entry is view within the archive hierarchy, not
for URLs like 'http://nohost/plone/weblog/entry'.

    >>> date = entry.getPublicationDate()
    >>> year = str(date.year())
    >>> month = str(date.month()).zfill(2)
    >>> day = str(date.day()).zfill(2)
    >>> archive_path = '%s/%s/%s' % (year, month, day)
    >>> browser.open('http://nohost/plone/weblog/%s/entry' % archive_path)
    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/atom+xml"...
     ...title="Atom feed"...
     ...http://nohost/plone/weblog/atom.xml...'

    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/rss+xml"...
     ...title="RSS 2.0 feed"...
     ...http://nohost/plone/weblog/rss.xml...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed11.rdf...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed.rdf...'


archive
*******

having one published entry also gives us an archive:

    >>> date = self.weblog.getEntry('entry').getPublicationDate()
    >>> year = str(date.year())
    >>> month = str(date.month()).zfill(2)
    >>> day = str(date.day()).zfill(2)

    >>> browser.open('http://nohost/plone/weblog/%s/' % year)
    >>> ('<h1>%s' % year) in browser.contents
    True

Viewing the archive should still give us a context where the portlets are rendered. We test this by checking for the quillslinks portlet:

    >> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'

    >>> from Products.CMFPlone.i18nl10n import monthname_english
    >>> browser.open('http://nohost/plone/weblog/%s/%s/' % (year, month))
    >>> ('<h1>%s' % monthname_english(month)) in browser.contents
    True

    >> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'

    >>> browser.open('http://nohost/plone/weblog/%s/%s/%s/' % (year, month, day))
    >>> browser.contents
    '...Blog entry...'

    >>> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'

topics
******

    >>> browser.open('http://nohost/plone/weblog/topics')
    >>> '<div id="weblogtopics">' in browser.contents
    True

Viewing the topics overview should still give us a context where the portlets are rendered. We test this by checking for the quillslinks portlet:

    >> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'


Having a published entry with the topic 'fishslapping' gives us the following:

    >>> browser.open('http://nohost/plone/weblog/topics/fishslapping')
    >>> '<div id="topic-summary">' in browser.contents
    True

    >>> 'Blog entry' in browser.contents
    True

    >>> '<h1>fishslapping</h1>' in browser.contents
    True

Viewing the topic view should still give us a context where the portlets are rendered. We test this by checking for the quillslinks portlet:

    >>> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'


author topics
*************

    >>> browser.open('http://nohost/plone/weblog/authors')
    >>> '<h1 class="documentFirstHeading">Weblog Authors</h1>' in browser.contents
    True

    >>> '<a href="http://nohost/plone/weblog/authors/portal_owner">portal_owner</a>' in browser.contents
    True


configure blog
**************

We need the `Manager` role to configure the weblog:

    >>> self.setRoles(("Manager",))

Now let's configure it ttw:

    >>> browser.open('http://nohost/plone/weblog')
    >>> browser.getLink('Configure').click()
    >>> browser.url
    'http://nohost/plone/weblog/config_view'

But we can also reach this screen via the management portlet:

    >>> browser.getLink('Configure Blog').click()
    >>> browser.url
    'http://nohost/plone/weblog/config_view'


Breadcrumbs
***********

Viewing an entry in its archive location should give us breadcrumbs that respect
the archive location (e.g. 'You are here: Home -> Blog -> 2008 -> December'). To
test this, first we'll set the publication date to something static that we can
check for (rather than just 'now'):

    >>> entry = self.weblog.getEntry('entry')
    >>> from DateTime.DateTime import DateTime
    >>> entry.setPublicationDate(DateTime('2008/12/16'))

Now let's check the breadcrumb is there for the year:

    >>> browser.open('http://nohost/plone/weblog/2008/12/16/entry')
    >>> import re
    >>> s = '<a href="http://nohost/plone/weblog/2008">2008</a>\s*<span class="breadcrumbSeparator">\s*&[a-z]{4,6};'
    >>> re.search(s, browser.contents) is not None
    True

We also check that we've got the order of the breadcrumbs correct. During
development, there was a problem with the entry appearing between 'Home' and
'Weblog'.

    >>> s_plone3 = '<a href="http://nohost/plone">Home</a>\s*<span class="breadcrumbSeparator">\s*&rarr;\s*</span>\s*<span dir="ltr">\s*<a href="http://nohost/plone/weblog">Test Weblog</a>'
    >>> s_plone4 = '<a href="http://nohost/plone">Home</a>\s*<span class="breadcrumbSeparator">\s*&rsaquo;\s*</span>\s*</span>\s*<span id="breadcrumbs-1" dir="ltr">\s*<a href="http://nohost/plone/weblog">Test Weblog</a>'
    >>> (re.search(s_plone3, browser.contents) is not None) or (re.search(s_plone4, browser.contents) is not None)
    True


Manage Comments View
********************

We'll test the 'manage_comments' view here - the view that is used to help keep
all comments within a blog in some sense of order.

Can we access the view?

    >>> browser.open('http://nohost/plone/weblog/@@manage_comments')

What about if there are some comments present within the blog? By default we
need the `Manager' role to add comments:

    >>> self.setRoles(("Contributor", "Reviewer", "Manager"))

We also need to enable comments for the portal type underlying our weblog entry.

    >>> entry = self.weblog.getEntry('entry')
    >>> # Remember, the return value from getEntry could be catalogbrain-ish, or
    >>> # an adapter, or an actual content-ish entry object.
    >>> entry_content = entry.getWeblogEntryContentObject()
    >>> portal_type = entry_content.portal_type

Now we need to enable commenting for our portal_type.

    >>> dtype = self.portal.portal_types[portal_type]
    >>> dtype.manage_changeProperties(allow_discussion=1)
    >>> entry_content.allowDiscussion(1)
    >>> entry_content.reindexObject()

Let's add a comment to our weblog entry.

    >>> dtool = self.portal.portal_discussion
    >>> discussion = dtool.getDiscussionFor(entry_content)
    >>> id = discussion.createReply(title='Parrots', text='... talk like people.')

Now, can we still access the comments view?

    >>> browser.open('http://nohost/plone/weblog/@@manage_comments')
