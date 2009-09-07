from Acquisition import aq_inner

from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from atreal.filecart.interfaces import IFileCartComments

class FileCartCommentsViewlet(ViewletBase):
    """
    """
    controls = ViewPageTemplateFile("controls.pt")

    def update(self):
        super(FileCartCommentsViewlet, self).update()
        #
        self.comments_length = IFileCartComments(self.context).comments.__len__()
        if getattr(self.request, 'showAllComments', False) == True:
            self.comments = IFileCartComments(self.context).comments.reverse()
            self.collapsed = None
            self.expanded = "filecartcollapsed"
        else:
            self.comments = IFileCartComments(self.context).comments.reverse()[:5]
            self.collapsed = "filecartcollapsed"
            self.expanded = None
        #
        self.portal_membership = getToolByName(self.context, 'portal_membership', None)
    
    index = ViewPageTemplateFile("comments.pt")

    def format_date(self, date):
        context = aq_inner(self.context)
        util = getToolByName(context, 'translation_service')
        return util.ulocalized_time(date, True, None, context)
    
    def anonymous(self):
        return self.portal_state.anonymous()

    def canViewComments(self):
        # Use portal_membership tool for checking permissions
        mtool = self.context.portal_membership
        checkPermission = mtool.checkPermission
        # checkPermissions returns true if permission is granted
        if checkPermission('atreal.filecart: View Download Comments', self.context):
            return True
        return False

    def canDeleteComments(self):
        # Use portal_membership tool for checking permissions
        mtool = self.context.portal_membership
        checkPermission = mtool.checkPermission
        # checkPermissions returns true if permission is granted
        if checkPermission('atreal.filecart: Delete Download Comments', self.context):
            return True
        return False

    def member_info(self, creator):
        if self.portal_membership is None:
            return None
        else:
            return self.portal_membership.getMemberInfo(creator)
