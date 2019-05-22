import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


# Build a dataframe with 4 connections

df = pd.DataFrame({'from': ['hmi',
                            'switch1', 'switch1', 'switch1',
                            'switch2', 'switch2', 'switch2',
                            'switch3', 'switch3', 'switch3',
                            'switch4', 'switch4', 'switch4'
                            ],
                   'to':['switch1',
                         'switch2', 'switch3', 'switch4',
                         'h1', 'h2', 'h3',
                         'h4', 'h5', 'h6',
                         'h7', 'h8', 'h9'
                         ]})

lst = 4*['yellow'] + 10*['green']
lst_size = 4*[2500] + 10*[1000]
carac = pd.DataFrame({'ID': ['switch1', 'switch2', 'switch3', 'switch4',
                             'hmi', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9'
                             ],
                      'myvalue': lst,
                      'size': lst_size
                      })

G = nx.from_pandas_edgelist(df, 'from', 'to')

carac= carac.set_index('ID')
carac=carac.reindex(G.nodes())



# Plot it
nx.draw(G, with_labels=True, node_color=carac['myvalue'], node_size=carac['size'])

plt.show()
