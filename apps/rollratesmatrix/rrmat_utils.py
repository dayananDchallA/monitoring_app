import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

import pandas as pd
import plotly.express as px
from pathlib import Path

from core.misc_utils import sort_year_quarters, create_multiselect_all_param

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_roll_rate_matrix(params):
    """
    Read roll rate matrix data from snowflake
    """
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

def rrmat_params_layout(df, params):
    """
    Function to create and display the parameters

    Args:
        df (pd.DataFrame): The input dataframe

    Returns:
        ds_orig_qtr (streamlit widget): Dev Sample Origination quarter selected
        pds_orig_qtr (streamlit widget): PostDev Sample Origination quarter selected
    """

    # Get the list of values for the parameters

    # Uncomment after implementing the logic for calculating pcts
    #switch_to_opts = ["Number of Applications #","Percentage %"]

    sample_col = params['sample_col']
    time_prd_col = params['time_prd_col']
    oq_col = params['oq_col']
    
    ds_orig_qtr_opts = list(df[df[sample_col]=="Dev Sample"][oq_col].unique())
    ds_orig_qtr_opts = sort_year_quarters(ds_orig_qtr_opts)

    pds_orig_qtr_opts = list(df[df[sample_col]=="Post-Dev Sample"][oq_col].unique())
    pds_orig_qtr_opts = sort_year_quarters(pds_orig_qtr_opts)
        
    time_period_opts = df[time_prd_col].sort_values().unique()

    
    # Create and display the parameters
    ds_orig_qtr = create_multiselect_all_param(w_label='Dev Sample Origination Quarter',
                                               lov=ds_orig_qtr_opts,
                                               ph_text="Select the Dev Sample Origination Quarter...",
                                               w_key="rrm_ds_oq"
                                               )
    
    pds_orig_qtr = create_multiselect_all_param(w_label='Post Dev Sample Origination Quarter',
                                               lov=pds_orig_qtr_opts,
                                               ph_text="Select the Post Dev Sample Origination Quarter...",
                                               w_key="rrm_pds_oq"
                                               )
            
    # time_period = st.sidebar.selectbox('Time Period', 
    #                 time_period_opts,
    #                 placeholder="Select the Time Period...",
    #                 key="rrm_tp")

    return ds_orig_qtr, pds_orig_qtr


def roll_rate_matrix(df, ds_orig_qtr, pds_orig_qtr, params) -> None:
    """
    This function generates roll rate matrices for the Dev Sample and Post-Dev Sample.
    
    Args:
        df (DataFrame): The input dataframe.
        ds_orig_qtr (list): List of quarters for the Dev Sample.
        pds_orig_qtr (list): List of quarters for the Post-Dev Sample.
    
    Returns:
        None
    """

    app_type = params['app_type']
    time_prd_col = params['time_prd_col']
    sample_col = params['sample_col']
    oq_col = params['oq_col']
    metric_val = params['metric_val']
    prev_arr_bucket = params['prev_arr_bucket']
    curr_arr_bucket = params['curr_arr_bucket']

    # Step 1: Filter data for the specified time period
    rr_mat_df = df[df[app_type] =="Consumer"]
    #rr_mat_df = rr_mat_df[rr_mat_df[time_prd_col]==st.session_state.rrm_tp]

    # Step 2: Separate data into Dev Sample and Post-Dev Sample subsets
    rr_mat_df_ds = rr_mat_df[rr_mat_df[sample_col]=="Dev Sample"]
    rr_mat_df_pds = rr_mat_df[rr_mat_df[sample_col]=="Post-Dev Sample"]

    # Step 3: Filter data based on specified quarters
    rr_mat_df_ds = rr_mat_df_ds[rr_mat_df_ds[oq_col].isin(ds_orig_qtr)]
    rr_mat_df_pds = rr_mat_df_pds[rr_mat_df_pds[oq_col].isin(pds_orig_qtr)]

    # Step 4: Convert metric_val column to integer type
    rr_mat_df_ds[metric_val] = rr_mat_df_ds[metric_val].astype("int")
    rr_mat_df_pds[metric_val] = rr_mat_df_pds[metric_val].astype("int") 

    # Step 5: Group data by previous and current arrears buckets to aggregate
    rr_mat_df_ds = rr_mat_df_ds.groupby([prev_arr_bucket,curr_arr_bucket]).agg({metric_val:sum}).reset_index()
    rr_mat_df_pds = rr_mat_df_pds.groupby([prev_arr_bucket,curr_arr_bucket]).agg({metric_val:sum}).reset_index()

    # Step 6: Create pivot tables for Dev Sample and Post-Dev Sample

    rr_mat_df_ds_num = pd.crosstab(index=rr_mat_df_ds[prev_arr_bucket],
                             columns=rr_mat_df_ds[curr_arr_bucket],
                             values=rr_mat_df_ds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             colnames=['Current Arrear Buckets'],
                             margins=False
                             )
    
    rr_mat_df_ds_perc = pd.crosstab(index=rr_mat_df_ds[prev_arr_bucket],
                             columns=rr_mat_df_ds[curr_arr_bucket],
                             values=rr_mat_df_ds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             margins=False,
                             normalize='index'
                             ).style.format('{:.2%}')
    
    rr_mat_df_pds_num = pd.crosstab(index=rr_mat_df_pds[prev_arr_bucket],
                             columns=rr_mat_df_pds[curr_arr_bucket],
                             values=rr_mat_df_pds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             colnames=['Current Arrear Buckets'],
                             margins=False
                             )
    
    rr_mat_df_pds_perc = pd.crosstab(index=rr_mat_df_pds[prev_arr_bucket],
                             columns=rr_mat_df_pds[curr_arr_bucket],
                             values=rr_mat_df_pds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             margins=False,
                             normalize='index'
                             ).style.format('{:.2%}')
    
    
    # Display results
    _c0,_c1 = st.columns(2)
    with _c0:
        st.markdown("##### Consumer Roll Rate Matrix(%) - Dev Sample")
        st.dataframe(rr_mat_df_ds_perc,use_container_width=True,height=270)

    with _c1:
        st.markdown("##### Consumer Roll Rate Matrix(%) - Post-Dev Sample")
        st.dataframe(rr_mat_df_pds_perc, use_container_width=True,height=270)

    st.markdown("#")
    _c2,_c3 = st.columns(2)
    with _c2:
        st.markdown("##### Consumer Roll Rate Matrix (# of Applications) - Dev Sample")
        st.dataframe(rr_mat_df_ds_num,use_container_width=True,height=270)

    with _c3:
        st.markdown("##### Consumer Roll Rate Matrix (# of Applications) - Post-Dev Sample")
        st.dataframe(rr_mat_df_pds_num, use_container_width=True,height=270)



def roll_rate_matrix_decile(df, ds_orig_qtr, pds_orig_qtr, params) -> None:
    """
    Generates roll rate matrices by decile for the Dev Sample and Post Dev Sample.

    Args:
        df (pd.DataFrame): The input dataframe.
        ds_orig_qtr (list): List of quarters for the Dev Sample.
        pds_orig_qtr (list): List of quarters for the Post Dev Sample.

    Returns:
        None
    """
    
    app_type = params['app_type']
    decile = params['decile']
    pred_score_dec = params['pred_score_dec']
    sample_col = params['sample_col']
    oq_col = params['oq_col']
    prev_arr_bucket = params['prev_arr_bucket']
    curr_arr_bucket = params['curr_arr_bucket']
    metric_val = params['metric_val']

    # Filter data based on app_type and time period
    rr_mat_dec_df = df[df[app_type] =="Consumer"]
    #rr_mat_dec_df = rr_mat_dec_df[rr_mat_dec_df[time_prd_col]==st.session_state.rrm_tp]

    # Get unique decile options
    decile_opts = list(rr_mat_dec_df.sort_values(decile)[pred_score_dec].unique())
                
    # Display parameter selection for deciles
    st.markdown("##### Parameters: ")
    deciles = create_multiselect_all_param(w_label='Deciles',
                                               lov=decile_opts,
                                               ph_text="Select the Deciles...",
                                               w_key="rrm_deciles"
                                               )

    st.divider()

    # Filter data based on selected deciles
    rr_mat_dec_df = rr_mat_dec_df[rr_mat_dec_df[pred_score_dec].isin(deciles)]
    
    # Separate data into Dev Sample and Post Dev Sample subsets
    rr_mat_dec_ds = rr_mat_dec_df[rr_mat_dec_df[sample_col]=="Dev Sample"]
    rr_mat_dec_pds = rr_mat_dec_df[rr_mat_dec_df[sample_col]=="Post-Dev Sample"]

    # Further filter data based on specified quarters
    rr_mat_dec_ds = rr_mat_dec_ds[rr_mat_dec_ds[oq_col].isin(ds_orig_qtr)]
    rr_mat_dec_pds = rr_mat_dec_pds[rr_mat_dec_pds[oq_col].isin(pds_orig_qtr)]

    # Group data by previous and current arrears buckets
    rr_mat_dec_ds = rr_mat_dec_ds.groupby([prev_arr_bucket,curr_arr_bucket]).agg({metric_val:sum}).reset_index()
    rr_mat_dec_pds = rr_mat_dec_pds.groupby([prev_arr_bucket,curr_arr_bucket]).agg({metric_val:sum}).reset_index()

    rr_mat_dec_ds_num = pd.crosstab(index=rr_mat_dec_ds[prev_arr_bucket],
                             columns=rr_mat_dec_ds[curr_arr_bucket],
                             values=rr_mat_dec_ds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             colnames=['Current Arrear Buckets'],
                             margins=False
                             )
    
    rr_mat_dec_ds_perc = pd.crosstab(index=rr_mat_dec_ds[prev_arr_bucket],
                             columns=rr_mat_dec_ds[curr_arr_bucket],
                             values=rr_mat_dec_ds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             margins=False,
                             normalize='index'
                             ).style.format('{:.2%}')
    
    rr_mat_dec_pds_num = pd.crosstab(index=rr_mat_dec_pds[prev_arr_bucket],
                             columns=rr_mat_dec_pds[curr_arr_bucket],
                             values=rr_mat_dec_pds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             colnames=['Current Arrear Buckets'],
                             margins=False
                             )
    
    rr_mat_dec_pds_perc = pd.crosstab(index=rr_mat_dec_pds[prev_arr_bucket],
                             columns=rr_mat_dec_pds[curr_arr_bucket],
                             values=rr_mat_dec_pds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             margins=False,
                             normalize='index'
                             ).style.format('{:.2%}')

    # Display results if deciles are selected, otherwise show info message
    if(len(deciles)>0):
        _c0,_c1 = st.columns(2)
        with _c0:
            st.markdown("##### Consumer Roll Rate Matrix By Decile(%) - Dev Sample")
            st.dataframe(rr_mat_dec_ds_perc,use_container_width=True,height=270)

        with _c1:
            st.markdown("##### Consumer Roll Rate Matrix By Decile(%) - Post Dev Sample")
            st.dataframe(rr_mat_dec_pds_perc, use_container_width=True,height=270)

        st.markdown("#")
        _c2,_c3 = st.columns(2)
        with _c2:
            st.markdown("##### Consumer Roll Rate Matrix By Decile(Number of Applications#) - Dev Sample")
            st.dataframe(rr_mat_dec_ds_num,use_container_width=True,height=270)

        with _c3:
            st.markdown("##### Consumer Roll Rate Matrix By Decile(Number of Applications#) - Post Dev Sample")
            st.dataframe(rr_mat_dec_pds_num, use_container_width=True,height=270)

    else:
        st.info("Select Deciles..")

def roll_rate_matrix_sb(df, ds_orig_qtr, pds_orig_qtr, params) -> None:
    """
    Generates roll rate matrices by scorecard bands for the Dev Sample and Post Dev Sample.

    Args:
        df (pd.DataFrame): The input dataframe.
        ds_orig_qtr (list): List of quarters for the Dev Sample.
        pds_orig_qtr (list): List of quarters for the Post Dev Sample.

    Returns:
        None
    """

    app_type = params['app_type']
    bucket = params['bucket']
    pred_score_bucket = params['pred_score_bucket']
    sample_col = params['sample_col']
    oq_col = params['oq_col']
    prev_arr_bucket = params['prev_arr_bucket']
    curr_arr_bucket = params['curr_arr_bucket']
    metric_val = params['metric_val']

    # Filter data based on app_type and time period
    rr_mat_sb_df = df[df[app_type] =="Consumer"]
    #rr_mat_sb_df = rr_mat_sb_df[rr_mat_sb_df[time_prd_col]==st.session_state.rrm_tp]

    # Get the unique values for scorecard bands
    sb_opts = list(rr_mat_sb_df.sort_values(bucket)[pred_score_bucket].unique())

    # Display parameter selection for scorecard bands
    st.markdown("##### Parameters: ")
    sbs = create_multiselect_all_param(w_label='Scorecard Buckets',
                                               lov=sb_opts,
                                               ph_text="Select the Scorecard Buckets...",
                                               w_key="rrm_sb"
                                               )
    st.divider()

    # Filter the dataframe for the scorebands selected
    rr_mat_sb_df = rr_mat_sb_df[rr_mat_sb_df[pred_score_bucket].isin(sbs)]

    # Split the dataframe into Dev and Post Dev Sample dataframes
    rr_mat_sb_ds = rr_mat_sb_df[rr_mat_sb_df[sample_col]=="Dev Sample"]
    rr_mat_sb_pds = rr_mat_sb_df[rr_mat_sb_df[sample_col]=="Post-Dev Sample"]

    # Filter for the respective origination quarters
    rr_mat_sb_ds = rr_mat_sb_ds[rr_mat_sb_ds[oq_col].isin(ds_orig_qtr)]
    rr_mat_sb_pds = rr_mat_sb_pds[rr_mat_sb_pds[oq_col].isin(pds_orig_qtr)]

    # Group by previous and current arrear buckets and aggregate
    rr_mat_sb_ds = rr_mat_sb_ds.groupby([prev_arr_bucket,curr_arr_bucket]).agg({metric_val:sum}).reset_index()
    rr_mat_sb_pds = rr_mat_sb_pds.groupby([prev_arr_bucket,curr_arr_bucket]).agg({metric_val:sum}).reset_index()

    # Cross tabulate the data
    rr_mat_sb_ds_num = pd.crosstab(index=rr_mat_sb_ds[prev_arr_bucket],
                             columns=rr_mat_sb_ds[curr_arr_bucket],
                             values=rr_mat_sb_ds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             colnames=['Current Arrear Buckets'],
                             margins=False
                             )
    
    rr_mat_sb_ds_perc = pd.crosstab(index=rr_mat_sb_ds[prev_arr_bucket],
                             columns=rr_mat_sb_ds[curr_arr_bucket],
                             values=rr_mat_sb_ds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             margins=False,
                             normalize='index'
                             ).style.format('{:.2%}')
    
    rr_mat_sb_pds_num = pd.crosstab(index=rr_mat_sb_pds[prev_arr_bucket],
                             columns=rr_mat_sb_pds[curr_arr_bucket],
                             values=rr_mat_sb_pds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             colnames=['Current Arrear Buckets'],
                             margins=False
                             )
    
    rr_mat_sb_pds_perc = pd.crosstab(index=rr_mat_sb_pds[prev_arr_bucket],
                             columns=rr_mat_sb_pds[curr_arr_bucket],
                             values=rr_mat_sb_pds[metric_val],
                             aggfunc=sum,
                             rownames=['Previous vs Current'],
                             margins=False,
                             normalize='index'
                             ).style.format('{:.2%}')
    

    # Display the results if scorecard bands are selected
    if(len(sbs)>0):
        _c0,_c1 = st.columns(2)
        with _c0:
            st.markdown("##### Consumer Roll Rate Matrix By Scorecard Buckets(%) - Dev Sample")
            st.dataframe(rr_mat_sb_ds_perc,use_container_width=True,height=270)

        with _c1:
            st.markdown("##### Consumer Roll Rate Matrix By Scorecard Buckets(%) - Post Dev Sample")
            st.dataframe(rr_mat_sb_pds_perc, use_container_width=True,height=270)

        st.markdown("#")
        _c2,_c3 = st.columns(2)
        with _c2:
            st.markdown("##### Consumer Roll Rate Matrix By Scorecard Buckets(Number of Applications#) - Dev Sample")
            st.dataframe(rr_mat_sb_ds_num,use_container_width=True,height=270)

        with _c3:
            st.markdown("##### Consumer Roll Rate Matrix By Scorecard Buckets(Number of Applications#) - Post Dev Sample")
            st.dataframe(rr_mat_sb_pds_num, use_container_width=True,height=270)
    else:
        st.info("Select Scorecard Buckets..")
