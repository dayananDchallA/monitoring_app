
import streamlit as st
import pandas as pd
 
import plotly.express as px
from natsort import natsorted, natsort_keygen
from itertools import product
 
from pathlib import Path
 
from core.misc_utils import create_multiselect_all_param, sort_deciles_and_vintiles, interactive_plotly

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_vintage_data(params):
    """
    Read vintage data from snowflake
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    oq_col = params['oq_col']
    mob = params['mob']
    view_by = params['view_by']

    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")

    # sort by origination quarter
    df = df.sort_values(by=[oq_col,mob],ascending=True)
    
    # Temporary code to only get Consumer data
    #df = df[df[app_type]=='Consumer']

    # Split the dataframe into Quarterly, Decile and Scorecard band
    #vin_df = df[df[dataset_name]=="Quarterly"]
    vin_df = df[df[view_by]=="Summary"]

    #vin_dec_df = df[(df[dataset_name]=="Scorecard Band") & (df[view_by]=="Decile")]
    vin_dec_df = df[df[view_by]=="Decile"]
    
    #vin_sb_df = df[(df[dataset_name]=="Scorecard Band") & (df[view_by]=="Scorecard Band")]
    vin_sb_df = df[df[view_by]=="Ventile"]

    return df, vin_df, vin_dec_df, vin_sb_df

def vin_params_layout(vin_df, params):
    """
    Function to create and display the parameters

    Args:
        vin_df (pd.DataFrame): The input dataframe

    Returns:
        ds_orig_qtr (streamlit widget): Dev Sample Origination quarter selected
        pds_orig_qtr (streamlit widget): PostDev Sample Origination quarter selected
    """

    sample_col = params['sample_col']
    oq_col = params['oq_col']

    ds_orig_qtr_opts = list(vin_df[vin_df[sample_col]=='Dev Sample'][oq_col].unique())

    pds_orig_qtr_opts = list(vin_df[vin_df['Data Description']=='Post-Dev Sample']["Origination Quarter"].unique())

    ds_orig_qtr = create_multiselect_all_param(
                    w_label='Dev Sample Origination Quarter',
                    lov= ds_orig_qtr_opts,
                    ph_text="Select the Dev Sample Origination Quarter...",
                    w_key="vin_ds_oq"
    )

    pds_orig_qtr = create_multiselect_all_param(
                    w_label='Post Dev Sample Origination Quarter',
                    lov= pds_orig_qtr_opts,
                    ph_text="Select the Post Dev Sample Origination Quarter...",
                    w_key="vin_pds_oq"
    )

    return ds_orig_qtr, pds_orig_qtr

# Function to parse the months from the header
def get_month_limit(header):
    try:
        parts = header.split("In")[1].split()  # Split to get the part with the month number
        months = int(parts[0])  # Extract the number of months
        return months + 1  # Add 1 to get the required limit
    except (IndexError, ValueError):
        return 1000  # In case of invalid format, return None

def vin_plot(df, params, xcol, ycol, color_col, sample, orig_qtr, hover_cols, title,key, container) -> None:
    """
    Plots a line chart using Plotly Express based on the provided data and parameters.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the data.
        xcol (str): The column name for the x-axis.
        ycol (str): The column name for the y-axis.
        color_col (str): The column name for color grouping (e.g., different categories).
        sample (str): The value to filter the data by (e.g., sample type).
        orig_qtr (list): List of original quarters to filter the data by.
        hover_cols (list): List of columns to display as hover information.
        title (str): Title for the plot.

    Returns:
        None
    """
    st.markdown("##### "+title)

    app_type = params['app_type']
    sample_col = params['sample_col']
    oq_col = params['oq_col']
    
    # Filter the DataFrame based on session state app type, sample, and original quarters
    vin_plot_df = df[df[app_type]=="CONSUMER"]
    vin_plot_df = vin_plot_df[vin_plot_df[sample_col]==sample]
    vin_plot_df = vin_plot_df[vin_plot_df[oq_col].isin(orig_qtr)]

    # Create a line chart using Plotly Express
    vin_fig = px.line(vin_plot_df, 
                      x=xcol, 
                      y=ycol, 
                      markers=True,
                      color=color_col,
                      hover_data=hover_cols
                    )

    # Customize the plot layout
    vin_fig.update_layout(showlegend=True)
    vin_fig.update_layout(yaxis_tickformat="1%")
    vin_fig.update_layout(legend_title_text="")

    vin_fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=3.1,
        xanchor="right",
        x=0.9,
        font=dict(
            size=10,
            color="black")
    ))

    vin_fig.update_layout(yaxis_range=[0,vin_plot_df[ycol].max()+0.005])

    # Cut the xaxis to the number of cumulative months+1
    x_cut = ycol.split(' ')[-1].replace('M','')
    if(x_cut.isdigit()):
        x_cut = int(x_cut)
        vin_fig.update_layout(xaxis_range=[0,x_cut+1])

    # Display the plot using Streamlit
    #st.plotly_chart(vin_fig, theme="streamlit", use_container_width=True, on_select="rerun", config={'displayModeBar': False})

    interactive_plotly(vin_fig,key=key, container=container)


def vin_qtr_plots(df, ds_orig_qtr, pds_orig_qtr, params) -> None:
    """
    Generate quarterly plots for the given DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing relevant data.
        ds_orig_qtr (str): The original quarter for the "Training" sample.
        pds_orig_qtr (str): The original quarter for the "Post_Training" sample.

    Returns:
        None
    """

    sample_col = params['sample_col']
    mob  = params['mob']
    oq_col = params['oq_col']

    # Natural sort the Cumulative Columns
    ycols = natsorted(df.filter(like='Runtot Rate').columns.tolist())
    samples = df[sample_col].unique().tolist()

    st.markdown("##### Consumer")
    st.markdown(' ')

    # Create the quarterly plots for each arrear bucket
    for idx, ycol in enumerate(ycols):
        cols = st.columns(len(samples))
        for c, sample in zip(range(len(cols)),samples):
            
            if sample=='Dev Sample':
                orig_qtr = ds_orig_qtr
                title = ycol.replace('Runtot Rate','Quarterly') + " - " + sample
            elif sample=='Post-Dev Sample':
                orig_qtr = pds_orig_qtr
                title = ycol.replace('Runtot Rate','Quarterly') + " - " + sample
            

            with cols[c]:
                vin_plot(df, 
                        params,
                        xcol=mob, 
                        ycol=ycol, 
                        color_col=oq_col, 
                        sample=sample, 
                        orig_qtr=orig_qtr,
                        hover_cols=["Origination Quarter",
                                    "Arrears 30 In 3 Runtot Rate",
                                    "Month On Book",
                                    "Arrears 30 In 3 Runtot Count",
                                    "Application Count"],
                        container=cols[c],
                        title=title,
                        key='vin_qtr_plots{}{}'.format(idx,sample)
                        )


def vin_dec_plots(df, ds_orig_qtr, pds_orig_qtr, params) -> None:
    """
    Generate decile plots for the given DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing relevant data.
        ds_orig_qtr (str): The original quarter for the "Training" sample.
        pds_orig_qtr (str): The original quarter for the "Post_Training" sample.

    Returns:
        None
    """

    sample_col = params['sample_col']
    cum_90_in_18 = params['cum_90_in_18']
    pred_score_dec = params['pred_score_dec']
    mob = params['mob']


    # Set variables and parameter values
    samples = df[sample_col].unique().tolist()
    ycols = [cum_90_in_18]

    decile_opts = list(df.sort_values(pred_score_dec)[pred_score_dec].astype(str).unique())
    decile_opts = sort_deciles_and_vintiles(decile_opts)

    # Create the multiselect parameters for deciles
    st.markdown("##### Parameters: ")
    deciles = create_multiselect_all_param(
                    w_label='Deciles',
                    lov= decile_opts,
                    ph_text= "Select the Deciles...",
                    w_key="vin_deciles")

    st.divider()

    # Filter the DataFrame based on the selected deciles
    df = df[df[pred_score_dec].astype(str).isin(deciles)]

    st.markdown("##### Consumer")
    st.markdown(' ')

    # Create the decile plots for each arrear bucket and sample
    for idx, ycol in enumerate(ycols):
        for sample in samples:
            
            # Select the appropriate origination quarter based on the sample
            if sample=='Dev Sample':
                orig_qtr = ds_orig_qtr
                title = (ycol.replace('Runtot Rate','')).replace('M',' Months by Decile') + " - " + sample
            elif sample=='Post-Dev Sample':
                orig_qtr = pds_orig_qtr
                title = (ycol.replace('Runtot Rate','')).replace('M','Months by Decile') + " - " + sample

            
            # Generate the decile plot
            vin_dec_plot(df, 
                        params,
                        xcol=mob, 
                        ycol=ycol, 
                        color_col=pred_score_dec, 
                        sample=sample, 
                        orig_qtr=orig_qtr,
                        hover_cols=["Predicted Score Decile",
                                    "Origination Quarter",
                                    "Month On Book",
                                    ycol,
                                    "Arrears 90 In 18 Runtot Count",
                                    "Application Count"],
                        title=title,
                        key='vin_deciles{}{}'.format(idx,sample)
                        )
            
def vin_sb_plots(df, ds_orig_qtr, pds_orig_qtr, params) -> None:
    """
    Generate scorecard bucket plots for the given DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing relevant data.
        ds_orig_qtr (str): The original quarter for the "Training" sample.
        pds_orig_qtr (str): The original quarter for the "Post_Training" sample.

    Returns:
        None
    """

    sample_col = params['sample_col']
    cum_90_in_18 = params['cum_90_in_18']
    bucket = params['bucket']
    pred_score_bucket = params['pred_score_bucket']
    mob = params['mob']

    # Set the variables and parameter values
    samples = df[sample_col].unique().tolist()
    ycols = [cum_90_in_18]

    sb_opts = list(df.sort_values(bucket)[pred_score_bucket].unique())
    #sb_opts_all = ["All"] + sb_opts

    # Create the multiselect parameters for scorecard buckets
    st.markdown("##### Parameters: ")
    buckets = create_multiselect_all_param(
                    w_label="Scorecard Buckets",
                    lov= sb_opts,
                    ph_text= "Select the Buckets...",
                    w_key="vin_buckets"
    )

    st.divider()

    # Filter the DataFrame based on the selected scorecard buckets
    df = df[df[pred_score_bucket].isin(buckets)]

    #df = df.sort_values(by=pred_score_dec, key= natsort_keygen())

    st.markdown("##### Consumer")
    st.markdown(' ')

    for idx, ycol in enumerate(ycols):
        for sample in samples:

            if sample=='Dev Sample':
                orig_qtr = ds_orig_qtr
                title = (ycol.replace('Runtot Rate','')).replace('m',' Months by Scorecard Band') + " - " + sample
            elif sample=='Post-Dev Sample':
                orig_qtr = pds_orig_qtr
                title = (ycol.replace('Runtot Rate','')).replace('m','Months by Scorecard Band') + " - " + sample

            vin_dec_plot(df, 
                        params,
                        xcol=mob, 
                        ycol=ycol, 
                        color_col=pred_score_bucket, 
                        sample=sample, 
                        orig_qtr=orig_qtr,
                        hover_cols=["Predicted Score Bucket",
                                    "Origination Quarter",
                                    "Month On Book",
                                    ycol,
                                    "Arrears 90 In 18 Runtot Count",
                                    "Application Count"],
                        title=title,
                        key='pred_score_bucket{}{}'.format(idx,sample)
                        )
            
                
def vin_dec_plot(df, params, xcol, ycol, color_col, sample, orig_qtr, hover_cols, title, key) -> None:

    st.markdown("##### "+title)

    app_type = params['app_type']
    sample_col = params['sample_col']
    oq_col = params['oq_col']
    bucket = params['bucket']
    
    vin_plot_df = df[df[app_type]=='CONSUMER']
    vin_plot_df = vin_plot_df[vin_plot_df[sample_col]==sample]
    vin_plot_df = vin_plot_df[vin_plot_df[oq_col].isin(orig_qtr)]

    vin_plot_df = vin_plot_df.sort_values([oq_col , bucket])

    vin_fig = px.line(vin_plot_df, 
                      x=xcol, 
                      y=ycol, 
                      color=color_col,
                      symbol=oq_col,
                      markers=True,
                      hover_data=hover_cols,
                      color_discrete_sequence=px.colors.qualitative.Light24,
                    )
    
    pred_deciles = []

    for trace in vin_fig["data"]:
        dec,score,_ = trace["name"].split(",")
        trace["legendgroup"] = dec+", "+score
        
        if dec+score not in pred_deciles and trace["marker"]['symbol'] == 'circle':
            trace["showlegend"] = True
            trace["mode"] = 'lines'
            trace["name"] = dec+", "+score
            pred_deciles.append(dec+score)
        else:
            trace["showlegend"] = False
            trace["mode"] = 'lines'

    vin_fig.update_layout(showlegend=True)
    vin_fig.update_layout(yaxis_tickformat="1%")
    vin_fig.update_layout(legend_title_text="")

    vin_fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.1,
        xanchor="right",
        x=0.9,
        font=dict(
            size=9,
            color="black")
    ))

    vin_fig.update_layout(yaxis_range=[0,vin_plot_df[ycol].max()+0.005])
    vin_fig.update_layout(xaxis_range=[0,19])

    interactive_plotly(vin_fig, use_container_width=True, config={'displayModeBar': False}, key=key)