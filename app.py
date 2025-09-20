import streamlit as st
import pandas as pd
import pydeck as pdk
import json

st.set_page_config(page_title="WW1 – Historisk vs alternativt", layout="wide")
st.title("Første verdenskrig – Historisk vs alternativt scenario")

# --- Last inn slagdata ---
try:
    with open("data/slag.json") as f:
        slag = json.load(f)
except FileNotFoundError:
    st.error("Finner ikke 'data/slag.json'. Legg filen i /data/ og redeploy.")
    st.stop()

# --- Session state for elevenes valg ---
if "valg" not in st.session_state:
    st.session_state.valg = {}

# --- Velg slag og ta beslutning ---
slag_valg = st.selectbox("Velg et slag:", list(slag.keys()))
if slag_valg:
    data = slag[slag_valg]
    st.write(f"**{slag_valg} ({data['År']})**")
    st.write("Historisk utfall:", data["Faktisk"])

    valg = st.radio("Hva ville du gjort?", list(data["Valg"].keys()))
    if st.button("Lagre mitt valg"):
        st.session_state.valg[slag_valg] = valg
        st.success(f"Ditt valg for {slag_valg} er lagret!")

# --- Bygg alternativ tidslinje og kart ---
historisk_kartpunkter = []
alternativ_kartpunkter = []

for slag_navn, data in slag.items():
    historisk_kartpunkter.append({
        "Navn": slag_navn,
        "Lat": data["Lat"],
        "Lon": data["Lon"],
        "Kontroll": "Historisk"
    })
    valgt = st.session_state.valg.get(slag_navn)
    if valgt:
        alternativ_kartpunkter.append({
            "Navn": slag_navn,
            "Lat": data["Lat"],
            "Lon": data["Lon"],
            "Kontroll": valgt
        })
    else:
        alternativ_kartpunkter.append({
            "Navn": slag_navn,
            "Lat": data["Lat"],
            "Lon": data["Lon"],
            "Kontroll": "Historisk"
        })

# --- Vis tidslinje ---
st.subheader("Alternativ tidslinje")
for slag_navn, data in slag.items():
    valgt = st.session_state.valg.get(slag_navn)
    if valgt:
        st.write(f"{slag_navn} ({data['År']}): {data['Valg'][valgt]['Beskrivelse']}")
    else:
        st.write(f"{slag_navn} ({data['År']}): {data['Faktisk']}")

# --- Kartvisning: historisk vs alternativt ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Historisk kontroll")
    df_hist = pd.DataFrame(historisk_kartpunkter)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_hist,
        get_position='[Lon, Lat]',
        get_color='[0, 100, 200, 160]',
        get_radius=60000,
        pickable=True
    )
    view_state = pdk.ViewState(latitude=df_hist["Lat"].mean(), longitude=df_hist["Lon"].mean(), zoom=4)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state,
                             tooltip={"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}))

with col2:
    st.markdown("### Alternativ kontroll")
    df_alt = pd.DataFrame(alternativ_kartpunkter)
    layer_alt = pdk.Layer(
        "ScatterplotLayer",
        data=df_alt,
        get_position='[Lon, Lat]',
        get_color='[200, 30, 0, 160]',
        get_radius=60000,
        pickable=True
    )
    view_state_alt = pdk.ViewState(latitude=df_alt["Lat"].mean(), longitude=df_alt["Lon"].mean(), zoom=4)
    st.pydeck_chart(pdk.Deck(layers=[layer_alt], initial_view_state=view_state_alt,
                             tooltip={"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}))
