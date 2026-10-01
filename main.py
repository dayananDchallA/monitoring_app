import streamlit as st
from core import MultiPageApp
from apps.home.home import HomePage
from apps.rollratesmom.roll_rates_mom import RollRatesMonthPage
from apps.vintagecurves.vintage_curves import VintageCurvesPage
from apps.acceptancerate.acceptance_rates import AcceptanceRatesPage
from apps.rollratesmatrix.roll_rates_mat import RollRatesMatrixPage
from apps.systemstability.stability import SystemStabilityPage

if __name__ == "__main__":

    app = MultiPageApp(debug=False)

    app.add_page("", HomePage, is_home=True)
    app.add_page("Acceptance Rate", AcceptanceRatesPage)
    app.add_page("Roll Rates MoM", RollRatesMonthPage)
    app.add_page("Roll Rates Matrix", RollRatesMatrixPage)
    app.add_page("Vintage Curves", VintageCurvesPage)
    app.add_page("Vintage Curves", VintageCurvesPage)
    app.add_page("System Stability", SystemStabilityPage)

    app.run()