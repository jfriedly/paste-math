#!/usr/bin/python2.7

import httplib, urllib, sys

# Define the parameters for the POST request and encode them in
# a URL-safe format.

def read(filename):
    with open(filename, 'r') as f:
        output = f.read()
    return output

def write(filename, input):
    with open(filename, 'w') as f:
        f.write(input)

def sendrecieve(input, num):
    complier_level = ['WHITESPACE_ONLY', 'SIMPLE_OPTIMIZATIONS', 
        'ADVANCED_OPTIMIZATIONS']
    params = urllib.urlencode([
        ('js_code', input),
        ('compilation_level', complier_level[num]),
        ('output_format', 'text'),
        ('output_info', 'compiled_code'),
      ])

    # Always use the following value for the Content-type header.
    headers = { "Content-type": "application/x-www-form-urlencoded" }
    conn = httplib.HTTPConnection('closure-compiler.appspot.com')
    conn.request('POST', '/compile', params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def main(filename, num):
    print "%s..." % filename,
    sys.stdout.flush()
    filenameparts = filename.split('.')
    if filenameparts[-1] == 'js' and len(filenameparts) == 2:
        try:
            try:
                content = read(filename)
            except Exception as e:
                print "read error"
                #print e
                raise Exception()
            try:
                data = sendrecieve(content, num)
            except Exception as e:
                print "connection error"
                #print e
                raise Exception()
            try:    
                write(filenameparts[0] + '.min.js', data)
            except Exception as e:
                print "write error"
                #print e
                raise Exception()
        except:
            pass
        else:
            print "done"
        finally:
            pass
    else:
        print "skipped"

if __name__ == '__main__':
    if sys.argv[1][:3] == '-c=' and sys.argv[1][3] in ['0', '1', '2']:
        num = int(sys.argv[1][3])
        for filename in sys.argv[2:]:
            main(filename, num)

    elif sys.argv[1][:17] == '--compiler-level=' and \
         sys.argv[1][17] in ['0', '1', '2']:
        num = int(sys.argv[1][17])
        for filename in sys.argv[2:]:
            main(filename, num)
    
    elif len(sys.argv) > 1 and sys.argv[1][0] != '-':
        for filename in sys.argv[1:]:
            main(filename, 0)

    else:
        print "usage: minify-js.py [options] file [file] ..."
        print "\t-c, --compiler-level=COMPILER_LEVEL"
        print "\t\t0: Whitespace removal only (default)"
        print "\t\t1: Simple Optimizations"
        print "\t\t2: Advanced Optimizations"