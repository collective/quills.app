from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote_plus
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note

from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEntry


class DiscussionReply(BrowserView):
    """
    """

    def __call__(self,
                 subject,
                 body_text,
                 text_format='plain',
                 username=None,
                 password=None):
        """This method is lifted almost directly from CMFPlone's
        discussion_reply.cpy skin script. Modifications start at the point where
        we try to adapt to IWeblogEntry.
        """
        req = self.request
        if username or password:
            # The user username/password inputs on on the comment form were used,
            # which might happen when anonymous commenting is enabled. If they typed
            # something in to either of the inputs, we send them to 'logged_in'.
            # 'logged_in' will redirect them back to this script if authentication
            # succeeds with a query string which will post the message appropriately
            # and show them the result.  if 'logged_in' fails, the user will be
            # presented with the stock login failure page.  This all depends
            # heavily on cookiecrumbler, but I believe that is a Plone requirement.
            came_from = '%s?subject=%s&amp;body_text=%s' % (req['URL'], subject, body_text)
            came_from = url_quote_plus(came_from)
            portal_url = self.context.portal_url()
            return req.RESPONSE.redirect(
                '%s/logged_in?__ac_name=%s'
                '&amp;__ac_password=%s'
                '&amp;came_from=%s' % (portal_url,
                                       url_quote_plus(username),
                                       url_quote_plus(password),
                                       came_from,
                                       )
                )
        # if (the user is already logged in) or (if anonymous commenting is enabled and
        # they posted without typing a username or password into the form), we do
        # the following
        mtool = getToolByName(self.context, 'portal_membership')
        creator = mtool.getAuthenticatedMember().getId()
        dtool = getToolByName(self.context, 'portal_discussion')
        tb = dtool.getDiscussionFor(self.context)
        id = tb.createReply(title=subject, text=body_text, Creator=creator)
        reply = tb.getReply(id)
        # TODO THIS NEEDS TO GO AWAY!
        if hasattr(dtool.aq_explicit, 'cookReply'):
            dtool.cookReply(reply, text_format='plain')
        parent = tb.aq_parent
        # return to the discussable object.
        obj = self.context.plone_utils.getDiscussionThread(tb)[0]
        try:
            entry = IWeblogEntry(obj).__of__(self.context.aq_inner.aq_parent)
            # Check for the existence of a parent weblog to see if `obj' should
            # be treated as having an archive url.
            if IWeblog.providedBy(entry.getWeblog()):
                weview = getMultiAdapter((obj, self.request),
                                         name=u'weblogentry_view')
                base = weview.getArchiveURLFor(entry)
        except TypeError:
            base = obj.getTypeInfo().getActionInfo('object/view',
                                                               obj)['url']
        anchor = reply.getId()
        from Products.CMFPlone.utils import transaction_note
        transaction_note('Added comment to %s at %s' % (parent.title_or_id(),
                                                        reply.absolute_url()))
        self.context.plone_utils.addPortalMessage(_(u'Comment added.'))
        target = '%s#%s' % (base, anchor)
        return req.RESPONSE.redirect(target)
