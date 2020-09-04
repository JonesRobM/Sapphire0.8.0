import numpy as np
import functools
import operator
import multiprocessing as mp
from functools import partial
from ase.io import read

def distance(a, b):
    
    """ Robert
    
    A simple distance function which takes arguments of
    
    a, b
        These are expected to be arrays containing three elements
        (x, y, z)
        Being the respective euclidean coordinates for atoms a and b
        at a given point in time.
        
    Reurns a single float being the euclidean distance between the atoms.
    
    """
    
    dx = abs(a[0] - b[0])
     
    dy = abs(a[1] - b[1])
     
    dz = abs(a[2] - b[2])
 
    return np.sqrt(dx**2 + dy**2 + dz**2)



def get_CoM(positions):
    return (np.average(positions, axis = 0))

def get_subspecieslist(specie, elements, positions):
    Temp = np.column_stack((elements,positions))
    Temp = [x for x in Temp if x[0] == specie]
    return np.array(np.delete(Temp,0,1), dtype = np.float64)

def CoM_Dist(positions, CoM = None, homo = False, specie = None, elements = None):
    
    if homo == False:
        return [distance(x, CoM) for x in positions]
    elif homo == True:
        Temp = get_subspecieslist(specie, elements, positions)
        CoM = get_CoM(Temp)
        return [distance(x, CoM) for x in Temp]
    else:
        raise TypeError("You weren't supposed to do that.")
        
    

def Euc_Dist(positions, homo = False, specie = None, elements = None):
    
    if homo == False:
        Distances=[]
        for i in range(len(positions)-1):
            for j in range(i+1,len(positions)):
                Euc = distance(positions[i],positions[j])

                Distances.append(Euc)
        return Distances
    
    elif homo == True:
        Distances = []
        Temp = get_subspecieslist(specie, elements, positions)
        if (len(Temp)>1) is False:
            return None
        else:
            for i in range(len(Temp)-1):
                for j in range(i+1,len(Temp)):
                    Euc = distance(Temp[i],Temp[j])

                    Distances.append(Euc)
            return Distances
    else:
        raise TypeError("You weren't supposed to do that.")
    

        
def Hetero(positions, species, elements):
        
    """ Robert
    
    Note that no species need to be defined for this function as it is understood that LoDiS
    only has provision for mono/bimetallic systems (for the time being) although this
    function could be further generalised (albeit it a potential cost to computation time).
    """
    
    TempA = get_subspecieslist(species[0], elements, positions)
    TempB = get_subspecieslist(species[1], elements, positions)
    try:
        np.shape(TempA)[1]
        try:
            np.shape(TempB)[1]
            Dist=[]
            for a in TempA:
                Temp = [ distance(a,b) for b in TempB]
                Dist.append(Temp)
            return Dist
        except IndexError:
            Dist=[]
            for x in TempA:
                Dist.append( [distance(x, TempB) ])
            return Dist
            print("You have only one of a specific atom type in your simulation. I hope that this is correct.", "\n")
    except IndexError:
        try:
            np.shape(TempB)[1]           
            return [ distance(TempA, b) for b in TempB ]
            print("You have only one of a specific atom type in your simulation. I hope that this is correct.", "\n")
        except IndexError:
            print("Why the actual fuck do you only have two atoms?", "\n")
            return None
    


class Lindemann():
    
    def __init__(self, File, N_Atoms = 0, CPUs = 1, Ho = False, Specie = None, Elements = None, Range = None):
        self.File = read(File, index = ':')
        self.N_Atoms = N_Atoms
        self.CPUs = CPUs
        if Ho is True:
            self.Ho = True
            self.Specie = Specie
            self.Elements = Elements
            self.N_Atoms = len( [ x for x in self.Elements if x == self.Specie ] )
        if Range is None:
            self.Range = range(self.N_Atoms)
        else:
            self.Range = Range
    
    def Lin_Func(self, Dist_List):
        return np.sqrt( np.average( [ a**2 for a in Dist_List ] ) - np.average(Dist_List)**2 )/ np.average(Dist_List)
    
    
    def Lin_List(self, index1, index2):
        List = []
        for T in range(0,len(self.File)):
            if self.Ho is True:
                atoms = get_subspecieslist(self.Specie, self.Elements, self.File[T].get_positions())
            else:
                atoms = self.File[T].get_positions()
            List.append(distance(atoms[index1],atoms[index2]))
        return self.Lin_Func(List)
    
    def Func(self, File, index1):
        A = [ self.Lin_List(index1, x) for x in range(self.N_Atoms) if x!= index1 ]
        return sum(A)/len(A)
    
    def Main_Lind(self):
        iterable = range(self.N_Atoms)
        pool = mp.Pool(self.CPUs)
        function = partial(self.Func, self.File)
        New_Sample = pool.map(function, iterable)
        pool.close()
        pool.join()
        return New_Sample

    
def RDF(positions, Res=100, R_Cut=10.0, Hetero = False, Species = None, Elements = None):
    
    """ Robert
    
    Args:
        Resolution: 
            int data type representing how finely you wish to make 
            the grid. Usually set in the order of 100
        
        Trajectory: 
            Single frame of xyz coordinates for a set of atoms
            Is expected to be iterated over and so will only take a single frame of xyz
        
        R_Cut: 
            Float type variable which indicates how far you wish to create
            the distribution for.
            Good practice is to set it to ~0.5 Diameter of the cluster
            Tested with 10 Angstroms
    Returns:
        Radii:
            A numpy array of all the radii the distribution has been computed over
            Will have length of "Resolution" and is to be used as the x axis on
            an RDF plot.
        
        G:
            A numpy array of the (unnormalised) calculated RDF values corresponding 
            to the respective radius in Radii. To be set on the y axis in a given
            RDF plot.
            
    Note bene:
        
        In the future, this function will be generalised to calculate 
            (full, homo, hetero)
        RDF plots. 
        Given that for the time being, we are mostly concerned with monometallic systems
        This is not a HUGE issue.
    """
    
            
    dr = R_Cut / Res
    Radii = np.linspace(0, R_Cut, Res)
    Volumes=np.zeros(Res)
    G=np.zeros(Res)
    if not Hetero:
        for i, atom1 in enumerate(positions):
            for j in range(Res):
                r1 = j * dr #Inner radius for the spherical shell
                r2 = r1 + dr #Outer radius increased by increment dr
                v1 = 4.0 / 3.0 * np.pi * r1**3
                v2 = 4.0 / 3.0 * np.pi * r2**3
                Volumes[j] += v2 - v1 #Volume to consider when evaluating distribution
        
            for atom2 in positions[i:]:
                Distance = distance(atom1, atom2)
                index = int(Distance / dr)
                if 0 < index < Res:
                    G[index] += 2 #Identifies when there is an atom at this distance
    else:
        TempA = get_subspecieslist(Species[0], Elements, positions)
        TempB = get_subspecieslist(Species[1], Elements, positions)
        for i, atom1 in enumerate(TempA):
            for j in range(Res):
                r1 = j * dr #Inner radius for the spherical shell
                r2 = r1 + dr #Outer radius increased by increment dr
                v1 = 4.0 / 3.0 * np.pi * r1**3
                v2 = 4.0 / 3.0 * np.pi * r2**3
                Volumes[j] += v2 - v1 #Volume to consider when evaluating distribution

            for atom2 in TempB:
                Distance = distance(atom1, atom2)
                index = int(Distance / dr)
                if 0 < index < Res:
                    G[index] += 2 #Identifies when there is an atom at this distance
        

    for i, value in enumerate(G):
        G[i] = value / Volumes[i] #Rescaling the distribution with respect to enclosing volume
    return Radii, G