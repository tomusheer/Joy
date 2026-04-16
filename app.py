import streamlit as st
from src.recommend import get_recommendations

st.set_page_config(page_title="JoyBuy Query Refinement", layout="centered")

st.title("JoyBuy Query Refinement")
st.caption("Generate grouped search refinement tiles for e-commerce queries.")

query = st.text_input("Enter a search query", placeholder="e.g. aptamil, lipstick, headphones")

if st.button("Generate recommendations", type="primary"):
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Generating recommendations..."):
            result = get_recommendations(query.strip())

        if "error" in result:
            st.error(result["error"])
        else:
            provider = result.get("_provider")
            if provider:
                st.caption(f"Provider: {provider}")

            if result.get("query_type_label"):
                st.subheader(result["query_type_label"])

            notes = result.get("notes", [])
            for note in notes:
                st.info(note)

            groups = result.get("groups", [])
            if groups:
                for group in groups:
                    header = group.get("header", "Group")
                    tiles = group.get("tiles", [])
                    st.markdown(f"### {header}")
                    if tiles:
                        cols = st.columns(min(len(tiles), 4))
                        for i, tile in enumerate(tiles):
                            cols[i % len(cols)].button(tile, disabled=True, key=f"{header}_{i}_{tile}")
                    else:
                        st.write("No tiles returned.")
            else:
                st.json(result)