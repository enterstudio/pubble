#!/usr/bin/env python
import re
from argparse import ArgumentParser


def parse(filename):


    resultstables = {}

    with open(filename) as f:
        for line in f:
            if line.startswith('#:GATKTable:'):
                # New table found
                # Ignore the first line with format information. 

                # Capture the table name and description from the second line.
                nextrow = f.next()
                m = re.match(r'^#:GATKTable:(.*):(.*)$', nextrow)
                if not m:
                    continue
                tablename = m.groups()[0]
                tabledescription = m.groups()[1]

                # Capture the column header info
                nextrow = f.next().rstrip()
                tableheader = re.split('\s+', nextrow)
                tableheader.pop(0) #Drop the table name

                # Capture data from all rows that start with the current tablename
                rows = []
                nextrow = f.next().rstrip()
                while nextrow.startswith(tablename):
                    rowdata = re.split('\s+', nextrow)
                    rowdata.pop(0) # Drop the table name from the row
                    rows.append(rowdata) # Save data to list of rows
                    nextrow = f.next().rstrip()

                resultstables[tablename] = {
                    'description': tabledescription,
                    'header': tableheader,
                    'rows': rows
                    }
            
    return {'varianteval': resultstables}

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    results = parse(args.filename)

    print results


#  #:GATKTable:20:3:%s:%s:%s:%s:%s:%d:%d:%d:%.2f:%s:%d:%.2f:%.1f:%d:%s:%d:%.1f:%d:%s:%d:;
#  #:GATKTable:VariantSummary:1000 Genomes Phase I summary of variants table
#  VariantSummary  CompRod  EvalRod  JexlExpression  Novelty  nSamples  nProcessedLoci  nSNPs    TiTvRatio  SNPNoveltyRate  nSNPsPerSample  TiTvRatioPerSample  SNPDPPerSample  nIndels  IndelNoveltyRate  nIndelsPerSample  IndelDPPerSample  nSVs  SVNoveltyRate  nSVsPerSample
#  VariantSummary  dbsnp    set1     none            all             1      3137161264  3435755       2.06            1.21         3435755                2.06       3435545.0   708708              7.62            708708          708597.0  2001          68.27           2001
