from zope.interface.interfaces import IInterface
from zope.component import queryUtility

from atreal.filecart.interfaces import IFileCartMarker


def is_filecart_installed():
    """ 
    """
    return queryUtility(IInterface, name=u'atreal.filecart.interfaces.IFileCartSite', default=False)


def markObject(obj, event):
    """
    """
    if not is_filecart_installed():
        return
    try:
        IFileCartMarker(obj).process()
    except AttributeError, e:
        print "atreal.filecart: error in event"
        return
