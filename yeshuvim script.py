import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def invert(string):
    """
    A function which invert a string.
    Parameters
    ----------
    string : string
        the string to invert.

    Returns
    -------
    string
        An inverted string.

    Required libraries
    ------------------
    None.
    """
    return string[::-1]

#Defining the analysis period.
period = {'start': 2004,
          'end' : 2018}

#Insert the folder address here.
base_address = r''

#Importing the data.
yeshuvim = pd.read_csv(base_address + '\yeshuvim.csv')
prices = pd.read_csv(base_address + '\ppi and cpi.csv', index_col = 'Year')
cities = pd.read_csv(base_address + '\cities.csv')

#Calculating Wage per Capita, Working Population and Wage per Working Population.
results = pd.DataFrame()
cities.replace(['..', '#VALUE!'], np.nan, inplace = True)
cities.dropna(inplace = True)
cities['Average Wage'] = cities['Average Wage'].astype(float)
cities['Number of Employees'] = cities['Number of Employees'].astype(int)
cities['Wage per Capita'] = cities['Average Wage'] * cities['Number of Employees'] / (cities['Population'] * 1000)
cities['Working Pop'] = cities['Population'] * (1 - (cities['65+ percentage'] + cities['0-17 percentage']) / 100) * 1000
cities['Wage per Working Pop'] = cities['Average Wage'] * cities['Number of Employees'] / cities['Working Pop']

#Choosing the price indexת PPI or CPI.
price_index = 'PPI'

#Dividing the analysis population into the relevant groups.
analysis = dict(haredim = cities[cities['City'].isin(yeshuvim['Haredi'])],
                meorav = cities[cities['City'].isin(yeshuvim['Meorav'])],
                not_haredi = cities[cities['City'].isin(yeshuvim['Rest'])],
                arabs = cities[cities['City'].isin(yeshuvim['Arabs'])],
                israel = cities)

#Calculating Average Wage, Real Average Wage, Wage per Capita, Real Wage per Capita, and indicies for both in each group of the population.
for year in np.arange(period['start'], period['end'] + 1):
    for migzar in analysis.keys():
        results.loc[year, migzar + ' Average Wage'] = np.average(analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Average Wage'], weights = analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Population'])       
        results.loc[year, migzar + ' Real Average Wage'] = results.loc[year, migzar + ' Average Wage'] / prices.loc[year, price_index] * 100
        results.loc[year, migzar + ' Real Average Wage Index'] = results.loc[year, migzar + ' Real Average Wage'] / results.loc[period['start'], migzar + ' Real Average Wage'] * 100
        results.loc[year, migzar + ' Average Wage per Capita'] = np.average(analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Wage per Capita'], weights = analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Population'])       
        results.loc[year, migzar + ' Real Average Wage per Capita'] = results.loc[year, migzar + ' Average Wage per Capita'] / prices.loc[year, price_index] * 100
        results.loc[year, migzar + ' Real Average Wage per Capita Index'] = results.loc[year, migzar + ' Real Average Wage per Capita'] / results.loc[period['start'], migzar + ' Real Average Wage per Capita'] * 100
        results.loc[year, migzar + ' Number of Employees / Working Pop'] = np.average(analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Number of Employees'] / (analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Working Pop']), weights = analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Population'])
        results.loc[year, migzar + ' Average Wage per Working Pop'] = np.average(analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Wage per Working Pop'], weights = analysis[migzar].loc[analysis[migzar]['Year'] == year, 'Population'])       
        results.loc[year, migzar + ' Real Wage per Working Pop'] = results.loc[year, migzar + ' Average Wage per Working Pop'] / prices.loc[year, price_index] * 100


#Creating a function to draw the plot.
def plot_graph(item, index = False):
    
    yticks = list(np.arange(0, int(results['not_haredi' + item].max()) + 1000, step = 1000))
    ylabels = [f'{label:,}' for label in yticks]
    labels = [invert('ישובים חרדיים'),
              invert('ישובים מעורבים חרדיים ולא-חרדיים'),
              invert('ישובים יהודיים לא-חרדיים'),
              invert('יישובים ערביים'),
              invert('ישראל')]
    
    colors = ['tab:blue',
              'tab:orange',
              'tab:green',
              'tab:red',
              'tab:purple']
    
    plt.figure(figsize = (10,5), dpi = 500)
    x = results.index
    
    for migzar, label, color in zip(list(analysis.keys()), labels, colors):
        y = results[migzar + item]
        plt.plot(x, y, label = label, color = color)
        if index:
            plt.annotate(invert('באחוזים: הגידול המצטבר משנת הבסיס'), (period['start'] + 8, results['not_haredi' + item].max() / 8), bbox = dict(boxstyle = 'round', fc = 'w'))
            if migzar == 'arabs':
                plt.annotate('+' + str(int(np.round(results.loc[period['end'], migzar + index] - 100, 0))) + '%', (period['end'] - 0.4, results.loc[period['end'], migzar + item] + 200), color = color)
            else:
                plt.annotate('+' + str(int(np.round(results.loc[period['end'], migzar + index] - 100, 0))) + '%', (period['end'] - 0.4, results.loc[period['end'], migzar + item] - 250), color = color)
    
    graph = dict(start = invert(str(period['start'])),
                  end = invert(str(period['end'])))
    
    graph_period = graph['end'] + '-' + graph['start']

    plt.title(invert('שכר ריאלי לנפש בישראל ובערים שונות, ' + graph_period), fontsize = 15)
    if price_index == 'CPI':
        plt.ylabel(invert('שכר לנפש לחודש במחירי 0202'), fontsize = 12)
    else:
        plt.ylabel(invert('שכר לנפש לחודש במחירי 5102'), fontsize = 12)
    plt.xlabel(invert('שנה'), fontsize = 12)
    plt.xticks(np.arange(period['start'] , period['end'] + 1))
    plt.yticks(yticks, ylabels)
    
    plt.text(period['start'] - 1, - results['not_haredi' + item].max() / 5,invert('מקור: חישובים לפי קבצי הרשויות המקומיות של הלמ"ס 9102-2002'))
    plt.text(period['end'], - results['not_haredi' + item].max() / 5, '@tom_sadeh')     
    plt.legend()

#Plotting.

#Plotting.
plot_graph(' Real Average Wage per Capita', index = ' Real Average Wage per Capita Index')

