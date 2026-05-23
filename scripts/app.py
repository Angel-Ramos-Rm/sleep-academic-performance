from pathlib import Path
import streamlit as st


dir_path = Path(__file__).parent


# Note that this needs to be in a method so we can have an e2e playwright test.
def run() -> None:
    page = st.navigation(
        {
            "Pages": [
                st.Page(
                    dir_path/"introduccion.py", title="Bienvenido"
                )
            ]
        }
    )
    page.run()


if __name__ == "__main__":
    run()


    