import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial.qhull import QhullError
import re
from datetime import datetime

def filename_to_seconds(filename):
    # Remove file extension
    filename = filename.removesuffix('.png')

    # Extract the date part from the filename (assuming the format is fixed)
    date_part = filename.split('-')[1]  # 'YYYY.MM.dd'
    time_part = filename.split('-')[2]  # 'hh.mm.ss.sss'
    
    # Combine into one string
    datetime_str = date_part + ' ' + time_part.replace('.', ':')
    datetime_obj = datetime.strptime(datetime_str, '%Y.%m.%d %H:%M:%S:%f')
    
    # Define the reference datetime (start of 2020)
    reference_datetime = datetime(2020, 1, 1)
    
    # Calculate the seconds since the start of 2020
    seconds_since_start = (datetime_obj - reference_datetime).total_seconds()
    return seconds_since_start

def compute_nearest_neighbors_distribution(df):
    # Extract points from the DataFrame
    points = df[['x', 'y']].values

    # Compute Delaunay triangulation
    try:
        tri = Delaunay(points)
        #tri = Delaunay(points)

        # Create a dictionary to hold the neighbors of each point
        #neighbors = {i for i in range(len(points))}
        neighbors = {i: set() for i in range(len(points))}

        # Iterate over the simplices (triangles) to find neighbors
        for simplex in tri.simplices:
            for i in simplex:
                neighbors[i].update(simplex)

        # Compute the distribution of the number of neighbors
        num_neighbors = [len(neighbors[i]) for i in range(len(points))]
        neighbor_distribution = np.bincount(num_neighbors)
    except QhullError as e:
        print(f"Error during Delaunay triangulation: {e}")
        neighbor_distribution = []
        # You can handle the error here, e.g., by returning a default value or skipping the operation

    return neighbor_distribution[1:]



def generate_plots_zip(final_points:list, plot_data01:list, plot_data02:list):
    """"
    Args:
        final_points (list): Each element is a tuple with the name of the image, x and y coordinates

    Return:
        (tuple): plot1, plot2
    
    Example:
        Structure of final_points list:
        [('save-2023.11.07-13.41.12.704.png', 173, 1), ('save-2023.11.07-13.41.12.704.png', 54, 1), .... ]
    
    """

    ################################################
    # First PLOT ZIP
    ################################################

    # Create the DataFrame from the list of tuples
    df = pd.DataFrame(final_points, columns=['filename', 'x', 'y'])
    df.sort_values('filename', inplace=True)
    #df['Time'] = pd.factorize(df['filename'])[0]
    df['Time'] = df['filename'].apply(filename_to_seconds)
    #df['Time'] = df['Time']-df['Time'].min()


    # Add a new column 'id' that assigns a unique integer to each filename
    df['color'] = pd.factorize(df['filename'])[0]
    df['color'] += 1
    
    # print(f"{df}")
    #points = [(x, y) for _, x, y in final_points]
    #x_values, y_values = zip(*points)
    counts = df['Time'].value_counts().reset_index()
    counts.columns = ["Time", "Number"]
    counts.sort_values('Time', inplace=True)
    # print(f"counts: {counts}")

    plot_zip01 = px.line(counts, x="Time", y="Number")
    plot_zip01.update_layout(
        xaxis_title="Time (seconds)",
        yaxis_title="Density of triangles per squared micron",
        title="Evolution in number of deposited triangles",
        font=dict(size=15),
        title_font_size=24
    )

    x_values = plot_zip01.data[0]['x']  
    y_values = plot_zip01.data[0]['y']  
    plot_data01.clear()
    plot_data01.extend(list(zip(x_values, y_values)))

    ################################################
    # Second PLOT ZIP
    ################################################
    # Define the vectors p61 and p62
    p61 = np.arange(0.1, 0.7, 0.01)
    p62 = np.arange(0.1, 1, 0.01)
    
    # Calculate the corresponding y values for the lines
    y1 = 1 / (2 * np.pi * p61**2)
    y2 = 1 - p62
    
    # Create a Plotly figure
    plot_zip02 = go.Figure()
    
    # Add first line plot
    #plot_zip02.add_trace(go.Scatter(x=p61, y=y1, mode='lines', name='y = 1/(2πp^2)',
                             #line=dict(width=4)))
    
    # Add second line plot
    #plot_zip02.add_trace(go.Scatter(x=p62, y=y2, mode='lines', name='y = 1-p',
                             #line=dict(dash='dash', width=4)))
    
    #return plot_zip01, plot_zip02
    # Add points for true data
    #print(f"{df['color'].unique()}")

    df['Order'] = ""    # Si no entra en el bucle no crea la columna

    for id_value in df['color'].unique():
        # Create a new DataFrame that only contains rows for the current id
        df_id = df[df['color'] == id_value]
    
        ## Call the function with the newly created DataFrame
        distribution = compute_nearest_neighbors_distribution(df_id)
        if len(distribution) == 0:
            mu2 = 1.0
            p6 = 0.5
            order = p6/mu2
        else:
            prob = distribution / np.sum(distribution)
            mean_nn = np.sum([(x+1)*prob[x] for x in range(len(prob))])
            mu2  = np.sum([(x+1-mean_nn)**2*prob[x] for x in range(len(distribution))])
            if len(prob)>=6:
                p6 = prob[5]
            else:
                p6 = 0
            if mu2 == 0:
                order = 0
            else: 
                order = p6/mu2
        df.loc[df['color'] == id_value, 'mu2'] = mu2
        df.loc[df['color'] == id_value, 'p6'] = p6
        #df.loc[df['color'] == id_value, 'Order'] = order

       # plot_zip02.add_trace(go.Scatter(x=np.array(p6), y=np.array(mu2), 
       #                          mode='markers', name='True Data', 
       #                          marker=dict(size=10)))
    #print(f"order: {df['Order'].unique()}") 
    #plot_zip02 = px.line(df, x="Time", y="Order")
    plot_zip02.add_trace(go.Scatter(x=df['Time'], y=df["mu2"], mode='lines', name='μ₂',
                             line=dict(width=4)))
    plot_zip02.add_trace(go.Scatter(x=df['Time'], y=df["p6"], mode='lines', name='p₆',
                             line=dict(width=4)))
    # Update layout for custom axis labels, title, and styles
    plot_zip02.update_layout(
        title="Evolution of order (based on Lemaitre's plot)",
        xaxis_title="Time",
        yaxis_title="Lemaitre's parameters: p₆/μ₂",
        #xaxis=dict(range=[0, df["Time"].max()], showgrid=True),
        #yaxis=dict(range=[0, .5], showgrid=True),
        font=dict(size=15),
        title_font_size=24
    )

    x_values = plot_zip02.data[0]['x']  
    y_values = plot_zip02.data[0]['y']  
    plot_data02.clear()
    #plot_data02.extend(list(zip(x_values, y_values)))
    plot_data02.extend(list(zip(df['Time'],df['mu2'],df['p6'])))
    
    return plot_zip01, plot_zip02

def generate_plots_image(final_points:list, plot_data01:list, plot_data02:list):
    """"
    Args:
        final_points (list): Each element is a tuple with the name of the image, x and y coordinates

    Return:
        (tuple): plot1, plot2
    
    Exmaple:
        Structure of final_points list:
        [('Image', 173, 1), ('Image', 54, 1), .... ]
    
    """

    ################################################
    # First PLOT
    ################################################

    # print(f"Final points: {final_points}")
    # Create the DataFrame from the list of tuples
    df = pd.DataFrame(final_points, columns=['filename', 'x', 'y'])

    # Add a new column 'id' that assigns a unique integer to each filename
    df['color'] = pd.factorize(df['filename'])[0]
    df['color'] += 1
    #df = pd.read_csv('assets/example_points.csv')

    distribution = compute_nearest_neighbors_distribution(df)

    plot_img01= px.bar(distribution, text_auto=True,
             title='Distribution of neighbors', labels={'number of neighbors': 'Count'})

    # Extraer los datos de la figura plot_img01
    x_values = plot_img01.data[0]['x']  # Esto representa las categorías o etiquetas en el eje x
    y_values = plot_img01.data[0]['y']  # Esto representa los valores en el eje y (la altura de las barras)

    plot_data01.clear()
    plot_data01.extend(list(zip(x_values, y_values)))
    
    # Updating the layout to hide the legend and add custom axis labels
    plot_img01.update_layout( 
                showlegend=False, 
                xaxis_title='Number of neighbors', 
                yaxis_title='Count',
                font=dict(size=15),
                title_font_size=24)

    ################################################
    # Second PLOT
    ################################################
    prob = distribution / np.sum(distribution)
    if len(prob)>=6:
        p6 = prob[5]
    else:
        p6 = 0
    mean_nn = np.sum([(x+1)*prob[x] for x in range(len(prob))])
    mu2  = np.sum([(x+1-mean_nn)**2*prob[x] for x in range(len(distribution))])

    print(f"p₆:{p6} μ₂:{mu2}")  # for debugging
    # Define auxiliary vectors p61 and p62
    p61 = np.arange(0.1, 0.7, 0.01)
    p62 = np.arange(0.1, 1, 0.01)
    
    # Calculate the corresponding y values for the lines
    y1 = 1 / (2 * np.pi * p61**2)
    y2 = 1 - p62
    
    # Create a Plotly figure
    plot_img02 = go.Figure()
    
    # Add first line plot
    plot_img02.add_trace(go.Scatter(x=p61, y=y1, mode='lines', name='y = 1/(2πp^2)',
                             line=dict(width=4)))
    
    # Add second line plot
    plot_img02.add_trace(go.Scatter(x=p62, y=y2, mode='lines', name='y = 1-p',
                             line=dict(dash='dash', width=4)))
    
    # Add points for true data
    plot_img02.add_trace(go.Scatter(x=np.array(p6), y=np.array(mu2), 
                             mode='markers', name='True Data', 
                             marker=dict(size=10)))
    
    # Extraer datos de cada serie
    serie_blue_x = plot_img02.data[0]['x']  # p61
    serie_blue_y = plot_img02.data[0]['y']  # y1

    serie_red_x = plot_img02.data[1]['x']  # p62
    serie_red_y = plot_img02.data[1]['y']  # y2

    serie_green_x = plot_img02.data[2]['x']  # p6 (convertido a np.array)
    serie_green_y = plot_img02.data[2]['y']  # mu2 (convertido a np.array)

    # Agregamos todos los valores en una lista de 3 elementos
    plot_data02.clear()
    plot_data02.append(list(zip(serie_blue_x, serie_blue_y)))
    plot_data02.append(list(zip(serie_red_x, serie_red_y)))
    plot_data02.append(list(zip(serie_green_x, serie_green_y)))

    # print("*"*10,"\n",plot_data02)
    
    print(f"p₆:{p6} μ₂:{mu2}")
    # Update layout for custom axis labels, title, and styles
    plot_img02.update_layout(
        title="Lemaitre's plot",
        xaxis_title="p₆",
        yaxis_title="μ₂",
        xaxis=dict(range=[0, 1], showgrid=True),
        yaxis=dict(range=[0, 15], showgrid=True),
        font=dict(size=15),
        title_font_size=24
    )

    return plot_img01, plot_img02


