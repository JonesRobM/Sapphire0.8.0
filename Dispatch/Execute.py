
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
