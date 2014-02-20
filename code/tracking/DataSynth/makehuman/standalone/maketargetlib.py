#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Library with common functionality for MakeTarget tool 

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2012

**Licensing:**         GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
--------

.. image:: ../images/files_data.png
   :align: right   
   
This library implements base functionality used by the standalone maketarget 
tool.
"""

'''The global version for the entire tool.'''
VERSION = "1.2"

'''The minimum distance a vert from original has to be moved before it is added
in a target.'''
EPSILON = 0.001
EPSILON_SQUARED = EPSILON*EPSILON

class Vector3(object):
    '''Simple 3D vector class.'''
    
    def __init__(self):
        '''Construct a zero vector (0,0,0).'''
        self.x = 0
        self.y = 0
        self.z = 0
        
    def __init__(self, x, y=None, z=None):
        '''Construct vector (x,y,z).
        If the first argument is another Vector3 instance this acts as
        copy constructor.'''
        if isinstance(x, Vector3):
            # Copy constructor
            self.x = x.x
            self.y = x.y
            self.z = x.z
        else:
            self.x = x
            self.y = y
            self.z = z
    
    def __eq__(self, other):
        '''Equals operator'''
        if isinstance(other, Vector3):
            return self.x==other.x and self.y==other.y and self.z==other.z
        else:
            return 0
            
    def __ne__(self, other):
        '''Not equals operator'''
        if isinstance(other, Vector3):
            return self.x!=other.x or self.y!=other.y or self.z!=other.z
        else:
            return 1
            
    def __add__(self, other):
        '''Addition operator'''
        if isinstance(other, Vector3):
            return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)
        else:
            raise TypeError, "unsupported operand type for +"
            
    def add(self, other):
        '''Faster in-place addition'''
        self.x = self.x + other.x
        self.y = self.y + other.y
        self.z = self.z + other.z

    def __sub__(self, other):
        '''Subtract operator'''
        if isinstance(other, Vector3):
            return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)
        else:
            raise TypeError, "unsupported operand type for -"
            
    def sub(self, other):
        '''Faster in-place subtraction'''
        self.x = self.x - other.x
        self.y = self.y - other.y
        self.z = self.z - other.z
        
    def squaredDistance(self, other):
        '''Calculate squared distance (distance*distance) between this and other
        vert. Distance is kept squared because the square root operator is
        expensive. Squared distance suffices for distance comparisons.'''
        dx = self.x-other.x
        dy = self.y-other.y
        dz = self.z-other.z
        return dx*dx + dy*dy + dz*dz
        
    def __str__(self):
        '''Informal textual representation. Used by str() and print'''
        return "x=%f y=%f z=%f"%(self.x, self.y, self.z)


class Obj(object):
    '''Represents an .obj wavefront. Only the vertices are loaded into memory as they
    are only used. Maintains a ref to the file it was loaded from.'''
    
    def __init__(self, path):
        '''Create a wavefront obj by loading it from a file at specified path.
        If path is another Obj instance, this acts as copy constructor.'''
        if isinstance(path, Obj):
            # Copy constructor
            self.filepath = path.filepath
            self.verts = list()
            for v in path.verts:
                self.verts.append( Vector3(v) )
        else:
            self.filepath = path
            self.verts = list()
            self.faces = list()
            self._loadVerts(path)
        
    def getNbVerts(self):
        '''The number of vertices in this obj.'''
        return len(self.verts)
        
    def getDifferenceAsTarget(self, obj):
        '''Subtract obj from this obj and output difference as target.
        Usually obj is the base object while this is an edit of the base.'''
        if obj.getNbVerts() != self.getNbVerts():
            e = Exception("Cannot subtract OBJs: different number of vertices. (%s has %d and %s has %d vertices)."% (self.filepath, self.getNbVerts(), obj.filepath, obj.getNbVerts()))
            e.errCode = -1
            raise e
        result = Target()
        for i in range(self.getNbVerts()):
            if self.verts[i].squaredDistance(obj.verts[i]) > EPSILON_SQUARED: 
                result.addVertDiff(i, self.verts[i] - obj.verts[i])
        return result
        
    def subtractTarget(self, target):
        '''Subtract target from this obj. Vertices of this obj are altered.'''
        if target.getMaxVertIndex() > self.getNbVerts():
            e = Exception("Target contains more vertices (%d) than this obj (%d)."% (target.getMaxVertIndex(), self.getNbVerts()))
            e.errCode = -1
            raise e
        for index, vertDiff in target.verts.items():
            self.verts[index].sub(vertDiff)
            
    def addTarget(self, target):
        '''Add target to this obj. Vertices of this obj are altered.'''
        if target.getMaxVertIndex() > self.getNbVerts():
            e = Exception("Target contains more vertices (%d) than this obj (%d)."% (target.getMaxVertIndex(), self.getNbVerts()))
            e.errCode = -1
            raise e
        for index, vertDiff in target.verts.items():
            self.verts[index].add(vertDiff)
        
    def _loadVerts(self, path):
        """
        This function is a little utility function to load only the vertex data
        from a wavefront obj file.

        Parameters
        ----------
        path:
            *string*. A string containing the operating system path to the
            file that contains the wavefront obj.
        """
        fd = open(path)
        data = fd.readline()
        lineNb = 0
        try:
            while data:
                lineNb = lineNb +1
                dataList = data.split()
                if dataList and dataList[0] == "v":
                    self.verts.append( Vector3( float(dataList[1]),\
                                                float(dataList[2]),\
                                                float(dataList[3])) )
                elif dataList and dataList[0] == "f" and len(dataList) >= 5:
                    # We are only interested in the quads
                    self.faces.append([ int(dataList[1].split("/")[0]),\
                                        int(dataList[2].split("/")[0]),\
                                        int(dataList[3].split("/")[0]),\
                                        int(dataList[4].split("/")[0]) ] )
            
                data = fd.readline()
            fd.close()
        except Exception as e:
            print e
            e = Exception("Error while parsing OBJ file %s at line %d."% (path, lineNb))
            e.errCode = -1
            raise e
        finally:
            fd.close()
        return
        
    def write(self, outPath):
        '''Writes full .obj back to file using altered vertices and original data from the obj.'''
        outfile = open(outPath, 'w')
        infile = open(self.filepath, 'r')
        vertsWritten = False
        inData = infile.readline()
        while inData:
            dataList = inData.split()
            if dataList[0] == "v":
                if not vertsWritten:
                    # Write verts upon discovering first vert in source obj
                    vertsWritten = True
                    for vert in self.verts:
                        outfile.write("v %f %f %f\n"% (vert.x, vert.y, vert.z))
                else:
                    # Don't write verts from source file
                    pass
            else:
                # Copy from input to output
                outfile.write(inData)
                outfile.write("\n")
                
            inData = infile.readline()
        infile.close()
        outfile.close()
    
        
class Target(object):
    '''Represents a target. Targets contain the difference of certain vertices
    of an obj relative to the base.obj.'''
    
    def __init__(self, path=False):
        '''Create a target. If path is specified the target is loaded from
        the file, otherwise an empty target is created.'''
        self.filepath = path
        self.verts = dict()
        self.maxVertIndex = 0
        if path:
            self._loadVerts(path)
        
    def addVertDiff(self, index, vertexDiff):
        '''Add a difference vector to this target.'''
        if index > self.maxVertIndex:
            self.maxVertIndex = index
        self.verts[index] = vertexDiff
        
    def getNbVerts(self):
        '''The number of vertices in this target.'''
        return len(self.verts)
        
    def getMaxVertIndex(self):
        '''The maximum vertex index found in this target.'''
        return self.maxVertIndex
        
    def _loadVerts(self, path):
        '''Load vertices in this target from the specified file.'''
        fd = open(path)
        data = fd.readline()
        lineNb = 0
        try:
            while data:
                lineNb = lineNb +1
                dataList = data.split()
                if dataList:
                    index = int(dataList[0])
                    self.addVertDiff(index, Vector3(float(dataList[1]), \
                                                    float(dataList[2]), \
                                                    float(dataList[3]) ))
                    data = fd.readline()
            fd.close()
        except Exception as e:
            e = Exception("Error while parsing target file %s at line %d."% (path, lineNb))
            e.errCode = -1
            raise e
        finally:
            fd.close()
        return
        
    def write(self, outPath):
        '''Write this target to specified file.'''
        outfile = open(outPath, 'w')
        for index in self.verts:
            vert = self.verts[index]
            outfile.write("%d %f %f %f\n"% (index, vert.x, vert.y, vert.z))
        outfile.close()

