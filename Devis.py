# -*- coding: utf-8 -*-
import streamlit as st
from fpdf import FPDF
from datetime import date
import os
import tempfile
import time
import io
import sys
import base64
import re  # AJOUTÉ : Nécessaire pour l'extraction de texte (regex)
from PIL import Image
import pdfplumber

# --- CONFIGURATION INITIALE ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

AIMA_LOGO_PATH = resource_path("aima_logo.png")
if not os.path.exists(AIMA_LOGO_PATH):
    AIMA_LOGO_PATH = "C:/Users/perso/Desktop/aima_logo.png" 


st.set_page_config(layout="wide", page_title="AIMA - Gestion de Devis & Factures")

# --- INITIALISATION SESSION STATE ---
if 'manual_items_dict' not in st.session_state:
    st.session_state.manual_items_dict = []
if 'active_catalog' not in st.session_state:
    st.session_state.active_catalog = []
if 'catalog_selector' not in st.session_state:
    st.session_state.catalog_selector = []
if 'counters' not in st.session_state:
    st.session_state.counters = {"DEVIS": {}, "FACTURE": {}}
if "client_name_val" not in st.session_state:
    st.session_state["client_name_val"] = ""
if "client_addr_val" not in st.session_state:
    st.session_state["client_addr_val"] = ""

# --- DONNÉES ET CONSTANTES ---
LOCATIONS = {
    "OSSERAIN-RIVAREYTE": {"address": "1009 Route des Aügas, 64390 Osserain-Rivareyte", "email": "osserain@assoaima.org", "phone": "05 59 38 17 86"},
    "SALIES-DE-BÉARN": {"address": "154 Chemin du Haou, 64270 Salies-de-Béarn", "email": "salies@assoaima.org", "phone": "05 59 38 03 30"},
    "CASTETNAU-CAMBLONG": {"address": "11 Rue du Bourg, 64190 Castetnau-Camblong", "email": "lehangardaima.castetnau@gmail.com", "phone": "05 59 66 16 90"},
    "CAME": {"address": "409 Chemin de Gensanne, 64520 Came", "email": "lehangardaima.came@gmail.com", "phone": "05 59 31 97 53"}
}
LIEUX_ARTICLES = ["Osserain-Rivareyte","Came", "Salies-de-Béarn", "Castetnau-Camblong"]
MODES_PAIEMENT = ["Virement Bancaire", "Chèque","Chorus", "Espèces", "Carte Bancaire"]

data_prices = { "Fauteuil à roulette COMFORTO": 0.0, "Fauteuil de bureau ADDFORM": 0.0, "Fauteuil de bureau EUROSIT": 0.0, "Fauteuil de bureau STEELCASE": 0.0, "Fauteuil de bureau majencia": 0.0, "Fauteuil de bureau Interstuhl Hero": 0.0, "Fauteuil de bureau GIRSBERGER": 0.0, "Chaise opérateur Haworth": 0.0, "Fauteuil ergonomique Addform": 0.0, "Fauteuil Horma Teknion": 0.0, "Fauteuil dessinateur Forma 5": 0.0, "Chaise opérateur Viasit Drumback gris": 0.0, "Fauteuil Savera Teknion": 0.0, "Fauteuil Bejot Eleven Blanc": 0.0, "Fauteuil opérateur REXITT": 0.0, "Fauteuil Steelcase sans accoudoirs": 0.0, "Fauteuil Aresline Trendy": 0.0, "Fauteuil System 55 Haworth": 0.0, "Siège Cobi Steelcase": 0.0, "Fauteuil Comforto": 0.0, "CHAISE PLASTISQUE PIED ALU": 0.0, "Chaises empilables": 0.0, "Chaise scolaire T6": 0.0, "Chaise 4 pieds bicolore": 0.0, "Lot chaises d’école Rondo": 0.0, "Bureau": 0.0, "Bureau 70 x 122 cm": 0.0, "Bureau avec retour": 0.0, "Bureau FrameOne Steelcase": 0.0, "Bureau individuel": 0.0, "Bureau sur roulettes": 0.0, "Grand bureau individuel": 0.0, "Table pliante sans marque": 0.0, "Bureau haut": 0.0, "Bureau Frameone Steelcase": 0.0, "Bureau individuel ou bench de 2 ou 4 postes de travail": 0.0, "Bureau Majencia": 0.0, "Bureau d’angle SteelCase": 0.0, "Bureau individuel 4 pieds": 0.0, "Bench 2 places Sedus en 120 cm": 0.0, "Bench 2.0 Platten Steelcase": 0.0, "Bench Majencia 120×160 cm": 0.0, "Bench Steelcase Frame One": 0.0, "Benchs 2 places Sedus en 160 cm (3 modèles)": 0.0, "Table carrée 160×160": 0.0, "Table de réunion": 0.0, "Table de réunion carrée 140×140": 0.0, "Bench 4 postes": 0.0, "Bench 4 postes réglables": 0.0, "Bureau électrique Teknion": 0.0, "Table ronde Strafor": 0.0, "Table de réunion 12 personnes": 0.0, "Table de réunion en trapèze": 0.0, "Table de réunion Sedus": 0.0, "Table ovale Steelcase": 0.0, "Table de réunion haute Steelcase": 0.0, "Console": 0.0, "Table de réunion haute Ahrend": 0.0, "Table pliante Wiesner-Hager": 0.0, "Tabla basse sokoa": 0.0, "Table basse ronde": 0.0, "Table de restauration – 4 pers": 0.0, "Table bois massif": 0.0, "Table de Jardin": 0.0, "Table bistrot carrée": 0.0, "Table scolaire bicolore T6": 0.0, "Table scolaire T6": 0.0, "Table rectangulaire COMPO": 0.0, "Table de café/thé": 0.0, "Armoire basse": 0.0, "Armoire internat": 0.0, "Armoire mi-haute blanche": 0.0, "Armoires plateau tournant à rideaux": 0.0, "Vitrine sur roulettes": 0.0, "Armoire haute vitrée": 0.0, "Armoire basse portes battantes": 0.0, "Armoire basse portes coulissantes": 0.0, "Armoire haute portes battantes": 0.0, "Armoire haute portes battantes NowyStyl": 0.0, "Armoire métallique blanche rideaux coulissants": 0.0, "Caisson 3 Tiroirs": 0.0, "Caisson blanc": 0.0, "Caisson de bureau 2 tiroirs Majencia (réf : Abidos)": 0.0, "Caisson de bureau 3 tiroirs": 0.0, "Caisson de bureau Dior 3 tiroirs": 0.0, "Caisson de bureau Kinnarp’s": 0.0, "Caisson de bureau Sedus": 0.0, "Caisson haut de bureau (réf : Abidos)": 0.0, "Coussins d’assise pour caisson": 0.0, "Caisson de rangement “tower” Steelcase": 0.0, "Tour latérale de bureau bicolore": 0.0, "Tour latérale de bureau blanche": 0.0, "Crédence de bureau Haworth": 0.0, "Vestiaire 3 portes": 0.0, "Vestiaire Métallique": 0.0, "Vestiaire métallique gris": 0.0, "Vestiaire, casier multicases à code": 0.0, "Vestiaire 4 “Porte Z”": 0.0, "Vestiaire 6 “Porte Z”": 0.0, "Rayonnage Professionnel": 0.0, "Alcôve / Isoloir / Coin Lecture": 0.0, "Alcôve de réunion 4 places": 0.0, "Alcôve Manufacture du Design": 0.0, "Espace de travail individuel Ahrend": 0.0, "Banque D’Accueil": 0.0, "Caisse garde meuble 8m3": 0.0, "claustra de restauration": 0.0, "Claustra perforé": 0.0, "Accueil grande taille": 0.0, "Lit simple Souvignet": 0.0, "Lit Mathou": 0.0, "Lit SoftLock Mathou": 0.0, "Lit CatLock Mathou": 0.0, "Lit métal": 0.0, "Distributeur de gel hydroalcoolique": 0.0, "Pétrin mélangeur": 0.0, "Mixeur turbo broyeur": 0.0, "Imprimante PRO SHARP MX 5112N": 0.0, "Liseuse LED": 0.0, "Tour PC HP Windows 10": 0.0, "our PC LENOVO": 0.0, "Multiprises – 3 prises avec interrupteur et ports USB-A et USB-C": 0.0, "Carrelage": 0.0, "Dalle de faux plafond acoustique": 0.0, "Dalle de faux plafond Artic 20mm": 0.0, "Dalle de faux plafond Blanka": 0.0, "Dalle de plafond acoustique Tonga bords A cobalt": 0.0, "Dalle de plafond Armstrong Metal": 0.0, "Dalle de plafond Artic": 0.0, "Dalle de plafond Rockfon Blanka": 0.0, "Dalle faux plafond All Cork": 0.0, "Porte pleine sans cadre": 0.0, "Profilés métalliques": 0.0, "Systèmes à galandage + châssis pour porte coulissante": 0.0, "Poubelle Tri Sélectif Rubbermaid": 0.0, "Classeurs 2 anneaux": 0.0, "Chevet": 0.0, "Commode": 0.0, "Couette 140 x 200 cm": 0.0, "Oreiller 55 x 55 cm": 0.0, "Rideau Occultant": 0.0, "Miroir rond": 0.0, "Pupitre de conférence": 0.0, "Triporteur": 0.0, "Porte manteau": 0.0, "Panetière": 0.0 }

# --- FONCTIONS ---
def get_base64_logo(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{data}"
        except Exception: return None
    return None

def import_items_from_pdf(uploaded_pdf):
    try:
        new_items = []
        with pdfplumber.open(uploaded_pdf) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

                # Extract table with explicit settings to handle merged cells better
                table = page.extract_table({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                })

                if table:
                    for row in table:
                        if not row or len(row) < 4:
                            continue

                        designation = str(row[0]).strip() if row[0] else ""
                        raw_pu = str(row[1]).strip() if row[1] else ""
                        raw_total = str(row[3]).strip() if row[3] else ""

                        # Skip headers, totals, empty rows
                        skip_keywords = ["Designation", "TOTAL", "Signature", "P.U", 
                                        "adhesion", "Livraison", "Remise", "NET", ""]
                        if any(x in designation for x in skip_keywords):
                            continue
                        if not designation:
                            continue

                        # Try P.U. first, fall back to Total
                        price = 0.0
                        for raw in [raw_pu, raw_total]:
                            try:
                                cleaned = (raw.replace('€', '').replace(' ', '')
                                          .replace('\xa0', '').replace(',', '.')
                                          .strip())
                                if cleaned:
                                    price = float(cleaned)
                                    break
                            except:
                                continue

                        new_items.append({
                            "id": str(time.time()) + designation[:10],
                            "nom": designation,
                            "prix": price
                        })

            # --- CLIENT EXTRACTION (improved for side-by-side layout) ---
            # Extract text from first page only, right half (client is on the right)
            first_page = pdf.pages[0]
            page_width = first_page.width
            
            # Crop to right half of page where client box is
            right_half = first_page.within_bbox((page_width / 2, 0, page_width, first_page.height))
            right_text = right_half.extract_text() or ""
            
            # Now find DESTINATAIRE block in the right half text
            client_match = re.search(
                r"DESTINATAIRE\s*:\s*([^\n]+)\n(.*?)(?=DEVIS|FACTURE|N°|$)",
                right_text, re.DOTALL
            )
            if client_match:
                client_name_line = client_match.group(1).strip()
                client_addr_block = client_match.group(2).strip()
                lines = [l.strip() for l in client_addr_block.split('\n') if l.strip()]
                
                st.session_state["client_name_val"] = client_name_line
                st.session_state["client_addr_val"] = "\n".join(lines[:4])  # max 4 address lines

            # --- LIVRAISON ---
            match_liv = re.search(r"Livraison.*?(\d[\d\s]*[\.,]\d{2})", full_text)
            if match_liv:
                price_str = match_liv.group(1).replace(' ', '').replace(',', '.')
                st.session_state["imported_liv_price"] = float(price_str)
                st.session_state["imported_liv"] = True

            # --- REMISE ---
            match_remise = re.search(r"Remise\s*-?\s*(\d[\d\s]*[\.,]\d{2})", full_text)
            if match_remise:
                price_str = match_remise.group(1).replace(' ', '').replace(',', '.')
                st.session_state["imported_remise_globale"] = float(price_str)
                st.session_state["include_remise_globale"] = True

        return new_items

    except Exception as e:
        st.error(f"Erreur d'extraction : {e}")
        import traceback
        st.error(traceback.format_exc())
        return []

class AIMA_PDF(FPDF):
    def __init__(self, logo_path=None, doc_type="DEVIS"):
        super().__init__()
        self.logo_path = logo_path
        self.doc_type = doc_type

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path): 
            self.image(self.logo_path, 10, 8, 33)
        self.set_y(15); self.set_font('Arial', 'B', 20); self.set_text_color(24, 73, 115) 
        self.cell(0, 10, self.doc_type.upper(), 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-30); self.set_font('Arial', 'I', 7.5); self.set_text_color(100, 100, 100)
        self.cell(0, 4, "TVA non applicable, Art. 261-7b du code général des impôts", 0, 1, 'C')
        self.cell(0, 4, "IBAN : FR90 2004 1010 0112 2207 4K02 259 BIC : PSSTFRPPBOR", 0, 1, 'C')
        self.cell(0, 4, "Association AIMA - Siege social : 1009 Route des Augas 64390 - Osserain-Rivareyte | SIRET : 508 544 715 00057", 0, 1, 'C')
        self.set_font('Arial', '', 7); self.cell(0, 4, f'Page {self.page_no()}', 0, 0, 'R')

    def draw_first_page_info(self, doc_num, ref_text, selected_date, client_name, client_address, aima_info, status, realized_by, pay_mode):
        status_colors = {"En attente": {"r": 255, "g": 193, "b": 7}, "Accepté": {"r": 40, "g": 167, "b": 69}, "Refusé": {"r": 220, "g": 53, "b": 69}}
        color = status_colors.get(status, {"r": 128, "g": 128, "b": 128})
        
        self.set_xy(150, 20); self.set_font('Arial', 'B', 10); self.set_fill_color(color["r"], color["g"], color["b"]); self.set_text_color(255, 255, 255)
        self.cell(50, 8, f"STATUT: {status.upper()}", 0, 1, 'C', True)
        
        y_boxes = 38 
        
        self.set_xy(10, y_boxes); self.set_fill_color(51, 139, 140); self.set_text_color(255, 255, 255); self.set_font('Arial', 'B', 9)
        self.cell(80, 7, "Association AIMA", 1, 1, 'C', True)
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 8); self.set_x(10)
        self.multi_cell(80, 4, aima_info.encode('latin-1', 'replace').decode('latin-1'), 1, 'C')
        
        y_bottom_left = self.get_y() 
        
        self.set_xy(120, y_boxes); self.set_fill_color(51, 139, 140); self.set_text_color(255, 255, 255); self.set_font('Arial', 'B', 9)
        self.cell(80, 7, f"DESTINATAIRE : {client_name.upper()}", 1, 1, 'C', True)
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 9); self.set_x(120)
        self.multi_cell(80, 5, client_address.encode('latin-1', 'replace').decode('latin-1'), 1, 'C')
        
        y_bottom_right = self.get_y()

        self.set_xy(10, y_bottom_left + 2); self.set_font('Arial', '', 8.5)
        info_text = f"{self.doc_type} N°: {doc_num}\nRéf: {ref_text}\nDate: {selected_date.strftime('%d/%m/%Y')}\nRéalisé par: {realized_by}\nPaiement: {pay_mode}"
        self.multi_cell(75, 4.2, info_text.encode('latin-1', 'replace').decode('latin-1'), 1, 'L')
        
        return max(self.get_y(), y_bottom_right) + 5

# --- RENDER ROW INTERFACE ---
def render_item_row(label, default_price, key_suffix, is_manual=False, index=0, mode="DEVIS"):
    col_info, col_img = st.columns([1.8, 1])
    with col_info:
        st.write(f"### {label}")
        c1, c2, c3, c4, c5 = st.columns([1, 0.6, 1, 1.3, 1.2])
        p = c1.number_input(f"P.U. (EUR)", value=float(default_price), format="%.2f", key=f"p_{key_suffix}")
        q = c2.number_input(f"Qté", min_value=1, value=1, key=f"q_{key_suffix}")
        rem_val = c3.number_input("Remise (%)", min_value=0, max_value=100, value=0, key=f"rem_{key_suffix}")
        loc_val = c4.selectbox("Lieu de stockage", options=LIEUX_ARTICLES, key=f"loc_{key_suffix}") if mode == "DEVIS" else ""
        imgs = c5.file_uploader(f"Photos", type=["jpg","png"], accept_multiple_files=True, key=f"img_{key_suffix}")
        if is_manual: st.button("❌ Supprimer", key=f"del_{key_suffix}", on_click=lambda idx=index: st.session_state.manual_items_dict.pop(idx))
        else: st.button("❌ Supprimer", key=f"del_{key_suffix}", on_click=lambda name=label: (st.session_state.catalog_selector.remove(name) if name in st.session_state.catalog_selector else None))
    with col_img:
        if mode == "DEVIS" and imgs:
            sub_cols = st.columns(3)
            for idx, img in enumerate(imgs[:3]): sub_cols[idx].image(img, use_container_width=True)
    st.divider()
    row_total_initial = p * q
    row_total_net = row_total_initial - (row_total_initial * (rem_val / 100))
    return {"Désignation": label, "P.U.": p, "Qté": q, "Total": row_total_net, "Lieu": loc_val, "Images": imgs[:3] if imgs else []}, row_total_net

# --- MAIN APP ---
st.sidebar.header("📝 Paramètres")
doc_type = st.sidebar.selectbox("Type de document", ["DEVIS", "FACTURE"])
doc_status = st.sidebar.selectbox("État du suivi", ["En attente", "Accepté", "Refusé"])
realized_by = st.sidebar.text_input("Réalisé par", value="Equipe AIMA")
pay_mode = st.sidebar.selectbox("Mode de paiement", MODES_PAIEMENT)

if st.sidebar.button("🔄 Réinitialiser tout"):
    st.session_state.clear(); st.rerun()

selected_loc_name = st.sidebar.selectbox("Lieu d'expédition", options=list(LOCATIONS.keys()))
loc_data = LOCATIONS[selected_loc_name]
aima_pdf_info = f"Le Hangar d'AIMA - {selected_loc_name}\n{loc_data['address']}\nTél : {loc_data['phone']}\nMail : {loc_data['email']}\nSIRET: 508 544 715 00057"

c_name = st.sidebar.text_input("Client", value=st.session_state.get("client_name_val", ""), key="client_input_widget")
c_addr = st.sidebar.text_area("Adresse Client", value=st.session_state.get("client_addr_val", ""), key="client_addr_widget")
st.session_state["client_name_val"] = c_name
st.session_state["client_addr_val"] = c_addr

prefix = "FAC" if doc_type == "FACTURE" else "DEV"
client_clean = c_name.strip().upper().replace(" ", "-") if c_name else "CLIENT"
if client_clean not in st.session_state.counters[doc_type]: st.session_state.counters[doc_type][client_clean] = 1
current_count = st.session_state.counters[doc_type][client_clean]
d_num = st.sidebar.text_input(f"N° {doc_type}", value=f"{prefix}-{client_clean}-{str(current_count).zfill(3)}")
d_date = st.sidebar.date_input("Date", value=date.today())
d_ref = st.sidebar.text_input("Référence", value="AIMA-2026-INT")

st.sidebar.divider(); st.sidebar.subheader("⚙️ Frais Annexes") 
include_adh = st.sidebar.checkbox(f"Adhésion annuelle {d_date.year}", value=True)
include_liv = st.sidebar.checkbox("Livraison par nos soins au pied de l'immeuble", value=st.session_state.get("imported_liv", False))
liv_total = st.sidebar.number_input("Prix livraison", value=st.session_state.get("imported_liv_price", 0.0)) if include_liv else 0.0
# Change this line in your sidebar section:
include_remise_globale = st.sidebar.checkbox("Remise ", value=st.session_state.get("include_remise_globale", False))
montant_remise_globale = st.sidebar.number_input("Montant Remise", value=st.session_state.get("imported_remise_globale", 0.0)) if include_remise_globale else 0.0

st.markdown(f'<h1 style="text-align: center; color: #184973;">AIMA - Devis & Factures</h1>', unsafe_allow_html=True)

col_cat, col_imp = st.columns([2, 1])
with col_cat: selected_catalog = st.multiselect("📦 Catalogue :", options=sorted(list(data_prices.keys())), key="catalog_selector")
with col_imp:
    uploaded_pdf = st.file_uploader("📥 Importer PDF (Devis -> Facture)", type="pdf")
    if uploaded_pdf and st.button("🚀 Extraire Tout"):
        extracted = import_items_from_pdf(uploaded_pdf)
        if extracted: st.session_state.manual_items_dict.extend(extracted); st.rerun()

st.markdown("### ➕ Article personnalisé")
cm1, cm2, cm3 = st.columns([3, 1, 0.5])
with cm1: custom_name = st.text_input("Désignation", placeholder="Nom...")
with cm2: custom_price = st.number_input("Prix P.U.", min_value=0.0)
with cm3: 
    if st.button("✅"):
        if custom_name: st.session_state.manual_items_dict.append({"id": f"c_{time.time()}", "nom": custom_name, "prix": custom_price}); st.rerun()

st.divider()
items_to_pdf = []; total_global_items = 0.0
st.session_state.active_catalog = [x for x in st.session_state.active_catalog if x['name'] in selected_catalog]
for item in selected_catalog:
    if item not in [x['name'] for x in st.session_state.active_catalog]: st.session_state.active_catalog.append({'name': item, 'price': data_prices.get(item, 0.0)})

for i, item_data in enumerate(st.session_state.active_catalog):
    res, price = render_item_row(item_data['name'], item_data['price'], f"cat_{i}", mode=doc_type)
    items_to_pdf.append(res); total_global_items += price

for i, m in enumerate(st.session_state.manual_items_dict):
    res, price = render_item_row(m['nom'], m['prix'], f"man_{m['id']}", is_manual=True, index=i, mode=doc_type)
    items_to_pdf.append(res); total_global_items += price

grand_total = total_global_items + (1.0 if include_adh else 0.0) + (liv_total if include_liv else 0.0) - (montant_remise_globale if include_remise_globale else 0.0)
st.sidebar.markdown(f"### **TOTAL : {grand_total:,.2f} EUR**")

# --- GÉNÉRATION PDF ---
if items_to_pdf and st.button(f"📄 GÉNÉRER {doc_type} PDF"):
    pdf = AIMA_PDF(logo_path=AIMA_LOGO_PATH, doc_type=doc_type)
    pdf.add_page()
    y_pos = pdf.draw_first_page_info(d_num, d_ref, d_date, c_name, c_addr, aima_pdf_info, doc_status, realized_by, pay_mode)
    
    if doc_type == "DEVIS":
        cols_w = [60, 20, 12, 25, 43, 30] # Largeurs ajustées pour donner plus de place aux prix
        headers = ["Designation", "P.U.", "Qte", "Total", "Photos", "Lieu"]
    else:
        cols_w = [115, 25, 15, 35] # Largeurs ajustées
        headers = ["Designation", "P.U.", "Qte", "Total"]

    pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(240, 240, 240); pdf.set_xy(10, y_pos)
    for i, h in enumerate(headers): pdf.cell(cols_w[i], 8, h, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Arial", '', 8)
    for row in items_to_pdf:
        nom_p = row['Désignation'].encode('latin-1', 'replace').decode('latin-1')
        lieu_p = str(row['Lieu']).encode('latin-1', 'replace').decode('latin-1')
        h_row = 32 if (doc_type == "DEVIS" and row['Images']) else 10
        if pdf.get_y() + h_row > 260: pdf.add_page()
        
        y_c = pdf.get_y()
        # Désignation (multi-ligne si besoin)
        pdf.rect(10, y_c, cols_w[0], h_row)
        pdf.multi_cell(cols_w[0], 5, nom_p, 0, 'L')
        
        curr_x = 10 + cols_w[0]
        # P.U. - Correction : Utilisation d'une largeur fixe et alignement centré
        pdf.set_xy(curr_x, y_c)
        pdf.cell(cols_w[1], h_row, f"{row['P.U.']:,.2f}", 1, 0, 'C')
        
        curr_x += cols_w[1]
        # Qté
        pdf.set_xy(curr_x, y_c)
        pdf.cell(cols_w[2], h_row, str(row['Qté']), 1, 0, 'C')
        
        curr_x += cols_w[2]
        # Total - Correction : Largeur garantie pour éviter le débordement
        pdf.set_xy(curr_x, y_c)
        pdf.cell(cols_w[3], h_row, f"{row['Total']:,.2f}", 1, 0, 'C')
        
        curr_x += cols_w[3]
        
        if doc_type == "DEVIS":
            # Photos
            pdf.set_xy(curr_x, y_c); pdf.cell(cols_w[4], h_row, "", 1, 0)
            if row['Images']:
                for idx, img_file in enumerate(row['Images']):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    with Image.open(img_file) as pimg:
                        if pimg.mode in ("RGBA", "P"): pimg = pimg.convert("RGB")
                        pimg.thumbnail((400, 400)); pimg.save(tmp.name, "JPEG")
                    pdf.image(tmp.name, curr_x + 1 + (idx * 14), y_c + 2, w=12); tmp.close(); os.remove(tmp.name)
            curr_x += cols_w[4]
            # Lieu
            pdf.set_xy(curr_x, y_c); pdf.cell(cols_w[5], h_row, lieu_p, 1, 1, 'C')
        else: 
            pdf.ln(h_row)

    # --- SECTION RÉCAPITULATIVE (TOTAL) ---
    needed_space = 60 
    if pdf.get_y() + needed_space > 265: pdf.add_page()

    pdf.ln(5)
    y_final = pdf.get_y()
    
    # Configuration des colonnes du récapitulatif
    col_label_w = 75 
    col_amount_w = 40 
    
    # --- LOGIQUE D'ALIGNEMENT DIFFÉRENCIÉE ---
    if doc_type == "DEVIS":
        # On garde l'ancien style : bloc à gauche (x=10)
        summary_x = 10
    else:
        # Style Facture : Alignement synchronisé sur le bord droit du tableau
        total_table_width = sum(cols_w) # Largeur totale de la facture
        right_margin_x = 10 + total_table_width
        summary_x = right_margin_x - (col_label_w + col_amount_w)
    
    pdf.set_font("Arial", '', 9)
    
    # Lignes de détails (Adhésion, Livraison, Remise)
    if include_adh: 
        pdf.set_xy(summary_x, pdf.get_y())
        pdf.cell(col_label_w, 7, "Cout adhesion annuelle 2026", 1)
        pdf.cell(col_amount_w, 7, "1.00 EUR", 1, 1, 'C')
    if include_liv:
        pdf.set_xy(summary_x, pdf.get_y())
        pdf.cell(col_label_w, 7, "Livraison par nos soins au pied de l'immeuble", 1)
        pdf.cell(col_amount_w, 7, f"{liv_total:,.2f} EUR", 1, 1, 'C')
    if include_remise_globale and montant_remise_globale > 0:
        pdf.set_xy(summary_x, pdf.get_y())
        pdf.cell(col_label_w, 7, "Remise", 1)
        pdf.cell(col_amount_w, 7, f"- {montant_remise_globale:,.2f} EUR", 1, 1, 'C')

    # Ligne du TOTAL NET
    pdf.set_xy(summary_x, pdf.get_y())
    pdf.set_fill_color(51, 139, 140)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col_label_w, 10, "TOTAL NET", 1, 0, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    if grand_total > 1000000: pdf.set_font("Arial", 'B', 8)
    pdf.cell(col_amount_w, 10, f"{grand_total:,.2f} EUR", 1, 1, 'C')

    # --- SIGNATURE (Inchangée, alignée sur Devis uniquement) ---
    if doc_type == "DEVIS":
        sig_width = cols_w[4] + cols_w[5] # Somme colonnes Photos + Lieu
        sig_x_aligned = 10 + cols_w[0] + cols_w[1] + cols_w[2] + cols_w[3]
        
        pdf.set_xy(sig_x_aligned, y_final)
        pdf.set_font("Arial", '', 9)
        pdf.cell(sig_width, 8, "Signature :", 1, 1, 'L')
        pdf.set_x(sig_x_aligned)
        pdf.cell(sig_width, 25, "", 1, 1)
    # ... (code précédent inchangé)

    pdf_content = pdf.output(dest='S')
    if isinstance(pdf_content, str):
        final_pdf_bytes = pdf_content.encode('latin-1')
    else:
        final_pdf_bytes = bytes(pdf_content)

    st.download_button(
        label=f"💾 Télécharger {doc_type}",
        data=final_pdf_bytes,
        file_name=f"{d_num}.pdf",
        mime="application/pdf"
    )
