# Plone imports
from Products.CMFCore.utils import getToolByName

def setup_gs_profiles(portal, profiles, out):
    setup_tool = getToolByName(portal, 'portal_setup')
    for extension_id in profiles:
        try:
            setup_tool.runAllImportStepsFromProfile('profile-%s' % extension_id)
        except Exception, e:
            print >> out, "Error while trying to GS import %s (%s, %s)" \
                          % (extension_id, repr(e), str(e))
            raise

def addNewDiscussionReplyFormAction(portal, out=None):
    # We use this to stop discussion_reply_form from ending up redirecting to
    # a URL that doesn't take account of the weblog archive.
    # See quills.app.browser.discussionreply for more details.
    pfc = getToolByName(portal, 'portal_form_controller')
    pfc.addFormAction(object_id='discussion_reply_form',
                      status='success',
                      context_type='',
                      button='',
                      action_type='traverse_to',
                      action_arg='string:discussion_reply_redirect')
    if out is not None:
        print >> out, "Added form controller action to over-ride discussion_reply."

def delNewDiscussionReplyFormAction(portal, out=None):
    pfc = getToolByName(portal, 'portal_form_controller')
    # PFC has a terrible API for deleting which is clearly only intended to
    # happen ttw. This code is adapted from pfc._delFormActions.
    from Products.CMFFormController.FormAction import FormActionKey
    try:
        pfc.actions.delete(FormActionKey(object_id='discussion_reply_form',
                                         status='success',
                                         context_type='',
                                         button='',
                                         controller=pfc)
                          )
        msg = 'Removed form controller action that over-rode discussion_reply.'
    except KeyError:
        # The action wasn't found so it must have been removed already.
        msg = 'Did not find (for removal) form controller action that over-rode discussion_reply.'
    if out is not None:
        print >> out, msg
