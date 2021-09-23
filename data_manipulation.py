import pandas as pd


def process_data_PBI(files):
    # This function reads the csv file, and sets up the data to being manipulating the data

    """Strategies.csv
        Factors.csv
        SR.csv
        SP.csv
        StR.csv
        RS.csv
        PD.csv
        IG.csv
        HY.csv
        Baseline.csv
        """

    result_files = []
    for file in files:
        file = date_format(file)
        column_names_format(file)

    ig = pd.read_csv('C:/Users/sooky/Documents/Data/IG_7-1.csv')
    hy = pd.read_csv('C:/Users/sooky/Documents/Data/HY_7-1.csv')

    ig = universe(ig, 'Investment Grade')
    hy = universe(hy, 'High Yield')

    combine = ig.append(hy)
    ig['ID'] = ig['Cusip'].astpe(str) + '_IG_' + ig['Date'].astype(str)
    hy['ID'] = hy['Cusip'].astpe(str) + '_HY_' + hy['Date'].astype(str)

    ig_factor = benchmark_factor(ig)
    hy_factor = benchmark_factor(hy)

    ig_metric = benchmark_metric(ig)
    hy_metric = benchmark_metric(hy)

    combined_factor = hy_factor.append(ig_factor)
    combined_metric = hy_metric.append(ig_metric)

    result_files.append(combine)
    result_files.append(combined_factor)
    result_files.append(combined_metric)


def universe(data, uni_class):
    if uni_class == 'Investment Grade':
        data['universe'] = 'Investment Grade'
    else:
        data['universe'] = 'High Yield'

    return data


def date_format(data):
    # data has prd_formatted as an object
    data.rename(columns={'prd_formatted': 'Date'}, inplace=True)
    data.Date = []
    for x in data.Date:
        data.Date.append(pd.Timestamp(x))

    return data


def column_names_format(data):
    # Renames the columns for legibility

    data.columns = data.columns.str.replace('[_]', ' ', regex=True)
    data.columns = data.columns.str.replace('[_]', ' ', regex=True)

    return data


def returns(data):
    # Rename the factors
    columns = data.columns.values.tolist()
    for column in columns:
        if "Prev" in column:
            data.rename(columns={column: str(column) + ' Momentum'}, inplace=True)
    data.columns = data.columns.str.replace("Prev ", '')

    # column_names will contain the column names that are needed in the analysis
    column_names = ['Date', 'Cusip', 'Universe', '1M Total Return', '1M Excess Return']

    # For calculating tracking error in the dashboard

    data = pd.melt(data, id_vars=column_names, value_vars=['OAD', 'DTS', 'Market Value', '3M Total Return Momentum',
                                                           '6M Total Return Momentum', '12M Total Return Momentum',
                                                           'Total Return Volatility'], value_name="variable_value")
    return data


def benchmark_factor(data):
    columns = data.columns.values.tolist()

    for column in columns:
        if "Prev" in column:
            data.rename(columns={column: str(column) + 'Momentum'}, inplace=True)
    data.columns = data.columns.str.replace("Prev ", '')

    # column_names will contain the column names that are needed in the analysis
    column_names = ['Date', 'Cusip', 'Universe', 'Id']

    data.drop(['Hybrid Momentum'], axis=1)
    data['Hybrid Momentum'] = data[['3M Total Return Momentum', '6M Total Return Momentum',
                                    '12M Total Return Momentum']].mean(axis=1)

    # Unpivot the data with the factors chosen in values_vars
    data = pd.melt(data, id_vars=column_names, value_vars=['OAD', 'Total Return Volatility', 'Market Value',
                                                           '3M Total Return Momentum', '6M Total Return Momentum',
                                                           '12M Total Return Momentum'], value_name="variable_value")
    data.dropna(subset=["variable_value"], inplace=True)

    return data


def benchmark_metric(data):
    return_type = []

    columns = data.columns.values.tolist()

    # Renaming the return types
    for column in columns:
        if (not "Momentum" in column) and ("M Total Return" in column):
            if len(column) == 3:
                return_type.append(column.upper())
            else:
                return_type.append(column)

    # column_names will contain the column names that are needed in the analysis
    column_names = ['Date', 'Cusip', 'Universe', 'Id', 'Market Value', 'Total Return Mtd']

    # Unpivot the data with the return types chosen in values_vars
    data = pd.melt(data, id_vars=column_names, value_vars=return_type, var_name="metric", value_name="metric_value")

    return data


def average(data):
    columns = data.columns.values.tolist()

    # Define the variables for calculating the averages
    avg = ['Amount Outstanding', 'OAD', 'Market Value', 'DTS', '3M Total Return Momentum',
           '6M Total Return Momentum', '12M Total Return Momentum']
    column_names = ['Date', 'Cusip', 'Universe']

    add_factors = []
    for column in columns:
        if "Prev" in column:
            data.rename(columns={column: str(column) + 'Momentum'}, inplace=True)
            if "Excess" not in column:
                add_factors.append(str(column) + 'Momentum')

    add_factors.append('OAD')
    add_factors.append('DTS')
    add_factors.append('Market Value')

    # Make a copy of columns to use as other factors for analysis
    for value in add_factors:
        data[str(value) + '/'] = data[value]

    # For readability, remove the word 'Prev'
    data.columns = data.columns.str.replace("Prev ", '')

    for each in avg:
        if (each != 'OAD') and (each != 'DTS') and (each != 'Market Value') and (not "Total Return Momentum" in each):
            column_names.append(each)

        else:
            name = str(each) + '/'
            column_names.append(name)

    data = pd.melt(data, id_vars=column_names, value_vars=['OAD', 'Total Return Volatility', 'Market Value',
                                                           '3M Total Return Momentum', '6M Total Return Momentum',
                                                           '12M Total Return Momentum'], value_name="variable_value")

    data.columns = data.columns.str.replace('[/]', '', regex=True)
    data.dropna(subset=["variable_value"], inplace=True)

    return data
