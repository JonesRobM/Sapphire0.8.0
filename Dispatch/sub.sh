
#!/bin/bash -l

# 1. Force bash as the executing shell.

#$ -S /bin/bash

# 2. Request ten minutes of wallclock time (format hours:minutes:seconds).

#$ -l h_rt=48:00:00

# 3. Request 1 gigabyte of RAM (must be an integer)

#$ -l mem=8G

# 4. Request 15 gigabyte of TMPDIR space (default is 10 GB)

#$ -l tmpfs=15G

#$ -pe mpi 24

# 5. Set the name of the job.

#$ -N Sim

# 6. Set the working directory to somewhere in your scratch space.  This is

# a necessary step with the upgraded software stack as compute nodes cannot

# write to $HOME.

# Replace '<your_UCL_id>' with your UCL user ID :)

#$ -wd /scratch/home/mmm0547/LoDiS_Jobs

# 7. Your work *must* be done in $TMPDIR

#$ -P Gold

#$ -A KCL_Baletto

#Load modules

module load python/3.8.0

cat > Execute.py << EOF

import multiprocessing as mp
import functools
import operator
from functools import partial
import shlex, subprocess
import os
def Run_Lodis(Directory):
    os.chdir(Directory)
    args = ['/home/mmm0547/LoDiS_GIT/base/LODIS_all', '<', 'input', '>', 'out' ]
    subprocess.call(args, shell = False)

iterable = ['To_Thomas/fcc110Pt85_IDh421/1345/', 'To_Thomas/fcc111Pt85_IDh421/1345/', 'To_Thomas/fcc111Pt147Dh441_rlx/1345/', 'To_Thomas/fcc111Pt68_hdh_from431/1345/', 'To_Thomas/fcc111Pt147Co_rlx/1345/', 'To_Thomas/fcc100Pt76_DPC/1345/', 'To_Thomas/fcc100Pt147Dh441_rlx/1345/', 'To_Thomas/fcc110Pt55_Ih/1345/', 'To_Thomas/fcc100Pt55_Ih/1345/', 'To_Thomas/fcc111Pt55_Ih/1345/', 'To_Thomas/fcc110Pt68_hdh_from431/1345/', 'To_Thomas/fcc110Pt147Co_rlx/1345/', 'To_Thomas/fcc111Pt76_DPC/1345/', 'To_Thomas/fcc110Pt147Dh441_rlx/1345/', 'To_Thomas/fcc111Pt147_Ih/1345/', 'To_Thomas/fcc110Pt76_DPC/1345/', 'To_Thomas/fcc100Pt55_Co/1345/', 'To_Thomas/fcc100Pt68_hdh_from431/1345/', 'To_Thomas/fcc100Pt147Co_rlx/1345/', 'To_Thomas/fcc111Pt55_Co/1345/', 'To_Thomas/fcc110Pt147_Ih/1345/', 'To_Thomas/fcc110Pt55_Co/1345/', 'To_Thomas/fcc100Pt147_Ih/1345/', 'To_Thomas/fcc100Pt85_IDh421/1345/'] 
Home = os.getcwd()
Iter = [Home+'/'+ x for x in iterable]

pool = mp.Pool(24)


pool.map(Run_Lodis, Iter)

pool.close()

pool.join()
EOF

python3 Execute.py >> Info.txt
