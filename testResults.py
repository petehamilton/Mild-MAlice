import sys
import re
import subprocess

FILENAME = '[a-zA-Z0-9_/]*(?P<fileName>ex\d+.alice)'
COMPILE_STR = 'Compiling ' + FILENAME
RUN_STR = 'Running ' + FILENAME
ERROR_STR = '----------------'
NO_OUTPUT_STR = r'\+\+\+\+\+\+\+\+\+\+\+\+\+\+\+\+\+\+'

def nextRow( i, array ):
    return i+1, array[i+1]

def processResults(fName):
    results = {}
    resultFile = open(fName, 'r')
    resultArray =  resultFile.read().split("\n")
    i = 0
    while i < len(resultArray):
        row = resultArray[i]
        m = re.match( COMPILE_STR, row )
        if m:
            fileName = m.group('fileName')
            i, row = nextRow( i, resultArray )
            if re.match( RUN_STR, row ):
                i, row = nextRow( i, resultArray )
                if re.match( NO_OUTPUT_STR, row ):
                    results[fileName] = ''
                else:
                    results[fileName] = row
            elif re.match(ERROR_STR, row):
                i, row = nextRow( i, resultArray )
                results[fileName] = row
            else:
                results[fileName] = ''
        i += 1
    return results
            
            
def compareResults( expected, actual ):
    for key, value in expected.items():
        if actual[key] != value:
            print key
            print "Expected %s\nGot %s\n" %(value, actual[key])

if __name__ == "__main__":
    if len(sys.argv) > 2:
        resultsName = sys.argv[1]
        testName = sys.argv[2]
    else: 
        resultsName = 'milestone2/output.txt'
        testName = 'output.txt'
    
    subprocess.call("./test.sh > %s" %testName, shell = True)
    expectedResults = processResults(resultsName)
    actualResults = processResults(testName)
    assert( len(actualResults) == len(expectedResults) )
    compareResults( expectedResults, actualResults )
