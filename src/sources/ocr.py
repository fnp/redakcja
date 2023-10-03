from lxml import etree


def add_page_to_master(master, ocr_filename):
    """ Simplest implementation: just dump text to an akap. """
    with open(ocr_filename) as f:
        txt = f.read()

    txt = txt.strip()

    if len(master):
        master[-1].tail = (master[-1].tail or '') + '\n\n' + txt + '\n\n'
    else:
        master.text = (master.text or '') + '\n\n' + txt + '\n\n'


def add_page_to_master_as_stanzas(master, ocr_filename):
    """ Simplest implementation: just dump text to an akap. """
    with open(ocr_filename) as f:
        txt = f.read()

    strofa = etree.SubElement(master, 'strofa')
    strofa.text="\n"
    for piece in txt.split('\n'):
        if not piece.strip(): continue
        strofa.text += piece + '/\n'
    

def add_page_to_master_as_p(master, ocr_filename):
    """ Simplest implementation: just dump text to an akap. """
    with open(ocr_filename) as f:
        txt = f.read()

    for piece in txt.strip().split('\n\n'):
        if not piece.strip(): continue
        p = etree.SubElement(master, 'akap')
        p.text = piece
