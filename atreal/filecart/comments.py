import time

from zope.interface import implements
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from atreal.filecart.interfaces import IFileCartComments, IFileCartCommentsUtility

from UserDict import DictMixin
from persistent import Persistent
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

class OrderedPersistentDict(DictMixin, Persistent):
    def __init__(self, data=None):
        self._data = PersistentMapping()
        self._keylist = PersistentList()
        if not data is None:
            self.update(data)
  
    def __setitem__(self, key, val):
        self._data[key] = val
        if key in self._keylist:
            self._keylist.remove(key)
        self._keylist.append(key)    
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __delitem__(self, key):
        self._keylist.remove(key)
        del self._data[key]
    
    def keys(self):
        return self._keylist[:]

    def reverse(self):
        items = list(self.items())
        items.reverse()
        return items

    
class FileCartComments(object):
    """
    """
    implements(IFileCartComments)
    
    key = "filecart"
    _comments = None
    
    def __init__(self, context):
        """
        """
        self.context = context
    
    @property
    def comments(self):
        """
        """
        if self._comments is None:
            annotations = IAnnotations(self.context)
            if not annotations.has_key(self.key):
                annotations[self.key] = OrderedPersistentDict()
            self._comments = annotations[self.key]
        return self._comments
    
    def hasComments(self):
        """
        """
        annotations = IAnnotations(self.context)
        if annotations.has_key(self.key):
            return True
        else:
            return False
    
    def setComment(self, comment):
        """
        """
        self.comments[time.time()]=comment
    
    def cleanComments(self):
        """
        """
        annotations = IAnnotations(self.context)
        if annotations.has_key(self.key):
            del annotations[self.key]
        self._comments = None
    

class FileCartCommentsUtility(object):
    """
    """
    implements(IFileCartCommentsUtility)
    
    def commentDownload(self, context, brains, comment):
        bad_objects = []
        i = 0
        for brain in brains:
            try:
                IFileCartComments(brain.getObject()).setComment(comment)
                i += 1
            except:
                bad_objects.append(brain.getPath())
                continue
        return i, bad_objects
    
    def cleanAllComments(self, context):
        pc = getToolByName(context, 'portal_catalog')
        bad_objects = []
        i = 0
        brains = pc(object_provides = 'atreal.filecart.interfaces.IFileCartable')
        for brain in brains:
            try:
                process = getattr(IFileCartComments(brain.getObject()), 'cleanComments', None)
                if process != None:
                    process()
                i += 1
            except:
                bad_objects.append(brain.getPath())
                continue
        return i, bad_objects

