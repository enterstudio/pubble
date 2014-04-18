#!/usr/bin/env python

from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
from chqpoint import Analysis
from xhtml2pdf.pisa import CreatePDF
from parsers import flagstatparser


# This maps each output file name to its parser module
# The key is the output 'name' in the chqpoint json
# file used to import the analysis
parsers = {
    'flagstat': flagstatparser
}


class ReportMaker:

    def __init__( self, analysisroot, analysismap ):

        self.results = {}
        for resultsfile in self.getresultsfiles( analysisroot, analysismap ):
            parser = parsers[ resultsfile[ 'name' ]]
            self.results.update( parser.parse(( resultsfile[ 'path' ] )))

    def getresultsfiles( self, analysisroot, analysismap ):

        analysis = Analysis.new(
            path=analysisroot, 
            configfile=analysismap
        )

        return analysis.getoutputs()

    def renderpdf(self, templatefile, destfile):

        html = self.renderhtmltext(templatefile)
        with open(destfile,'w') as f:
            CreatePDF(
                src=html,
                dest=f
            )

    def renderhtml( self, templatefile, destfile ):

        with open( destfile, 'w' ) as f:
            f.write( self.renderhtmltext( templatefile ) )

    def renderhtmltext( self, templatefile ):

        templateLoader = FileSystemLoader( searchpath=["templates", "/"] )
        templateEnv = Environment( loader=templateLoader )
        template = templateEnv.get_template( templatefile )
        outputText = template.render( self.results )
        return outputText

        
if __name__=='__main__':

    parser = ArgumentParser()
    parser.add_argument( '--analysisroot' )
    parser.add_argument( '--chqpointmap' )
    parser.add_argument( '--htmltemplate' )
    parser.add_argument( '--htmldestfile' )
    parser.add_argument( '--pdftemplate' )
    parser.add_argument( '--pdfdestfile' )

    args = parser.parse_args()

    r = ReportMaker(
        args.analysisroot, 
        args.chqpointmap
    )

    r.renderhtml( args.htmltemplate, args.htmldestfile )
    r.renderpdf( args.pdftemplate, args.pdfdestfile )

