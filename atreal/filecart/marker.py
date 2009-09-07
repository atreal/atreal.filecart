
from zope.interface import implements, alsoProvides, noLongerProvides
from zope.component import queryUtility

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from atreal.filecart.browser.controlpanel import IFileCartSchema
from atreal.filecart.interfaces import IFileCartMarker, IFileCartMarkerUtility, IFileCartable
from atreal.filecart import FileCartMessageFactory as _

class FileCartMarker(object):
    """
    """
    implements(IFileCartMarker)

    def __init__(self, context):
        """
        """
        self.context = context

    @property
    def _options(self):
        _siteroot = queryUtility(IPloneSiteRoot)
        return IFileCartSchema(_siteroot)
    
    @property
    def cartable_portal_types (self):
        """ Return the cartable portal types
        """
        return  getattr (self._options, 'cartable_file_types', [])

    def process(self):
        """ Proceed to the markage
        """
        if not self.context.portal_type in self.cartable_portal_types:
            self.clear()
        else:
            self.add()

    def add(self):
        """ Add the markage
        """
        if IFileCartable.providedBy(self.context):
            return
        alsoProvides(self.context, IFileCartable)
        self.context.reindexObject(idxs=['object_provides'])
    
    def clear(self):
        """ Clear the markage
        """
        if not IFileCartable.providedBy(self.context):
            return
        noLongerProvides(self.context, IFileCartable)
        self.context.reindexObject(idxs=['object_provides'])
    

class FileCartMarkerUtility(object):
    """
    """
    implements(IFileCartMarkerUtility)
    
    def update(self, context, news, olds):
        """ Update only objects with a change of configuration
        """
        i = 0
        bad_objects = []
        for new in news:
            j, bads = self._walker(context, 'add', new)
            i += j
            bad_objects += bads
        for old in olds:
            j, bads = self._walker(context, 'clear', old)
            i += j
            bad_objects += bads
        return i, bad_objects

    def updateAll(self, context):
        """ Update all objects on portal 
        """
        return self._walker(context, 'process')
    
    def _walker(self, context, meth, portal_type = ''):
        """ 
        """
        pc = getToolByName(context, 'portal_catalog')
        bad_objects = []
        i = 0
        if portal_type != '':
            brains = pc(portal_type=portal_type)
        else:
            brains = pc()
        
        for brain in brains:
            try:
                process = getattr(IFileCartMarker(brain.getObject()), meth, None)
                if process != None:
                    process()
                i += 1
            except:
                bad_objects.append(brain.getPath())
                continue
        return i, bad_objects
    
