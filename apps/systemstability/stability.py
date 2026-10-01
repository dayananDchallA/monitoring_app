import streamlit as st
from numpy import log2, log
from natsort import natsort_keygen
from apps.common import AppTemplate
from core.misc_utils import page_logo_and_title,create_multiselect_all_param
from pathlib import Path
import pandas as pd

@st.cache_data(ttl="1d", show_spinner="Data refresh in progress...")
def read_stability_data(params):
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

def color_negative_red(val):
    color = 'background-color: red' if val >= 0.25 else 'background-color: green' if val < 0.1 else 'background-color: orange' if val < 0.25 else 'background-color: darkorange'
    return color
 
def _format_arrow(val):
    return f"{'↑' if val > 0 else '↓'} {abs(val):.0f}%" if val != 0 else f"{val:.0f}%"
 
def _color_arrow(val):
    return "color: green" if val > 0 else "color: red" if val < 0 else "color: black"

class SystemStabilityPage(AppTemplate):

    def run(self):
        ss_df = read_stability_data(self.app_params)

        page_logo_and_title("System Stability",
                            byline="""The system stability allows us to see changes in the scoring distribution of Through the Door (TTD) applicants and is a lead indicator to risk in the book. Specifically, even if we maintain the same approval rates for different score bands but the TTD population scores shift, the originated book risk would shift in time with it""")

        qtr_options = ss_df['Application Quarter'].unique().tolist()

        selected_qtrs = create_multiselect_all_param(w_label='Application Quarters' ,lov=qtr_options, ph_text="Select the Quarters you want to view...", w_key="qtr_key")

        st.divider()

        st.markdown("##### Consumer System Stability")

        ss_df = ss_df[ss_df['Application Quarter'].isin(selected_qtrs)]

        ss_df['Actual Application Count By Band'] = ss_df.groupby('Scoreband')['Actual Application Count By Scoreband'].transform('sum')

        if len(selected_qtrs) == len(qtr_options) or set(selected_qtrs).issubset(set(qtr_options)):
            ss_df['Actual %'] = (ss_df['Actual Application Count By Band']/ss_df['Actual Application Count By Scoreband'].sum())*100
        else:
            ss_df['Actual %'] = (ss_df['Actual Application Count By Scoreband']/ss_df['Actual Application Count By Qtr Band'])*100

        ss_df['Expected %'] = (ss_df['Expected Application Count By Scoreband']/ss_df['Expected Total Application Count'])*100
        
        ss_df['Actual-Expected'] = (ss_df['Actual %']-ss_df['Expected %'])
        
        ss_df['log'] = log(ss_df['Actual %']/ss_df['Expected %'])

        ss_df['PSI'] = (ss_df['Actual-Expected']/100)*ss_df['log']
        
        ss_df = ss_df.sort_values(
            by="Scoreband",
            key=natsort_keygen()
        )
        
        ss_df = ss_df.round(2)
        
        ss_df_psi = ss_df[['Scoreband','Actual %','Expected %','PSI']].drop_duplicates()
        ss_df_psi = ss_df_psi.style.format({'Actual %':'{:.1f}', 'Expected %':'{:.1f}','PSI':'{:.2f}'}).map(color_negative_red, subset=['PSI'])
        st.dataframe(ss_df_psi, 
                    hide_index=True,use_container_width=True,
                    height=750)