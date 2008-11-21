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
