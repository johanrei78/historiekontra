# -*- coding: utf-8 -*-
"""
WW1 – Historisk vs alternativt scenario
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import copy

st.set_page_config(page_title="WW1 – Historisk vs alternativt", layout="wide")
st.title("Første verdenskrig – Historisk vs alternativ utvikling")

# --- Last inn slagdata fra JSON ---
try:
    with open("data/slag.json", encoding="utf-8") as f:
        slag = json.load(f)
except FileNotFoundError:
    st.error("Finner ikke 'data/slag.json'. Legg filen i /data/ og kjør appen på nytt.")
    st.stop()

# --- Original tidslinje (grunnlag) ---
tidslinje_original = {
    "1914": {"Hendelse": "Skuddene i Sarajevo", 
             "Beskrivelse": "Skuddene mot erkehertug Franz Ferdinand utløste krigen.", 
             "Konsekvens": "Østerrike-Ungarn erklærer krig mot Serbia."},
    "1915": {"Hendelse": "Kjemisk krigføring introduseres", 
             "Beskrivelse": "Giftgass brukes ved Ypres.", 
             "Konsekvens": "Endrer krigens brutalitet."},
    "1916": {"Hendelse": "Slagene ved Somme og Verdun", 
             "Beskrivelse": "To av de blodigste slagene under krigen.", 
             "Konsekvens": "Store tap på begge sider, liten framgang."},
    "1917": {"Hendelse": "USA går inn i krigen", 
             "Beskrivelse": "USA erklærer krig mot Tyskland.", 
             "Konsekvens": "Forsterker de alliertes styrker betydelig."},
    "1918": {"Hendelse": "Våpenhvile signeres", 
             "Beskrivelse": "Tyskland overgir seg og våpenhvilen trer i kraft 11. november.", 
             "Konsekvens": "Krigen avsluttes, Versaillestraktaten senere i 1919."}
}

# --- Session state for elevenes valg ---
if "valg" not in st.session_state:
    st.session_state.valg = {}

# --- UI: velg slag og ta beslutning ---
st.subheader("Beslutningsspill")
slag_valg = st.selectbox("Velg et slag:", list(slag.keys()))

if slag_valg:
    data = slag[slag_valg]
    st.write(f"**{slag_valg} ({data['År']})**")
    st.write("Faktisk utfall:", data["Faktisk"])

    valg = st.radio("Hva ville du gjort?", list(data["Valg"].keys()))

    if st.button("Lagre mitt valg"):
        st.session_state.valg[slag_valg] = valg
        st.success(f"Ditt valg for {slag_valg} er lagret!")

# --- Bygg alternativ tidslinje og kart ---
alternativ_tidslinje = copy.deepcopy(tidslinje_original)
historisk_kartpunkter = []
alternativ_kartpunkter = []

for slag_navn, data in slag.items():
    # Historiske punkter (alltid)
    historisk_kartpunkter.append({
        "Navn": slag_navn,
        "Lat": data["Lat"],
        "Lon": data["Lon"],
        "Scenario": "Historisk"
    })

    # Elevenes valg -> alternative konsekvenser
    if slag_navn in st.session_state.valg:
        valgt = st.session_state.valg[slag_navn]
        alternativ_kartpunkter.append({
            "Navn": slag_navn,
            "Lat": data["Lat"],
            "Lon": data["Lon"],
            "Scenario": "Alternativ"
        })
        # legg inn evt. nye hendelser
        if "Effekter" in data["Valg"][valgt]:
            for år, nytt in data["Valg"][valgt]["Effekter"].items():
                alternativ_tidslinje[år] = nytt
    else:
        alternativ_kartpunkter.append({
            "Navn": slag_navn,
            "Lat": data["Lat"],
            "Lon": data["Lon"],
            "Scenario": "Historisk"
        })

# --- Tidslinje med slider ---
st.subheader("Utforsk tidslinjen")
år_valg = st.slider("Velg år", min_value=1914, max_value=1918, step=1)
år_str = str(år_valg)

if år_str in alternativ_tidslinje:
    hendelse = alternativ_tidslinje[år_str]
else:
    hendelse = tidslinje_original.get(år_str, {"Hendelse": "Ingen registrert hendelse", 
                                               "Beskrivelse": "", 
                                               "Konsekvens": ""})

st.markdown(f"### {år_valg}: {hendelse['Hendelse']}")
st.write("**Beskrivelse:**", hendelse["Beskrivelse"])
st.write("**Konsekvens:**", hendelse["Konsekvens"])

# --- Kartvisning: side om side ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Historisk")
    df_hist = pd.DataFrame(historisk_kartpunkter)
    if not df_hist.empty:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_hist,
            get_position='[Lon, Lat]',
            get_color='[0, 100, 200, 160]',  # blå = historisk
            get_radius=60000,
            pickable=True
        )
        tooltip = {"html": "<b>{Navn}</b><br/>Scenario: {Scenario}"}
        view_state = pdk.ViewState(latitude=df_hist["Lat"].mean(), longitude=df_hist["Lon"].mean(), zoom=4)
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

with col2:
    st.markdown("### Alternativ")
    df_alt = pd.DataFrame(alternativ_kartpunkter)
    if not df_alt.empty:
        layer_alt = pdk.Layer(
            "ScatterplotLayer",
            data=df_alt,
            get_position='[Lon, Lat]',
            get_color='[200, 30, 0, 160]',  # rød = alternativ
            get_radius=60000,
            pickable=True
        )
        tooltip_alt = {"html": "<b>{Navn}</b><br/>Scenario: {Scenario}"}
        view_state_alt = pdk.ViewState(latitude=df_alt["Lat"].mean(), longitude=df_alt["Lon"].mean(), zoom=4)
        st.pydeck_chart(pdk.Deck(layers=[layer_alt], initial_view_state=view_state_alt, tooltip=tooltip_alt))
