from zope.interface import Interface
from zope.component import getUtility, getMultiAdapter, adapts
from zope.interface import implements
from zope.schema import TextLine, Choice, List, Bool
from zope.formlib import form
from zope.event import notify
from Acquisition import aq_inner

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.protect import CheckAuthenticator
from plone.app.controlpanel.events import ConfigurationChangedEvent

from plone.app.form.validators import null_validator
from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Products.statusmessages.interfaces import IStatusMessage

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from atreal.filecart.interfaces import IFileCartMarkerUtility, IFileCartCommentsUtility
from atreal.filecart import FileCartMessageFactory as _
from plone.app.controlpanel.form import ControlPanelForm

class IFileCartSchema(Interface):

    cartable_file_types = List(
        title = _(u'fc_label_cartable_file_types',
                  default=u"Cartable File Types"),
        required = False,
        default = [],
        description = _(u"fc_help_cartable_file_types",
                        default=u"Cartable Content delivered through the web/virtually"),
        value_type = Choice( title=u"cartable_file_types", source="plone.app.vocabularies.ReallyUserFriendlyTypes" )
        )
    
class FileCartControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IFileCartSchema)

    def __init__(self, context):
        super(FileCartControlPanelAdapter, self).__init__(context)

    cartable_file_types = ProxyFieldProperty(IFileCartSchema['cartable_file_types'])
    
class FileCartControlPanel(ControlPanelForm):
    template = ZopeTwoPageTemplateFile('controlpanel.pt')
    form_fields = form.FormFields(IFileCartSchema)
    label = _("FileCart settings")
    description = _("FileCart settings for this site.")
    form_name = _("FileCart settings")

    @form.action(_(u'Update all contents'), name=u'update')
    def handle_update_action(self, action, data):
        CheckAuthenticator(self.request)
        filecartmarkerutility = getUtility(IFileCartMarkerUtility)
        nb_items, bad_items = filecartmarkerutility.updateAll(self.context)
        updated = u'%d %s' % (nb_items, _(u'objects updated.'))
        if not bad_items:
            self.status = updated
        else:
            self.status = u'%s, %d %s: %s' % (updated,
                                              len(bad_items),
                                              _(u'update(s) on object(s) failed'),
                                                ','.join(bad_items),
                                             )        


    @form.action(_(u'Clean all contents'), name=u'clean')
    def handle_clean_action(self, action, data):
        CheckAuthenticator(self.request)
        filecartcommentsutility = getUtility(IFileCartCommentsUtility)
        nb_items, bad_items = filecartcommentsutility.cleanAllComments(self.context)
        cleaned = u'%d %s' % (nb_items, _(u'objects cleaned.'))
        if not bad_items:
            self.status = cleaned
        else:
            self.status = u'%s, %d %s: %s' % (cleaned,
                                              len(bad_items),
                                              _(u'clean-up on object(s) failed'),
                                                ','.join(bad_items),
                                             )

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        #
        msg = self.handle_update_action(data)
        if msg is None:
            msg = u""
        #
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")+msg
            notify(ConfigurationChangedEvent(self, data))
            #self._on_save(data)
        else:
            self.status = _("No changes made.")
    
    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''

    def available(self):
        root = aq_inner(self.context).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)
    

    def handle_update_action(self, data):
        #
        CheckAuthenticator(self.request)
        #
        news = data ['cartable_file_types']
        olds = getattr(self.context, 'cartable_file_types', [])
        adds = []
        for new in news:
            if new in olds:
                olds.remove(new)
            else:
                adds.append(new)
        if len(olds)==0 and len(adds)==0:
            return
        #
        filecartutility = getUtility(IFileCartMarkerUtility)
        #
        nb_items, bad_items = filecartutility.update(self.context, adds, olds)
        updated = u'%d %s' % (nb_items, _(u'objects updated.'))
        if not bad_items:
            return updated
        else:
            return u'%s, %d %s: %s' % (updated,
                                              len(bad_items),
                                              _(u'update(s) on object(s) failed'),
                                                ','.join(bad_items),
                                             )        
    
