import streamlit as st
from apps.common import AppTemplate
from core import page_logo_and_title,create_app_type_param
from apps.vintagecurves.vintage_utils import read_vintage_data, vin_params_layout, vin_qtr_plots, vin_dec_plots, vin_sb_plots


class VintageCurvesPage(AppTemplate):

    def run(self):

        # # Create a single select prompt
        vin_df,vin_qtr_df,vin_dec_df,vin_sb_df = read_vintage_data(self.app_params)

        # vin_glance_df = read_vintage_glance_data(filter_condition)

        # Create the logo, title and related elements
        page_logo_and_title("Vintage Curves Analysis",
                            byline="""The vintage curves can be used to review calibration and stability of performance through time, calibration is indicated by the decile and bucket tables and stability is measured through the consistency of decile and scorecard band curves through time.
                        <br><br>The vintage curves presented here are based on the day count definition of default and not the $ inferred arrears used in other standard reports, hence there will be differences
                        <br><br>The quarterly curves use all originated loans but the decile and scorecard bands use cuts of the training data based on score.""")
                        #<br><br>See the last table for roll rates between the early stage defaults and late stage""")

        st.markdown('#')
        
        # vin_glance_df = vin_glance_df[['Decile', 'Data Description', 'Probability']]
        # vin_glance_df = sort_df_by_decile(vin_glance_df, 'Decile')
        # # Pivot the DataFrame to have 'dev' and 'prod' probabilities side by side for each decile
        # pivot_df = vin_glance_df.pivot(index='Decile', columns='Data Description', values='Probability').reset_index()

        # # Sort the DataFrame by the extracted numeric part of 'decile'
        # pivot_df['decile_num'] = pivot_df['Decile'].apply(lambda x: int(x.split(',')[0]))
        # pivot_df = pivot_df.sort_values(by='decile_num').drop(columns='decile_num')
        
        # # Calculate the difference between 'dev' and 'prod' probabilities
        # pivot_df['difference'] = pivot_df['Post-Dev Sample'] - pivot_df['Dev Sample']

        # # Function to format the difference with arrows
        # def format_diff(diff):
        #     if diff > 0:
        #         return f"↑ {diff:.2f}"
        #     elif diff < 0:
        #         return f"↓ {diff:.2f}"
        #     else:
        #         return f"{diff:.2f}"

        # # Apply custom formatting for display
        # styled_df = pivot_df[['Decile','Dev Sample', 'Post-Dev Sample', 'difference']].style.applymap(
        #     lambda x: 'color: red' if x < 0 else 'color: green' if x > 0 else '',
        #     subset=['difference']
        # ).format(format_diff, subset=['difference'])

        # # Display the table in Streamlit
        # st.write("##### Summarized probability of default view")
        # st.dataframe(styled_df,hide_index=True)

        # #st.dataframe(vin_glance_df.style.hide())

        ds_orig_qtr, pds_orig_qtr = vin_params_layout(vin_df, self.app_params)

        _quarterly, _decile, _scoreband = st.tabs(["Quarterly","Decile","Scorecard Band"])

        with _quarterly:
            vin_qtr_plots(vin_qtr_df, ds_orig_qtr,pds_orig_qtr, self.app_params)

        with _decile:
            st.markdown("### Test")
            vin_dec_plots(vin_dec_df, ds_orig_qtr, pds_orig_qtr, self.app_params)

        with _scoreband:
            vin_sb_plots(vin_sb_df, ds_orig_qtr, pds_orig_qtr, self.app_params)