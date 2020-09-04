from Post_Process import ProcessV2
import pickle
import time
import multiprocessing as mp

def collect_result(result):
    global results
    results.append(result)

Supported=[
        'rdf', 'cna', 'adj', 'pdf', 'pdfhomo', 'agcn', 'nn', 'MoI',
        'SimTime', 'EPot', 'ETot', 'EKin', 'EDelta', 'MeanETot', 'Temp'
           ]

System = {
        'base_dir' : '/media/k1899676/Seagate/PhD/20/June/CMD/AuPt/Au891Pt309/NVT/1000/Sim-1345/',
        'movie_file_name' : 'movie.xyz',
        'energy_file_name' : 'energy.out',
        #'Path_to_Pot' : '/path/to/potential/file/file.pot',
        'New_agcn_movie' : True,
        
        'Homo' : ['Au', 'Pd'], 'HomoQuants' : [ 'HoPDF', 'HoRDF', 'CoM', 'HoAdj', 'CoMDist', 'MidCoMDist', 'Lind', 'euc'], 
        'Hetero' : True, 'HeteroQuants' : [ 'HePDF', 'HeRDF', 'HeAdj' ],
        
        'Start' : 0, 'End' : 200, 'Step' : 10, 'Skip' : 10, 'UniformPDF' : False, 'Band' : 0.05,
        
        'HCStats' : True,
        
        'SimTime': True, 'EPot': True, 'ETot' : True, 
        'EKin' : True, 'EDelta' : True, 'MeanETot' : True, 'Temp' : True
        }

Quantities = {
        'euc' : None, 'rdf' : None, 'pos' : None,  'CoMDist' : None, 'MoI' : None,
        'adj' : None, 'pdf' : None, 'agcn' : None, 'nn' : None, 'CoM' : None,
        'SimTime': None, 'EPot': None, 'ETot' : None, 'Lind' : None,
        'EKin' : None, 'EDelta' : None, 'MeanETot' : None, 'Temp' : None
        }

Analysis = {
    "JSD" : ["rdf", "pdf"],
    "Kullback" : ["rdf", "pdf"],
    "PStat" : ["rdf", "pdf"]
    }


Data = ProcessV2.Process(System, Quantities)
Data.Initialising()
Data.run_pdf()
Data.clean_pdf()
Data.run_core()
Data.clean_core()

Data.New_File()



Meta = Data.analyse(Analysis)

with open(System['base_dir']+"MetaTrial.csv", "wb") as file:
    pickle.dump(Data.metadata, file, protocol=pickle.HIGHEST_PROTOCOL)
