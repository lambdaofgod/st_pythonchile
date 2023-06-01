import streamlit as st

from helpers import *


def get_events_data():
    # Shared gsheet_id
    gsheet_id = "1nctiWcQFaB5UlIs6z8d1O6ZgMHFDMAoo3twVxYnBUws"
    # Data for the talks (charlas)
    df = read_googlesheet(gsheet_id, "charlas", ["Fecha", "Orden", "Track"]).rename(
        columns={
            "Fecha": "Date",
            "Orden": "Order",
            "Autor": "Author",
            "Título": "Title",
        },
    )
    df.columns = [unidecode(s.strip()) for s in df.columns]
    df["author_clean_name"] = df["Author"].apply(clean_name)
    df = df.loc[df["Author"] != "", :]  # Filter out empty rows
    df = df.loc[df["Title"] != "", :]  # Filter out empty rows
    return df


def display_search(df):
    """
    Displays the search bar interface
    """
    # A little bit of cleaning, to make searching more easy
    # df_lower should get the columns
    columns_spanish_names = [
        "Evento",
        "Lugar",
        "Fecha",
        "Tipo",
        "Autor",
        "Título",
        "Video",
        "Recursos",
    ]
    columns_english_names = [
        "Event",
        "Location",
        "Date",
        "Type",
        "Author",
        "Title",
        "Video",
        "Resources",
    ]

    df = df.copy().rename(
        columns=dict(zip(columns_spanish_names, columns_english_names))
    )
    df_lower = df.copy()
    df_lower.columns = [unidecode(s.lower().strip()) for s in df_lower.columns]
    for col in df_lower.columns:
        df_lower[col] = df_lower[col].apply(lambda x: unidecode(x.lower().strip()))

    # We use the following columns to show data
    show_cols = columns_english_names

    # Start the page
    st.title("Python Chile: Event Records")
    # Intro text
    st.caption(
        f"Discover and learn from the more than **{df.shape[0]}** talks, keynotes, and workshops we have held at Python Chile."
    )

    c1, c2, c3 = st.columns([8, 1, 1])
    # The search bar
    examples = [
        "data science",
        "machine learning",
        "streamlit",
        "pyladies",
        "comunidad",
        "industria",
    ]
    if "example" not in st.session_state:
        st.session_state.example = examples[random.randint(0, len(examples) - 1)]
    text_search = c1.text_input(
        "Search by author, title, description, or tags. Separate concepts with a semicolon (;)",
        placeholder=st.session_state.example,
    )
    text_search = unidecode(text_search.lower())
    # Get keywords from search bar
    keyword_list = [keyword.strip() for keyword in text_search.split(";")]
    # Add options
    talk_options = ["Any", "Talk", "Keynote", "Workshop"]
    type_sel = c2.selectbox("Type", talk_options)
    c3.markdown("")
    c3.markdown("")
    rec_required = c3.checkbox("Recorded", value=False)

    # Configure how many cards
    N_cards_per_col = 5

    if text_search:
        mask = get_mask_for_keyword_list(df_lower, keyword_list)
        if type_sel != talk_options[0]:
            mask_new = df_lower["type"] == type_sel.lower()
            mask = np.logical_and(mask, mask_new)
        if rec_required:
            mask_new = df_lower["video"] != ""
            mask = np.logical_and(mask, mask_new)
        df_search = df.loc[mask, show_cols].reset_index()
        # Show the cards
        N_cards_per_col = 5
        for n_row, row in df_search.iterrows():
            i = n_row % N_cards_per_col
            if i == 0:
                st.write("")
                cols = st.columns(N_cards_per_col, gap="large")
            create_card(row, cols[n_row % N_cards_per_col])
    else:
        # Configure how many cards
        N_cards = N_cards_per_col * 1
        # Show the cards
        st.write("#### Latest videos")
        df_latest = df[show_cols].head(N_cards).reset_index()
        for n_row, row in df_latest.iterrows():
            i = n_row % N_cards_per_col
            if i == 0:
                st.write("")
                cols = st.columns(N_cards_per_col, gap="large")
            create_card(row, cols[n_row % N_cards_per_col])
        st.write("")
        st.write("#### Randomly selected videos")
        df_random = df[show_cols].sample(N_cards).reset_index()
        for n_row, row in df_random.iterrows():
            i = n_row % N_cards_per_col
            if i == 0:
                st.write("")
                cols = st.columns(N_cards_per_col, gap="large")
            create_card(row, cols[i])

    # Add color to cards
    add_color_to_cards()
