'''
Jacob Kulik
DATA Initiative Lab
'''
import matplotlib.pyplot as plt
import pandas as pd  
import numpy as np  
from scipy.stats import pearsonr

LAB_FILE = "lab_assignment.csv"
STOCK_FILE = "Jacob_Kulik_data_wrangling.csv"

def read_csv(lab, stock):
    '''
    Function will read in our csv files
    
    Function will take 2 infiles

    Function will return 2 dataframes
    '''
    
    # Creates dataframes with the data from the files
    df = pd.read_csv(lab)
    df2 = pd.read_csv(stock)
    
    return df, df2

def unique_companies(df):
    '''
    Function will return the unique tickers in our df, so we can use crsp to
    export stock info for these companies
    
    Function will take a df
    
    Function will print a list of tickers that is easy to copy into crsp
    '''
    companies = df['TICKER'].unique()
    companies_str = str(companies)
    
    # I used this function to paste the companies into CRSP
    print(companies_str.replace("'", ""))
    
def add_year(df):
    '''
    Function will add a year column to the df
    
    Function will take a df
    
    Function will return the updated df
    '''
    df['YEAR'] = np.nan
    
    # One df uses the YYYYMMDD format while the other doesn't,
    # so I want to bring them in the same YYYY style
    for i in range(0, df.shape[0]):
        long_date = df.loc[i, 'date']
        year = int(long_date/10000)
        df.loc[i, 'YEAR'] = year

def stock_dict(stock):
    '''
    Function will create a dictionary for every year in every stock in the data
    
    Function will take a df
    
    Function will return a dictionary
    '''
    stock_dict = {}
    for i in range(0, stock.shape[0]):
        cur_ticker = stock.loc[i, 'TICKER']
        cur_year = stock.loc[i, 'YEAR']
        cur_prc = stock.loc[i, 'PRC']
        # Creates a new key in the main dictionary if the stock hasn't already
        # been added
        if cur_ticker not in stock_dict:
            stock_dict[cur_ticker] = {}
            
        # Creates a new year key in the sub dictionary
        if cur_year not in stock_dict[cur_ticker]:
            stock_dict[cur_ticker][cur_year] = []
            
        # Adds the stock price to the right location
        stock_dict[cur_ticker][cur_year].append(cur_prc)
    
    return stock_dict
        
     
def merge_stock(lab, stock_dict):
    '''
    Function will use the dictionary to add a column to the lab dataframe
    
    Function will take a df and a dictionary
    
    Function will return the updated df
    '''
    lab['PRC'] = np.nan
    for i in range(0,lab.shape[0]):
        cur_ticker = lab.loc[i, 'TICKER']
        cur_year = lab.loc[i, 'YEAR']
        # Some companies were not public for a certain year so I must only
        # Use public current tickers for the current year
        if (cur_ticker in stock_dict) and (cur_year in stock_dict[cur_ticker]):
            cur_prc = stock_dict[cur_ticker][cur_year][-1]
            #print(cur_prc)
            lab.loc[i, 'PRC'] = cur_prc

def salary_prc_dict(lab):
    '''
    Function creates a dictionary with salaries and share prices for multiple tickers
    
    Function takes a df
    
    Function returns a dictionary
    '''
    plot_dict = {}
    for i in range(0, lab.shape[0]):
        cur_ticker = lab.loc[i, 'TICKER']
        cur_income = lab.loc[i, 'TDC1']
        cur_salary = lab.loc[i, 'SALARY']
        cur_prc = lab.loc[i, 'PRC']
        
        if cur_income > 0:
            cur_income = cur_income
        else:
            # When the compensation doesn't exist in the provided spreadsheet,
            # The salary will be used
            cur_income = cur_salary
        
        # This gets rid of any nan values because nan>0 returns false
        if cur_prc > 0:
            salary_prc = [cur_income, cur_prc]
            
            # Creates a new key in the main dictionary if the stock hasn't already
            # been added
            if cur_ticker not in plot_dict:
                plot_dict[cur_ticker] = []
    
            plot_dict[cur_ticker].append(salary_prc)
        
    return plot_dict

def average(list):
    '''
    Function will take the average of a list
    
    Function will take a list
    
    Function will return an float
    '''
    return sum(list)/len(list)

def average_dict(ticker_dict):
    '''
    Function will take the average salary for one share price across multiple executives
    
    Function will take a dictionary
    
    Function will return a dictionary with the averages as values  
    '''
    average_dict = []
    
    
    cur_coord = ticker_dict[0]
    # Keeping track of the stock price
    cur_y = cur_coord[1]
    cur_salaries = []
    for coord in ticker_dict:
        if coord[1] == cur_y:
            cur_salaries.append(coord[0])
            
        else:
            # Taking the average once we have all salaries for one time period
            updated_salary_prc = [average(cur_salaries), cur_y]
            
            average_dict.append(updated_salary_prc)

            cur_salaries = [coord[0]]
            # Updating the stock price in order to start again
            cur_y = coord[1]
            
    # I must copy this code one more time as the final stock price won't get
    # added otherwise
    updated_salary_prc = [average(cur_salaries), cur_y]
    average_dict.append(updated_salary_prc)
    return average_dict

def average_graph_dict(plot_dict):
    '''
    Function will graph the share price against average executive income for the companies
    
    Function will take a dictionary
    
    Function will return a list of correlations and create many plots
    '''
    correlations = []
    for ticker in plot_dict:
        plt.figure(figsize= (12,8))
        
        average_stock = average_dict(plot_dict[ticker])
        
        x_val = []
        y_val = []
        # Separates the information for each ticker into a list of x's and y's
        for pair in average_stock:
            # For ease of viewing, pairs used to be (salary, prc) but 
            # stock price is the independent variable so I must switch their spots
            y_val.append(pair[0])
            x_val.append(pair[1])
            
        plt.scatter(x_val, y_val)
        
        # Pearson's correlation function
        if len(x_val) > 1 and len(y_val) > 1:
            # Required x and y values of at least 2
            corr, _ = pearsonr(x_val, y_val)
            correlations.append(corr)
        else:
            # Not appending the manually set correlation
            corr = 0.0
        
        # Turning the x and y vals into arrays to plot the line of best fit
        x = np.array(x_val)
        y = np.array(y_val)
        # Least squares polynomial
        m, b = np.polyfit(x, y, 1)
        
        plt.plot(x, m*x + b, "-", color = "Red", label = "Line of Best Fit")
        
        # Basic graphing information
        fig_title = "'" + ticker + "' Share Price vs. Average Executive Compensation"
        plt.title(fig_title)
        plt.legend()
        plt.xlabel('Share Price (Dollars) \n Pearsons correlation: %.3f' % corr)
        plt.ylabel("Average Executive Compensation (Thousands of Dollars)")
        fig_name = ticker + "_StockPrice_to_AverageExecCompensation.png"
        # Uncomment line 237 if you want to save the graphs as pngs
        #plt.savefig(fig_name)
        plt.show()
        
    return correlations

def plot_c(corrs):
    '''
    Function will plot the breakdown of pearson's correlations
    
    Function will take a list
    
    Function will return nothing, but make a plot    
    '''
    correlations = [0,0,0,0,0,0,0,0,0,0]
    correlation_names = ["Negative, Very Strong", "Negative, Strong", 
                         "Negative, Moderate", "Negative, Weak",
                         "Negative, Very Weak", "Positive, Very Weak",
                         "Positive, Weak", "Positive, Moderate",
                         "Positive, Strong", "Positive, Very Strong"]
    
    # Breakdown based on different correlation values
    for corr in corrs:
        if corr >= 0.8:
            correlations[9] += 1
        elif corr >= 0.6:
            correlations[8] += 1
        elif corr >= 0.4:
            correlations[7] += 1
        elif corr >= 0.2:
            correlations[6] += 1
        elif corr > 0:
            correlations[5] += 1
        elif corr >= -0.2:
            correlations[4] += 1
        elif corr >= -0.4:
            correlations[3] += 1
        elif corr >= -0.6:
            correlations[2] += 1
        elif corr >= -0.8:
            correlations[1] += 1
        else:
            correlations[0] += 1
    
    # Basic graphing information
    plt.figure(figsize = (14,10))
    plt.bar(correlation_names, correlations)
    plt.xlabel("Correlation Strength")
    plt.xticks(fontsize = 8, rotation = 30)
    plt.ylabel("Frequency")
    plt.title("Correlation Breakdown of Share Price to Executive Compensation")
    plt.savefig("_CorrelationFrequency.png")
    

if __name__ == '__main__':
    lab_data, stock_data = read_csv(LAB_FILE, STOCK_FILE)
    add_year(stock_data)
    stock_dict = stock_dict(stock_data)   
    merge_stock(lab_data, stock_dict)
    plot_dict = salary_prc_dict(lab_data)
    #correlations = average_graph_dict(plot_dict)
    #plot_c(correlations)    