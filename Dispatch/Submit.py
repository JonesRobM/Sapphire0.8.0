import os
import sys


class sub():
    
    def __init__(self, Destinations, LoDis_Path):
        self.Iterable = Destinations
        self.LoDiS_Path = LoDis_Path
    
    def Submission(self, Time, Name, WD):
        with open('sub.sh', "w+") as file:
            file.write(
                        "\n#!/bin/bash -l\n"
                        
                        "\n# 1. Force bash as the executing shell.\n"
                        "\n#$ -S /bin/bash\n"
                        
                        "\n# 2. Request ten minutes of wallclock time (format hours:minutes:seconds).\n"
                        "\n#$ -l h_rt=%s\n"
                        
                        "\n# 3. Request 1 gigabyte of RAM (must be an integer)\n"
                        "\n#$ -l mem=8G\n"
                        
                        "\n# 4. Request 15 gigabyte of TMPDIR space (default is 10 GB)\n"
                        "\n#$ -l tmpfs=15G\n"
                        
                        "\n#$ -pe mpi 24\n"
                        
                        "\n# 5. Set the name of the job.\n"
                        "\n#$ -N %s\n"
                        
                        "\n# 6. Set the working directory to somewhere in your scratch space.  This is\n"
                        
                        "\n# a necessary step with the upgraded software stack as compute nodes cannot\n"
                        "\n# write to $HOME.\n"
                        
                        "\n# Replace '<your_UCL_id>' with your UCL user ID :)\n"
                        "\n#$ -wd %s\n"
                        
                        "\n# 7. Your work *must* be done in $TMPDIR\n" 
                        
                        "\n#$ -P Gold\n"
                        "\n#$ -A KCL_Baletto\n"
                        
                        "\n#Load modules\n"
                        
                        "\nmodule load python/3.8.0\n"
                        %( Time, Name, WD ))
            
        with open('sub.sh', "a+") as file:
            file.write("\ncat > Execute.py << EOF\n"
                       
                       "\nimport multiprocessing as mp\n"
                       "import functools\n"
                       "import operator\n"
                       "from functools import partial\n"
                       "import shlex, subprocess\n"
                       "import os\n"
                        
                        
                            
                       "def Run_Lodis(PathToLoDiS, Directory):\n"
                       "    os.chdir(Directory)\n"  
                       "    args = '/home/mmm0547/LoDiS_GIT/base/LODIS_all < input > out'\n"
                        
                       "    subprocess.call(args, shell = False)\n"
                       "\niterable = %s \n"

		       "Home = os.getcwd()\n"
		       "Iter = [Home+'/'+ x for x in iterable]\n"
                       "\npool = mp.Pool(24)\n"
                       "\n"
                       "\npool.map(Run_Lodis, Iter)\n"
                       %( self.Iterable ))
            
        with open('sub.sh', "a+") as file:
            file.write("\nP.close()\n"
                       "\nP.join()"
                       "\nEOF\n"
		       "\npython3 Execute.py >> Info.txt\n")
