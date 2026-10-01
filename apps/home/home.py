import streamlit as st
import pandas as pd
from apps.common import AppTemplate
from core import page_logo_and_title


class HomePage(AppTemplate):

    def run(self):

        page_logo_and_title("Model Monitoring Application :stethoscope:")

        st.markdown('####')

        with st.expander(" ",expanded=True,):

            _c1, _c2 = st.tabs([":mag:",":open_book:"])
            
            with _c1:
                st.markdown('####')
                st.markdown("#### Analysis Available")
                st.markdown("""
                            | Name | Description |
                            | :----------------------- | :----------------------------------------------------------- |
                            | [Acceptance Rate](/?page=Acceptance+Rate&monitoring=paf) | The approval rates of higher risk customers can be tracked here, the approval rate and origination rates can be used as a lead indicator to future book performance |
                            | [Roll Rates MoM](/?page=Roll+Rates+MoM) | The roll rates month-on-month are intended to show the roll rate (% of accounts within a given bucket the previous month, rolling up to the next bucket e.g. 60-89 to 90-119). |
                            | [Roll Rates Matrix](/?page=Roll+Rates+Matrix&monitoring=paf) | The roll rate month-on-month analysis gives an overview through time of upward roll rates e.g. from bucket 1 to bucket 2. This is monitored because increases in roll rates between the development sample and post-development sample may mean we have an increase in actual delinquent loans vs predicted delinquent (although this can be verified by looking at the vintage page). |
                            | [Vintage Curves Analysis](/?page=Vintage+Curves) | The vintage curves can be used to review calibration and stability of performance through time, calibration is indicated by the decile and bucket tables and stability is measured through the consistency of decile and scorecard band curves through time. |
                            | [System Stability](/?page=System+Stability&monitoring=paf) | The system stability allows us to see changes in the scoring distribution of Through the Door (TTD) applicants and is a lead indicator to risk in the book. |
                            """, unsafe_allow_html=True)


            # with _c1:

            #     st.markdown("#### Analysis Available")
            #     st.markdown("""
            #                 | Name | Description |
            #                 | :----------| :------------|
            #                 | [Roll Rates MoM](/?page=Roll+Rates+MoM) | The roll rates month-on-month are intended to show the roll rate (% of accounts within a given bucket the previous month, rolling up to the next bucket e.g. 60-89 to 90-119). |
            #                 | [Roll Rates Matrix](/?page=Roll+Rates+Matrix) | The roll rates matrix |
            #                 | [Acceptance Rate](/?page=Acceptance+Rate) | The approval rates of higher risk customers can be tracked here, the approval rate and origination rates can be used as a lead indicator to future book performance |
            #                 | [Vintage Curves Analysis](/?page=Vintage+Curves) | The vintage curves can be used to review calibration and stability of performance through time, calibration is indicated by the decile and bucket tables and stability is measured through the consistency of decile and scorecard band curves through time. |
            #                 | [Characteristic Analysis - Approve vs Decline](/?page=CA+-+Approve+vs+Decline) | Characteristic Analysis allows you to view performance and approval rates for the underlying modelling variables and the buckets/ bins used to construct the model predictions. |
            #                 | [Characteristic Analysis - Feature Performance](/?page=Characteristic+Analysis+-+FP) | Characteristic Analysis allows you to view performance and approval rates for the underlying modelling variables and the buckets/ bins used to construct the model predictions. |
            #                 | [Population Stability](/?page=Population+Stability) | The Population Stability Index (or PSI) is a measure that determines shifts in portfolio between the expected population- this is the population the model is trained on- and the actual, this is the loans post the training data. |
            #                 | [Loss Rate](/?page=Loss+Rate) | The Loss Rate |
            #                 | [System Stability](/?page=System+Stability) | The system stability allows us to see changes in the scoring distribution of Through the Door (TTD) applicants and is a lead indicator to risk in the book. |
            #                 """, unsafe_allow_html=True)

                st.markdown('####')

                st.subheader("Purpose :mag:")
                st.markdown("There are three main elements that scorecard monitoring is intended to do.")

                st.markdown("""
                            | Element | Purpose |
                            |:--------|:--------|
                            |Discrimination | How well does the model discriminate between good and bad loans, this is most often evidenced by gini but can be more commonly understood via metrics such as the proportion of total defaults that a given % of applications/ originations capture e.g. 70% of all defaults are in the bottom 10% of scores.<br><br>High levels of discrimination are key to a good scorecard model and pages such as vintage analysis, characteristic analysis .. . . <br><br>Given that default outcomes modelled are often based over 18m, there are also early default indicators embedded within the monitoring that will allow early warning on discrimination changes.|
                            |Stability | How well the model does through time and across populations, specifically, is Gini maintained for the model through time? Is Gini maintained for the different segments of the population? Stability is key to maintaining model performance.<br><br>The monitoring application focusses on stability through the following pages: <br><kbd> </kbd><kbd> </kbd><kbd>- System Stablity</kbd> <br><br>Changes in stability are evidenced by changes in gini over time which may then be attributed to changes in the book composition i.e. gini increased by 2% as we now originate more of a cohort for which the model has a higher gini.|
                            |Calibration | How well the predicted outcomes calibrate to the actual outcomes. For example, for a given score range {200-300}, if the model says the expected probability of default for this cohort is 40% then do 40% of accounts within this cohort actually default?<br><br>Calibration is evidenced by the expected PD vs the actual PD and is included in page: |
                        """, unsafe_allow_html=True)
                    ##st.markdown('####')

            

            with _c2:
                st.header("Guide :open_book:")
                st.markdown("Throughout the monitoring application, you will see the following aggregations used- below are the definitions:")
                st.markdown("""
                            | Aggregation | Interpretation |
                            |:------------|:---------------|
                            | Dev Sample (or “Development Sample”) | The development sample refers to the training data used to construct the scorecard model. <br><br> This is the data the model is built on and is the predictions made are based on what the algorithms have learned from this training data. <br><br> Details on the development samples are provided in the next table.|
                            | Post Dev Sample (or “Post the Development Sample”) | Post Dev Sample refers to the period after the end of development sample and represents applications or originations that the model has not seen. <br><br> For stability and discrimination, we are interested in how the performance varies across time for this sample; for calibration, we are interested in how the models' predictions from the dev sample calibrate to the post dev sample. |
                            | Decile | Deciles are used throughout the analysis and are based on 10 equally sized buckets from the training data representing 10% of the scored training data each. They are used predominantly to compare the same credit risk through time e.g. is bucket 1 performing through time as it has done in the past. |
                            | Scorecard Band | Scorecard bands are a more granular form of the deciles and are 20 equally sized buckets from the training data representing 5% of the scored training data each. <br><br> Similar to deciles, they are also used to compare the same risk through time but at a more granular level. |
                            """, unsafe_allow_html=True)
                
            #     st.markdown("#### ")
            #     st.markdown("#### Details on the development samples:")
            #     st.markdown("""
            #                 | Development Sample | Sample Size and Composition | Time Period Used | Target Variable/ Default Definition |
            #                 |:-------------------|:---------------------------|:-----------------|:-----------------------------------|
            #                 | Consumer | Total: 110,623 <br><br> Originated: 93,664 <br><br> Declined: 16959 <br><br> | 01/07/2018 to 31/03/2022 | 90+ within 18 months of origination |
            #     """,unsafe_allow_html=True)

            #     st.info("&emsp; *the first of July 2018 is the first date where CCR contribution rates included coverage for the at least 50% of various products from the largest financial institutions, CCR data before this is less reliable due to lower contribution rates so, on bureau advice, we elect not to include.")
            #     st.markdown("#### ")
            #     st.markdown("""
            #                 | Post Development Sample | Time Period Used |
            #                 |:-------------------|:---------------------------|
            #                 | Consumer | 01/04/22 to Present |
            #     """,unsafe_allow_html=True)
            #     st.markdown("####")