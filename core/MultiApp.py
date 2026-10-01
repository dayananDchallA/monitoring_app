from abc import ABC
import streamlit as st
from streamlit.runtime.scriptrunner.script_runner import get_script_run_ctx
from typing import Dict, Type
from apps import AppTemplate
from PIL import Image
from core.misc_utils import loadconfig


HIDE_ST_STYLE = """
                <style>
div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
				        .appview-container .main .block-container{
                            padding-top: 0rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 0rem;
                        }  
                        .appview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        .reportview-container {
                            padding-top: 0rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 0rem;
                        }
                        .reportview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        header[data-testid="stHeader"] {
                            z-index: -1;
                        }
                        div[data-testid="stToolbar"] {
                        z-index: 100;
                        }
                        div[data-testid="stDecoration"] {
                        z-index: 100;
                        }
                        .reportview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        div[data-stale="false"] > iframe[title="hydralit_components.NavBar.nav_bar"] {
                        z-index: 99;
                    }
                </style>
                """


class MultiPageApp(ABC):
    def __init__(self, hide_st_stuff = True, debug=False):
        self.pages: Dict[str, Type[AppTemplate]] = {}
        self.hiddenpages: Dict[str, Type[AppTemplate]] = {}
        self.hide_st_stuff = hide_st_stuff
        self.home_app = None
        self.hidden_apps = []
        self.debug = debug
        if self.debug:
            self.hide_st_stuff = False
        self.setup_app()
        self.params = loadconfig()

    def add_page(self, title: str, page_class: Type[AppTemplate], is_home=False, is_hidden = False) -> None:

        if is_home:
            self.home_app = title
        

        if is_hidden:
            self.hiddenpages[title] = page_class(title=title, params=self.params, debug=self.debug, home_app=self.home_app)
        else:
            self.pages[title] = page_class(title=title, params=self.params, debug=self.debug, home_app=self.home_app)

    def setup_app(self) -> None:

        img = Image.open("./static/favicon.png")

        st.set_page_config(
            page_title="Model Monitoring Application",
            page_icon=img,
            layout="wide"
        )

        if self.hide_st_stuff:
            st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)


    # Utility function to get the page from URL query parameters
    def get_page_from_url(self) -> str:
        return st.query_params.get("page", self.home_app)

    # Function to navigate to a new page
    def navigate_to_page(self, page: str) -> None:
        ctx = get_script_run_ctx()
        if ctx is None:
            raise RuntimeError("Failed to get the script run context.")
        
        st.query_params.page = page
        st.session_state.current_page = page
        st.rerun()


    def run(self) -> None:

        url_page = self.get_page_from_url()

        # Initialize session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = url_page

        st.sidebar.image("./static/logo.png")
        st.sidebar.header("Monitoring Application :stethoscope:",divider="rainbow")
        st.sidebar.subheader('Analysis Selector')


        if url_page in self.hiddenpages.keys():
            current_page_class = self.hiddenpages[url_page]
            current_page_class.load()
        else:
            selected_page = st.sidebar.selectbox(
                "Select the analysis you want to view",
                options=list(self.pages.keys()),
                index=list(self.pages.keys()).index(url_page)
            )
            # Handle page navigation
            if selected_page != url_page:
                self.navigate_to_page(selected_page)

            # Render the current page
            current_page_class = self.pages[selected_page]
            current_page_class.load()