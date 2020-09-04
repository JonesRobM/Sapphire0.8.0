import builtins
import numpy as np
import time
import datetime
import functools
import operator
import multiprocessing as mp
from contextlib import closing
from inspect import getmembers, isfunction
import getpass
import platform
from termcolor import colored
import os
import sys
from ase.io import read
import wikiquote

__version__ = '0.7.0'

Units = 'Angstrom & ev'

from Post_Process import Adjacent
from Post_Process import Kernels
from Post_Process import DistFuncs
from Post_Process import AGCN
from Post_Process import CNA
from Post_Process import Stats

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class Process():
    
    def __init__(self, System=None, Quantities=None):
        self.System=System
        self.Quantities=Quantities
        self.filename=System['base_dir']+System['movie_file_name']
        
        self.Tbar = False
        
        """
        Tells the programme which calculable objects are supported by the current version
        """
        
        self.Supported=[
                'rdf', 'cna', 'adj', 'pdf',  'agcn', 'nn', 'CoM', 'CoMDist', 'MoI',
                'SimTime', 'EPot', 'ETot', 'EKin', 'EDelta', 'MeanETot', 'Temp'
                ]

        
        self.metadata={}
    
        self.result_cache={}
        
        """
        This list contains unique strings which are liable to require smaller storage objects in the metadata
        """
        
        self.Spool = ['pdf', 'PDF', 'rdf', 'RDF', 'R_Cut', 'Cut']
        self.T = time.time()
        
        print( colored(f"""
        
  _____         _____  _____  _    _ _____ _____  ______ 
 / ____|  /\   |  __ \|  __ \| |  | |_   _|  __ \|  ____|
| (___   /  \  | |__) | |__) | |__| | | | | |__) | |__   
 \___ \ / /\ \ |  ___/|  ___/|  __  | | | |  _  /|  __|  
 ____) / ____ \| |    | |    | |  | |_| |_| | \ \| |____ 
|_____/_/    \_\_|    |_|    |_|  |_|_____|_|  \_\______|
                                                  
 
                          ____ 
                         /\__/\ 
                        /_/  \_\ 
                        \ \__/ / 
                         \/__\/ 
                                                                                                               
            """, 'blue'),"\n" )
            
            
            
    
        print("\nRunning version  -- %s --\n" %(__version__))
        print("\nCurrent user is [ %s ]\n" %(getpass.getuser()))
        print("\nCalculation beginning %s\n"%(datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")))
        print("\nArchitecture : [ %s ]\n" %platform.machine())
        print("\nUnits : [ %s ]\n"%Units)
        try:
            print(wikiquote.quotes(wikiquote.random_titles(max_titles=1)[0]), "\n")
        except DisambiguationPageException:
            pass
        except NoSuchPageException:
            pass
    
    def Initialising(self):
        tick = time.time()
        
        with open(self.System['base_dir']+'Sapphire_Info.txt', "w") as f:
            f.write("""
                            
                      _____         _____  _____  _    _ _____ _____  ______ 
                     / ____|  /\   |  __ \|  __ \| |  | |_   _|  __ \|  ____|
                    | (___   /  \  | |__) | |__) | |__| | | | | |__) | |__   
                     \___ \ / /\ \ |  ___/|  ___/|  __  | | | |  _  /|  __|  
                     ____) / ____ \| |    | |    | |  | |_| |_| | \ \| |____ 
                    |_____/_/    \_\_|    |_|    |_|  |_|_____|_|  \_\______|
                                                                      
                     
                                              ____ 
                                             /\__/\ 
                                            /_/  \_\ 
                                            \ \__/ / 
                                             \/__\/ 
                                                                                                                                   
                                """)
            
        
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write("\nInitialising...\n")
            
            
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write('\nReading from the %s file.\n' %(self.filename))
            
    
        
            """
            In the full version, the user will either be called for these arguments or may simply submit a script.
            I'd like for both versions to be effective. But, for now, it shall remain hard-coded to faciliate 
            debugging and support transparency.
         
            
            Edit:
                
                So there is indeed now a submission script which the user may run.
                
                An example of this may be seen in input.py
            
            """
            
            
            """
            
            Robert:
                
                This long section below simply sanitises the user input and feeds forward what the input
                arguments mean for the calculation.
                
                There is A LOT of exception handling here and there is probably more to come as the code expands
                
            """
        
        
            try:
                self.System['Start']
                if type(self.System['Start']) is not int:
                    self.Start = 0
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Bad value set for initial frame. Start has been set to 0 by default. Please set an integer value in the future.\n')
                        
                else:
        
                    self.Start = self.System['Start']
                    f.write('Initial frame at %s.\n' %(self.Start))
                    
                
            except KeyError:
                self.Start = 0
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write('No value set for initial frame. Start has been set to 0 by default.\n')
                    
            
            self.metadata['Start'] = self.Start
        
            try:
                self.System['End']
                if type(self.System['End']) is not int:
                    self.End  = len(read(self.filename, index= ':'))
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Bad value set for final frame. End has been set to %s, the final frame in this trajectory.\n'
                              '\nPlease set an integer value in the future.\n' %(self.End))
                        
                    
                elif self.System['End']<self.Start:
                    self.End  = len(read(self.filename, index= ':'))
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Bad value set for final frame. End has been set to %s, the final frame in this trajectory.\n'
                              '\nPlease set a value greater than your start frame in the future.\n' %(self.End))
                        
                
                else: 
                    self.End = self.System['End']
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Final frame set to %s.\n' %(self.End))
                        
                
            except KeyError:
                self.End  = len(read(self.filename, index= ':'))
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write('No value set for final frame. End has been set to %s, the final frame in this trajectory.\n'%(self.End))
                    
                
            self.metadata['End'] = self.End
                    
            try:
                self.System['Step']
                if type(self.System['Step']) is not int:
                    self.Step = 1
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Bad value set for Step. This has been set to 1 by default. Please set an integer value in the future.\n')
                        
                        
                else:
                    self.Step = self.System['Step']
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Step set to %s.\n' %(self.Step))
                        
                    
            except KeyError:
                self.Step = 1
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write('No value set for Step. The default of 1 has been used instead.\n')
                    
                
            self.metadata['Step'] = self.Step
            
            try:
                self.System['Skip']
                if type(self.System['Skip']) is not int:
                    self.Skip = int(self.End-self.Start)/25.0
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Bad value set for Skip. This has been set to %s such that R_Cut will be evaluated roughly every 25 frames.\n'
                              'Be aware that this may slow down your processing considerably.\n' %(self.Skip))
                        
                    
                else:
                    self.Skip = self.System['Skip']
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Skip has been set to %s.\n' %(self.Skip))
                        
                    
            except KeyError:
                self.Skip = int(self.End-self.Start)/25.0
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write('No value set for Skip. This has been set to %s such that R_Cut will be evaluated roughly every 25 frames.\n'
                              'Be aware that this may slow down your processing considerably.\n' %(self.Skip))
                    
                
            self.metadata['Skip'] = self.Skip
        
            self.Time=int((self.End-self.Start)/self.Step)
            
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Reading trajectory from frames %s to %s with an increment of %s.\n" %(self.Start, self.End, self.Step))
                
            
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write('The PDF and, by extension, R_Cut will be evaluated every %s frames.\n' %(self.Skip))
                
            
            
            try:
                self.System['UniformPDF']
                if self.System['UniformPDF'] is False:
                    self.PDF = Kernels.Kernels.Gauss
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('The set method for calculating the PDF is with a Gaussian kernel function.\n\nBe aware that this method'
                              'is slower than using a Uniform kernel. However; the distribution will be smoother.\n')
                        
                    
                    self.metadata['pdftype'] = 'Gauss'
                    try:
                        self.System['Band']
                        if bool(type(self.System['Band']) is float or int):
                            self.Band = self.System['Band']
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write('Bandwidth for the Kernel Density Estimator set to %s.\n' %(self.Band))
                                
                            
                            self.metadata['Band'] = self.Band
                        else:
                            self.Band = 0.05
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write('Bad value set for the Kernel function bandwidth.\nDefaulting to % for the Gaussian Kernel Density Estimator.\n' %(self.Band))
                                
                            
                            metadata['Band'] = self.Band
                    except KeyError:
                        self.Band = 0.05
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write('Default setting for the Gaussian Kernel Density Estimator is set to %s.\n' %(self.Band))
                            
                        
                        self.metadata['Band'] = self.Band
                        
                else:
                    self.PDF = Kernels.Kernels.Uniform
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('The selected method for calculating the PDF is with a Uniform kernel function. \n Be aware that this method'
                              'may yield non-smooth distributions for certain structures. However; this is a much faster calculator.\n')
                        
                        
                    self.metadata['pdftype'] = 'Uniform'
                    try:
                        self.System['Band']
                        if bool(type(self.System['Band']) is float or int):
                            self.Band = self.System['Band']
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write('Bandwidth for the Kernel Density Estimator set to %s.\n' %(self.Band))
                                
                                
                            self.metadata['Band'] = self.Band
                        else:
                            self.Band = 0.25
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write('Bad value set for the Kernel function bandwidth.\nDefaulting to % for the Uniform Kernel Density Estimator.\n' %(self.Band))
                                
                                
                            self.metadata['Band'] = self.Band
                    except KeyError:
                        self.Band = 0.25
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write('Default setting for the Uniform Kernel Density Estimator is set to %s.\n' %(self.Band))
                            
                            
                        self.metadata['Band'] = self.Band
                        
            except KeyError:
                self.PDF = Kernels.Kernels.Uniform
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write('The default method for calculating the PDF is with a Uniform kernel function. \n Be aware that this method'
                          'may yield non-smooth distributions for certain structures. However; this is a much faster calculator.\n')
                    
                    
                self.metadata['pdftype'] = 'Uniform'
                try:
                    self.System['Band']
                    if bool(type(self.System['Band']) is float or int):
                        self.Band = self.System['Band']
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write('Bandwidth for the Kernel Density Estimator set to %.\n' %(self.Band))
                            
                            
                        self.metadata['Band'] = self.Band
                    else:
                        self.Band = 0.25
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write('Bad value set for the Kernel function bandwidth.\nDefaulting to % for the Uniform Kernel Density Estimator.\n' %(self.Band))
                            
                            
                        self.metadata['Band'] = self.Band
                except KeyError:
                    self.Band = 0.25
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write('Default setting for the Uniform Kernel Density Estimator is set to %.\n' %(self.Band))
                        
                        
                    self.metadata['Band'] = self.Band
        
        
            try: 
                self.System['energy_file_name']
        
                self.energy = np.loadtxt(self.System['base_dir']+self.System['energy_file_name'])
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write('Reading from the %s file.\n' %(self.System['energy_file_name']))
                    
                    
            except KeyError:
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write("No energy file given, no quantities related to energy will be evaluated.\n")
                    
                    
                self.System['SimTime'] = False; self.System['EPot'] = False; self.System['ETot'] = False; self.System['EKin'] = False
                self.System['EDelta'] = False; self.System['MeanETot'] = False; self.System['Temp'] = False
                
            for x in self.Supported:
                try:
                    self.Quantities[x]
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Calculating the %s.\n" %(x)) 
                        
                        
                    globals()[x] = True
                    self.Quantities[x] = np.empty((self.Time,), dtype=object)
                    if x == 'pdf':
                        self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                        self.Quantities['R_Cut'] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                    if x == 'rdf':
                        self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                except KeyError:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Will not calculate %s in this run.\n" %(x))
                        
                        
                    globals()[x] = False
        
        
                """
            
                Robert:
                
                    I know that this quantities dictionary is a mess, the general idea is that this will
                    be filled up with information from the class implementation 'automatically'. Because
                    this has been thrown together in an afternoon with all of the calculators rejigged for
                    ease of calling as opposed to efficiency, it looks ugly as sin! Sorry, team.
                
                
                    Supported quantities as of this release:
                    
                        Euclidean distance: euc - Pairwise distance between all atoms
                    
                        RDF: rdf - radial distribution function
                    
                        Common Neighbour Analysis: cna - all signatures and the number of observed counts
                    
                        Adjacency matrix: adj - Sparse matrix of truth elements regarding whether or not two atoms are neighbours
                    
                        Pair distance distribution function: pdf - Kernel densiy estimator (uniform approximation) for the pdf.
                        This function also sets a new R_Cut each time it is called and calculated.
                    
                        Atop generalised coordination number: agcn - ask Fra
                    
                        Nearest neighbours: nn - Number of nearest neighbours each atom has. 
                
                """
                
            try: 
                self.System['HCStats']
                if bool(self.System['HCStats']) is not False:
                    self.Quantities['h'] = np.empty((self.Time,), dtype=object); globals()['h'] = True
                    self.Quantities['c'] = np.empty((self.Time,), dtype=object); globals()['c'] = True
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Will be calculating and evaluating collectednes and concertednes of cluster rearrangement.\n")
                        
                        
                else:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Will not be calculating collectednes or concertednes of cluster rearrangements.\n")
                        
            except KeyError:
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write("Will not be calculating collectednes or concertednes of cluster rearrangements.\n")
                    
            
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Initialising system environment took %.3f seconds.\n" %(time.time()-tick))
                
        
    
            from Post_Process import CNA
            tick = time.time()
    
            # Load the simulation dataset to be analyzed.
            self.Masterkey = []
        
            
            
            """
            Robert:
                
                This next block loads up the first frame of the trajectory and sets some initial file parameters and decides how to treat
                poly-metallic or mono-metallic systems depending on the user input.
                
                Note that this is NOT robust for growth simulations.
                
                It is a future goal to have the calculation react dynamically to a grand ensemble style of simulation 
                but that is not present on this version.
                
            """
            
            self.Dataset = read(self.filename, index = 0)
            self.all_positions = self.Dataset.get_positions()
            self.max_dist = max(DistFuncs.Euc_Dist(self.all_positions))
            self.metadata['CoMSpace'] = np.linspace(0, self.max_dist/2, 100)
            self.all_atoms = self.Dataset.get_chemical_symbols()
    
            used=set()
            self.Species = [x for x in self.all_atoms if x not in used and (used.add(x) or True)]
        
            self.NAtoms = len(self.all_atoms)
    
            tick = time.time()
            self.metadata['Elements'] = self.all_atoms
            self.metadata['Species'] = self.Species
            self.metadata['NSpecies']=len(self.Species)
            self.metadata['NFrames'] = self.Time
            self.metadata['NAtoms'] = self.NAtoms
            
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Checking user input for calculating homo properties in this run.\n")
                
                
            try:
                self.System['Homo']
                
                if self.System['Homo'] is None:
                    try:
                        self.System['HomoQuants']
                        if self.System['HomoQuants'] is None:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("No bimetallic properties for homo species will be calculated in this run.\n")
                                
                            
                        else:
                            self.System['Homo'] = self.metadata['Species']
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("No homo atom species requested, but you wish to calculate bimetallic homo properties." 
                                      "\n Instead we shall calculate homo properties for %s and hetero properties for the system.\n" %(self.metadata['Species']))
                                
                       
                            for x in self.System['HomoQuants']:
                                for y in self.System['Homo']:
                                    self.Quantities[x+y] = np.empty((self.Time,), dtype=object); globals()[x+y] = True
                                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                        f.write("Calculating %s as a homo property.\n" %(x+y))
                                        
                                        
                                    if 'PDF' in x:
                                        self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                                        self.Quantities['Cut'+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object); globals()['Cut'+y] = True
                                    elif 'RDF' in x:
                                        self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                    except KeyError:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("Will not be calculating any homo properties this run.\n") 
                            
                        
                        
                elif False in [x not in self.metadata['Species'] for x in self.System['Homo']]:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Specie entered in homo not found in the system. The only observed species are %s and you have requested to observe %s." 
                              "\n Defaulting to atoms found in the system for evaluation.\n" %(self.metadata['Species'], self.System['Homo']))
                        
                    
                    self.System['Homo'] = self.metadata['Species']
                    try:
                        self.System['HomoQuants']
                        if self.System['HomoQuants'] is None:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("No homo properties will be calculated in this run.\n")
                                
                            
                        else:
                            for x in self.System['HomoQuants']:
                                for y in self.System['Homo']:
                                    self.Quantities[x+y] = np.empty((self.Time,), dtype=object); globals()[x+y] = True
                                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                        f.write("Calculating %s as a homo property.\n" %(x+y))
                                        
                                    
                                    if 'PDF' in x:
                                        self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                                        self.Quantities['Cut'+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object); globals()['Cut'+y] = True
                                    elif 'RDF' in x:
                                        self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                    except KeyError:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("Will not be calculating any homo properties this run as no qauntities have been given to calculate.\n") 
                            
                        
                        
                else:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Homo atom properties will be caluclated for %s in this run.\n" %(self.System['Homo']))
                        
                    
                    try:
                        self.System['HomoQuants']
                        if self.System['HomoQuants'] is None:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("No bimetallic properties will be calculated in this run as none have been requested.\n")
                                
                            
                        else:
                            for x in self.System['HomoQuants']:
                                for y in self.System['Homo']:
                                    self.Quantities[x+y] = np.empty((self.Time,), dtype=object); globals()[x+y] = True
                                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                        f.write("Calculating %s as a homo property.\n" %(x+y))
                                        
                                    
                                    if 'PDF' in x:
                                        self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                                        self.Quantities['Cut'+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object); globals()['Cut'+y] = True
                                    elif 'RDF' in x:
                                        self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                    except KeyError:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("Will not be calculating any homo properties this run.\n")
                            
                        
                        
            except KeyError:
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write("No homo atoms have been requested for calculation. Checking if bimetallic properties have been requested.\n")
                    
                
                
                try:
                    self.System['HomoQuants']
                    if self.System['HomoQuants'] is None:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("No homo properties have been requested, either. Continuing to calculate whole system properties, only.\n")
                            
                        
                    else:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("You have requested to calculate %s while not asking for any atoms. Defaulting to considering all species identified in the system.\n" %(self.System['HomoQuants']))
                            
                        
                        self.System['Homo'] = self.metadata['Species']
                        
                        for x in self.System['HomoQuants']:
                            for y in self.System['Homo']:
                                self.Quantities[x+y] = np.empty((self.Time,), dtype = object); globals()[x+y] = True
                                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                    f.write("Calculating %s as a homo property.\n" %(x+y))
                                    
                                
                                if 'PDF' in x:
                                    self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object)
                                    self.Quantities['Cut'+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object); globals()['Cut'+y] = True
                                elif 'RDF' in x:
                                    self.Quantities[x+y] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype=object)
                                
                except KeyError:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("No homo quantities have been requested, either.\n")
                        
                    
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Finished evaluating user input for homo atomic properties.\n")
                
            
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Checking user input for hetero atomic species.\n")
                
            
            try:
                self.System['Hetero']
                if self.System['Hetero'] is not True:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Bad input detected for the 'Hetero' argument'. \n Checking if the user has requested hetero quantities to calculate.\n")
                        
                    
                    try: 
                        self.System['HeteroQuants']
                        if self.System['HeteroQuants'] is None:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("Bad input variable decalred for calculating hetero quantities. No hetero quantities will be evaluated.\n")
                                
                            
                        else:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("User has requested hetero quantities without specifying the desire to do so. We shall assume that this is an error and calculate anyway.\n")
                                
                            
                            self.System['Hetero'] = True
                            for x in self.System['HeteroQuants']:
                                self.Quantities[x] = np.empty((self.Time,), dtype = object); globals()[x] = True
                                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                    f.write("Calculating %s as a hetero property.\n" %(x))
                                    
                                
                                if 'PDF' in x:
                                    self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object)
                                    self.Quantities['HeCut'] = np.empty((int((self.Time*self.Step)/(self.Skip))), dtype = object); globals()['HeCut'] = True
                                elif 'RDF' in x:
                                    self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype =object)
                    except KeyError:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("No hetero quantities requested and so none shall be calculated.\n")
                            
                
                else:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Hetero quantities have been requested by the user.\n")
                        
                        
                    try:
                        self.System['HeteroQuants']
                        if self.System['HeteroQuants'] is None:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("Bad input variable decalred for calculating hetero quantities. No hetero quantities will be evaluated.\n")
                                
                            
                        else:
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("User has requested hetero quantities.\n")
                            self.System['Hetero'] = True
                            for x in self.System['HeteroQuants']:
                                self.Quantities[x] = np.empty((self.Time,), dtype = object); globals()[x] = True
                                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                    f.write("Calculating %s as a hetero property.\n" %(x))
                                    
                                    
                                if 'PDF' in x:
                                    self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype = object)
                                    self.Quantities['HeCut'] = np.empty((int((self.Time*self.Step)/(self.Skip))), dtype = object); globals()['HeCut'] = True
                                elif 'RDF' in x:
                                    self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype =object)
                    except KeyError:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("No hetero quantities requested and so none shall be calculated.\n")
                            
                        
            except KeyError:
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write("No input variable declared for 'Hetero' calculations. Checking if user has requested quantities without specifying the wish to calculate.\n")
                    
                
                try:
                    self.System['HeteroQuants']
                    if self.System['HeteroQuants'] is None:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("Bad input variable decalred for calculating hetero quantities. Nothing hetero will happen here, today!\n")
                            
                        
                    else:
                        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                            f.write("User has requested hetero quantities.\n")
                            
                        
                        self.System['Hetero'] = True
                        for x in self.System['HeteroQuants']:
                            self.Quantities[x] = np.empty((self.Time,), dtype = object); globals()[x] = True
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("Calculating %s as a hetero property.\n" %(x))
                                
                            
                            if 'PDF' in x:
                                self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype =object)
                                self.Quantities['HeCut'] = np.empty((int((self.Time*self.Step)/(self.Skip))), dtype = object); globals()['HeCut'] = True
                            elif 'RDF' in x:
                                self.Quantities[x] = np.empty((int((self.Time*self.Step)/(self.Skip)),), dtype =object)
                except KeyError:
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("No hetero quantities requested and so none shall be calculated.\n")
                        
                    
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Finished evaluating input arguments for homo/hetero calculations.\n")
                
                       
            #This block initialises the metadata
            for key in self.Quantities:
                self.metadata[key] = self.Quantities[key]
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("Initialising Metadata took %.3f seconds.\n" %(time.time() - tick))
                f.write("This system contains %s atoms.\n"
                      "Consisting of %s as present atomic species.\n" %(self.NAtoms, self.Species))
            try:
                if self.System['New_agcn_movie'] is True:
                    self.New_Obj = np.empty((self.Time,), dtype=object)
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Creating a new movie file.\n")
                        
                    
            except KeyError:   
                with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                    f.write("Will not be creating a new movie file.\n")
                    
            
            self.L1 = list(range(self.metadata['Start'], self.metadata['End'], self.metadata['Skip']*self.metadata['Step']))
            self.L2 = list(range(self.metadata['Start'], self.metadata['End'], self.metadata['Step']))
            self.L3 = [x for x in self.L2 if x not in self.L1]
            

                
            
            
        
        
    def calculate(self, i):
        
        
        """
        Robert:
            
            And we finally get to the meat and bones of the calculator.
            
            This is simply broken down into a series of small blocks.
            
            Each frame is instantiated by loading in the particular frame of the trajectory. 
            While this is time intensive, it saves a lot on memory by not storing an entire trajectory
            in the memory for the entire duration.
            
            The positions of the atoms are stored in an array and analysis may begin from there.
            
            Each block is laid out in the following fashion:
            
                
                Are each of the required quantities calculated and is this wanted?
                    Y: Calculate and save to metadata by calling a calculator from an external module
                    
                    N: Pass and continue.
                    
            The premise being that the programme will be able to notice that you have not calculated a dependency for a given quantity
            E.g., no Homo quantities in a bimetallic situation
            And will not perform any future calculations which depend on this.
            
            These quantities are organised by their names as keys which are stored in frame wise metadata dictionaries.
            
            At the end of the calculation, these frame wise dictionaries are unloaded into a global dictionary and emptied for the next frame.
        """
                
        
        T0=time.time()
    

        temptime=time.time()
        self.All_Atoms = read(self.filename, index = i)
        self.result_cache['pos'] = self.All_Atoms.get_positions()
        self.result_cache['euc'] = DistFuncs.Euc_Dist(self.result_cache['pos'])
        try:
            self.metadata['MoI'][int(i/self.Step)] = self.All_Atoms.get_moments_of_inertia()
        except KeyError:
            pass
        
        #All RDF calculations performed in the following block
        try:
            if i%(self.Skip*self.Step)==0 and bool(globals()['rdf']) is True: 
                self.result_cache['rdf'] = DistFuncs.RDF(self.result_cache['pos'], 100, 10.0)
                self.metadata['rdf'][int(i/(self.Step*self.Skip))] = self.result_cache['rdf'] 
                try:
                    if bool(bool(self.System['Homo'])*bool('HoRDF' in self.System['HomoQuants'])) is True:
                        for x in self.System['Homo']:
                            self.result_cache['homopos'+x] = DistFuncs.get_subspecieslist(x, self.metadata['Elements'], self.result_cache['pos'])
                            self.metadata['HoRDF'+x][int(i/(self.Step*self.Skip))] = DistFuncs.RDF(self.result_cache['homopos'+x])
                except KeyError:
                    pass
                try:
                    if bool(bool(self.System['Hetero'])*globals()['HeRDF']) is True:
                        self.metadata['HeRDF'][int(i/(self.Step*self.Skip))] = DistFuncs.RDF(self.result_cache['pos'], Res=100, R_Cut=10.0, Hetero = True, 
                                                                              Species = self.metadata['Species'], Elements = self.metadata['Elements'])
                except KeyError:
                    pass
        except KeyError:
            pass
    
        #All PDF calculations performed in the following block
        try:
            if i%(self.Skip*self.Step)==0 and bool(globals()['pdf']) is True:
                self.result_cache['pdf'] = self.PDF(self.result_cache['euc'], self.Band)
                self.metadata['pdf'][int(i/(self.Step*self.Skip))] = self.result_cache['pdf']
                self.R_Cut = self.result_cache['pdf'][-1]
                self.metadata['R_Cut'][int(i/(self.Step*self.Skip))] = self.R_Cut
                try:
                    if bool(bool(self.System['Homo'])*bool('HoPDF' in self.System['HomoQuants'])) is True:
                        for x in self.System['Homo']:
                            self.result_cache['homoed'+x] = DistFuncs.Euc_Dist(positions=self.result_cache['pos'], homo = True, specie = x, elements = self.metadata['Elements'])
                            if self.result_cache['homoed'+x] is not None:
                                self.metadata['HoPDF'+x][int(i/(self.Step*self.Skip))] = self.PDF(self.result_cache['homoed'+x], self.Band)
                                self.metadata['Cut'+x][int(i/(self.Step*self.Skip))] = self.metadata['HoPDF'+x][int(i/(self.Step*self.Skip))][-1]
                            else:
                                pass
                except KeyError:
                    pass
                try:
                    if bool(self.System['Hetero']*globals()['HePDF']) is True:
                        self.result_cache['heteropos'] = DistFuncs.Hetero(self.result_cache['pos'], self.metadata['Species'], self.metadata['Elements'])
                        self.result_cache['heterodist'] = functools.reduce(operator.iconcat, self.result_cache['heteropos'], [])
                        if self.result_cache['heterodist'] is not None:
                            self.metadata['HePDF'][int(i/(self.Step*self.Skip))] = self.PDF(self.result_cache['heterodist'], self.Band)
                            self.metadata['HeCut'][int(i/(self.Step*self.Skip))] = self.metadata['HePDF'][int(i/(self.Step*self.Skip))][-1]
                        else:
                            self.metadata['HePDF'][int(i/(self.Step*self.Skip))] = None
                            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                                f.write("There was an error with the heterogenous distance array. No PDF calculated for frame %s.\n"%(i))
                                
                except KeyError:
                    pass
        except KeyError:
            pass

    
        #This block evaluates all of the CoM calculations.
        try:
            if bool(globals()['CoM']) is True:
                self.result_cache['CoM'] = self.All_Atoms.get_center_of_mass()
                self.metadata['CoM'][int(i/self.Step)] = self.result_cache['CoM']
                try:
                    if bool(globals()['CoMDist']) is True:
                        self.Temp_Val = DistFuncs.CoM_Dist(self.result_cache['pos'], 
                                                      CoM = self.result_cache['CoM'], 
                                                      homo = False, specie = None, elements = None)
                        
                        self.metadata['CoMDist'][int(i/self.Step)] = self.PDF(self.Temp_Val, self.Band*5, mon = True,
                                                                              Space = self.metadata['CoMSpace'])[1]
                except KeyError:
                    pass               
        except KeyError:
            pass
        
        #This block evaluates mono-metallic CoM calculations.

        try:
            if bool(bool(self.System['Homo'])*bool('CoM' in self.System['HomoQuants'])) is True:
                for x in self.System['Homo']:
                    self.Temp_Val = DistFuncs.get_subspecieslist( specie = x, 
                                                                              elements = self.metadata['Elements'], 
                                                                              positions = self.result_cache['pos']) 
                    self.result_cache['CoM'+x] = DistFuncs.get_CoM(self.Temp_Val)
                    self.metadata['CoM'+x][int(i/self.Step)] = self.result_cache['CoM'+x]
                    
                    self.New_Temp = DistFuncs.CoM_Dist(self.Temp_Val, self.result_cache['CoM'+x])
                    
                    try:
                        if 'CoMDist' in self.System['HomoQuants']:
                            self.Dist = self.PDF(self.New_Temp, self.Band*5, mon = True, Space = self.metadata['CoMSpace'])
                            try:
                                self.metadata['CoMDist'+x][int(i/self.Step)] = self.Dist[1]
                            except TypeError:
                                pass
                    except KeyError:
                        pass
                    try:
                        if 'MidCoMDist' in self.System['HomoQuants']:
                            self.Temp_Val = DistFuncs.CoM_Dist(DistFuncs.get_subspecieslist( specie = x, 
                                                                                            elements = self.metadata['Elements'], 
                                                                                            positions = self.result_cache['pos']), CoM = self.result_cache['CoM'] )
                            self.Dist = self.PDF(self.Temp_Val, Band = self.Band*5, mon = True, Space = self.metadata['CoMSpace'])
                            try:
                                self.metadata['MidCoMDist'+x][int(i/self.Step)] = self.Dist[1]
                            except TypeError:
                                pass
                    except KeyError:
                        pass
        except KeyError:
            pass


 
        #This block calculates the CNA signatures for the whole system, only
        try:
            if bool(globals()['cna']) is True:
                self.result_cache['cna'] = CNA.get_cnas(i, self.metadata['R_Cut'][int(i/(self.Step*self.Skip))], self.Masterkey, self.filename)
                self.metadata['cna'][int(i/self.Step)] = self.result_cache['cna']
        except KeyError:
            pass
        
        
        #This block evaluates the adjacency matrices for the whole system, homo pair(s), & hetero atoms 
        
        try:
            if bool(globals()['adj']) is True:
                self.result_cache['adj'] = Adjacent.Adjacency_Matrix(self.result_cache['pos'], self.result_cache['euc'], self.metadata['R_Cut'][int(i/(self.Step*self.Skip))])
                self.metadata['adj'][int(i/(self.Step))] = self.result_cache['adj']
        except KeyError:
            pass
        
        
        try:
            if bool(bool(self.System['Homo'])*bool('HoAdj' in self.System['HomoQuants'])) is True:
                for x in self.System['Homo']:
                    self.result_cache['HomoED'+x] = DistFuncs.Euc_Dist(self.result_cache['pos'], homo = True, specie = x, elements = self.metadata['Elements'])
                    
                    self.metadata['HoAdj'+x][int(i/self.Step)] = Adjacent.get_coordination(Adjacent.Adjacency_Matrix(
                                                                                               DistFuncs.get_subspecieslist
                                                                                               (
                                                                                               x, self.metadata['Elements'], self.result_cache['pos']
                                                                                               ),
                                                                                               self.result_cache['HomoED'+x], self.metadata['R_Cut'][int(i/(self.Step*self.Skip))]) )
        except KeyError:
            pass
        try:
            if bool(self.System['Hetero']*globals()['HeAdj']) is True:
                self.result_cache['HeDist'] = DistFuncs.Hetero(self.result_cache['pos'], self.metadata['Species'], self.metadata['Elements'])
                if self.result_cache['heteropos'] is not None:
                    self.metadata['HeAdj'][int(i/self.Step)] = Adjacent.get_coordination_hetero(self.result_cache['HeDist'], self.metadata['R_Cut'][int(i/(self.Step*self.Skip))])
                else:
                    self.metadata['HeAdj'] = None
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("There was an error with hetero positions, no respective adjacency matrix calculated for frame %s.\n" %(i))
                        
        except KeyError:
            pass
        
    
        #This block evaluates the atop generalised coordination number for the whole system
        try:
            if bool(globals()['agcn']*globals()['nn']*globals()['adj']) is True:
                self.Agcn, self.NN = AGCN.agcn_generator(self.result_cache['adj'], NN = True)
                self.metadata['agcn'][int(i/self.Step)] = self.Agcn; self.metadata['nn'][int(i/self.Step)] = self.NN
            elif bool(globals['agcn']*globals()['adj']) is True:
                self.Agcn = AGCN.agcn_generator(self.result_cache['adj'])[0]
                self.metadata['agcn'][int(i/self.Step)] = self.Agcn
            elif bool(globals['nn']*globals()['adj']) is True:
                _,self.NN = AGCN.agcn_generator(self.result_cache['adj'], NN = True)
                self.metadata['nn'][int(i/self.Step)] = self.NN
        except KeyError:
            pass
        
        try:
            if self.Tbar is True:
                ##This is simply a progress updater which informs the user how every 5% is getting along.
                if (100*i / (self.Time/self.Step)) % 5 == 0:
                    Per = int(100*i / (self.Time/self.Step))
                    with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                        f.write("Currently performed %.3f%% of the calculation.\n" %(Per))
                        f.write('['+int(Per/5)*'##'+(20-int(Per/5))*'  '+']\n')
                        
        except KeyError:
            pass
        
        
        try:
            if self.System['New_agcn_movie'] is True:
                self.Temp_aGCN = (np.column_stack( (self.all_atoms,self.result_cache['pos'],self.Agcn) ))
        except KeyError:
            pass


        self.Masterkey.sort()
        self.metadata['masterkey']=self.Masterkey
    
        """
                    
        #############################################################################################
        
        Robert:
            And now we check to see if the users wishes to evaluate any of the quantities
            from the energy file and add them to the metadata.
        
        """
    
        try:
            if bool(globals()['SimTime']) is True:
                self.metadata['SimTime'][int(i/self.Step)] = self.energy[:,0][int(i)]
        except KeyError:
            pass
        
        try:
            if bool(globals()['EPot']) is True:
                self.metadata['EPot'][int(i/self.Step)] = self.energy[:,1][int(i)]
        except KeyError:
            pass
        
        try:
            if bool(globals()['ETot']) is True:
                self.metadata['ETot'][int(i/self.Step)] = self.energy[:,2][int(i)]
        except KeyError:
            pass
        
        try:
            if bool(globals()['EKin']) is True:
                self.metadata['EKin'][int(i/self.Step)] = self.energy[:,3][int(i)]
        except KeyError:
            pass
            
        try:
            if bool(globals()['EDelta']) is True:
                self.metadata['EDelta'][int(i/self.Step)] = self.energy[:,4][int(i)]
        except KeyError:
            pass
            
        try:
            if bool(globals()['MeanETot']) is True:
                self.metadata['MeanETot'][int(i/self.Step)] = self.energy[:,5][int(i)]
        except KeyError:
            pass
            
        try:
            if bool(globals()['Temp']) is True:
                self.metadata['Temp'][int(i/self.Step)] = self.energy[:,6][int(i)]
        except KeyError:
            pass
        
        
    
        return self.metadata, self.Temp_aGCN
    
    
    def run_pdf(self, cores = mp.cpu_count()-1):
        
        """
        Robert:
            
            This section of the code runs the calculator over the list of frame indices
            which the user wishes to calculate the PDDF and R_Cut for.
            
            The reason for doing these first is that when parallelising over the remainder of the
            simulation - one may call the R_Cut values as they are calculated and saved
            a - priori.
            
            The default number of threads to parallelise over is 1 fewer than the machine has available.
            If you run a quad-core machine, then the default will be to run 7 threads in parallel.
            
            Change this value at your own risk.
        """
        
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write("\nComputing the R_Cut calculations over %s threads.\n"%cores)
            
            
        p = mp.Pool(cores) #Create an instance of parallel workers.
        self.result_pdf = np.asanyarray(p.map(self.calculate, (self.L1))) #Provide the workers with the calculate function and list to iterate over.
        p.close()
        p.join()
        self.T0=time.time()
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write('Time for completing RCut calculation is %s.\n' %(time.strftime("%H:%M:%S", time.gmtime((self.T0-self.T)))))
            
        
        #Then split up the two return values of metadata for analysis and freshly written xyz file.
        
        self.aGCN_Data = self.result_pdf[:,1] #This separately writes the new xyz file with aGCN value as a new column.
        
        #This may be extended to include other local atomic properties such as pressure & cna pattern.
        
        self.result_pdf = self.result_pdf[:,0]
        self.T1 = time.time()
        return self.result_pdf, self.aGCN_Data
        

    
    def clean_pdf(self):
        
        """
        Robert:
            This function is called to read out the frame wise metadata dictionaries created
            by each worker in then 'run' function and then read it into the global metadata dictionary which is organised by 
            key and then by frame.
        """
            
        
        self.Keyring = list(self.Quantities.keys()) #Identify the keys to be evaluated.
        
        
    
        #Add all of the calculated frames for a particular key to the global metadata.
        
        #Then remove the key from the metadata.
        
        #The spool contains strings which indicate a key will have fewer total 'active' frames.
        
        #E.g., For PDDF calculations as these are expensive.
    
        for Key in self.Quantities.keys():
            for i in self.L1:
                for code in self.Spool:
                    if code in Key:
                        self.metadata[Key][self.L1.index(i)] = self.result_pdf[self.L1.index(i)][Key][self.L1.index(i)] #Organise the global metadata frame-wise for each key.
                        try:
                            self.Keyring.remove(Key)
                        except ValueError: #This is still here in case the user requests a weird quantity to calculate. Hopefully never raised but I'm scared to remove this.
                            continue
                            
                            
        for Key in self.Keyring:
            for i in self.L1:
                self.New_Obj[int(i/self.Step)] = self.aGCN_Data[self.L1.index(i)] #Write the aGCN to the new xyz file.
                try:
                    self.metadata[Key][int(i/self.Step)] = self.result_pdf[self.L1.index(i)][Key][int(i/self.Step)]
                except TypeError:
                    continue
                    try:
                        self.Keyring.remove(Key)
                    except ValueError: #These exception exceptions are hangovers from debugging and appear to still be useful... 
                        continue
                except IndexError:
                    continue
                
        #The following section updates the CNA masterkey as a 'living/breathing' component of the analysis.
                    
        self.metadata['masterkey'] = self.result_pdf[0]['masterkey']
        
        for i in self.L1:
            for item in self.result_pdf[self.L1.index(i)]['masterkey']:
                if item not in self.metadata['masterkey']:
                    self.metadata['masterkey'].append(item)
                    

        self.Tbar = True
        
                
    def run_core(self, cores = mp.cpu_count()-1):
        
        """
        Robert:
            As above for the PDDF calculations.
            
            Only here we calculate over all remaining frames.
            
            All analyses and functions are facsimilies of their above counterparts.
            
        """
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write("\nComputing the core calculations over %s threads.\n"%cores)
            
        
        self.Keyring_core=list(self.Quantities.keys()) #Only compute over remaining quantities

        p = mp.Pool(cores)
        self.result_core = np.asanyarray(p.map(self.calculate, (self.L3)))
        p.close()
        p.join()
        
        self.T2 = time.time()
        
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write('Time for completing core calculation is %s.\n' %(time.strftime("%H:%M:%S", time.gmtime((self.T2-self.T1)))))
            
            
        self.aGCN_Data = self.result_core[:,1]
        self.result_core = self.result_core[:,0]
        return self.result_core, self.aGCN_Data
    
    def clean_core(self):
        
        
        """
        Robert:
            
            Exactly the same deal as above for the clean_pdf function
        """
        
        for obj in self.Spool:
            for Key in self.Keyring_core:
                if obj in Key:
                    self.Keyring_core.remove(Key)
                else:
                    continue
        
                    
        for key in self.Keyring_core:
            for i in self.L3:
                self.New_Obj[int(i/self.Step)] = self.aGCN_Data[self.L3.index(i)]
                try:
                    self.metadata[key][int(i/self.Step)] = self.result_core[self.L3.index(i)][key][int(i/self.Step)]
                except TypeError:
                    continue
                    try:
                        self.Keyring.remove(Key)
                    except ValueError:
                        continue
                except IndexError:
                    continue
                    try:
                        self.Keyring.remove(Key)
                    except ValueError:
                        continue

        for i in self.L3:
            for item in self.result_core[self.L3.index(i)]['masterkey']:
                if item not in self.metadata['masterkey']:
                    self.metadata['masterkey'].append(item)
        self.T3 = time.time()
        
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write('Time for completing core clean is %s.\n' %(time.strftime("%H:%M:%S", time.gmtime((self.T3-self.T2)))))
            f.write('Time for completion is %s.\n' %(time.strftime("%H:%M:%S", time.gmtime((self.T3-self.T)))))
            
                

    def analyse(self, Stat_Tools):
        
        """
        Robert:
            
            This function is a little bit clunky in design but it attempts to stitch together disparate
            analysis functions which are of varying size and require different functions being called on
            different distributions / quantities.
            
            In general, the user will define which functions they wish to call on each distribution in the input file.
            
            This will then create a function object for each tool to be used and enters it into a tuple with the metadata keys
            for quantities to be analysed by that function.
            
            E.g., Jenson Shannon Divergence on the Radial Distribution Function.
            
            New metadata keys are then created for these analysed distributions and their frame-wise analysis values are stored 
            under these keys.
            
            Moreover, for H / C statistics, these have T-1 and T-2 entries respectively and so new storage arrays for them
            must be instantiated separately while the latter is dependent on the former.
            
            This is likely the most sensitive function of the entire project so be careful when investigating.
            
            """
            
        #This block handles the Lindemann indices.
        try:
            if bool(globals()['Lind']) is True:
                Lind_Line = DistFuncs.Lindemann(self.filename, N_Atoms = self.metadata['NAtoms'], 
                                                CPUs = mp.cpu_count()-1)
                self.metadata['Lind'] = Lind_Line.Main_Lind()
                
        except KeyError:
            pass
            
        try:
            if bool(bool(self.System['Homo'])*bool('Lind' in self.System['HomoQuants'])) is True:
                for x in self.System['Homo']:
                    Lind_Line = DistFuncs.Lindemann(self.filename, N_Atoms = self.metadata['NAtoms'], 
                                                    CPUs = mp.cpu_count()-1, 
                                                    Ho = True, Specie = x, Elements = self.metadata['Elements'])
                    self.metadata['Lind' + x] = Lind_Line.Main_Lind()
        except KeyError:
            pass
            

        self.Stat_Tools = Stat_Tools
        self.functions_list = [o for o in getmembers(Stats.Dist_Stats) if isfunction(o[1])]
        for i in range(1, int((self.End - self.Start)/self.Step) ):
        
            #This  block calculates the concertedness and collectivity of atom rearrangements    
            if bool(self.System['HCStats']*i) is not False:
                self.result_cache['r'] = Adjacent.R(self.metadata['adj'][i], self.metadata['adj'][i-1])
                self.metadata['h'][i-1] = Adjacent.Collectivity(self.result_cache['r'])
                if not(i<3):
                    self.metadata['c'][i-2] = Adjacent.Concertedness(self.metadata['h'][i-1], self.metadata['h'][i-3])
            
        #This block reconfigures the CNA signatures to include all observed throughout the trajeectory
        
        try:
            self.Quantities['cna']
            self.cna = self.metadata['cna']
            for j in range(0, int( (self.End - self.Start) / self.Step ) ):
                self.metadata['cna'][j] = CNA.get_heights(self.cna, self.metadata['masterkey'], j)
        except KeyError:
            with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
                f.write("No CNA signatures to be calculated.\n")
                
        
        
        """
        This next block creates a dictionary whose keys are the analysis tools to be implemented.
        The first entry is the function to be called.
        All of the subsequent entries are the keys, as they appear in the metadata, to be processed.
        """
        
        self.Stat_Keys = self.Stat_Tools.keys()
        self.Meta_Keys = self.metadata.keys()
        self.Calc_Dict = {}
        for obj in self.Stat_Keys:
            for item in self.functions_list:
                if obj.lower() in item[0].lower():
                    self.Calc_Dict[item[0]] = [item[1]]
                    
        for A_Key in self.Stat_Keys:
            for M_Key in self.Meta_Keys:
                for obj in self.Stat_Tools[A_Key]:
                    if obj.lower() in M_Key.lower():
                        if M_Key.lower() is 'pdftype':
                            pass
                        else:
                            self.Calc_Dict[A_Key].append(M_Key)
            self.Calc_Dict[A_Key].remove('pdftype')
                            
        """
        This next block reads over the previously created dictionary and then doctors the relevant
        metadata entry to be ready for processing.
        
        That is to say, that the heights of the distributions are to be analysed as the x-axis are 
        largely uniform across the sample.
        """
        
        for A_Key in self.Stat_Keys:
            for obj in self.Calc_Dict[A_Key][1:]:
                self.metadata[A_Key+obj] = np.empty((len(self.metadata[obj]),), dtype=object)
                Init = self.metadata[obj][0][1] # This is the initial distribution to which we shall make comparrisons 
                for frame in range( len(self.metadata[obj]) ):
                    try:
                        Temp = self.metadata[obj][frame][1] #This is the y-axis of the distribution under consideration
                        
                        self.metadata[A_Key+obj][frame] = self.Calc_Dict[A_Key][0](Init, Temp)
                    except TypeError:
                        continue
        return self.metadata
                    
    def New_File(self, new_movie='agcn_movie.xyz'):
        
        """
        Robert:
            
            This function, at the moment, is only supporting the introduction of the aGCN
            to the new xyz file. 
            
            But this is easily appended to as needs dictate.
            
            My intention is to read out a veritable zoo of interesting quantities such as:
                
                - Atomic pressure / strain
                - CNA Pattern
                - Magnitude of force
                - Distance to CoM
                
                - etc...
            
            The reason for this being a means of providing good visual intuition
            behind systems analysed.
            
            This is simply a quality of life and visualisation function and should not be relied upon 
            to provide statistically meaningful results.
            
            I'm tempted to add in the option to create a new folder for the files generated by this code
            and so a future feature here may be to call a 'new path' argument which will try to change to
            a new directory and make a way if possible
            
            Chisa?
            
        """
        
        with open(self.System['base_dir'] + new_movie, 'w+') as self.movie:
            self.movie.write(str(self.metadata['NAtoms']) +'\n')
            self.movie.write('\t' + "This was made by Jones' post-processing code." + '\n')
            for Frame in self.New_Obj:
                for items in Frame:
                    self.movie.write(' \t'.join(str(item) for item in items) +'\n')
                self.movie.write(str(self.metadata['NAtoms']) + '\n')
                self.movie.write('\n')
        with open(self.System['base_dir']+'Sapphire_Info.txt', "a") as f:
            f.write("This movie has been saved as %s in %s.\n" %(new_movie, self.System['base_dir']))
            f.write('Time for writing new aGCN trajectroy is %s.\n' %(time.strftime("%H:%M:%S", time.gmtime((time.time()-self.T3)))))
    
