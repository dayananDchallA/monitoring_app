import streamlit as st
from apps.common import AppTemplate
from core import page_logo_and_title, create_app_type_param, create_sidebar_param_area
from core.misc_utils import loadconfig
from apps.rollratesmom.rrmom_utils import read_roll_rates_mom_data, plot_roll_rate_mom, read_roll_rates_decile_data, plot_roll_rate_dec, read_roll_rates_ventile_data, plot_roll_rate_sb

import pandas as pd
from pathlib import Path

class RollRatesMonthPage(AppTemplate):

    def run(self):
        # Read the data for roll rates
        # Define the project root directory dynamically
        page_logo_and_title(title="Roll Rates Month on Month Anlysis")
        # Create three tabs for Monthly, Decile and Scorecard Band views
        rr_plot,rr_dec,rr_sb = st.tabs(["Monthly View","Decile","Scorecard Band"])

        # MoM plot    
        with rr_plot:
            byline = "Monthly roll rates plots show the number of contracts (not $ balance) migrating from a lower bucket in the previous month to their current bucket this month.<br><br>Within the tooltip, the roll rate name is defined as the bucket migrated from the previous month to the current bucket this month e.g. 60-89 to 90-119. The loan pool month refers to the roll rate from from the bucket at t-1 to the loan pool month."
            st.markdown('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
            rr_plot_df_all = read_roll_rates_mom_data(self.app_params)
            plot_roll_rate_mom(rr_plot_df_all, self.app_params, key='rr_plot_df_all', container=rr_plot)
            # if st.session_state.app_type:
            #     rr_plot_df_all = roll_rate_mom_data(roll_rate_df)

            #     plot_roll_rate_mom(rr_plot_df_all,key='rr_plot_df_all',container=rr_plot)
            # else:
            #     st.info("Please select a value for the Application Borrower Type parameters")

        # Decile plots
        with rr_dec:
            byline="""The deciles are 10 equally sized buckets representing 10% of the development sample with bucket 1 being the worst 10% of applications in the development sample and bucket 10 being the best 10%. The buckets show the upper and lower bounds of scores contained within the buckets.<br><br>The reason why we view this data through deciles is because we’re specifically interested in whether roll rates are increasing or decreasing through time for the same parts of the score distribution i..e the same bucket. The portfolio roll rate may increase because the portfolio origination composition has tilted toward higher risk loans but the this page allows the user to determine whether the same risk buckets are performing the similarly through time"""
            st.markdown('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
            rr_plot_decile_df = read_roll_rates_decile_data(self.app_params)
            plot_roll_rate_dec(rr_plot_decile_df,self.app_params, key='roll_rate_df_dec',container=rr_dec)

        # Scorecard Band plots
        with rr_sb:
            byline = "The scorecard bands are 20 equally sized buckets representing 5% of the development sample with bucket 1 being the worst 5% of applications in the development sample and bucket 20 being the best 5%. The buckets show the upper and lower bounds of scores contained within the buckets.<br><br>The reason why we view this data through scorecard bands is because we’re specifically interested in whether roll rates are increasing or decreasing through time for the same parts of the score distribution i..e the same bucket. The portfolio roll rate may increase because the portfolio origination composition has tilted toward higher risk loans but the this page allows the user to determine whether the same risk buckets are performing the similarly through time<br><br>This is breakdown is merely a more granular view of the deciles."
            st.markdown('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
            rr_plot_ventile_df = read_roll_rates_ventile_data(self.app_params)
            plot_roll_rate_sb(rr_plot_ventile_df,self.app_params, key='roll_rate_df_sb',container=rr_sb)