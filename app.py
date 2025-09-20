# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import pydeck as pdk
import json

st.set_page_config(page_title="WW1 – Interaktiv historiekart", layout="wide")
st.title("Første verdenskrig – Historisk vs alternativt scenario")

# --- Last inn slagdata ---
try:
    with open("data/slag.json", encoding="utf-8") as f:
        slag = json.load(f)
except FileNotFoundError:
    st.error("Finner ikke 'data/slag.json'. Legg filen i /data/ og redeploy.")
    st.stop()

# --- Session state ---
if "valg" not in st.session_state:
    st.session_state.valg = {}
if "valgt_slag" not in st.session_state:
    st.session_state.valgt_slag = None

# --- Sidebar: år-filter og detaljer ---
st.sidebar.header("Filter og valg")
år_min = int(min([data["År"] for data in slag.values()]))
år_max = int(max([data["År"] for data in slag.values()]))
år_filter = st.sidebar.slider("Vis slag mellom år", år_min, år_max, (år_min, år_max))

if st.session_state.valgt_slag:
    navn = st.session_state.valgt_slag
    data = slag[navn]
    st.sidebar.markdown(f"**{navn} ({data['År']})**")
    st.sidebar.markdown(f"Historisk utfall: {data['Faktisk']}")
    valg = st.sidebar.radio("Hva ville du gjort?", list(data["Valg"].keys()))
    if st.sidebar.button("Lagre valg"):
        st.session_state.valg[navn] = valg
        st.sidebar.success(f"Valg for {navn} lagret!")
else:
    st.sidebar.markdown("Klikk på et slag på kartet for å se detaljer her.")

# --- Bygg kartpunkter ---
historisk_kart = []
alternativ_kart = []

for navn, data in slag.items():
    if år_filter[0] <= data["År"] <= år_filter[1]:
        historisk_kart.append({
            "Navn": navn,
            "Lat": data["Lat"],
            "Lon": data["Lon"],
            "Kontroll": "Historisk"
        })
        valgt = st.session_state.valg.get(navn)
        alternativ_kart.append({
            "Navn": navn,
            "Lat": data["Lat"],
            "Lon": data["Lon"],
            "Kontroll": valgt if valgt else "Historisk"
        })

# --- Tabs for Tidslinje og Kart ---
tab1, tab2 = st.tabs(["Tidslinje", "Kart"])

with tab1:
    st.subheader("Alternativ tidslinje")
    for navn, data in slag.items():
        if år_filter[0] <= data["År"] <= år_filter[1]:
            valgt = st.session_state.valg.get(navn)
            beskrivelse = data["Valg"][valgt]["Beskrivelse"] if valgt else data["Faktisk"]
            color = "blue" if not valgt else "red"
            with st.expander(f"{navn} ({data['År']})"):
                st.markdown(f"<span style='color:{color}'>{beskrivelse}</span>", unsafe_allow_html=True)

with tab2:
    st.subheader("Historisk vs alternativt kart")
    col1, col2 = st.columns(2)

    # --- Historisk kart ---
    with col1:
        st.markdown("### Historisk kontroll")
        df_hist = pd.DataFrame(historisk_kart)
        layer_hist = pdk.Layer(
            "IconLayer",
            data=df_hist,
            get_icon="https://img.icons8.com/ios-filled/50/0000FF/flag.png",
            get_size=4,
            size_scale=15,
            get_position="[Lon, Lat]",
            pickable=True
        )
        view_state_hist = pdk.ViewState(latitude=df_hist["Lat"].mean(), longitude=df_hist["Lon"].mean(), zoom=4)
        st.pydeck_chart(pdk.Deck(layers=[layer_hist], initial_view_state=view_state_hist,
                                 tooltip={"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}))

    # --- Alternativt kart ---
    with col2:
        st.markdown("### Alternativ kontroll")
        df_alt = pd.DataFrame(alternativ_kart)
        layer_alt = pdk.Layer(
            "IconLayer",
            data=df_alt,
            get_icon="https://img.icons8.com/ios-filled/50/FF0000/flag.png",
            get_size=4,
            size_scale=15,
            get_position="[Lon, Lat]",
            pickable=True
        )
        view_state_alt = pdk.ViewState(latitude=df_alt["Lat"].mean(), longitude=df_alt["Lon"].mean(), zoom=4)
        st.pydeck_chart(pdk.Deck(layers=[layer_alt], initial_view_state=view_state_alt,
                                 tooltip={"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}))

st.info("Klikk på et flagg på kartet for å vise detaljer i sidebar. Tidslinjen og alternativt kart oppdateres etter valg.")
