import streamlit as st
import plotly.express as px
import pandas as pd
import json
import re


# def read_data_from_csv(file_path) -> pd.DataFrame:
#     """
#     Reads data from a CSV file and returns it as a pandas DataFrame.

#     :param file_path: The path to the CSV file.
#     :return: A pandas DataFrame containing the data from the CSV file.
#     """

#     # Read data from the CSV file
#     df = pd.read_csv(file_path)

#     # Clean column names: capitalize first letter and replace underscores with spaces
#     df.columns =  df.columns.str.title()
#     df.columns = df.columns.str.replace('_', ' ')
    
#     return df

def create_sidebar_param_area() -> None:
    """
    Creates a parameter area in the sidebar.

    :return: None
    """
    # Add a divider inside the sidebar
    st.sidebar.divider()

    # Add subheader for the Parameters
    st.sidebar.subheader("Parameters:")


def create_app_type_param(df, param_col_name, w_key="app_type") -> None:
    """
    Creates a select box in the sidebar for choosing an application borrower type.

    :param df: The input DataFrame containing the data.
    :param param_col_name: The name of the column containing application borrower types.
    :param w_key: The key for the select box (optional).
    :return: None
    """

    # Get unique application borrower types
    app_types = df[param_col_name].unique()

    st.sidebar.subheader("Parameters:")

    # Create a select box in the sidebar for Application Type
    selected_product_type = st.sidebar.selectbox(
        'Application Borrower Type',
        app_types,
        placeholder="Select application borrower type...",
        key=w_key,
    )

    return selected_product_type

def page_logo_and_title(title, subheader=None, byline=None):
    """
    Displays a logo image and a title in the streamlit app.

    Args:
        title: The title to display.
        subheader: The subheader to display.
        byline: The byline to display.

    Returns: 
        placeholder: Streamlit empty widget with contents
    """

    placeholder = st.empty()

    # Create two columns for the layout
    _c1, _c2= placeholder.columns([2, 1])

    # Display logo
    # with _c2:
    #     st.image("logo.png")

    # Display Title
    with _c1:
        st.header(title)
            #st.markdown("###### "+ subheader, unsafe_allow_html=True)
    
    if subheader!=None:
        st.subheader(subheader)

    if byline!=None:
        st.write('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
        #st.caption(subheader)
        
    # Display a rainbow divider
    #st.header("", divider="rainbow")

    return placeholder


def replace_na_cols(df, col_list) -> pd.DataFrame:
    """
    Replaces missing (NaN) values in specified columns of a DataFrame with zeros.

    :param df: The input DataFrame.
    :param col_list: List of column names to process.
    :return: A DataFrame with missing values replaced by zeros.
    """

    # Replace NaN values with zeros for all columns
    for col in col_list:
        df[col].fillna(value=0, inplace=True)

    return df

def create_multiselect_all_param(w_label, lov, ph_text, w_key):
    """
    Creates a multiselect widget in the Streamlit app sidebar.

    :param w_label: The label for the multiselect widget.
    :param lov: List of values to choose from.
    :param ph_text: Placeholder text for the multiselect widget.
    :param w_key: The key for the widget (optional).
    :return: A list of selected values.
    """

    # Add 'All' option to the list of values
    lov_all = ['All']+lov

    # Add 'All' option to the list of values
    selected_lovs = st.multiselect(
                            w_label,
                            lov_all,
                            placeholder=ph_text,
                            help = "You can choose multiple values for this parameter",
                            key=w_key,
                            default="All"
                        )
    
    # If 'All' is selected, return all values; otherwise, return the selected values
    if 'All' in selected_lovs:
        selected_lovs = lov
    
    return selected_lovs

def load_data_from_snowflake(
    table_name: str,
    configs: dict,
    sf_db: str = 'ANALYTICS_DB_PRD',
):
    """Run and save query as view to snowflake

    Args:
        table_name (str): Snowflake absolute table name
        configs (dict): Snowflake connection configs
    """

    # Append db to the table name
    table_name = sf_db+'.'+table_name

    # Create a query
    query = "SELECT * FROM "+table_name

    with Session.builder.configs(configs).create() as session:
        df = session.sql(query)
        # Convert date to timestamp
        df = df.select(
            *[
                col(c).cast("timestamp").alias(c) if t == "date" else col(c)
                for c, t in df.dtypes
            ]
        )

        # Convert Snowflake dataframe to pandas dataframe
        df = df.to_pandas()

        # Convert column names to title case and replace underscores with spaces
        df.columns =  df.columns.str.title()
        df.columns = df.columns.str.replace('_', ' ')

        return df


@st.cache_data(ttl="1d", show_spinner=":red[Loading Application Configuration]")
def loadconfig(use_db = False):
    """
    Load the application config from either a json file or the SF database.

    Parameters:
    use_db (bool): Use a local json file named "params.json" or load from the SF database.

    Returns:
    dict: The loaded config as a dictionary, or None if there was an error.
    """

    try:
        if use_db:
            # will add db loader here
            pass
        else:
            with open("params.json", 'r') as file:
                data = json.load(file)
                return data
            
    except FileNotFoundError:
        print(f"Error: The file params.json was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file params.json contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def flatten_dict_arrays(dict_array):
    result = []
    for dict_obj in dict_array:
        new_dict = {}
        for key, value in dict_obj.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    new_dict[f"{key}_{i}"] = item
            else:
                new_dict[key] = value
        result.append(new_dict)
    return result

def sort_deciles_and_vintiles(string_list):
    """
    Sorts a list of strings based on the leading digits before the first comma.

    Parameters:
    string_list (list): The list of strings to be sorted.

    Returns:
    list: A sorted list of strings based on the leading digits.
    """
    return sorted(string_list, key=lambda x: int(x.split(',')[0]))

def sort_dataframe_by_decile_and_quarter(df, decile_column, quarter_column):
    """
    Sorts a DataFrame by the specified decile/ventile column and quarter column.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be sorted.
    - decile_column (str): The name of the column containing decile or ventile strings.
    - quarter_column (str): The name of the column containing quarter information.

    Returns:
    - pd.DataFrame: The sorted DataFrame.
    """
    # Ensure the columns exist in the DataFrame
    if decile_column not in df.columns:
        raise ValueError(f"Column '{decile_column}' does not exist in the DataFrame.")
    if quarter_column not in df.columns:
        raise ValueError(f"Column '{quarter_column}' does not exist in the DataFrame.")

    # Sort the DataFrame by the leading digits in the decile/ventile column and then by the quarter column
    df = df.sort_values(
        by=[decile_column, quarter_column],
        key=lambda col: col.map(lambda v: int(v.split(',')[0]) if ',' in v else v)
    )

    return df

def filter_and_sort_dataframe(data, columns_to_filter=None):
    """
    Filters, formats, and optionally sorts a DataFrame based on the provided columns and formatting rules.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be processed.
    - columns_to_filter (list): The list of columns to keep in the DataFrame. If None, no filtering is done.
    Returns:
    - pd.DataFrame: The processed DataFrame.
    """
    # Filter the data based on columns_to_filter
    if columns_to_filter is not None:
        data = data[columns_to_filter].copy()
    
    # Format the columns (assumes that all "Rate" columns are percentages)
    for col in data.columns:
        if "Rate" in col:
            data[col] = data[col].astype(str) + "%"

    return data

def format_filter_and_relabel_dataframe(df, formatting_dict):
    """
    Formats, filters, and relabels a DataFrame based on the provided formatting dictionary.

    Parameters:
    df (pd.DataFrame): The DataFrame to format, filter, and relabel.
    formatting_dict (dict): A dictionary mapping column names to formatting options and new column labels.

    The formatting_dict should have the following structure:
    {
        'original_column_name': {
            'format': 'desired_format',  # Optional formatting string, e.g., '{:,.2f}'
            'label': 'new_column_label'  # Optional new column label
        },
        ...
    }

    Returns:
    pd.DataFrame: A new DataFrame with the applied formatting, filtering, and relabeling.
    """
    # Filter the DataFrame to include only the columns specified in the formatting_dict
    filtered_df = df[list(formatting_dict.keys())].copy()

    # Apply formatting and relabeling based on the formatting_dict
    for col, options in formatting_dict.items():
        if 'format' in options:
            filtered_df[col] = filtered_df[col].map(options['format'].format)
        
        if 'label' in options:
            filtered_df.rename(columns={col: options['label']}, inplace=True)

    return filtered_df

def show_selected_points(event, data_formatting_dict=None):

    st.write("Click a point to select and display, hold down the shift key and click to select multiple points whilst holding the shift key.")
    
    selected_points = event.selection.get("points", [])
    if len(selected_points) > 0:
        clean_selected_points = flatten_dict_arrays(selected_points)
        dfp = pd.DataFrame.from_records(clean_selected_points)
        if data_formatting_dict:
            dfp = format_filter_and_relabel_dataframe(dfp, data_formatting_dict)

        st.dataframe(dfp,hide_index=True)


def interactive_plotly(fig, key, container=None,use_container_width=True, on_select="rerun", config={'displayModeBar': False}, data_formatting_dict=None):
    

    event = st.plotly_chart(fig,container=container, config=config,theme="streamlit", use_container_width=use_container_width, on_select=on_select,key=key)
    show_selected_points(event, data_formatting_dict)



def interactive_plotly_decor(func):
    def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            show_selected_points(result)
    return wrapper

# def interactive_plotly(container=None):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             if container:
#                 with container:
#             else:
#             result = func(*args, **kwargs)
#             return result
#         return wrapper
#     return decorator


def sort_roll_rates(strings):
    """
    Sort a list of roll rate strings based on the first numerical value found in each string.

    Args:
        strings (list of str): The list of roll rate strings to be sorted.

    Returns:
        list of str: The sorted list of roll rate strings.
    """

    def extract_first_number(string):
        # Extract all numbers in the string
        numbers = re.findall(r'\d+', string)
        # Return the first number as an integer if found, otherwise return a large number to push it to the end
        return int(numbers[0]) if numbers else float('inf')

    # Sort the list using the custom key
    return sorted(strings, key=extract_first_number)

def sort_deciles_and_vintiles(string_list):
    """
    Sorts a list of strings based on the leading digits before the first comma.

    Parameters:
    string_list (list): The list of strings to be sorted.

    Returns:
    list: A sorted list of strings based on the leading digits.
    """
    return sorted(string_list, key=lambda x: int(x.split(', ')[0]))

def sort_df_by_quarter_decile(df, qtr_column, dec_column):
    """
    Sorts the DataFrame by 'quarter' and 'decile' columns in descending order.

    Parameters:
    df (pd.DataFrame): The DataFrame to sort, which must have 'quarter' and 'decile' columns.

    Returns:
    pd.DataFrame: A new DataFrame sorted by 'quarter' and 'decile'.
    """
    
    # Function to extract numeric decile for sorting
    def extract_numeric_decile(decile):
        return int(decile.split(',')[0])

    # Create a copy of the DataFrame to avoid modifying the original
    df_sorted = df.copy()

    # Add a new column with extracted numeric decile for sorting purposes
    df_sorted['numeric_decile'] = df_sorted[dec_column].apply(extract_numeric_decile)

    # Sort the DataFrame by quarter and numeric_decile in descending order
    df_sorted = df_sorted.sort_values(by=[qtr_column, 'numeric_decile'], ascending=[False, True])

    # Drop the numeric_decile column after sorting
    df_sorted.drop(columns='numeric_decile', inplace=True)

    return df_sorted

def sort_year_quarters(strings):
    """
    Sort a list of year and quarter strings in the format 'YYYY Qx'.

    Args:
        strings (list of str): The list of year and quarter strings to be sorted.

    Returns:
        list of str: The sorted list of year and quarter strings.
    """

    def extract_year_quarter(value):
        # Split the string into year and quarter parts
        year, quarter = value.split()
        # Return a tuple of year and quarter number for sorting
        return (int(year), int(quarter[1]))

    # Sort the list using the custom key
    return sorted(strings, key=extract_year_quarter)