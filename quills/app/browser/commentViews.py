from controllerView import FormControllerView, getToolByName
from quills.app.utilities import talkbackURL

class ManageCommentsView(FormControllerView):
    """ The view class for the comments management form """
    
    def __init__(self, context, request):
        super(ManageCommentsView, self).__init__(context, request)

        self.form_submitted = bool(request.get('form.submitted'))
        if bool(request.get('form.button.Delete')):
            self.mode = "delete"
        elif bool(request.get('form.button.Update')):
            self.mode = "update"
        elif bool(request.get('form.button.ResetFilter')):
            self.mode = "reset"
        else:
            self.mode = 'display'

        self.author = request.get('form.field.author', '')
        self.subject = request.get('form.field.subject', '')
        self.selected_comments = request.get('selected_comments', [])
        self.portal_catalog = getToolByName(self.context,'portal_catalog')

        self.contentFilter = {
            'portal_type' : 'Discussion Item', 
            'sort_on' : 'created', 
            'sort_order' : 'reverse',
            'path' : {'query' : '/'.join(self.context.getPhysicalPath()),}
        }

        self.filtered = False
        if self.mode in ['delete', 'display', 'update']:
            if self.author:
                self.contentFilter['Creator'] = self.author
                self.filtered = True
            if self.subject:
                self.contentFilter['Title'] = self.subject
                self.filtered = True
        if self.mode == "display":
            self.getComments()

    def validate(self):
        """ performs validation and returns an errors dictionary """
        errors = {}
        if self.mode=='delete':
            if self.selected_comments == []:
                errors['status'] = 'failure'    # errors must not be empty...            
                self.setMessage('You must select at least one comment for deletion.')
                self.getComments()
        return errors

    def control(self):
        """ performs the actions after a successful validation possibly
            returning an errors dictionary """

        if self.mode == "update":
            self.setMessage('Filter applied.')
        elif self.mode == "reset":
            self.setMessage('Filter reset.')
            self.author = None
            self.subject = None
        elif self.mode == "delete":
            discussion_tool = getToolByName(self.context, 'portal_discussion')
            for path in self.selected_comments:
                self.deleteReply(discussion_tool, self.portal_catalog, path)
            self.setMessage('%s comments have been deleted.' % str(len(self.selected_comments)))

        self.getComments()
        return {}
            
    def deleteReply(self, dtool, pcatalog, path):
        discussion_item = pcatalog(path=path)[0].getObject()
        obj = discussion_item.parentsInThread()[0]
        discussion = dtool.getDiscussionFor(obj)
        discussion.deleteReply(discussion_item.getId())

    def getComments(self):
        self.comment_brains = self.portal_catalog(self.contentFilter)
        self.num_of_comments = len(self.comment_brains)
        self.has_comments = self.num_of_comments > 0
        return self.comment_brains

    def talkbackURL(self, item):
        return talkbackURL(item)
