import os
import sys

sys.path.append('/home/mmm0547/Jones/Codes/SapphireV0.8.0')

from Dispatch import LoDiSInputMaker, Submit

Home = os.getcwd()

Destinations = []

for root, dirs, files in os.walk("To_Thomas/"):
    try:

        System = {'base_dir' : root+'/', 'irand' : 1345, 'type_process' : 'nvt', 
                  'filepos' : files[0], 'npas' : 4000000, 'scrivo' : 2000, 
                  'tinit' : 600, 'npast' : 2000,
                  'potdir' : '/home/mmm0547/POT_FILES/'}
        A = LoDiSInputMaker.inp(System)

        A.nvt()
        Destinations.append( System['base_dir'] + str(System['irand']) + '/' )
        #print(Destinations)
        os.chdir(Home)
    except IndexError:
        pass
Script = Submit.sub(Destinations, LoDis_Path = 'home/mmm0547/LoDiS_GIT/base/LODIS_all')
Script.Submission('48:00:00', 'Sim', str(Home))
