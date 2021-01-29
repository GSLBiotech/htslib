#!/usr/bin/env python

import os
import sys

NEW_RECIPES = [
'$(TOP_OBJS) $(BUILT_PROGRAMS_OBJS): %.obj: %.c\n',
'	$(CC) $(CFLAGS) -I. $(CPPFLAGS) /c $<\n',
'$(CRAM_OBJS) $(TEST_OBJS): %.obj: %.c\n',
'	$(CC) $(CFLAGS) -I. $(CPPFLAGS) /Fo$@ /c $<\n',
'LIBHTS_OBJS = $(TOP_OBJS) $(CRAM_OBJS)\n',
]

class Args:
  def __init__(self, argv):
    if '-h' in argv[ -1 ]:
      msg = 'usage: {0} [--static]'.format( argv[ 0 ] )
      sys.exit( msg )

    self.m_static = '--static' in argv
    self.m_output = 'Makefile.msvc'

    if self.m_static:
      self.m_output += '.static'

class Makefile:
  def __init__(self):
    self.__parse()

  def appendSuffix(self, pattern, delim, suffix):
    oldText = pattern + delim
    for i,line in enumerate( self.m_lines ):
      begin = line.find( oldText )
      if begin < 0:
        continue
      end = begin + len( oldText )
      newText = pattern + suffix + delim
      self.m_lines[ i ] = line[ : begin ] + newText + line[ end : ] 

  def createProgramObjs(self):
    files, begin, end = self.getFilesInSection( 'BUILT_PROGRAMS' )
    files.insert( 0, 'BUILT_PROGRAMS_OBJS = \\\n' )
    result = [line.replace( '.exe', '.obj' ) for line in files ]
    result.append( '\n' )
    return result

  def createCramObjs(self, files):
    result = [ 'CRAM_OBJS = \\\n' ]
    for file in files:
      if 'cram/' in file:
        result.append( file )
    result.append( '\n' )
    return result

  def createTopObjs(self, files):
    result = [ 'TOP_OBJS = \\\n\tmsvc.obj \\\n' ]
    for file in files:
      if 'cram/' not in file:
        result.append( file )
    result.append( '\n' )
    return  result

  def createTestObjs(self):
    result = [ 'TEST_OBJS = \\\n' ]
    for line in self.m_lines:
      if line.startswith( 'test/' ):
        if '.obj: test/' in line:
          index = line.find( ':' )
          name  = line[ : index ]
          result.append( '\t' + name + ' \\\n')
    result.append( '\n' )
    return result

  def dump(self):
    n = len( self.m_lines )
    for i in xrange( n ):
      print( i,self.m_lines[ i ] ),

  def dumpRange(self, begin, end):
    for i in xrange( begin, end + 1 ):
      print( i,self.m_lines[ i ] ),

  def findLineIndex(self, pattern):
    for i,line in enumerate( self.m_lines ):
      if line.startswith( pattern ):
        return i
    return -1

  def getFilesInSection(self, pattern):
    n = len( self.m_lines )
    i = 0
    result = []
    begin,end = None,None

    while i < n:
      if not self.m_lines[ i ].startswith( pattern ):
        i += 1
        continue
      begin = i
      while i < n:
        if self.m_lines[ i ].startswith( '\n' ):
          end = i
          break
        i += 1

    i = begin + 1
    while i < end:
      result.append( self.m_lines[ i ] )
      i += 1

    return result, begin, end

  def groupObjs(self):
    files, begin, end = self.getFilesInSection( 'LIBHTS_OBJS' )

    programs = self.createProgramObjs()
    crams    = self.createCramObjs( files )
    tops     = self.createTopObjs( files )
    tests    = self.createTestObjs()
    sections = programs + crams + tops + tests + NEW_RECIPES
   
    self.removeRange( begin, end )
    self.insertLineList( begin, sections )    

  def insertLineList(self, index, lines):
    n = len( lines )
    i = n - 1
    while i >= 0:
      self.m_lines.insert( index, lines[ i ] )
      i -= 1
  
  def prepend(self, text):
    i = 0
    while self.m_lines[ i ].startswith( '#' ):
      i += 1

    self.m_lines.insert( i + 1, text )
 
  def removeLineStartsWith(self, pattern):
    i = len( self.m_lines ) - 1
    while i >= 0:
      if self.m_lines[ i ].startswith( pattern ):
        self.m_lines.pop( i )
      i -= 1

  def removeRange(self, begin, end):
    i = end
    while i >= begin:
      self.m_lines.pop( i )
      i -= 1

  def removeRecipe(self, pattern):
    begin,end = None,None
    n = len( self.m_lines )
    i = 0
    while i < n:
      if not self.m_lines[ i ].startswith( pattern ):
        i += 1
        continue

      begin = i
      while i < n:
        if self.m_lines[ i ].startswith( '\n' ):
          end = i
          break
        i += 1
      break

    if begin and end:
      while end >= begin:
        self.m_lines.pop( end )
        end -= 1

  def replaceAssign(self, name, value):
    i = len( self.m_lines ) - 1
    while i >= 0:
      if self.m_lines[ i ].startswith( name + ' ' ):
        line = self.m_lines[ i ]
        j = line.index( '=' ) + 1
        self.m_lines[ i ] = line[ :j ] + ' ' + value + '\n'
        break
      i -= 1

  def replaceLineStartsWith(self, old, new):
    for i,line in enumerate( self.m_lines ):
      if old in line:
        self.m_lines[ i ] = new       

  def replaceString(self, old, new):
    for i,line in enumerate( self.m_lines ):
      if old in line:
        self.m_lines[ i ] = line.replace( old, new )       

  def write(self, name):
    with open( name, 'w' ) as f:
      f.write( ''.join( self.m_lines ) )
        
  def __parse(self):
    self.m_lines = []
    with open( 'Makefile' ) as f:
      for line in f:
        self.m_lines.append( line )

def getCflags(static):
  result = r'/MD /O2 /TC /I. /I$(TPS)\pthreads4w\include /I$(TPS)\wingetopt\include /I$(TPS)\zlib\include /I$(TPS)\bzip2\include /I$(TPS)\xz\include /DWINGETOPT_SHARED_LIB'
  if static:
    result = result.replace( '/MD', '/MT' )
    result = result.replace( '\\include', '\\static\\include' )
    result = result.replace( 'WINGETOPT_SHARED_LIB', 'PTW32_STATIC_LIB /DLZMA_API_STATIC' )
  return result

def getLdflags(static):
  result = r'/libpath:$(TPS)\pthreads4w\lib /libpath:$(TPS)\zlib\lib /libpath:$(TPS)\bzip2\lib /libpath:$(TPS)\xz\lib /libpath:$(TPS)\wingetopt\lib'
  if static:
    result = result.replace( '\\lib', '\\static\\lib' )
  return result

def createMakefile( args ):
  makefile = Makefile()
  makefile.prepend( 'LINK   = link\n' )
  makefile.replaceAssign( 'CC', 'cl' )
  makefile.removeLineStartsWith( 'AR ' )
  makefile.removeLineStartsWith( 'RANLIB ' )
  makefile.removeLineStartsWith( 'htslib_default_libs ' )

  cflags = getCflags( args.m_static )
  makefile.replaceAssign( 'CFLAGS', cflags )

  ldflags = getLdflags( args.m_static )
  makefile.replaceAssign( 'LDFLAGS', ldflags )
  makefile.replaceAssign( 'LIBS', r'ws2_32.lib wingetopt.lib liblzma.lib pthreadVC2.lib zlib.lib libbz2.lib' )

  for program in 'bgzip htsfile tabix'.split():
    for delim in [' \\', ':' ]:
      makefile.appendSuffix( program, delim, '.exe' )

  makefile.appendSuffix( '\ttabix', '', '.exe' )

  makefile.removeRecipe( '.c.o:' )
  makefile.replaceString( '.o', '.obj' )
  makefile.replaceString( '.a', '.lib' )

  makefile.replaceLineStartsWith( '\t$(CC) -shared -Wl,--out-implib=hts.dll', '\t$(CC) $(LIBHTS_OBJS) /dll /out:$@ $(LDFLAGS) $(LIBS)' )

  makefile.replaceString( '\t$(CC)', '\t$(LINK)' )
  makefile.removeLineStartsWith( '\techo \'#define HAVE_DRAND48' )  
  makefile.removeLineStartsWith( '\techo \'#define HAVE_LIBCURL' )
  
  makefile.removeLineStartsWith( '\t$(AR)' )
  makefile.removeLineStartsWith( '\t$(AR)' )
  
  makefile.replaceString( '\t-$(RANLIB) $@', '\tlib $(LIBHTS_OBJS) /out:$@' )
  makefile.replaceString( '-lpthread', '' )
  makefile.replaceString( '-o $@', '/out:$@' )
  makefile.removeLineStartsWith( 'NONCONFIGURE_OBJS' )
  makefile.groupObjs()

  if args.m_static: 
    makefile.replaceString( 'lib-static lib-shared', 'lib-static' )
    for section in ['BUILT_PROGRAMS ', 'BUILT_PROGRAMS_OBJS ']:
      files, begin, end = makefile.getFilesInSection( section )
      makefile.removeRange( begin, end )

  makefile.write( args.m_output )

def main( argv ):
  args = Args( argv )
  createMakefile( args )  

if '__main__' == __name__:
  main( sys.argv )
