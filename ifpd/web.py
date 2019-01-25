# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: web-services and related functions.
'''



# ==============================================================================

import urllib.request, urllib.error
import xml.etree.ElementTree

UCSC_DAS_URI = 'http://genome.ucsc.edu/cgi-bin/das/'

def internet_on():
    '''Check internet connection status.
    From: https://stackoverflow.com/a/3764660'''
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout = 1)
        return True
    except urllib.error.URLError as e: 
        return False

def get_webpage_content(uri):
    '''Get the content of a web-page.'''
    try:
        page = urllib.request.urlopen(uri)
        pageContent = page.read()
        page.close()
    except urllib.error.URLError as e:
        raise
    return pageContent

def assert_UCSC_DSN(dsn):
    '''Runs assert checks on a UCSC DAS DSN (XML format only!).'''
    assert 0 < len(dsn), "no databases found."
    attrib = dsn[0].attrib
    assert "id" in attrib.keys(), "database has no 'id' key."
    assert "version" in attrib.keys(), "database has no 'version' key."

def print_UCSC_DSN(dsn):
    '''Prints info on a UCSC DAS DSN (XML format only!).'''
    attrib = dsn[0].attrib
    print(f'"{attrib["id"]}" (v{attrib["version"]}) : {dsn[0].text}')

def list_UCSC_reference_genomes(verbose = False, UCSC_DAS_URI = UCSC_DAS_URI):
    '''Retrieves list of UCSC DAS reference genome IDs.
    Use verbose to print a readable list.'''

    assert internet_on(), "cannot connect to the internet."

    dsnXMLdata = get_webpage_content(f'{UCSC_DAS_URI}/dsn')

    databases = set()
    for dsn in xml.etree.ElementTree.fromstring(dsnXMLdata):
        assert_UCSC_DSN(dsn)
        if verbose:
            print_UCSC_DSN(dsn)
        databases.add(dsn[0].attrib["id"])

    return(databases)

def get_sequence_from_UCSC(region, genome, UCSC_DAS_URI = UCSC_DAS_URI):
    '''Retrieve the sequence of a certain reference genome region from UCSC DAS
    server. As the input region definition follows the bed format, the chromEnd
    position is not included.'''
    chrom, chromStart, chromEnd = region
    base_uri = f'{UCSC_DAS_URI}/{genome}/dna'
    uri_query = f'?segment={chrom}:{chromStart},{chromEnd-1}'
    seqXMLdata = get_webpage_content(base_uri+uri_query)

    seq = xml.etree.ElementTree.fromstring(seqXMLdata)[0][0].text
    seq = seq.replace('\n', '').replace('\r', '').replace(' ', '')
    return seq.upper()

def get_segment_size_from_UCSC(genome, chrom, UCSC_DAS_URI = UCSC_DAS_URI):
    if chrom.startswith('chr'):
        chrom = chrom[3:]

    base_uri = f'{UCSC_DAS_URI}/{genome}/entry_points'
    chromXMLdata = get_webpage_content(base_uri)

    chromList = xml.etree.ElementTree.fromstring(chromXMLdata)[0]
    chromIDs = [chrom.attrib['id'] for chrom in chromList]
    
    return int(chromList[chromIDs.index(chrom)].attrib['stop'])

def check_reference_genome(refGenome, UCSC_DAS_URI = UCSC_DAS_URI):
    refGenomeList = list_UCSC_reference_genomes(
      UCSC_DAS_URI = UCSC_DAS_URI)
    return refGenome in refGenomeList

def get_chromosome_size(chrom, refGenome,
    UCSC_DAS_URI = UCSC_DAS_URI):
    return get_segment_size_from_UCSC(refGenome, chrom,
        UCSC_DAS_URI = UCSC_DAS_URI)

def check_chromosome_size(chrom, chromSize, refGenome,
    UCSC_DAS_URI = UCSC_DAS_URI):
    return chromSize <= get_chromosome_size(chrom, refGenome, UCSC_DAS_URI)

def check_sequence(region, sequence, refGenome, UCSC_DAS_URI = UCSC_DAS_URI):
    '''Connects to UCSC to check if a sequence is correct.'''
    regionSequence = get_sequence_from_UCSC(
      region, refGenome, UCSC_DAS_URI)
    assert_msg = f'\nSequence: {sequence}'
    assert_msg += f'\nUCSC seq: {regionSequence}'
    return (sequence == regionSequence, assert_msg)

# END ==========================================================================

################################################################################
