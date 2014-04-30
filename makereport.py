#!/usr/bin/env python

from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
import os
import re
from shutil import copy, rmtree
import tempfile
from xhtml2pdf.pisa import CreatePDF

from chqpoint import Analysis
from parsers import samtoolsparser, gatkparser, fastqcparser

# This dict maps each output file name to its parser module
# The key is the output 'name' in the chqpoint json
# file used to import the analysis
#

parsers = {
    'flagstat': samtoolsparser.flagstat,
    'varianteval': gatkparser.varianteval,
    'fastqc_duplication_levels': fastqcparser.duplication_levels
}


class ReportMaker:

    TEMPLATEDIR = os.path.join(os.path.dirname(__file__), 'templates')

    def __init__(self, analysisroot, analysismap):

        self.results = {}
        self.imagefiles = {}

        for resultsfile in self.getresultsfiles(analysisroot, analysismap):
            resultsname = resultsfile['name']
            parser = parsers[resultsname]
            (results, imagefile) = parser(resultsfile['path'])
            if results:
                self.results.update(results)
            if imagefile:
                self.imagefiles[resultsname] = imagefile

    def getresultsfiles(self, analysisroot, analysismap):

        analysis = Analysis.new(
            path=analysisroot, 
            configfile=analysismap
        )

        return analysis.getoutputs()

    def renderpdf(self, templatefile, destfile):

        tempdir = tempfile.mkdtemp()
        htmlfile = os.path.join(tempdir, 'temp.html')
        self.renderhtml(templatefile, htmlfile)

        with open(htmlfile) as src:
            with open(destfile,'w') as dest:
                CreatePDF(
                    src=src,
                    dest=dest,
                    path=tempdir
            )

        rmtree(tempdir)

    def renderhtml(self, templatefile, destfile):

        self.handleimagefiles(destfile)

        with open(destfile, 'w') as f:
            f.write(self.renderhtmltext(templatefile))

    def renderhtmltext(self, templatefile):

        templateLoader = FileSystemLoader(searchpath=[self.TEMPLATEDIR, "/"])
        templateEnv = Environment(loader=templateLoader)
        template = templateEnv.get_template(templatefile)
        outputText = template.render(self.results)
        return outputText

    def supportingfilesdir(self, destfile):

        prefix = re.sub('\.html$', '', destfile)
        return prefix + '_files'

    def handleimagefiles(self, destfile):

        self.results['imagefiles'] = {}

        destdir = self.supportingfilesdir(destfile)
        if not os.path.exists(destdir):
            os.mkdir(destdir)

        for imagename in self.imagefiles:
            imagefile = self.imagefiles[imagename]
            self.results['imagefiles'][imagename] = os.path.join(
                destdir, os.path.basename(imagefile))
            copy(imagefile, destdir)
        
if __name__=='__main__':

    parser = ArgumentParser()
    parser.add_argument('--analysisroot')
    parser.add_argument('--chqpointmap')
    parser.add_argument('--htmltemplate')
    parser.add_argument('--htmldestfile')
    parser.add_argument('--pdftemplate')
    parser.add_argument('--pdfdestfile')

    args = parser.parse_args()

    r = ReportMaker(
        args.analysisroot, 
        args.chqpointmap
    )

    r.renderhtml(args.htmltemplate, args.htmldestfile)
#    r.renderpdf(args.pdftemplate, args.pdfdestfile)
