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
                ),
                st.Page(
                    dir_path / "data.py", title="Exploración de datos"
                ),
                st.Page(
                    dir_path / "distribuciones.py", title="Distribuciones y Dispersión"
                ),
                st.Page(
                    dir_path / "correlacion.py", title="Correlación"
                ),
            ]
        }
    )
    page.run()


if __name__ == "__main__":
    run()


    