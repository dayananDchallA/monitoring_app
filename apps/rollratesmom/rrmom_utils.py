import pandas as pd
from pathlib import Path
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from natsort import natsort_keygen
import plotly.express as px
from core.misc_utils import interactive_plotly, sort_roll_rates, sort_deciles_and_vintiles, create_multiselect_all_param

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_roll_rates_mom_data(params):
    """
    Read the roll rates data from the Excel file
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path,sheet_name="MoM_Dev_Sample")
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

@st.cache_data(ttl="2d", show_spinner="Data refresh in progress...")
def read_roll_rates_decile_data(params):
    """
    Read the roll rates data from the Excel file
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path,sheet_name="Decile_Dev")
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

@st.cache_data(ttl="3d", show_spinner="Data refresh in progress...")
def read_roll_rates_ventile_data(params):
    """
    Read the roll rates data from the Excel file
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path,sheet_name="Ventile_Dev")
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

def plot_line_chart(df, xcol, ycol, color_col, label_dict, legend_vis=True,ytick_format="1%",legend_title="", legend_pos="h", y_indent="bottom", y_pos=1.1, x_indent="right", x_pos=0.9, font_size=10, font_color="black", cat_orders = None):
    """
    Create a line chart using Plotly Express.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the data.
        xcol (str): The column name for the x-axis.
        ycol (str): The column name for the y-axis.
        color_col (str): The column name for color grouping.
        label_dict (dict): A dictionary specifying custom axis labels.
        legend_vis (bool, optional): Whether to show the legend. Defaults to True.
        ytick_format (str, optional): Format for y-axis tick labels. Defaults to "1%".
        legend_title (str, optional): Title for the legend. Defaults to "".
        legend_pos (str, optional): Orientation of the legend ("h" for horizontal, "v" for vertical). Defaults to "h".
        y_indent (str, optional): Vertical anchor position for the legend. Defaults to "bottom".
        y_pos (float, optional): Y position for the legend. Defaults to 1.1.
        x_indent (str, optional): Horizontal anchor position for the legend. Defaults to "right".
        x_pos (float, optional): X position for the legend. Defaults to 0.9.
        font_size (int, optional): Font size for legend labels. Defaults to 10.
        font_color (str, optional): Font color for legend labels. Defaults to "black".

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly figure object representing the line chart.
    """
    
    fig = px.line(df,
                  x=xcol,
                  y=ycol,
                  color=color_col,
                  labels=label_dict,
                  markers=True,
                  category_orders=cat_orders)
    
    fig.update_layout(showlegend=legend_vis)
    fig.update_layout(yaxis_tickformat=ytick_format)
    fig.update_layout(legend_title_text=legend_title)

    fig.update_layout(legend=dict(
        orientation=legend_pos,
        yanchor= y_indent,
        y=y_pos,
        xanchor=x_indent,
        x=x_pos,
        font=dict(
            size=font_size,
            color=font_color
        )
    ))

    return fig


def  plot_roll_rate_mom(df, params, key, container) -> None:
    """
    Plots roll rate data for different samples (Dev Sample and Post-Dev Sample).

    Args:
        df (pandas.DataFrame): The input DataFrame containing roll rate data.
        
    Returns: 
        None                                                                                                                
    """

    # Filter the DataFrame based on the app_type session state

    app_type = params['app_type']
    sample_col = params['sample_col']
    loan_pool_date = params['loan_pool_date']
    roll_rate_bucket = params['roll_rate_bucket']
    rate_col = params['rate_col']

    #print(st.session_state.app_type)
    rr_plot_df = df[df[app_type]=="Consumer"]    
    rr_plot_df[rate_col] = rr_plot_df[rate_col]/100

    # Create a plot for Dev Sample
    ds_fig = plot_line_chart(
        df= rr_plot_df[rr_plot_df[sample_col]=='Dev Sample'],
        xcol=loan_pool_date,
        ycol=rate_col,
        color_col=roll_rate_bucket,
        label_dict={loan_pool_date:"Month of Loan Pool Date",
                    rate_col:"Roll Rate %"},
        cat_orders={
            'Name' : ['Roll Rate: Current 1-29','Roll Rate: 1-29 to 30-59','Roll Rate: 30-59 to 60-89','Roll Rate: 60-89 to 90-119','Roll Rate: 90-119 to 120-149']
        }
        )
    
    # Create a plot for Post-Dev Sample
    pds_fig = plot_line_chart(
        df=rr_plot_df[rr_plot_df[sample_col]=='Post-Dev Sample'],
        xcol=loan_pool_date,
        ycol=rate_col,
        color_col=roll_rate_bucket,
        label_dict={loan_pool_date:"Month of Loan Pool Date",
                    rate_col:"Roll Rate %"}
        ,cat_orders={
            'Name' : ['Roll Rate: Current 1-29','Roll Rate: 1-29 to 30-59','Roll Rate: 30-59 to 60-89','Roll Rate: 60-89 to 90-119','Roll Rate: 90-119 to 120-149']
        }

    )

    # Display the plots
    st.markdown("#")
    st.markdown("##### Consumer - Dev Sample", 
                help="The consumer development sample constitutes 110,623 samples from the 1st of July until 31st of March 2022 and is based on originations and declines with a target variable of 90+ within first 18m")
    #st.plotly_chart(ds_fig, use_container_width=True)
    interactive_plotly(ds_fig,key='ds_fig')
    
    st.markdown("##### Consumer - Post-Dev Sample",
                help="Post-Dev Sample refers to the period after the end of development sample and represents applications or originations that the model has not seen.")
    #st.plotly_chart(pds_fig, use_container_width=True)
    interactive_plotly(pds_fig,key=key, container=container)


def plot_roll_rate_dec(df, params, key, container) -> None:
    """
    Plots roll rate decile data for different samples (Dev Sample and Post-Dev Sample).
    
    Args:
        df(pd.DataFrame) : The input DataFrame containing roll rate data.
    
    Returns: 
        None
    """

    app_type = params['app_type']
    roll_rate_bucket = params['roll_rate_bucket']
    rate_col = params['rate_col']
    decile_col = params['decile_col']
    metric_col = params['metric_col']
    pred_score_dec = params['pred_score_dec']
    sample_col = params['sample_col']
    loan_pool_date = params['loan_pool_date']

    # Filter for MoM Decile data for the application type
    rr_dec_df = df[(df[app_type]=="Consumer") & (df[metric_col]=='MoM by Decile')]

    # Create the lovs for the parameters   
    arrear_bucket_opts = list(rr_dec_df[roll_rate_bucket].unique())
    arrear_bucket_opts = sort_roll_rates(arrear_bucket_opts)

    dec_options = list(rr_dec_df[decile_col].astype('int').astype('str').unique())
    dec_options = rr_dec_df[pred_score_dec].unique()
    dec_options = sort_deciles_and_vintiles(dec_options)

    st.markdown("##### Parameters: ")
    _dec1, _dec2 = st.columns([0.5,0.5])

    # Create multiselect parameters
    with _dec1:
        selected_deciles = create_multiselect_all_param(w_label='Decile', 
                                                        lov=dec_options, 
                                                        ph_text='Select the Deciles you want to view...', 
                                                        w_key='deciles_key')

    # Create a single select param for Arrear Buckets
    with _dec2:
        selected_arrear_buckets = st.selectbox('Arrear Buckets',
                                    arrear_bucket_opts,
                                    placeholder="Select Arrear buckets...",
                                    key="arrear_bucket_key"
                                    )
    
    # Filter the dataframe and prepare the param cols
    rr_dec_df = rr_dec_df[rr_dec_df[roll_rate_bucket]==selected_arrear_buckets]
    rr_dec_df = rr_dec_df[rr_dec_df[pred_score_dec].isin(selected_deciles)]
    dec_cols = list(rr_dec_df.sort_values(decile_col)[pred_score_dec].unique())

    col_order = ['LOAN_POOL_MONTH'] + dec_cols

    # Filter for the Dev sample data and sort
    rr_dec_df_ds = rr_dec_df[rr_dec_df[sample_col]=='Dev Sample'].pivot(index=loan_pool_date,columns=pred_score_dec,values=rate_col).reset_index()
    rr_dec_df_ds["LOAN_POOL_MONTH"] = pd.to_datetime(rr_dec_df_ds[loan_pool_date]).dt.strftime('%b %y')
    rr_dec_df_ds = rr_dec_df_ds.sort_values(loan_pool_date)

    # Filter for the Post-Dev sample data and sort
    rr_dec_df_pds = rr_dec_df[rr_dec_df[sample_col]=='Post-Dev Sample'].pivot(index=loan_pool_date,columns=pred_score_dec,values=rate_col).reset_index()
    rr_dec_df_pds["LOAN_POOL_MONTH"] = pd.to_datetime(rr_dec_df_pds[loan_pool_date]).dt.strftime('%b %y')
    rr_dec_df_pds = rr_dec_df_pds.sort_values(loan_pool_date)

    # Create the grid options for the Aggrid display table
    gb = GridOptionsBuilder.from_dataframe(rr_dec_df_ds[col_order])

    gb.configure_default_column(
                resizable=True,
                filterable=True,
                sortable=True,
                editable=False,
                autoHeaderHeight = True,
                width=84
                
            )

    # Set the configuration for the LOAN_POOL_MONTH column
    gb.configure_column(
                field='LOAN_POOL_MONTH',
                header_name= "Month of Loan Pool Date",
                wrapHeaderText = True,
                width=100,
            )

    #  Set the option to select rows in the Aggrid table
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)

    # Build the grid options object
    go = gb.build()
    st.divider()

    _dec3, _dec4 = st.columns(2)
    _dec5, _dec6 = st.columns(2)
    _dec7, _dec8 = st.columns(2)

    with _dec3:
        st.markdown("##### Consumer - Dev Sample", 
                help="The consumer development sample constitutes 110,623 samples from the 1st of July until 31st of March 2022 and is based on originations and declines with a target variable of 90+ within first 18m")

    with _dec4:
        st.markdown("##### Consumer - Post-Dev Sample",
                    help="Post-Dev Sample refers to the period after the end of development sample and represents applications or originations that the model has not seen.")

    with _dec7:
        # Display bar plot for Dev Sample data
        rr_dec_fig1 = generate_bar_plots(
            df = rr_dec_df_ds.melt(id_vars=[loan_pool_date,'LOAN_POOL_MONTH']).sort_values(by=pred_score_dec, key= natsort_keygen()),
            xcol = loan_pool_date, 
            ycol = 'value', 
            color_discrete_seq=px.colors.qualitative.Alphabet,
            color_col = pred_score_dec
        )

        interactive_plotly(rr_dec_fig1,key=key, container=container)

    with _dec8:
        # Display bar plot for Post-Dev Sample data 
        rr_dec_fig2 = generate_bar_plots(
            df=rr_dec_df_pds.melt(id_vars=[loan_pool_date,'LOAN_POOL_MONTH']).sort_values(by=pred_score_dec, key= natsort_keygen()),
            xcol= loan_pool_date,
            ycol= 'value',
            color_col= pred_score_dec
        )

        #t.plotly_chart(rr_dec_fig2, use_container_width=True)
        interactive_plotly(rr_dec_fig2,key='rr_dec_fig2',container=_dec8)
    
    with _dec5:
        # Display AgGrid table for Dev Sample data
        st.dataframe(rr_dec_df_ds[col_order], key="ds_rrmomdec",hide_index=True)
    
    with _dec6:
        # Display AgGrid table for Post-Dev Sample data
        st.dataframe(rr_dec_df_pds[col_order], key="pds_rrmomdec",hide_index=True)
    
def generate_bar_plots(df, xcol, ycol, color_col,color_discrete_seq=None , facet_by=None,legend_vis=True ,legend_title="",legend_pos="h",y_indent="bottom",y_pos=1.1,x_indent="right",x_pos=0.9,font_size=10,font_color="black"):
    """
    Plots the bar charts for roll rate decile plots

    Args:
        df (pandas.DataFrame) : The input Dataframe containing the decile data to plot
        xcol (str): The column name for the x-axis.
        ycol (str): The column name for the y-axis.
        color_col (str): The column name for color grouping.
        color_discrete_seq (px.colors.qualitative.<value>): The discrete color sequence from plotly express
        facet_by (str): The column name for faceting.
        legend_vis (bool, optional): Whether to show the legend. Defaults to True.
        legend_title (str, optional): Title for the legend. Defaults to "".
        legend_pos (str, optional): Orientation of the legend ("h" for horizontal, "v" for vertical). Defaults to "h".
        y_indent (str, optional): Vertical anchor position for the legend. Defaults to "bottom".
        y_pos (float, optional): Y position for the legend. Defaults to 1.1.
        x_indent (str, optional): Horizontal anchor position for the legend. Defaults to "right".
        x_pos (float, optional): X position for the legend. Defaults to 0.9.
        font_size (int, optional): Font size for legend labels. Defaults to 10.
        font_color (str, optional): Font color for legend labels. Defaults to "black".
    Returns:
        plotly.graph_objs._figure.Figure: A Plotly figure object representing the line chart.
    """

    _fig = px.bar(
        df,
        x=xcol,
        y=ycol,
        color=color_col,
        facet_col=facet_by,
        color_discrete_sequence=color_discrete_seq
    )

    _fig.update_layout(showlegend=legend_vis)
    _fig.update_layout(legend_title_text=legend_title)
    _fig.update_layout(legend=dict(
        orientation=legend_pos,
        yanchor=y_indent,
        y=y_pos,
        xanchor=x_indent,
        x=x_pos,
        font=dict(
            size=font_size,
            color=font_color
        )
    ))

    _fig.update_layout(yaxis_title="")

    return _fig

def plot_roll_rate_sb(df, params, key, container) -> None:
    """
    Plots roll rate scorecard band data for different samples (Dev Sample and Post-Dev Sample).

    Args:
        df(pd.DataFrame) : The input DataFrame containing roll rate data.
    
    Returns:
        None
    """

    app_type = params['app_type']
    roll_rate_bucket = params['roll_rate_bucket']
    rate_col = params['rate_col']
    decile_col = params['decile_col']
    metric_col = params['metric_col']
    pred_score_dec = params['pred_score_dec']
    sample_col = params['sample_col']
    loan_pool_date = params['loan_pool_date']
    pred_score_sb = params['pred_score_sb']
    sb_bucket_col = params['sb_bucket_col']

    # Filter for MoM Decile data for the application type
    rr_sb_df = df[(df[app_type]=="Consumer") & (df[metric_col]=='MoM by Ventile')]
    
    # Create the lovs for the parameters
    arrear_bucket_opts_sb = rr_sb_df[roll_rate_bucket].unique()
    arrear_bucket_opts_sb = sort_roll_rates(arrear_bucket_opts_sb)
    sb_options = list(rr_sb_df[pred_score_sb].astype('str').unique())
    sb_options = sort_deciles_and_vintiles(sb_options)

    # Display Parameters
    st.markdown("##### Parameters: ")
    _sb1, _sb2 = st.columns([0.5,0.5])

    with _sb1:
        selected_sbs = create_multiselect_all_param(w_label='Scorecard Bands', 
                                                    lov=sb_options, 
                                                    ph_text='Select the Scorecard Bands you want to view...', 
                                                    w_key='sb_key')
        
    with _sb2:
        selected_arrear_buckets = st.selectbox('Arrear Buckets',
                                    arrear_bucket_opts_sb,
                                    placeholder="Select Arrear Buckets...",
                                    key="arrear_bucket_key_sb"
                                    )
    
    # Filter data based on the parameters selected
    rr_sb_df = rr_sb_df[rr_sb_df[roll_rate_bucket]==selected_arrear_buckets]
    rr_sb_df = rr_sb_df[rr_sb_df[pred_score_sb].astype('str').isin(selected_sbs)]
    sb_cols = list(rr_sb_df.sort_values(sb_bucket_col)[pred_score_sb].unique())
    col_order = ["LOAN_POOL_MONTH"] + sb_cols

    # Filter dev sample data
    rr_sb_df_ds = rr_sb_df[rr_sb_df[sample_col]=='Dev Sample'].pivot(index=loan_pool_date,columns=pred_score_sb,values=rate_col).reset_index()
    rr_sb_df_ds["LOAN_POOL_MONTH"] = pd.to_datetime(rr_sb_df_ds[loan_pool_date]).dt.strftime('%b %y')
    rr_sb_df_ds = rr_sb_df_ds.sort_values(loan_pool_date)
    
    # Filter Post-Dev sample data
    rr_sb_df_pds = rr_sb_df[rr_sb_df[sample_col]=='Post-Dev Sample'].pivot(index=loan_pool_date,columns=pred_score_sb,values=rate_col).reset_index()
    rr_sb_df_pds["LOAN_POOL_MONTH"] = pd.to_datetime(rr_sb_df_pds[loan_pool_date]).dt.strftime('%b %y')
    rr_sb_df_pds = rr_sb_df_pds.sort_values(loan_pool_date)

    # Set config for grid options
    gb_sb = GridOptionsBuilder.from_dataframe(rr_sb_df_ds[col_order])

    gb_sb.configure_default_column(
                resizable=True,
                filterable=True,
                sortable=True,
                editable=False,
                autoHeaderHeight = True,
                width=84
                
            )

    gb_sb.configure_column(
                field='LOAN_POOL_MONTH',
                header_name= "Month of Loan Pool Date",
                wrapHeaderText = True,
                width=100,
            )

    gb_sb.configure_selection(selection_mode="multiple", use_checkbox=True)

    go_sb = gb_sb.build()
    st.divider()

    #st.markdown('<style>.stMarkdown > div { border: 0.1px solid #100; }</style>', unsafe_allow_html=True)

    # Generate and display plots and tables for scorecard buckets
    _sb3, _sb4 = st.columns(2, gap="small")
    _sb5, _sb6 = st.columns(2, gap="small")
    _sb7, _sb8 = st.columns(2, gap="small")

    with _sb3:
        st.markdown("##### Consumer - Dev Sample", 
                help="The consumer development sample constitutes 110,623 samples from the 1st of July until 31st of March 2022 and is based on originations and declines with a target variable of 90+ within first 18m")

    with _sb4:
        st.markdown("##### Consumer - Post-Dev Sample",
                    help="Post-Dev Sample refers to the period after the end of development sample and represents applications or originations that the model has not seen.")

    # Display bar plot for dev sample
    with _sb7:
        rr_sb_fig1 = generate_bar_plots(df=rr_sb_df_ds.melt(id_vars=[loan_pool_date,'LOAN_POOL_MONTH']).sort_values(by=pred_score_sb, key= natsort_keygen()),
                                        xcol=loan_pool_date,
                                        ycol='value',
                                        color_col=pred_score_sb,
                                        color_discrete_seq=px.colors.qualitative.Alphabet
                                        )
        
        #st.plotly_chart(rr_sb_fig1, use_container_width=True)
        interactive_plotly(rr_sb_fig1,key='rr_sb_fig1', container=_sb7)

    # Display bar plot for Post-Dev sample
    with _sb8:
        rr_sb_fig2 = generate_bar_plots(df=rr_sb_df_pds.melt(id_vars=[loan_pool_date,'LOAN_POOL_MONTH']).sort_values(by=pred_score_sb, key= natsort_keygen()),
                                        xcol=loan_pool_date,
                                        ycol='value',
                                        color_col=pred_score_sb,
                                        )
        
        #st.plotly_chart(rr_sb_fig2, use_container_width=True)
        interactive_plotly(rr_sb_fig2,key='rr_sb_fig2', container=_sb8)

    # Display table for dev sample
    with _sb5:
        st.dataframe(rr_sb_df_ds[col_order], key="ds_rrmomsb",hide_index=True)

    # Display table for Post-Dev sample
    with _sb6:
        st.dataframe(rr_sb_df_pds[col_order],key="pds_rrmomsb",hide_index=True)