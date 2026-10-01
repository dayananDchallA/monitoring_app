import streamlit as st
from apps.rollratesmatrix.rrmat_utils import *
from apps.common import AppTemplate
from core import page_logo_and_title,create_app_type_param


class RollRatesMatrixPage(AppTemplate):

    def run(self):

        df = read_roll_rate_matrix(self.app_params)

        # Create the logo, title and related elements
        page_logo_and_title(title="Roll Rates Matrix", subheader="Previous Arrear Buckets vs Current Arrear Buckets Analysis")

        st.markdown("Select origination quarter(s) to compare every loan originated in those quarters on a matrix view")
        ds_orig_qtr, pds_orig_qtr = rrmat_params_layout(df, self.app_params)

        _matrix, _decile, _scoreband = st.tabs(["Matrix","Decile","Scorecard Band"])

        metric_col = self.app_params['metric_col']
        with _matrix:
            byline = "The roll rate matrix differs from the month on month roll rates as the matrix view is agnostic on the exact date a loan rolled but instead looks at the entire time period and just compares t-1 to t. <br><br>This method is the most reliable approximation for the historical roll rates as it compares every loan at every time step and not just a loan based on last month vs this month.<br><br>The roll rates are based on loan counts and not $ balances"
            st.markdown('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
            rr_mat_df = df[df[metric_col]=="Matrix"]
            roll_rate_matrix(rr_mat_df, ds_orig_qtr, pds_orig_qtr, self.app_params)

        with _decile:
            byline="""The deciles are 10 equally sized buckets representing 10% of the development sample with bucket 1 being the worst 10% of applications in the development sample and bucket 10 being the best 10%. The buckets show the upper and lower bounds of scores contained within the buckets.<br><br>The reason why we view this data through deciles is because we’re specifically interested in whether roll rates are increasing or decreasing through time for the same parts of the score distribution i..e the same bucket. The portfolio roll rate may increase because the portfolio origination composition has tilted toward higher risk loans but the this page allows the user to determine whether the same risk buckets are performing the similarly through time"""
            st.markdown('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
            rr_mat_dec_df = df[df[metric_col]=="Matrix By Decile"]
            roll_rate_matrix_decile(rr_mat_dec_df, ds_orig_qtr, pds_orig_qtr, self.app_params)

        with _scoreband:
            byline = "The scorecard bands are 20 equally sized buckets representing 5% of the development sample with bucket 1 being the worst 5% of applications in the development sample and bucket 20 being the best 5%. The buckets show the upper and lower bounds of scores contained within the buckets.<br><br>The reason why we view this data through scorecard bands is because we’re specifically interested in whether roll rates are increasing or decreasing through time for the same parts of the score distribution i..e the same bucket. The portfolio roll rate may increase because the portfolio origination composition has tilted toward higher risk loans but the this page allows the user to determine whether the same risk buckets are performing the similarly through time<br><br>This is breakdown is merely a more granular view of the deciles."
            st.markdown('<p class="subhead-font">'+ byline +"</p>", unsafe_allow_html=True)
            rr_mat_sb_df = df[df[metric_col]=="Matrix By Scorecard Band"]
            roll_rate_matrix_sb(rr_mat_sb_df, ds_orig_qtr, pds_orig_qtr, self.app_params)