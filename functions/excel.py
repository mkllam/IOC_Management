import pandas as pd

# Function to read an excel file and save the data as a list
def read_excel_to_list(file_path):
    df = pd.read_excel(file_path)
    
    # Convert the dataframe to a list of dictionaries
    data_list = df.to_dict(orient='records')
    
    return data_list

def write_list_to_excel(data_list):
    # Convert the list of dictionaries to dataframe
    df = pd.DataFrame(data_list)

    #Write to Excel
    df.to_excel('output/outputfile.xlsx', index=False)
