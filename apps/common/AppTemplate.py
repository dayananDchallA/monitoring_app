from abc import ABC, abstractmethod
import streamlit as st
from streamlit.runtime.scriptrunner.script_runner import get_script_run_ctx
from apps.common import Loader, Loaders


class AppTemplate(ABC):
    """
    This is a template class that streamlit applications can inherit from that automatically structures them for use in a Multi-page application.

    A number of convenience methods are also included within the template.
    
    """

    def __init__(self, title=None, params=None, debug = False, home_app="", **kwargs):
        self.title = title
        self.home_app = home_app
        self.app_params = params['apps'].get(title,{})
        self.general_params = params.get('general',{})
        self.debug = debug
        self.__dict__.update(kwargs)


    def navigate_to_page(self, page: str) -> None:
        ctx = get_script_run_ctx()
        if ctx is None:
            raise RuntimeError("Failed to get the script run context.")
        
        st.query_params.page = page
        st.session_state.current_page = page
        st.rerun()


    def load(self):
        try:
            st.query_params.page = self.title


            #with Loader("Now loading {}".format(self.title), loader_name=Loaders.standard_loaders,index=[3,0,5]):               
            with st.empty().container():
                if self.title!=self.home_app:
                    st.html("""<a href="/?page={}" target="_parent">Home</a>""".format(self.home_app))
                self.run()
      
        except Exception as e:
            st.error(f"Error loading page '{self.title}': {e}")
            st.exception(e)


    @abstractmethod
    def run(self):
        raise NotImplementedError("Each page must implement a `run` method.")