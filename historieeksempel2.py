# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 13:42:52 2025

@author: johvik
"""

import streamlit as st
import pydeck as pdk
import pandas as pd

st.set_page_config(page_title="WW1: Historisk vs. alternativt kart", layout="wide")
st.title("Første verdenskrig – Historisk vs. alternativ utvikling")

# --- Original tidslinje ---
tidslinje_original = {
    "1914": {"Hendelse": "Skuddene i Sarajevo", "Beskrivelse": "Skuddene mot erkehertug Franz Ferdinand utløste krigen.", "Konsekvens": "Østerrike-Ungarn erklærer krig mot Serbia."},
    "1915": {"Hendelse": "Slaget ved Gallipoli", "Beskrivelse": "Allierte forsøkte å ta kontroll over Dardanellene.", "Konsekvens": "Kampene endte i nederlag for de allierte."},
    "1916": {"Hendelse": "Slaget ved Verdun", "Beskrivelse": "Et av de lengste og blodigste slagene i krigen.", "Konsekvens": "Store tap på begge sider, lite territorielt utbytte."},
    "1917": {"Hendelse": "USA går inn i krigen", "Beskrivelse": "USA erklærer krig mot Tyskland.", "Konsekvens": "Forsterker de alliertes styrker betydelig."},
    "1918": {"Hendelse": "Våpenhvile signeres", "Beskrivelse": "Tyskland overgir seg og våpenhvilen trer i kraft 11. november.", "Konsekvens": "Krigen avsluttes, Versaillestraktaten senere i 1919."}
}

# --- Slag med alternativer, effekter og kart ---
slag = {
    "Verdun": {
        "År": 1916,
        "Posisjon": {"Lat": 49.159, "Lon": 5.384},
        "Faktisk": "Frankrike forsvarte Verdun med enorme tap.",
        "Historisk_kart": {"Navn": "Verdun", "Lat": 49.159, "Lon": 5.384, "Kontroll": "Frankrike"},
        "Valg": {
            "Forsvar": {
                "Beskrivelse": "Frankrike holder linjen – store tap, men de stopper tyskerne.",
                "Effekter": {},
                "Kart": {"Navn": "Verdun", "Lat": 49.159, "Lon": 5.384, "Kontroll": "Frankrike"}
            },
            "Tilbaketrekning": {
                "Beskrivelse": "Frankrike mister Verdun, Tyskland får et strategisk overtak.",
                "Effekter": {
                    "1917": {"Hendelse": "USA nøler med å gå inn i krigen", "Beskrivelse": "Tysk styrke etter Verdun-seieren gjør USA mer forsiktige.", "Konsekvens": "Amerikansk inntreden utsettes eller uteblir."},
                    "1918": {"Hendelse": "Tyskland forhandler fra en sterk posisjon", "Beskrivelse": "Med Verdun i tysk kontroll og ingen amerikansk intervensjon, står Tyskland sterkere i forhandlinger.", "Konsekvens": "Krigen kan avsluttes på tysk vennligere vilkår."}
                },
                "Kart": {"Navn": "Verdun", "Lat": 49.159, "Lon": 5.384, "Kontroll": "Tyskland"}
            }
        }
    },
    "Somme": {
        "År": 1916,
        "Posisjon": {"Lat": 50.020, "Lon": 2.650},
        "Faktisk": "Britene gikk til frontalangrep, og tapene ble enorme.",
        "Historisk_kart": {"Navn": "Somme", "Lat": 50.020, "Lon": 2.650, "Kontroll": "Uavklart"},
        "Valg": {
            "Frontalangrep": {
                "Beskrivelse": "Store tap, liten framgang.",
                "Effekter": {},
                "Kart": {"Navn": "Somme", "Lat": 50.020, "Lon": 2.650, "Kontroll": "Uavklart"}
            },
            "Utsette angrep": {
                "Beskrivelse": "Tyskland får tid til å styrke linjene ytterligere.",
                "Effekter": {
                    "1917": {"Hendelse": "Tyskland dominerer vestfronten", "Beskrivelse": "Britisk nøling gir tyskerne styrke, og de allierte presses bakover.", "Konsekvens": "Stor risiko for at allierte mister moral og støtte."}
                },
                "Kart": {"Navn": "Somme", "Lat": 50.020, "Lon": 2.650, "Kontroll": "Tyskland"}
            }
        }
    }
}

# --- Session state ---
if "valg" not in st.session_state:
    st.session_state.valg = {}

# --- Elevens valg ---
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
alternativ_tidslinje = tidslinje_original.copy()
historisk_kartpunkter = []
alternativ_kartpunkter = []

for slag_navn, data in slag.items():
    # legg alltid inn historiske kartpunkter
    historisk_kartpunkter.append(data["Historisk_kart"])

    if slag_navn in st.session_state.valg:
        valgt = st.session_state.valg[slag_navn]
        konsekvenser = data["Valg"][valgt]["Effekter"]
        for år, nytt in konsekvenser.items():
            alternativ_tidslinje[år] = nytt
        alternativ_kartpunkter.append(data["Valg"][valgt]["Kart"])
    else:
        alternativ_kartpunkter.append(data["Historisk_kart"])

# --- Utforsk tidslinjen ---
st.subheader("Utforsk tidslinjen")
år_valg = st.slider("Velg år", min_value=1914, max_value=1918, step=1)
år_str = str(år_valg)

if år_str in alternativ_tidslinje:
    hendelse = alternativ_tidslinje[år_str]
else:
    hendelse = tidslinje_original[år_str]

st.subheader(f"{år_valg}: {hendelse['Hendelse']}")
st.write("**Beskrivelse:**", hendelse["Beskrivelse"])
st.write("**Konsekvens:**", hendelse["Konsekvens"])

# --- Kartvisning: side om side ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Historisk kart")
    df_hist = pd.DataFrame(historisk_kartpunkter)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_hist,
        get_position='[Lon, Lat]',
        get_color='[0, 100, 200, 160]',  # blå = historisk
        get_radius=60000,
        pickable=True
    )
    tooltip = {"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}
    view_state = pdk.ViewState(latitude=df_hist["Lat"].mean(), longitude=df_hist["Lon"].mean(), zoom=4)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
    st.pydeck_chart(r)

with col2:
    st.markdown("### Alternativt kart")
    df_alt = pd.DataFrame(alternativ_kartpunkter)
    layer_alt = pdk.Layer(
        "ScatterplotLayer",
        data=df_alt,
        get_position='[Lon, Lat]',
        get_color='[200, 30, 0, 160]',  # rød = alternativ
        get_radius=60000,
        pickable=True
    )
    tooltip_alt = {"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}
    view_state_alt = pdk.ViewState(latitude=df_alt["Lat"].mean(), longitude=df_alt["Lon"].mean(), zoom=4)
    r_alt = pdk.Deck(layers=[layer_alt], initial_view_state=view_state_alt, tooltip=tooltip_alt)
    st.pydeck_chart(r_alt)
