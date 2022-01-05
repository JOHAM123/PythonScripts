from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTImage, LTFigure, LTPage
from io import StringIO, BytesIO
from io import open
from subprocess import call
from pdfminer.pdftypes import PDFObjRef, dict_value, stream_value, PDFObject, resolve_all, resolve1
from pdfminer.psparser import literal_name
from pdfminer.pdffont import TrueTypeFont, PDFFont, PDFCIDFont
from pdfminer.psparser import PSLiteral
from pdfminer.psparser import LIT
import re
import json
# from pdfminer.high_level import extract_text
from pdfminer.utils import decode_text


def testfont(file):
    with open(file, 'rb') as pdf:
        parser = PDFParser(pdf)
        document = PDFDocument(parser)
    fonts = set()
    embedded = set()

    for page in PDFPage.get_pages(document):
        fontsList = page.resources.get('Font', {})
        for font in fontsList:
            fontobj = dict_value(fontsList.get(font, {}))
            f, e = reportEmbededFonts_Settings_walk(fontobj, fonts, embedded)

    fonts = fonts.union(f)
    embedded = embedded.union(e)

    unembedded = fonts - embedded
    return({"fonts": list(fonts), "embedded": list(
        embedded), "unembeded": list(unembedded)})


def reportEmbededFonts_Settings_walk(obj, fnt, emb):
    fontkeys = set(['FontFile', 'FontFile2', 'FontFile3'])
    descriptor = (dict_value(obj.get('FontDescriptor')))

    if 'BaseFont' in obj:
        fnt.add(obj['BaseFont'])
    if 'FontName' in descriptor and fontkeys.intersection(descriptor):
        print(descriptor.get('FontName'))
        emb.add(descriptor.get('FontName'))

    for k in obj:
        if hasattr(obj[k], 'keys'):
            reportEmbededFonts_Settings_walk(obj[k], fnt, emb)
    return fnt, emb


def testPagemode(file):
    with open(file, 'rb') as pdf:
        parser = PDFParser(pdf)
        document = PDFDocument(parser)
        pagemode = document.catalog.get('PageMode')
    print(pagemode)


def testPageNum(file):
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, '')

    pages = dict((page.pageid, pageno) for (pageno, page)
                 in enumerate(PDFPage.create_pages(document)))

    _result = []

    outlines = document.get_outlines()

    for (level, title, dest, action, se) in outlines:
        if dest is not None:
            _result.append(
                {"page_num": pages[dest[0].objid], "title": title, "zoomType": dest[1]})
        # print(pages[dest[0].objid], title,dest[1])
        else:
            _result.append({"page_num": pages[resolve1(action).get(
                'D')[0].objid], "title": title, "zoomType": resolve1(action).get('D')[1]})

    return _result


def testAttachment(file):
    files = []
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, '')
    pages = dict((page.pageid, pageno) for (pageno, page)
                 in enumerate(PDFPage.create_pages(document)))

    for page in PDFPage.get_pages(fp):
        annots = resolve1(page.annots)
        if annots is not None:
            for anot in annots:
                _anot = resolve1(anot)
                if _anot.get('Subtype') == LIT('FileAttachment'):
                    # print(_anot)
                    print({"page No": pages[page.pageid], "Author Name": _anot.get('T'), "attach_file_name": _anot.get('Contents'),
                           "attach_file_description": _anot.get('Subj'), "attach_icon": _anot.get('Name')})
    return files


def testblankPage(file):
    files = []
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, '')
    pages = dict((page.pageid, pageno) for (pageno, page)
                 in enumerate(PDFPage.create_pages(document)))

    for page in PDFPage.get_pages(fp):
        if len(page.contents) == 0:
            files.append({"page No": pages[page.pageid]})

    return files


allowedPageSizes = [
    {
        "type": "a4",
        "W": 8.3,
        "H": 11.7
    },
    {
        "type": "letter",
        "W": 8.5,
        "H": 11.0
    }
]
# standard dpi
DPI = 72
allowedPageOrientation = ["landscape"]


def get_nonallow_page_size(file):

    files = []
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, '')

    pages = dict((page.pageid, pageno) for (pageno, page)

                 in enumerate(PDFPage.create_pages(document)))

    allowPages = []

    nonallowPages = []

    for page in PDFPage.get_pages(fp):

        r = 0 if page.rotate is None else page.rotate

        w = page.mediabox[2]

        h = page.mediabox[3]

        pageno = pages[page.pageid]

        orientations_type, page_size_type = get_nonallow_page_size_walk(
            w, h, r)

        if orientations_type is None or page_size_type is None:

            nonallowPages.append(
                {"orientations_type": orientations_type, "page_size_type": page_size_type, "pageno": pageno})

        elif orientations_type is not None or page_size_type is not None:

            allowPages.append(

                {"orientations_type": orientations_type, "page_size_type": page_size_type, "pageno": pageno})

    files.append(

        {"allowablePages": allowPages, "nonallowPage": nonallowPages})

    return files


def get_nonallow_page_size_walk(w, h, r):

    orientations_type = None

    page_size_type = None

    # check for page orientation

    for o_type in allowedPageOrientation:

        if o_type == 'portrait' and (r == 180 or r == 0):

            orientations_type = o_type

            break

        elif o_type == 'landscape' and (r == 90 or r == 270):

            orientations_type = o_type

            break

    # check for layout a4 or letter

    for pageSize in allowedPageSizes:

        if (int(pageSize['W'] * DPI) == w) and int((pageSize['H'] * DPI) == h):

            page_size_type = pageSize['type']

    return orientations_type, page_size_type


CHARMAP_ENCODINGS = [
    'latin-1',
    'iso-8859-2',
    'macroman',
    'cp437'
]


def _check_grabled(text):
    # Define a regex that matches ASCII text.

    if re.compile('^[\x00-\x7f]*$').match(text):
        return 'asci'

    for encoding in CHARMAP_ENCODINGS:
        byte_range = bytes(list(range(0x80, 0x100)) + [0x1a])
        charlist = byte_range.decode(encoding)
        regex = '^[\x00-\x19\x1b-\x7f{0}]*$'.format(charlist)
        if (re.compile(regex).match(text)):
            return encoding
    return False


def testgrabbledText(file):
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, '')

    pages = dict((page.pageid, pageno) for (pageno, page)
                 in enumerate(PDFPage.create_pages(document)))
    outlines = document.get_outlines()
    grabledtext = []
    for (level, title, dest, action, se) in outlines:
        if not _check_grabled(title):
            if dest is not None:
                grabledtext.append(
                    {"page_num": pages[dest[0].objid], "title": title})
            else:
                grabledtext.append({"page_num": pages[resolve1(action).get(
                    'D')[0].objid], "title": title})
    return grabledtext


def test_first_Bookmark_missing(file):
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    outlines = doc.get_outlines()
    _result = True
    for (level, title, dest, action, se) in outlines:
        if dest is not None:
            _result = search_page_toc(dest[0].objid, fp)
            break
    return _result


def search_page_toc(objid, fp):
    pages = zip(PDFPage.get_pages(fp), range(1, 2))
    print(pages)
    for page, pagenum in pages:
        if page.pageid != objid:
            return False
        else:
            return True


def convert_pdf_to_string(file_path):
    output_string = StringIO()
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(
            rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return(output_string.getvalue())


def valid_toc(self, toc):
    with open(str(self._doc), "rb") as pdffile:
        parser = PDFParser(pdffile)
        document = PDFDocument(parser)
        try:
            real_toc = list(document.get_outlines())
        except PDFNoOutlines:
            return len(toc) == 0
        print("TOC from PDF file:", real_toc)
        if len(real_toc) != len(toc):
            print("Incorrect TOC length")
            return False
        for ref, real in zip(toc, real_toc):
            print("Checking", ref)
            if not ref[0] + 1 == real[0]:
                # level
                return False
            if not self._is_reference_to_ith_page(real[2][0], ref[1] - 1):
                # destination
                return False
            if not ref[2] == real[1]:
                # title
                return False
    return True


def testscannable(fp):
    fp = open(fp, 'rb')
    result = []
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        layout = device.get_result()
        for x in layout:
            if (isinstance(x, LTFigure)):
                for im in x:
                    if isinstance(im, LTImage):
                        # print(im.__dict__)
                        filterType = (im.stream.get_any(
                            ('filter', 'Filter'))).name
                        w, h = im.srcsize
                        print(im.stream)
                        print(resolve1(im.stream['Metadata']))
    #                     color_space = get_color_mode(
    #                         resolve1((im.colorspace)[0]))
    #                     compression_type = get_compression_type(filterType)
    #                     allowedSettings = ""
    #                     scan_setting_allowed = check_allowed_scanSettings(
    #                         color_space, allowedSettings, compression_type)

    #                     result.append({"scan_setting_allowed": scan_setting_allowed, "name": im.name, "resolution": {"W": w, "H": h},
    #                                    "compressionType": compression_type, "colorspace": color_space,
    #                                    "position": im.bbox})
    # return result


def check_allowed_scanSettings(color_space, allowedSettings, compression_type):
    allowedSettings = allowedSettings.ColorImage
    if color_space == "MonoChrome":
        allowedSettings = allowedSettings.MonoChrome
    elif color_space == "GrayScale":
        allowedSettings = allowedSettings.GrayScale

    if compression_type == allowedSettings["compression"]:
        return True
    return False


def get_compression_type(name):
    try:
        return COMPRESSION_TYPE[name]
    except KeyError:
        return name



COMPRESSION_TYPE = {
    'FlateDecode': 'Flate',
    'LZWDecode': 'Lempel-Ziv-Welch',
    'ASCII85Decode': 'ASCII85',
    'ASCIIHexDecode': 'ASCIIHex',
    'RunLengthDecode': 'Run length',
    'CCITTFaxDecode': 'CCITTFax',
    'DCTDecode': 'DCT',
}


def get_color_mode(cspace):

    if cspace == LIT('DeviceRGB'):
        return "ColorImage"
    elif cspace == LIT('DeviceCMYK'):
        return "MonoChrome"
    elif cspace == LIT('DeviceGray'):
        return "GrayScale"
    if cspace is not None and cspace[0] == LIT('Indexed'):
        cspace = resolve1(cspace[1])

    if cspace is not None and cspace[0] == LIT('ICCBased'):
        color_map = resolve1(cspace[1]).get('N')
        if color_map == 1:
            return "GrayScale"
        elif color_map == 3:
            return "ColorImage"
        elif color_map == 4:
            return "MonoChrome"
    return None

COLOR_SPACE = {
    "DeviceRGB": 'RGB',
    "DeviceCMYK": 'CMYK',
    "DeviceGray": 'Gray',


}
def get_missing_bookmark(file):
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, '')
    pages = zip(PDFPage.get_pages(fp), range(1, 2))
    first_page = next(pages)
    outlines = document.get_outlines()
    first_bookmark = next(outlines)

    _, _, dest, action, _ = first_bookmark
    page, _ = first_page

    if dest is not None:
        return dest[0].objid == page.pageid
    else:
        return resolve1(action).get(
            'D')[0].objid == page.pageid


PAGE_LAYOUT = {
    "Default": 'SinglePage',
    "SinglePage": 'SinglePage',
    "SinglePageContinuous": 'OneColumn',
    "Two-up(facing)": 'TwoPageLeft',
    "Two-upContinuous(facing)": 'TwoColumnLeft',
}

PAGE_MODE = {
    "Page Layout": 'UseNone',
    "Bookmarks Panel and Page": 'UseBookmark',
    "Pages Panel and Page": 'UseThumbs',
    "Attachment Panel and Page": 'UseAttachments',
    "Layers Panel and Page": 'UseOC',
}

MAGNIFICATION = {
    "Default": 'N/A',
    "Actual Page": 'FitXYZ',
    "FitPage": 'Fit',
    "FitWidth": 'FitH',
    "FitHeight": 'FitV',
    "FitVisible": 'FitBH',
    "X%": 'FitXYZ + Zoom',
}


def test_initial_view(file):
    fp = open(file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    pages = dict((page.pageid, pageno) for (pageno, page)
                 in enumerate(PDFPage.create_pages(document)))
    catalog = document.catalog
    pageLayout = (catalog.get('PageLayout')).name
    navigationTab = (catalog.get('PageMode')).name
    magnification = (dict_value(catalog.get('OpenAction')).get('D')[1]).name
    open_to_page = pages[dict_value(
        catalog.get('OpenAction')).get('D')[0].objid]
    print(
        PAGE_LAYOUT["Default"] == pageLayout and
        PAGE_MODE["Layers Panel and"] == navigationTab and
        MAGNIFICATION["FitWidth"] == magnification)

    return (pageLayout.name, navigationTab.name, magnification.name, open_to_page)

    # return str(document.catalog.get('PageLayout'))


def test_fast_web_view(file):
    fp = open(file, 'rb')
    # opt = self.pdf_reader.read()
    opt = fp.read()
    return (True if (opt.find(b'/Linearized') != -1) else False)


def test_pdfversion(file):

    fp = open(file, 'rb')
    pdfVersion = (str(fp.readlines()[0]).split('\\'))[0]
    v = re.findall(r'[\d\.\d]+', pdfVersion)
    return (v)


def test_pdf_doc_file_size(file):
    import sys
    fp = open(file, 'rb')

    return sys.getsizeof(fp.read())


if __name__ == '__main__':
    text_output = testscannable(
        'test2.pdf')
    print(text_output)
