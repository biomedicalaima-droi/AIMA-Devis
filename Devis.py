import streamlit as st
from fpdf import FPDF
from datetime import date
import os
import sys
import tempfile
from PIL import Image

# --- CONFIGURATION ET LOGO ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

AIMA_LOGO_PATH = resource_path("aima_logo.png")
AIMA_LOGO_PATH = "C:/Users/perso/Desktop/aima_logo.png"

# --- DONNÉES DE PRIX (Catalogue) ---
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
    "Ventilateur d’urgence": [60, 750], "Verticalisateur": [15, 175]
}

if 'manual_items_dict' not in st.session_state:
    st.session_state.manual_items_dict = []

# --- CLASSE PDF ---
class AIMA_PDF(FPDF):
    def header(self):
        if os.path.exists(AIMA_LOGO_PATH):
            self.image(AIMA_LOGO_PATH, 10, 3, 35)
        self.set_font('Arial', 'B', 14) 
        self.set_text_color(24, 73, 115)
        self.set_xy(95, 5) 
        self.cell(0, 10, "DEVIS D'EQUIPEMENT MEDICAL", 0, 1, 'L')
        self.set_draw_color(24, 73, 115)
        self.line(95, 13, 200, 13)

        if self.page_no() == 1:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.set_xy(10, 22) 
            self.cell(0, 5, "Association AIMA", 0, 1, 'L')
            self.set_font('Arial', '', 9)
            self.cell(0, 4, "Le Hangar d'AIMA Humanitaire et Médical", 0, 1, 'L')
            self.cell(0, 4, "10 avenue des Salines, 64270 Salies-de-Béarn", 0, 1, 'L')
            self.cell(0, 4, "Tél : +33 6 09 93 97 25" , 0, 1, 'L')
            self.cell(0, 4, "Mail : international@assoaima.org", 0, 1, 'L')
            self.cell(0, 4, "SIRET : 508 544 715 00057", 0, 1, 'L')
        else:
            self.set_y(25)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', '', 8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 4, "TVA non applicable, Art. 261-7b du code général des impôts", 0, 1, 'C')
        self.set_font('Arial', 'B', 8)
        self.cell(0, 4, "IBAN : FR90 2004 1010 0112 2207 4K02 259  BIC : PSSTFRPPBOR", 0, 1, 'C')
        footer_text = "Association AIMA - Siège social : 1009 Route des Aügas 64390 - Osserain-Rivareyte | SIRET : 508 544 715 00057"
        self.cell(0, 4, footer_text.encode('latin-1', 'replace').decode('latin-1'), 0, 0, 'C')

    def draw_table_header(self):
        self.set_font("Arial", 'B', 7.5)
        self.set_fill_color(24, 73, 115)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(255, 255, 255)
        curr_y = self.get_y()
        self.cell(55, 10, "Designation", 1, 0, 'C', True)
        x_pt = self.get_x()
        self.multi_cell(30, 5, "Participation\ntests/structure", 1, 'C', True)
        self.set_xy(x_pt + 30, curr_y)
        self.cell(12, 10, "Qté", 1, 0, 'C', True)
        x_ptot = self.get_x()
        self.multi_cell(23, 5, "Participation\nTotale", 1, 'C', True)
        self.set_xy(x_ptot + 23, curr_y)
        self.cell(70, 10, "Photo", 1, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(200, 200, 200)

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Générateur de Devis AIMA", layout="wide")
st.title("🏥 Plateforme de Devis Médicaux - AIMA")

st.sidebar.header("📝 Informations du Devis")
client_name = st.sidebar.text_input("Nom du Client", value="ONG- EPSPE")
client_address = st.sidebar.text_area("Adresse Client", value="10 BP 1001 cotonou, Bénin")
devis_num = st.sidebar.text_input("Numéro de Devis", value="2026-001")

selected_catalog = st.multiselect("Sélectionnez les dispositifs :", options=sorted(list(data_prices.keys())))

st.subheader("2. Détails et Photos")
final_items_to_print = []
total_global = 0.0

for item in selected_catalog:
    default_price = float(sum(data_prices[item]))
    c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
    with c1: st.markdown(f"**{item}**")
    with c2: unit_p = st.number_input(f"P.U. (€)", min_value=0.0, value=default_price, key=f"p_cat_{item}")
    with c3: qty = st.number_input(f"Qté", min_value=1, value=1, key=f"q_cat_{item}")
    with c4: img = st.file_uploader(f"Photo pour {item}", type=["jpg","png","jpeg"], key=f"i_cat_{item}")
    total_row = unit_p * qty
    total_global += total_row
    final_items_to_print.append({"Désignation": item, "P.U.": unit_p, "Qté": qty, "Total": total_row, "Image": img})

for i, m_item in enumerate(st.session_state.manual_items_dict):
    st.divider()
    c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
    with c1: 
        st.markdown(f"**{m_item['nom']}** (Manuel)")
        if st.button(f"🗑️ Supprimer", key=f"del_{i}"):
            st.session_state.manual_items_dict.pop(i); st.rerun()
    with c2: m_price = st.number_input(f"P.U. (€)", min_value=0.0, value=float(m_item['prix']), key=f"p_man_{i}")
    with c3: m_qty = st.number_input(f"Qté", min_value=1, value=m_item['qty_init'], key=f"q_man_{i}")
    with c4: m_img = st.file_uploader(f"Photo pour {m_item['nom']}", type=["jpg","png","jpeg"], key=f"i_man_{i}")
    total_row = m_price * m_qty
    total_global += total_row
    final_items_to_print.append({"Désignation": m_item['nom'], "P.U.": m_price, "Qté": m_qty, "Total": total_row, "Image": m_img})

st.write("---")
st.subheader("➕ Ajouter un article hors catalogue")
m1, m2, m3 = st.columns([3, 1, 1])
new_nom = m1.text_input("Désignation de l'article", key="input_nom")
new_prix = m2.number_input("Prix Unitaire (€)", min_value=0.0, key="input_prix")
new_qty = m3.number_input("Quantité initiale", min_value=1, value=1, key="input_qty")

if st.button("✨ Ajouter au devis"):
    if new_nom:
        st.session_state.manual_items_dict.append({"nom": new_nom, "prix": new_prix, "qty_init": new_qty})
        st.rerun()

# --- GÉNÉRATION PDF ---
if final_items_to_print:
    st.divider()
    st.markdown(f"### TOTAL GLOBAL : **{total_global} €**")
    
    if st.button("💾 Générer le PDF Officiel"):
        pdf = AIMA_PDF()
        pdf.add_page()
        euro = chr(128)
        
        pdf.set_xy(145, 22) 
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, f"Devis N°: {devis_num}", ln=1)
        pdf.set_x(145)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"Date: {date.today().strftime('%d/%m/%Y')}", ln=1)
        
        pdf.set_xy(10, 48) 
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"  DESTINATAIRE : {client_name.upper()}", ln=1, fill=True)
        pdf.set_font("Arial", '', 9)
        pdf.multi_cell(0, 5, client_address.encode('latin-1', 'replace').decode('latin-1'), fill=True)
        
        pdf.ln(5) 
        pdf.draw_table_header()
        
        for row in final_items_to_print:
            # --- ÉTAPE 1: CALCULER LA HAUTEUR NÉCESSAIRE ---
            # On teste la hauteur du texte pour la cellule "Designation" (largeur 55)
            # On définit une hauteur de ligne de base de 5mm pour le multi_cell
            temp_font_size = 9
            pdf.set_font("Arial", '', temp_font_size)
            
            # Calcul manuel simple du nombre de lignes basées sur la longueur du texte
            # (Largeur dispo 55mm, environ 35-40 caractères par ligne en Arial 9)
            text_raw = row['Désignation'].encode('latin-1', 'replace').decode('latin-1')
            char_per_line = 35 
            estimated_lines = max(1, (len(text_raw) // char_per_line) + 1)
            
            # Hauteur minimale pour que le texte respire
            h_text = estimated_lines * 6 
            
            # Si on a une image, on impose 45mm, sinon on prend le plus grand entre 12mm et le texte
            h = 45 if row['Image'] else max(12, h_text)

            # Gestion du saut de page
            if pdf.get_y() + h > 260:
                pdf.add_page()
                pdf.draw_table_header()
            
            x_start, y_start = pdf.get_x(), pdf.get_y()
            
            # --- ÉTAPE 2: DESSINER LES CELLULES AVEC LA MÊME HAUTEUR 'h' ---
            # Colonne Designation
            pdf.multi_cell(55, h/estimated_lines if estimated_lines > 1 else h, text_raw, border=1, align='L')
            
            # Revenir à côté pour les colonnes suivantes en utilisant la hauteur 'h' calculée
            pdf.set_xy(x_start + 55, y_start)
            pdf.cell(30, h, f"{row['P.U.']} {euro}", 1, 0, 'C')
            pdf.cell(12, h, str(row['Qté']), 1, 0, 'C')
            pdf.cell(23, h, f"{row['Total']} {euro}", 1, 0, 'C')
            
            # Colonne Photo
            img_x_box = pdf.get_x()
            pdf.cell(70, h, "", 1, 0)
            
            if row['Image']:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(row['Image'].getvalue())
                    tmp_path = tmp.name
                with Image.open(tmp_path) as img_file:
                    iw, ih = img_file.size
                aspect = iw / ih
                mw, mh = 66, h - 4
                if aspect > (mw / mh):
                    pw, ph = mw, mw / aspect
                else:
                    ph, pw = mh, mh * aspect
                pdf.image(tmp_path, img_x_box + (70 - pw)/2, y_start + (h - ph)/2, w=pw, h=ph)
                os.unlink(tmp_path)
            else:
                pdf.set_xy(img_x_box, y_start)
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(150, 150, 150)
                pdf.cell(70, h, "Non fournie", 0, 0, 'C')
                pdf.set_text_color(0, 0, 0)

            # On déplace le curseur à la ligne suivante (Y de départ + hauteur du bloc)
            pdf.set_xy(10, y_start + h)

        # Total Final
        pdf.ln(5)
        pdf.set_x(120)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(24, 73, 115)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(30, 10, "TOTAL TTC", 1, 0, 'C', True)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 10, f"{total_global} {euro}", 1, 1, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Télécharger le Devis", data=pdf_bytes, file_name=f"Devis_{devis_num}.pdf")
