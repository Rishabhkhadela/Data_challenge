import streamlit as st

from ai_hiring_intelligence import __version__
from ai_hiring_intelligence.core.config import get_settings


def main() -> None:
    settings = get_settings()
    st.set_page_config(
        page_title=settings.app_name,
        layout="wide",
    )
    st.title(settings.app_name)
    st.caption(f"Version {__version__} | Environment {settings.app_env}")
    st.info("Boilerplate application shell. Business logic is not implemented yet.")


if __name__ == "__main__":
    main()
