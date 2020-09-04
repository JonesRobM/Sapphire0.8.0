from Graphing import Reader, Plot_Funcs


#The system dictionary directs the Plotter module to find the completed simulations
#and then creates (if it does not exist) an image directory for plotted figures.

System = {
        'base_dir' : '/path/to/independent/trajectories/',
        'iter_dir' : ['Iter1', 'Iter2', 'Iter3', 'Iter4'],
        'plot_dir' : 'Images',
        'meta_name' : 'Metadata.csv',
        'save_meta' : True, 'save_errors' : True
        }

#These are the quantities which the user would like to be plotted. There will be
#a set name to call a given plotter and the arguments for that function can be 
#passed to the dictionary entry.

#One many find a list of supported plotters and their arguments in the documentation.


Quantities = { 
               'agcn_heat' : 
                      {'Name' : 'agcn_Heat.png'},
                      
               'prdf_plot' : 
                       {'Names' : ['pdf', 'rdf'], 'Frames' : range(0,2000,50), 'He' : True, 'Ho' : ['Au', 'Pt']},
                       
               'plot_stats' : 
                       {'Stats' : ['Kullback', 'JSD'], 'Quants' : ['pdf', 'rdf'], 'Temp' : False},
                       
               'com_plot_bi' : 
                       {'Dists' : ['CoMDist', 'MidCoMDist'], 'Species' : ['Au', 'Pt'], 'Frames' : range(0,2000,50)},
                       
               'cna_plot' : 
                       { 'Frames' : range(0,2000,50)},
                       
               'agcn_histo' : 
                       {'Frames' : range(0,2000,50)},
                       
               'com_full_plot' : 
                       {'Frames' : range(0,2000,50)},
                       
               'cum_com' : 
                       {'Frames' : range(0,2000,500)},
                       
               'cna_traj' :    
                       {'Sigs' : [(4,2,2), (4,2,1), (1,0,0), (2,0,0), (5,5,5), (3,1,1)]},
                'h_c' : None
        }

Pipeline = Reader.Read_Meta(System)
Metadata, Errors = Pipeline.Average()

Figures = Plot_Funcs.Plot_Funcs(Metadata, Errors, Quantities, System)
Figures.Make_Plots()
