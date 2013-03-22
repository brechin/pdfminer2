#!/usr/bin/env python2
import sys
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter


def getRealOutput(outfile):
    if outfile is not None:
        return file(outfile, 'wb')
    else:
        return sys.stdout


# main
def main(argv):
    import getopt

    def usage():
        print ('usage: %s [-d] [-p pagenos] [-m maxpages] [-P password] [-o output] [-C] '
               '[-n] [-A] [-V] [-M char_margin] [-L line_margin] [-W word_margin] [-F boxes_flow] '
               '[-Y layout_mode] [-O output_dir] [-t text|html|xml|tag] [-c codec] [-s scale] [-r] '
               '[-S] [-f] file ...' % argv[0])
        return 100

    try:
        (opts, args) = getopt.getopt(argv[1:], 'fSrdp:m:P:o:CnAVM:L:W:F:Y:O:t:c:s:')
    except getopt.GetoptError:
        return usage()
    if not args: return usage()
    # debug option
    debug = 0
    # input option
    password = ''
    pagenos = set()
    maxpages = 0
    # output option
    outfile = None
    outtype = None
    imagewriter = None
    layoutmode = 'normal'
    codec = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    roundCoords = False
    simplifyOutput = False
    formatOutput = False
    laparams = LAParams()
    for (k, v) in opts:
        if k == '-d':
            debug += 1
        elif k == '-p':
            pagenos.update(int(x) - 1 for x in v.split(','))
        elif k == '-m':
            maxpages = int(v)
        elif k == '-P':
            password = v
        elif k == '-o':
            outfile = v
        elif k == '-C':
            caching = False
        elif k == '-n':
            laparams = None
        elif k == '-A':
            laparams.all_texts = True
        elif k == '-V':
            laparams.detect_vertical = True
        elif k == '-M':
            laparams.char_margin = float(v)
        elif k == '-L':
            laparams.line_margin = float(v)
        elif k == '-W':
            laparams.word_margin = float(v)
        elif k == '-F':
            laparams.boxes_flow = float(v)
        elif k == '-Y':
            layoutmode = v
        elif k == '-O':
            imagewriter = ImageWriter(v)
        elif k == '-t':
            outtype = v
        elif k == '-c':
            codec = v
        elif k == '-s':
            scale = float(v)
        elif k == '-r':
            roundCoords = True
        elif k == '-S':
            simplifyOutput = True
        elif k == '-f':
            formatOutput = True

    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFResourceManager.debug = debug
    PDFPageInterpreter.debug = debug
    PDFDevice.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
        if outfile:
            if outfile.endswith('.htm') or outfile.endswith('.html'):
                outtype = 'html'
            elif outfile.endswith('.xml'):
                outtype = 'xml'
            elif outfile.endswith('.tag'):
                outtype = 'tag'
    if formatOutput and outtype.endswith('ml'):
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        outfp = StringIO()
    else:
        outfp = getRealOutput(outfile)
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                              imagewriter=imagewriter, layoutmode=layoutmode,
                              scale=scale, roundCoords=roundCoords, simplifyOutput=simplifyOutput)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp, codec=codec)
    else:
        return usage()
    for fname in args:
        fp = file(fname, 'rb')
        process_pdf(rsrcmgr, device, fp, pagenos, maxpages=maxpages, password=password,
                    caching=caching, check_extractable=True)
        fp.close()
    device.close()
    if formatOutput:
        root = outfp.getvalue()
        with getRealOutput(outfile) as realOutput:
            try:
                from bs4 import BeautifulSoup as bs
            except ImportError:
                bs = None
                sys.stderr.write('Could not import BeautifulSoup, skipping output formatting')
                realOutput.write(root)
            else:
                soup = bs(root)
                prettyHTML = soup.prettify()
                realOutput.write(prettyHTML)

    outfp.close()
    return


if __name__ == '__main__': sys.exit(main(sys.argv))
