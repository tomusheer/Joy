import streamlit as st
from src.recommend import get_recommendations

st.set_page_config(page_title="JoyBuy Query Refinement", layout="centered")

SAMPLE_QUERIES = [
    "aptamil",
    "lego",
    "lipstick",
    "headphones",
    "cooking oil",
    "tshirt",
]

def set_query(q):
    st.session_state["query"] = q

st.title("JoyBuy Query Refinement")
st.caption("Generate grouped search refinement tiles for e-commerce queries.")

if "query" not in st.session_state:
    st.session_state["query"] = ""

st.markdown("### Sample queries")
cols = st.columns(3)
for i, q in enumerate(SAMPLE_QUERIES):
    cols[i % 3].button(q, on_click=set_query, args=(q,), key=f"sample_{q}")

query = st.text_input(
    "Enter a search query",
    key="query",
    placeholder="e.g. aptamil, lipstick, headphones",
)

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
            query_type = result.get("query_type")
            query_type_label = result.get("query_type_label")
            notes = result.get("notes", [])
            groups = result.get("groups", [])

            top_cols = st.columns(2)
            with top_cols[0]:
                if query_type_label:
                    st.subheader(query_type_label)
                    if query_type:
                        st.caption(f"Code: {query_type}")
            with top_cols[1]:
                if provider:
                    st.subheader("Source")
                    st.caption(provider)

            if notes:
                for note in notes:
                    st.info(note)

            if groups:
                for group in groups:
                    header = group.get("header", "Group")
                    tiles = group.get("tiles", [])

                    st.markdown(f"### {header}")

                    if tiles:
                        row_cols = st.columns(min(4, len(tiles)))
                        for i, tile in enumerate(tiles):
                            row_cols[i % len(row_cols)].button(
                                tile,
                                disabled=True,
                                key=f"{header}_{i}_{tile}"
                            )
                    else:
                        st.caption("No tiles returned for this group.")
            else:
                st.warning("No recommendation groups returned.")

            with st.expander("View raw response"):
                st.json(result)