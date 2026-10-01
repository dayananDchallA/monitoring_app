import streamlit as st
import pandas as pd
import plotly.express as px
from apps.common import AppTemplate
from pathlib import Path
from core.misc_utils import interactive_plotly, page_logo_and_title, sort_deciles_and_vintiles, create_multiselect_all_param, filter_and_sort_dataframe, sort_df_by_quarter_decile



def plot_ar_lines(df, params, key, container):

    id_cols = params['id_cols']
    melt_vars = params['melt_vars']
    hover_cols = params['hover_cols']
    qtr_col = params['qtr_col']

    plot_df = pd.melt(df, 
                id_vars= id_cols,
                value_vars=melt_vars,
                var_name='Rate',
                value_name='Rate %')
    
    plot_df['Rate %'] = plot_df['Rate %']/100

    fig = px.line(plot_df,
                      x=qtr_col, 
                      y='Rate %',
                      color='Rate',
                      markers=True,
                      hover_data= hover_cols
                    )
        
    fig.update_layout(showlegend=True)
    fig.update_layout(yaxis_tickformat="1%")
    fig.update_layout(legend_title_text="")

    fig.update_layout(legend=dict(
            orientation="h",
            yanchor="top",
            y=3.1,
            xanchor="right",
            x=0.9,
            font=dict(
                size=10,
                color="black")
        ))

    interactive_plotly(fig, config={'displayModeBar': False}, key=key, container=container)


def show_ar_total(ar_total, params):
    st.markdown("##### "+'Origination vs Decline Rate - Aggregate Rate')

    ar_rate_cols = params['ar_rate_cols']
    app_type = params['app_type']

    _artplot, _arttable = st.tabs(['Plot','Table'])

    ar_total = ar_total[ar_total[app_type]=="Consumer"]

    #ar_total = sort_df_by_quarter(ar_total, 'Application Quarter')
    
    with _artplot:
        plot_ar_lines(ar_total, params, key='plot_ar', container=None)

    with _arttable:
        
        ar_total = ar_total[ar_rate_cols]
        ar_total_t = ar_total.set_index("Application Quarter").T
        st.dataframe(ar_total_t,hide_index=False)



def calculate_rates(df):
    df = df.groupby(['Application Borrower Type','Application Quarter']).agg({'Approved':'sum','Settled':'sum','Declined':'sum'}).reset_index()

    df['Orignation Rate'] = (df.Settled / (df.Settled+df.Approved)) * 100
    df['Approved Rate'] = ((df.Settled+df.Approved) / (df.Settled+df.Approved+df.Declined)) *100
    df['Declined Rate'] = (df.Declined / (df.Settled+df.Approved+df.Declined)) * 100

    return df

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_ar_total_data(params):
    """
    Read the roll rates data from the Excel file
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path,sheet_name="Total")
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_ar_decile_data(params):
    """
    Read the roll rates data from the Excel file
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path,sheet_name="Deciles")
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_ar_scorecard_data(params):
    """
    Read the roll rates data from the Excel file
    """
    # Define the project root directory dynamically
    project_root = Path(__file__).resolve().parents[2]

    data_file = params['sf_tab_name']
    file_path = project_root.joinpath(data_file)
    df = pd.read_excel(file_path,sheet_name="Ventiles")
    df.columns = df.columns.str.title()
    df.columns = df.columns.str.replace("_"," ")
    return df

class AcceptanceRatesPage(AppTemplate):

    def run(self):

        qtr_col = self.app_params['qtr_col']

        ar_total = read_ar_total_data(self.app_params)
        ar_total.sort_values(by=qtr_col,ascending=True,inplace=True)

        ar_decile = read_ar_decile_data(self.app_params)

        ar_scoreband = read_ar_scorecard_data(self.app_params)

        page_logo_and_title("Acceptance Rate", 
                            byline="""The approval rates of higher risk customers can be tracked here, 
                            the approval rate and origination rates can be used as a lead indicator to 
                            future book performance""")


        show_ar_total(ar_total, self.app_params)

        st.divider()
        
        with st.container():

            st.markdown("##### " + "Origination vs Decline Rate by Decile")

            dec_options = ar_decile['Decile'].unique().tolist()
            dec_options = sort_deciles_and_vintiles(dec_options)

            selected_deciles = create_multiselect_all_param(w_label='Deciles' ,lov=dec_options, ph_text="Select the Deciles you want to view...", w_key="dec_key")

            ar_decile = ar_decile[ar_decile['Decile'].isin(selected_deciles)]

            ar_decile_ds = ar_decile[ar_decile['Data Description']=='Dev Sample']
            ar_decile_pds = ar_decile[ar_decile['Data Description']=='Post-Dev Sample']

            _dscol,_pdscol = st.columns(2)

            with _dscol:
                st.markdown("##### " + "Dev Sample")
                
                ar_decile_plot_ds = calculate_rates(ar_decile_ds)

                _ardplot, _ardtable = st.tabs(['Plot','Table'])

                with _ardplot:
                    try:
                        plot_ar_lines(ar_decile_plot_ds, self.app_params, key='ar_decile_plot_ds', container=_ardplot)
                    except Exception as e:
                        print(e)

                with _ardtable:
                    st.dataframe(ar_decile_ds,hide_index=True)
                

            with _pdscol:
                st.markdown("##### " + "Post-Dev Sample")
                
                ar_decile_plot_pds = calculate_rates(ar_decile_pds)

                _ardpdsplot, _ardpdstable = st.tabs(['Plot','Table'])

                with _ardpdsplot:
                    plot_ar_lines(ar_decile_plot_pds, self.app_params, key='ar_decile_plot_pds', container=_pdscol)

                with _ardpdstable:
                    st.dataframe(ar_decile_pds,hide_index=True)

        st.divider()

        with st.container():

            st.markdown("##### " + "Origination vs Decline Rate by Scorecard Bands")

            sb_options = ar_scoreband['Scoreband'].unique().tolist()

            sb_options = sort_deciles_and_vintiles(sb_options)

            selected_sb = create_multiselect_all_param(w_label='Scorecard Bands' ,lov=sb_options, ph_text="Select the Scorecard Bands you want to view...", w_key="scb_key")

            ar_scoreband = ar_scoreband[ar_scoreband['Scoreband'].isin(selected_sb)]

            ar_sb_ds = ar_scoreband[ar_scoreband['Data Description']=='Dev Sample']
            ar_sb_pds = ar_scoreband[ar_scoreband['Data Description']=='Post-Dev Sample']

            _dscol,_pdscol = st.columns(2)

            with _dscol:
                st.markdown("##### " + "Dev Sample")

                ar_sb_plot_ds = calculate_rates(ar_sb_ds)

                _arsbplot, _arsbtable = st.tabs(['Plot','Table'])

                with _arsbplot:
                    plot_ar_lines(ar_sb_plot_ds, self.app_params, key='ar_sb_plot_ds',container=_arsbplot)

                with _arsbtable:
                    st.dataframe(ar_sb_ds,hide_index=True)
                

            with _pdscol:
                st.markdown("##### " + "Post-Dev Sample")
                
                ar_sb_plot_pds = calculate_rates(ar_sb_pds)

                _arsbpdsplot, _arsbpdstable = st.tabs(['Plot','Table'])

                with _arsbpdsplot:
                    plot_ar_lines(ar_sb_plot_pds, self.app_params, key='ar_sb_plot_pds',container=_arsbpdsplot)

                with _arsbpdstable:
                    st.dataframe(ar_sb_pds,hide_index=True)