# -*- coding: utf-8 -*-
import streamlit as st
from fpdf import FPDF
from datetime import date
import os
import tempfile
import time


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

AIMA_LOGO_PATH = resource_path("aima_logo.png")


# Configuration de la page Streamlit
st.set_page_config(layout="wide", page_title="AIMA - Gestion de Devis")

# --- CHEMIN DU LOGO ---
#AIMA_LOGO_PATH = "C:/Users/perso/Desktop/aima_logo.png"

# --- INITIALISATION ---
if 'manual_items_dict' not in st.session_state:
    st.session_state.manual_items_dict = []
if 'active_catalog' not in st.session_state:
    st.session_state.active_catalog = []
if 'catalog_selector' not in st.session_state:
    st.session_state.catalog_selector = []

# --- CALLBACKS ---
def delete_catalog_item(item_name):
    if item_name in st.session_state.catalog_selector:
        st.session_state.catalog_selector.remove(item_name)
    st.session_state.active_catalog = [x for x in st.session_state.active_catalog if x['name'] != item_name]

def delete_manual_item(index):
    st.session_state.manual_items_dict.pop(index)

# --- LOGO SIDEBAR ---
if os.path.exists(AIMA_LOGO_PATH):
    st.sidebar.image(AIMA_LOGO_PATH, use_container_width=True)
    st.sidebar.divider()

# --- BASE DE DONNÉES ---
data_prices = {
    "Abaisse-langue": [0, 1.5], "Anuscope": [0, 5], "Appareil de photothérapie": [45, 400],
    "Aspirateur à mucosités": [30, 150], "Aspirateur chirurgical": [30, 200], "Bain thermostaté": [30, 50],
    "Baquet roulant": [0, 5], "Béquille - Canne": [0, 5], "Berceau": [0, 30],
    "Bistouri électrique": [90, 300], "Boîte à instruments - Boîte de stérilisation": [0, 60],
    "Brancard simple": [0, 25], "Brancard sur chariot roulant": [0, 150], "Centrifugeuse": [60, 300],
    "Capnographe": [45, 80], "Cardiotocographe": [45, 400], "Chaise percée - Chaise pot": [0, 10],
    "Chambre d'inhalation": [0, 7.5], "Chariot médical": [0, 25], "Colposcope": [15, 500],
    "Concentrateur d’oxygène": [30, 250], "Consommable à usage unique": [0, 0.5],
    "Conteneur - Tambour de stérilisation": [0, 12.5], "Cupule": [0, 1.5],
    "Cuve-Bac à ultrasons pour nettoyage d'instruments": [15, 150], "Déambulateur": [0, 5],
    "Défibrillateur manuel": [60, 350], "Défibrillateur semi-automatique": [30, 250],
    "Dispositif d'immobilisation, d'ergothérapie (ex : attelle)": [0, 5], "Doppler": [30, 25],
    "Échographe": [120, 1500], "Échographe de type bladder scan": [30, 300],
    "Éclairage opératoire - Scialytique": [60, 500], "Électrocardiographe": [60, 250],
    "Étuve": [30, 50], "Fauteuil de dialyse": [0, 50], "Fauteuil de prélèvement": [0, 50],
    "Fauteuil roulant": [0, 50], "Garrot": [0, 5], "Garrot électrique": [30, 150],
    "Glucomètre": [0, 2.5], "Haricot": [0, 5], "Incubateur de néonatalogie fermé - Couveuse": [120, 400],
    "Incubateur de néonatalogie ouvert - Table de réanimation": [120, 400],
    "Instrumentation (Chirurgie/Gynéco/ORL/Ortho/etc.)": [0, 4], "Insufflateur manuel": [0, 25],
    "Lampe d’examen": [15, 50], "Laryngoscope": [15, 37.5], "Littérature médicale": [0, 0],
    "Lève-malade - Sangle lève-personne": [15, 17.5], "Lunettes - Montures": [0, 2.5],
    "Marteau à réflexes": [0, 5], "Masque facial pour ventilation-insufflation": [0, 5],
    "Microscope de paillasse": [30, 150], "Microscope opératoire": [60, 1100],
    "Mobilier hospitalier": [0, 25], "Moniteur 3 paramètres (ECG, SpO2, PNI)": [90, 350],
    "Moniteur 2 paramètres (SpO2, PNI)": [60, 250], "Moteur orthopédique": [30, 1000],
    "Nébuliseur": [30, 20], "Négatoscope": [15, 25], "Otoscope": [15, 15],
    "Oxymètre de pouls - Saturo-mètre": [30, 80], "Panier à instruments / stérilisation": [0, 5],
    "Paravent": [0, 20], "Pèse-bébé (manuel ou électronique)": [15, 20], "Pèse-personne": [0, 10],
    "Pied à sérum - Potence": [0, 12.5], "Pissette": [0, 2.5], "Plateau à instruments": [0, 2.5],
    "Poire à lavement": [0, 2.5], "Pompe d’auto-analgésie": [45, 100], "Pompe à nutrition entérale": [45, 75],
    "Pompe à perfusion": [45, 120], "Pompe à pousse-seringue": [45, 100], "Rampe chauffante": [30, 120],
    "Rampe de photothérapie": [30, 200], "Rehausseur WC / Siège de bain": [0, 5],
    "Spéculum gynécologique": [0, 4], "Spiromètre": [0, 10], "Stérilisateur à chaleur humide - Autoclave": [90, 600],
    "Stérilisateur à chaleur sèche - Poupinel": [45, 50], "Stéthoscope": [0, 5],
    "Table d'accouchement": [0, 200], "Table d'opération (manuelle/électrique)": [45, 1250],
    "Table de réanimation néonatale": [90, 90], "Table - Divan - Lit d'examen": [0, 175],
    "Tensiomètre automatique - Moniteur PNI": [30, 200], "Tensiomètre manuel - Sphygmomanomètre": [0, 5],
    "Tenues de soins et de bloc opératoire": [0, 5], "Thermo-soudeuse": [30, 50],
    "Tire-lait électrique": [15, 5], "Urinal - Bassin de lit": [0, 1.5],
    "Ventilateur d’anesthésie (sans halogénés)": [120, 1500], "Ventilateur d’anesthésie (avec cuve halogénés)": [120, 2000],
    "Ventilateur de réanimation / Artificielle": [120, 1200], "Ventilateur de soins intensifs": [120, 1200],
    "Ventilateur d’urgence": [60, 750], "Verticalisateur": [15, 175],
    "Wardrobe": [0, 100], "Low cabinet": [0, 40], "Desk": [0, 50], "Chair": [0, 10],
    "Chair waterproof": [0, 10], "Shower chair": [0, 20], "Commode chair without wheels": [0, 15],
    "Commode chair with wheels": [0, 20], "Trolley": [0, 80], "Bedside": [0, 20],
    "Chest of drawers": [0, 40], "Covers": [0, 2], "Walker without wheels": [0, 10],
    "Walker with wheels": [0, 15], "Manual armchair": [0, 15], "Electric armchair": [0, 40],
    "Manuel wheelchair": [0, 40], "Transfer wheelchair": [0, 40], "Electric wheelchair": [0, 150],
    "Electric bed": [0, 150], "Shower bed": [0, 200], "Medical mattress": [0, 20],
    "Pillows": [0, 1], "Footrest": [0, 10], "Adaptable table": [0, 30], "Table": [0, 15],
    "Table little": [0, 15], "Manual examination table": [0, 50], "Electric examination table": [0, 100],
    "Dining table": [0, 30]
}

# --- CLASSE PDF ---
class AIMA_PDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 20, 18, 42)
        self.set_font('Arial', 'B', 14); self.set_text_color(24, 73, 115)
        self.set_xy(110, 10); self.cell(90, 8, "DEVIS D'EQUIPEMENT MEDICAL", 0, 1, 'R'); self.ln(20)

    def draw_first_page_info(self, devis_num, ref_text, selected_date, client_name, client_address):
        y_boxes = 40
        self.set_fill_color(51, 139, 140); self.set_text_color(255, 255, 255)
        self.set_xy(10, y_boxes); self.set_font('Arial', 'B', 9); self.cell(80, 7, "Association AIMA", 1, 1, 'C', True)
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 8); self.set_x(10)
        info_text = "Le Hangar d'AIMA Humanitaire et Médical\n10 avenue des Salines, 64270 Salies-de-Béarn\nTél : +33 6 09 93 97 25\nMail : international@assoaima.org\nSIRET: 508 544 715 00057"
        self.multi_cell(80, 4, info_text, 1, 'C'); y_left = self.get_y()
        self.set_xy(120, y_boxes); self.set_fill_color(51, 139, 140); self.set_text_color(255, 255, 255)
        self.cell(80, 7, f"DESTINATAIRE : {client_name.upper()}", 1, 1, 'C', True)
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 9); self.set_x(120); self.multi_cell(80, 5, client_address, 1, 'C')
        y_right = self.get_y(); y_ref = y_left + 2; self.set_xy(10, y_ref); self.set_font('Arial', '', 8.5)
        self.multi_cell(55, 4.2, f"Devis N°: {devis_num}\nRéf: {ref_text}\nDate: {selected_date.strftime('%d/%m/%Y')}", 1, 'L')
        return max(self.get_y(), y_right) + 5

    def footer(self):
        self.set_y(-35); self.set_font('Arial', 'I', 7); self.set_text_color(100, 100, 100)
        self.cell(0, 4, "TVA non applicable, Art. 261-7b du code général des impôts", 0, 1, 'C')
        self.cell(0, 4, "IBAN : FR90 2004 1010 0112 2207 4K02 259 BIC : PSSTFRPPBOR", 0, 1, 'C')
        self.cell(0, 4, "Association AIMA - Siège social : 1009 Route des Aügas 64390 - Osserain-Rivareyte | SIRET : 508 544 715 00057", 0, 1, 'C')
        self.cell(0, 4, f'Page {self.page_no()}', 0, 0, 'R')

# --- FONCTION DE LIGNE ---
def render_item_row(label, default_price, key_suffix, is_manual=False, index=0):
    col_info, col_img = st.columns([1.5, 1])
    with col_info:
        st.write(f"### {label}")
        c1, c2, c3 = st.columns([1, 1, 1])
        p_val = float(sum(default_price)) if isinstance(default_price, list) else float(default_price)
        p = c1.number_input(f"P.U. (€)", value=p_val, format="%.2f", key=f"p_{key_suffix}")
        q = c2.number_input(f"Qté", min_value=1, value=1, key=f"q_{key_suffix}")
        imgs = c3.file_uploader(f"Photos (Copy enabled)", type=["jpg","png"], accept_multiple_files=True, key=f"img_{key_suffix}")
        
        if is_manual:
            st.button("❌ Supprimer", key=f"del_{key_suffix}", on_click=delete_manual_item, args=(index,))
        else:
            st.button("❌ Supprimer", key=f"del_{key_suffix}", on_click=delete_catalog_item, args=(label,))

    with col_img:
        if imgs:
            st.caption("Right-click image to Copy")
            sub_cols = st.columns(3)
            for idx, img in enumerate(imgs[:3]): 
                # Displaying images so they are "Copyable" via browser context menu
                sub_cols[idx].image(img, use_container_width=True)
    st.divider()
    return {"Désignation": label, "P.U.": p, "Qté": q, "Total": p*q, "Images": imgs[:3] if imgs else []}, (p * q)

# --- INTERFACE ---
col_h1, col_h2 = st.columns([1, 5])
with col_h1:
    if os.path.exists(AIMA_LOGO_PATH):
        st.image(AIMA_LOGO_PATH, width=120)
with col_h2:
    st.markdown('<h1 style="color: #2c3e50; margin-top: 20px;">Plateforme de Devis Médicaux - AIMA</h1>', unsafe_allow_html=True)

st.sidebar.header("📝 Paramètres")
c_name = st.sidebar.text_input("Client", value="ONG- EPSPE")
c_addr = st.sidebar.text_area("Adresse", value="10 BP 1001 cotonou, Bénin")
d_num = st.sidebar.text_input("N° Devis", value="2026-001")
d_ref = st.sidebar.text_input("Référence", value="AIMA-2026-INT")
d_date = st.sidebar.date_input("Date", value=date.today())

logo_upload = st.sidebar.file_uploader("Changer le logo du PDF", type=["png", "jpg"])
final_logo_path = AIMA_LOGO_PATH 
if logo_upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(logo_upload.getvalue()); final_logo_path = tmp.name

# --- GESTION CATALOGUE ---
selected_catalog = st.multiselect("📦 Sélectionner les dispositifs :", options=sorted(list(data_prices.keys())), key="catalog_selector")

items_to_pdf = []
total_global = 0.0

st.session_state.active_catalog = [x for x in st.session_state.active_catalog if x['name'] in selected_catalog]
for item in selected_catalog:
    if item not in [x['name'] for x in st.session_state.active_catalog]:
        st.session_state.active_catalog.append({'name': item, 'price': data_prices[item]})

for i, item_data in enumerate(st.session_state.active_catalog):
    res, price = render_item_row(item_data['name'], item_data['price'], f"cat_{item_data['name']}")
    items_to_pdf.append(res)
    total_global += price

# Ajout Manuel
st.subheader("➕ Article personnalisé")
m_cols = st.columns([2, 1, 1])
n_nom = m_cols[0].text_input("Désignation", key="manual_name")
n_prix = m_cols[1].number_input("Prix P.U.", min_value=0.0, format="%.2f", key="manual_price")
if m_cols[2].button("✅ Ajouter"):
    if n_nom: 
        unique_id = str(time.time()).replace(".","")
        st.session_state.manual_items_dict.append({"id": unique_id, "nom": n_nom, "prix": n_prix})
        st.rerun()

for i, m in enumerate(st.session_state.manual_items_dict):
    res, price = render_item_row(m['nom'], m['prix'], f"man_{m['id']}", is_manual=True, index=i)
    items_to_pdf.append(res)
    total_global += price

# --- GÉNÉRATION PDF ---
if items_to_pdf:
    st.subheader(f"TOTAL GLOBAL : {total_global:,.2f} EUR")
    if st.button("📄 GÉNÉRER LE DEVIS PDF"):
        pdf = AIMA_PDF(logo_path=final_logo_path)
        pdf.add_page()
        y_pos = pdf.draw_first_page_info(d_num, d_ref, d_date, c_name, c_addr)
        cols_w = [55, 20, 15, 20, 80]
        
        pdf.set_font('Arial', 'B', 9); pdf.set_fill_color(220, 220, 220)
        pdf.set_xy(10, y_pos)
        for h, w in zip(["Designation", "P.U.", "Qté", "Total", "Photos"], cols_w):
            pdf.cell(w, 8, h, 1, 0, 'C', True)
        pdf.ln()

        pdf.set_font("Arial", '', 9)
        for row in items_to_pdf:
            text_w = cols_w[0] - 2
            nb_lines = len(pdf.multi_cell(text_w, 4, row['Désignation'], split_only=True))
            h_row = max(nb_lines * 4 + 4, 32 if row['Images'] else 10)
            if pdf.get_y() + h_row > 250: pdf.add_page()
            
            y_c = pdf.get_y()
            pdf.rect(10, y_c, cols_w[0], h_row)
            pdf.set_xy(10, y_c + (h_row - (nb_lines * 4)) / 2)
            pdf.multi_cell(cols_w[0], 4, row['Désignation'].encode('latin-1', 'replace').decode('latin-1'), 0, 'L')
            
            pdf.set_xy(10 + cols_w[0], y_c)
            pdf.cell(cols_w[1], h_row, f"{row['P.U.']:,.2f}", 1, 0, 'C')
            pdf.cell(cols_w[2], h_row, str(row['Qté']), 1, 0, 'C')
            pdf.cell(cols_w[3], h_row, f"{row['Total']:,.2f}", 1, 0, 'C')
            
            img_x = pdf.get_x(); pdf.cell(cols_w[4], h_row, "", 1, 1)
            
            if row['Images']:
                for idx, img in enumerate(row['Images']):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(img.getvalue())
                        tmp_path = tmp.name
                    try:
                        pdf.image(tmp_path, img_x + (idx * 25) + 2, y_c + 2, h=h_row-4)
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)

        pdf.ln(5); pdf.set_x(130); pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(220, 220, 220)
        pdf.cell(30, 8, "TOTAL TTC", 1, 0, 'C', True); pdf.cell(40, 8, f"{total_global:,.2f} EUR", 1, 1, 'C')
        st.download_button("💾 Télécharger le Devis", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Devis_{d_num}.pdf", mime="application/pdf")

