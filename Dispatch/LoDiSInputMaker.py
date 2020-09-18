import shlex, subprocess
import os
import numpy as np
import sys
from ase.io import read

#The default arguments for essential arguments
Defaults = {
    'tstep' : '5.d-15', #Roughly ionic vibration frequency
    'npas' : 2000000, #10ns of simulation time
    'scrivo' : 2000, #Write every 10ps
    'tinit' : 300,
    'npast' : 2000,
    'vnu' : '5.0d11'
    }


class inp():
    
    def __init__(self, System=None):
        
        """
        Below are the necessary arguments required to run LoDiS
        """
        
        self.Args_List = ['irand', 'type_process', 'tstep',
                          'npast', 'scrivo', 'npas', 'tinit',
                          'filepos', 'vnu']
        
        self.Args_In = {}
        
        if System is None:
            sys.exit("\nNo information provided.\n")
               
        self.System = System
        
        for arg in self.Args_List:
            if arg in self.System:
                self.Args_In[arg] = self.System[arg]
            else:
                self.Args_In[arg] = Defaults[arg]
            
        self.Atoms = read(self.System['base_dir'] + self.System['filepos'])
        self.Natoms = len(self.Atoms)
        self.all_atoms = self.Atoms.get_chemical_symbols()

        used=set()
        self.Species = [x for x in self.all_atoms if x not in used and (used.add(x) or True)]
        if len(self.Species) == 1:
            self.sys = 'mon'
        elif len(self.Species) == 2:
            self.sys = 'bim'
        else:
            sys.exit("\nUnsupported number of chemical species.\n")
        
        if not self.System['potdir'] is None:
            Guess_Metals = True
            
            if os.path.isfile(self.System['potdir']+self.Species[0] + '_' + self.Species[-1]+'.pot'):
                self.Args_In['pot'] = self.System['potdir'] + self.Species[0]+ '_' + self.Species[-1]+'.pot'
            elif os.path.isfile(self.System['potdir']+self.Species[-1] + '_' + self.Species[0]+'.pot'):
                self.Args_In['pot'] = self.System['potdir']+self.Species[-1] + '_' + self.Species[0]+'.pot'
            else:

                
                sys.exit("\nNo potential file could be found for these metals.\n"
                         "\nTry linking directly to your own or alternatively,"
                         " find an appropriate rgl potential.\n")
        elif not self.System['potfile'] is None:
            if os.path.isfile(self.System['potfile']):
                self.Args_In['pot'] = self.System['potfile']
            else:
                sys.exit("\nNo potential file could be found for these metals.\n"
                         "\nTry linking directly to your own or alternatively,"
                         " find an appropriate rgl potential.\n")
        else:
            sys.exit("\nNo potential file could be found for these metals.\n"
                     "\nTry linking directly to your own or alternatively,"
                     " find an appropriate rgl potential.\n")
                
        if ('microcanon' in self.System['type_process'].lower()) or ('nve' in self.System['type_process'].lower()):
            self.Args_In['vnu'] = '0'

        os.mkdir(self.System['base_dir'] + str(self.System['irand']))
        os.chdir(self.System['base_dir'])
        
        with open('%s/input'%(self.System['irand']) , "w+") as openfile:
            openfile.write(
                "&simul\n irand = %s, \n type_process = '%s',\n tstep = %s,\n"
                           " npast = %s,\n scrivo = %s,\n npas = %s,\n tinit = %s,\n"
                           " vnu = %s,\n filepos = '%s',\n filepot = '%s',\n/\n"
                           
                           %( 
                             self.Args_In['irand'], self.Args_In['type_process'], self.Args_In['tstep'],
                             self.Args_In['npast'], self.Args_In['scrivo'], self.Args_In['npas'], self.Args_In['tinit'], 
                             self.Args_In['vnu'], '../' + self.Args_In['filepos'], self.Args_In['pot'])
                           )
            
        with open('%s/input'%(self.System['irand']), "a+") as openfile:
            openfile.write(
                "\n&system\n type_potential  = 'rgl',\n"
                " natom = %s,\n fattor = 1.d0,\n"
                " elem1 = '%s',\n elem2 = '%s',\n sys = '%s',\n/"
                %( self.Natoms, 
                   self.Species[0], self.Species[-1], self.sys ))
        
        getattr(self, self.System['type_process'])
    
    def itMD(self, input_params):
        self.params = input_params
        
        with open('%s/input'%(self.System['irand']), "a+") as openfile:
            openfile.write("\n&calor\n deltat = %s,\n tcaloric = %s,\n/"
                           %(self.params['deltat'], self.params['tcaloric']))

    
    def nvt(self):
        with open('%s/input'%(self.System['irand']), "a+") as openfile:
            openfile.write("\n&canon\n vel_af = .true\n/")
            
            
    def nve(self):
        with open('%s/input'%(self.System['irand']), "a+") as openfile:
            openfile.write("\n&canon\n vel_af = .true\n/")
    
    
    def growth(self):
        return None
    
    
    def metadynamics(self):
        return None
    
    def restart(self):
        return None
    
