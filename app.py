import streamlit as st
from src.recommend import get_recommendations

st.set_page_config(page_title="Search Tile Playground", layout="wide")

st.title("Search Tile Playground")
st.caption("Test grouped search refinement labels for random keywords.")

query = st.text_input(
    "Enter a search keyword",
    placeholder="e.g. wireless earbuds, tshirt, apple, baby formula"
)

if st.button("Generate recommendations", type="primary"):
    if not query.strip():
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Generating recommendations..."):
            result = get_recommendations(query.strip())

        if "error" in result:
            st.error(f"Error: {result['error']}")
            if "raw" in result:
                with st.expander("Raw response"):
                    st.write(result["raw"])
        else:
            groups = result.get("groups", [])

            top1, top2, top3 = st.columns([2, 2, 2])

            with top1:
                st.metric("Query", result.get("query", query))

            with top2:
                st.metric("Query type", result.get("query_type_label", "Unknown"))

            with top3:
                st.metric("Group count", len(groups))

            notes = result.get("notes", [])
            if notes:
                for note in notes:
                    st.info(note)

            brand_group_present = any(
                group.get("header", "").strip().lower() == "brand"
                for group in groups
            )

            if brand_group_present:
                st.info(
                    "Prototype note: brand labels are sample outputs for evaluation only. "
                    "Production should use actual JoyBuy available brands from catalog data."
                )

            if not groups:
                st.warning("No groups returned.")
            else:
                for group in groups:
                    with st.container(border=True):
                        st.subheader(group.get("header", "Untitled"))
                        tiles = group.get("tiles", [])

                        if tiles:
                            cols = st.columns(min(len(tiles), 6))
                            for i, tile in enumerate(tiles[:6]):
                                with cols[i]:
                                    st.button(
                                        tile,
                                        key=f"{group.get('header', 'group')}_{i}_{tile}"
                                    )
                        else:
                            st.write("No tiles.")