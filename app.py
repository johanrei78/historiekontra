import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="WW1: Historisk vs. alternativt scenario", layout="wide")
st.title("Første verdenskrig – Historisk vs. alternativt scenario")

# --- Hardkodet data ---
slag = {
    "Verdun": {
        "År": 1916,
        "Lat": 49.159,
        "Lon": 5.384,
        "Faktisk": "Frankrike forsvarte Verdun.",
        "Valg": {
            "Forsvar": {"Beskrivelse": "Frankrike holder linjen."},
            "Tilbaketrekning": {"Beskrivelse": "Frankrike trekker seg tilbake, Tyskland får overtak."}
        }
    },
    "Somme": {
        "År": 1916,
        "Lat": 50.020,
        "Lon": 2.650,
        "Faktisk": "Store tap for britene.",
        "Valg": {
            "Frontalangrep": {"Beskrivelse": "Store tap, liten framgang."},
            "Utsette angrep": {"Beskrivelse": "Tyskland får tid til å styrke linjene."}
        }
    }
}

# --- Session state ---
if "valg" not in st.session_state:
    st.session_state.valg = {}

# --- Elevens valg ---
slag_valg = st.selectbox("Velg et slag:", list(slag.keys()))
if slag_valg:
    data = slag[slag_valg]
    st.write(f"**{slag_valg} ({data['År']})**")
    st.write("Faktisk utfall:", data["Faktisk"])

    valg = st.radio("Hva ville du gjort?", list(data["Valg"].keys()))
    if st.button("Lagre mitt valg"):
        st.session_state.valg[slag_valg] = valg
        st.success(f"Ditt valg for {slag_valg} er lagret!")

# --- Alternativ tidslinje ---
st.subheader("Alternativ tidslinje")
for slag_navn, data in slag.items():
    valgt = st.session_state.valg.get(slag_navn)
    if valgt:
        st.write(f"{slag_navn}: {data['Valg'][valgt]['Beskrivelse']}")
    else:
        st.write(f"{slag_navn}: {data['Faktisk']}")

# --- Kartvisning ---
df = pd.DataFrame([
    {
        "Navn": k,
        "Lat": v["Lat"],
        "Lon": v["Lon"],
        "Kontroll": st.session_state.valg.get(k, "Historisk")
    }
    for k, v in slag.items()
])

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[Lon, Lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=60000,
    pickable=True
)
view_state = pdk.ViewState(latitude=df["Lat"].mean(), longitude=df["Lon"].mean(), zoom=4)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"html": "<b>{Navn}</b><br/>Kontroll: {Kontroll}"}))
