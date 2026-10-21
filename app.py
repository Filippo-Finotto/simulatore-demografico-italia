import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURAZIONE PAGINA
# ==============================================================================
st.set_page_config(
    page_title="DemographIA Italia | Proiezione 2025-2200",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CSS PERSONALIZZATO: LOOK DARK PREMIUM, GLASSMORPHISM & CARD
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.35);
    }
    
    .kpi-title {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    .kpi-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 10px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    
    .badge-pos {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-neg {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-neutral {
        background: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #1f2937;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #9ca3af;
        font-weight: 600;
        padding: 8px 18px;
        border: none !important;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# CARICAMENTO DATI
# ==============================================================================
def leggi_csv_sicuro(filepath, thousands=None):
    if not os.path.exists(filepath):
        return None
    try:
        df = pd.read_csv(filepath, sep=";", thousands=thousands, low_memory=False, encoding="utf-8")
        if len(df.columns) == 1:
            df = pd.read_csv(filepath, sep=",", thousands=thousands, low_memory=False, encoding="utf-8")
    except Exception:
        df = pd.read_csv(filepath, sep=",", thousands=thousands, low_memory=False, encoding="utf-8")
    df.columns = df.columns.astype(str).str.strip()
    return df

@st.cache_data
def carica_dati_base():
    df_raw = leggi_csv_sicuro("Dati_cittadinanza_2025.csv")
    
    if df_raw is not None:
        col_terr = [c for c in df_raw.columns if c.lower() in ['denominazione', 'territorio']][0]
        df_ita = df_raw[df_raw[col_terr].astype(str).str.strip().str.lower() == 'italia'].copy()
        col_utili = ['Stato di cittadinanza', 'Continente', 'Maschi', 'Femmine', 'Totale']
        df_ita = df_ita[col_utili].copy()
        df_ita['Stato di cittadinanza'] = df_ita['Stato di cittadinanza'].astype(str).str.strip()
        df_ita['Continente'] = df_ita['Continente'].astype(str).str.strip()
        
        for c in ['Maschi', 'Femmine', 'Totale']:
            df_ita[c] = pd.to_numeric(df_ita[c], errors='coerce').fillna(0).astype(float)
        
        mappa_continente = df_ita.drop_duplicates('Stato di cittadinanza').set_index('Stato di cittadinanza')['Continente'].to_dict()

        df_acq = leggi_csv_sicuro("acquisizioni_cittadinanza.csv", thousands=".")
        col_terr_acq = [c for c in df_acq.columns if 'territorio' in c.lower()][0]
        df_acq_ita = df_acq[df_acq[col_terr_acq].astype(str).str.strip().str.lower() == 'italia'].copy()
        col_paesi_acq = [c for c in df_acq_ita.columns if c not in ['Anno', col_terr_acq]]
        for c in col_paesi_acq:
            df_acq_ita[c] = pd.to_numeric(df_acq_ita[c], errors='coerce').fillna(0).astype(float)
        tot_acq = df_acq_ita[col_paesi_acq].sum()

        df_completo = df_ita.copy().set_index('Stato di cittadinanza')
        for c in ['Maschi', 'Femmine', 'Totale']:
            df_completo[c] = df_completo[c].astype(float)

        tot_da_togliere = float(tot_acq['Totale'])
        pm_ita = df_completo.loc['Italia', 'Maschi'] / df_completo.loc['Italia', 'Totale']
        df_completo.loc['Italia', 'Totale'] -= tot_da_togliere
        df_completo.loc['Italia', 'Maschi'] -= (tot_da_togliere * pm_ita)
        df_completo.loc['Italia', 'Femmine'] -= (tot_da_togliere * (1 - pm_ita))

        paesi_singoli_acq = [c for c in col_paesi_acq if c not in ['Totale', 'Altri paesi UE', 'Altri paesi extra-UE']]
        for p in paesi_singoli_acq:
            if p in df_completo.index and tot_acq[p] > 0:
                val = float(tot_acq[p])
                tot_p = df_completo.loc[p, 'Totale']
                pm = (df_completo.loc[p, 'Maschi'] / tot_p) if tot_p > 0 else 0.5
                df_completo.loc[p, 'Totale'] += val
                df_completo.loc[p, 'Maschi'] += val * pm
                df_completo.loc[p, 'Femmine'] += val * (1 - pm)
        df_completo = df_completo.reset_index()

        SOGLIA = 50_000
        df_ita_solo = df_completo[df_completo['Stato di cittadinanza'] == 'Italia'].copy()
        df_estero = df_completo[df_completo['Stato di cittadinanza'] != 'Italia'].copy()
        top_paesi = df_estero[df_estero['Totale'] >= SOGLIA].copy()
        sotto_soglia = df_estero[df_estero['Totale'] < SOGLIA].copy()
        
        continenti = sotto_soglia.groupby('Continente', as_index=False)[['Maschi', 'Femmine', 'Totale']].sum()
        continenti['Stato di cittadinanza'] = 'Altro (' + continenti['Continente'] + ')'
        continenti = continenti.set_index('Stato di cittadinanza')
        for c in ['Maschi', 'Femmine', 'Totale']:
            continenti[c] = continenti[c].astype(float)

        val_ue = float(tot_acq.get('Altri paesi UE', 0))
        if 'Altro (Europa)' in continenti.index and val_ue > 0:
            continenti.loc['Altro (Europa)', 'Totale'] += val_ue
            continenti.loc['Altro (Europa)', 'Maschi'] += val_ue * 0.5
            continenti.loc['Altro (Europa)', 'Femmine'] += val_ue * 0.5

        val_extra = float(tot_acq.get('Altri paesi extra-UE', 0))
        cont_extra = [c for c in ['Altro (Asia)', 'Altro (Africa)', 'Altro (America)', 'Altro (Oceania)'] if c in continenti.index]
        if cont_extra and val_extra > 0:
            peso_tot = continenti.loc[cont_extra, 'Totale'].sum()
            for c in cont_extra:
                quota = continenti.loc[c, 'Totale'] / peso_tot
                continenti.loc[c, 'Totale'] += val_extra * quota
                continenti.loc[c, 'Maschi'] += val_extra * quota * 0.5
                continenti.loc[c, 'Femmine'] += val_extra * quota * 0.5
        continenti = continenti.reset_index()

        df_finale = pd.concat([
            df_ita_solo[col_utili],
            top_paesi[col_utili].sort_values(by='Totale', ascending=False),
            continenti[col_utili].sort_values(by='Totale', ascending=False)
        ], ignore_index=True)

        df_res = leggi_csv_sicuro("Popolazione residente.csv").rename(columns={'Età': 'Eta', 'Totale maschi': 'Maschi', 'Totale femmine': 'Femmine'})
        df_stran = leggi_csv_sicuro("Popolazione straniera residente.csv").rename(columns={'Età': 'Eta'})
        for d in [df_res, df_stran]:
            d['Eta'] = d['Eta'].astype(str).str.extract(r'(\d+)')[0].astype(int)
            for c in ['Maschi', 'Femmine', 'Totale']:
                d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0).astype(float)
        df_res = df_res.sort_values(by='Eta').reset_index(drop=True)
        df_stran = df_stran.sort_values(by='Eta').reset_index(drop=True)
        
        df_autoctoni = df_res.copy()
        df_autoctoni['Maschi'] = df_res['Maschi'] - df_stran['Maschi']
        df_autoctoni['Femmine'] = df_res['Femmine'] - df_stran['Femmine']
        df_autoctoni['Totale'] = df_autoctoni['Maschi'] + df_autoctoni['Femmine']

        p_m_aut = df_autoctoni['Maschi'] / df_autoctoni['Maschi'].sum()
        p_f_aut = df_autoctoni['Femmine'] / df_autoctoni['Femmine'].sum()
        p_m_str = df_stran['Maschi'] / df_stran['Maschi'].sum()
        p_f_str = df_stran['Femmine'] / df_stran['Femmine'].sum()

        righe_base = []
        for _, r in df_finale.iterrows():
            paese = r['Stato di cittadinanza']
            cont = r['Continente']
            pm_curva = p_m_aut if paese == 'Italia' else p_m_str
            pf_curva = p_f_aut if paese == 'Italia' else p_f_str
            for eta in range(101):
                m_val = r['Maschi'] * pm_curva[eta]
                f_val = r['Femmine'] * pf_curva[eta]
                righe_base.append({
                    'Stato di cittadinanza': paese,
                    'Continente': cont,
                    'Eta': eta,
                    'Maschi': m_val,
                    'Femmine': f_val,
                    'Totale': m_val + f_val
                })
        df_simulazione = pd.DataFrame(righe_base)

        df_dec = leggi_csv_sicuro("Decessi2025.csv")
        df_dec_ita = df_dec[df_dec['Ripartizione'].astype(str).str.strip().str.lower() == 'italia'].copy()
        col_eta = [c for c in df_dec_ita.columns if 'eta' in c.lower() or 'età' in c.lower()][0]
        col_sopr = [c for c in df_dec_ita.columns if 'sopravvivenza' in c.lower()][0]
        df_dec_ita[col_eta] = pd.to_numeric(df_dec_ita[col_eta], errors='coerce').fillna(0).astype(int)
        df_m_sopr = df_dec_ita[df_dec_ita['Sesso'].str.strip().str.lower() == 'maschi'].drop_duplicates(col_eta).set_index(col_eta)[col_sopr]
        df_f_sopr = df_dec_ita[df_dec_ita['Sesso'].str.strip().str.lower() == 'femmine'].drop_duplicates(col_eta).set_index(col_eta)[col_sopr]

        df_nasc = leggi_csv_sicuro("Nascite2024.csv")
        mappa_nasc = df_nasc.set_index(df_nasc.columns[0])['Italia'].to_dict() if df_nasc is not None else {}
        donne_fert = df_simulazione[(df_simulazione['Eta'] >= 15) & (df_simulazione['Eta'] <= 49)].groupby('Stato di cittadinanza')['Femmine'].sum()
        dati_fec = {}
        nascite_aut = int(df_autoctoni.loc[df_autoctoni['Eta'] == 0, 'Totale'].values[0])
        for _, r in df_finale.iterrows():
            p = r['Stato di cittadinanza']
            c = r['Continente']
            n_d = donne_fert.get(p, 0)
            if p == 'Italia':
                nas = nascite_aut
            elif p in mappa_nasc:
                nas = mappa_nasc[p]
            else:
                top_list = df_finale[~df_finale['Stato di cittadinanza'].str.startswith('Altro')]['Stato di cittadinanza'].tolist()
                nas = sum(v for k, v in mappa_nasc.items() if mappa_continente.get(k) == c and k not in top_list)
            dati_fec[p] = (nas / n_d) if n_d > 0 else 0.033

        try:
            df_imm = pd.read_excel("immigrati_per_paese.xlsx", header=1)
            df_emig = pd.read_excel("emigrati_per_paese.xlsx", header=1)
            df_migr_ita = pd.read_excel("migrazioni_italiani.xlsx", header=1)
            for d in [df_imm, df_emig, df_migr_ita]:
                d.rename(columns={d.columns[0]: 'Paese'}, inplace=True)
                d.dropna(subset=['Paese'], inplace=True)
                d['Paese'] = d['Paese'].astype(str).str.strip()
            imm_dict = df_imm.set_index('Paese')[2024].dropna().to_dict()
            emig_dict = df_emig.set_index('Paese')[2024].dropna().to_dict()
            tot_isc = float(df_migr_ita.loc[23, 2024])
            tot_canc = float(df_migr_ita.loc[47, 2024])
            cont_list = ['Europa', 'Africa', 'Asia', 'America', 'Oceania']
            imm_ita = max(0.0, tot_isc - sum(float(imm_dict.get(c, 0)) for c in cont_list))
            emig_ita = max(0.0, tot_canc - sum(float(emig_dict.get(c, 0)) for c in cont_list))
            residuo_imm = {c: max(0.0, float(imm_dict.get(c, 0)) - sum(float(imm_dict.get(p, 0)) for p in df_finale['Stato di cittadinanza'] if mappa_continente.get(p) == c and p in imm_dict and not p.startswith('Altro'))) for c in cont_list}
            residuo_emig = {c: max(0.0, float(emig_dict.get(c, 0)) - sum(float(emig_dict.get(p, 0)) for p in df_finale['Stato di cittadinanza'] if mappa_continente.get(p) == c and p in emig_dict and not p.startswith('Altro'))) for c in cont_list}
            gruppi_res = {c: [p for p in df_finale['Stato di cittadinanza'] if mappa_continente.get(p) == c and (p not in imm_dict or p.startswith('Altro')) and p != 'Italia'] for c in cont_list}
            dati_saldi = {}
            for _, r in df_finale.iterrows():
                p = r['Stato di cittadinanza']
                c = r['Continente']
                if p == 'Italia':
                    s = imm_ita - emig_ita
                elif p in imm_dict and not p.startswith('Altro'):
                    s = float(imm_dict.get(p, 0)) - float(emig_dict.get(p, 0))
                else:
                    g_c = gruppi_res.get(c, [])
                    pop_g = df_finale[df_finale['Stato di cittadinanza'].isin(g_c)]['Totale'].sum()
                    q = (r['Totale'] / pop_g) if pop_g > 0 else 0
                    s = (residuo_imm.get(c, 0) - residuo_emig.get(c, 0)) * q
                dati_saldi[p] = int(round(s))
        except Exception:
            dati_saldi = {p: 5000 if p != 'Italia' else -35000 for p in df_finale['Stato di cittadinanza']}

        prop_m_dict = (df_finale.set_index('Stato di cittadinanza')['Maschi'] / df_finale.set_index('Stato di cittadinanza')['Totale']).to_dict()
        return df_simulazione, df_m_sopr, df_f_sopr, dati_fec, dati_saldi, prop_m_dict, df_finale

    else:
        paesi = ['Italia', 'Romania', 'Marocco', 'Albania', 'Cina', 'Bangladesh', 'Ucraina', 'Pakistan', 'Egitto', 'Filippine', 'Altro (Europa)', 'Altro (Africa)', 'Altro (Asia)']
        continenti = ['Europa', 'Europa', 'Africa', 'Europa', 'Asia', 'Asia', 'Europa', 'Asia', 'Africa', 'Asia', 'Europa', 'Africa', 'Asia']
        totali = [51_600_000, 1_100_000, 430_000, 420_000, 310_000, 160_000, 240_000, 150_000, 140_000, 165_000, 450_000, 520_000, 380_000]
        df_finale = pd.DataFrame({'Stato di cittadinanza': paesi, 'Continente': continenti, 'Totale': [float(x) for x in totali]})
        df_finale['Maschi'] = (df_finale['Totale'] * 0.49)
        df_finale['Femmine'] = df_finale['Totale'] - df_finale['Maschi']

        ages = np.arange(101)
        sim_rows = []
        for _, row in df_finale.iterrows():
            shape_age = np.exp(-((ages - (52 if row['Stato di cittadinanza'] == 'Italia' else 35)) ** 2) / 450)
            shape_age /= shape_age.sum()
            for eta in range(101):
                m_pop = row['Maschi'] * shape_age[eta]
                f_pop = row['Femmine'] * shape_age[eta]
                sim_rows.append({
                    'Stato di cittadinanza': row['Stato di cittadinanza'],
                    'Continente': row['Continente'],
                    'Eta': eta,
                    'Maschi': m_pop,
                    'Femmine': f_pop,
                    'Totale': m_pop + f_pop
                })
        df_simulazione = pd.DataFrame(sim_rows)
        surv = np.clip(1.0 - np.exp((ages - 105) / 10.5), 0.0, 0.999)
        df_m_sopr = pd.Series(surv, index=ages)
        df_f_sopr = pd.Series(np.clip(surv * 1.015, 0.0, 0.9995), index=ages)
        dati_fec = {p: 0.027 if p == 'Italia' else 0.048 for p in paesi}
        dati_saldi = {p: -40000 if p == 'Italia' else 12000 for p in paesi}
        prop_m_dict = {p: 0.49 for p in paesi}
        return df_simulazione, df_m_sopr, df_f_sopr, dati_fec, dati_saldi, prop_m_dict, df_finale

df_simulazione, df_m_sopr, df_f_sopr, tassi_fec_base, saldi_base, prop_m_paese, df_finale = carica_dati_base()


# ==============================================================================
# MOTORE DI SIMULAZIONE
# ==============================================================================
@st.cache_data
def esegui_simulazione(anno_inizio, anno_fine, mult_migr, tasso_fec_assoluto, conv_fec, eta_min_migr=18, eta_max_migr=38, eta_picco_migr=26):
    sopr_m = np.array([df_m_sopr.get(eta, 0.5) for eta in range(101)])
    sopr_f = np.array([df_f_sopr.get(eta, 0.5) for eta in range(101)])

    pesi_eta_migr = np.zeros(101)
    x_migr = np.arange(eta_min_migr, eta_max_migr + 1)
    campana = np.exp(-0.5 * ((x_migr - eta_picco_migr) / 4.5) ** 2)
    pesi_eta_migr[eta_min_migr:eta_max_migr + 1] = campana / campana.sum()

    lista_anni = []
    df_curr = df_simulazione.copy()
    df_curr['Anno'] = anno_inizio
    lista_anni.append(df_curr)

    elenco_paesi = df_finale['Stato di cittadinanza'].unique()
    mappa_cont = df_finale.set_index('Stato di cittadinanza')['Continente'].to_dict()
    
    tassi_fec_curr = tassi_fec_base.copy()
    fattore_fec = tasso_fec_assoluto / 1.24
    tassi_fec_curr['Italia'] *= fattore_fec
    tasso_ita_target = tassi_fec_curr['Italia']

    for anno in range(anno_inizio, anno_fine):
        righe_anno = []
        if conv_fec > 0:
            for p in elenco_paesi:
                if p != 'Italia':
                    tassi_fec_curr[p] += (tasso_ita_target - tassi_fec_curr[p]) * conv_fec

        for paese in elenco_paesi:
            sub = df_curr[df_curr['Stato di cittadinanza'] == paese].sort_values(by='Eta')
            m_c = sub['Maschi'].values.astype(float)
            f_c = sub['Femmine'].values.astype(float)

            m_n = np.zeros(101)
            f_n = np.zeros(101)
            m_n[1:101] = m_c[0:100] * sopr_m[0:100]
            f_n[1:101] = f_c[0:100] * sopr_f[0:100]
            m_n[100] += m_c[100] * sopr_m[100]
            f_n[100] += f_c[100] * sopr_f[100]

            d_fert = f_c[15:50].sum()
            nascite = d_fert * tassi_fec_curr.get(paese, 0.033)
            ratio_m = 184283 / 358173
            m_n[0] = nascite * ratio_m
            f_n[0] = nascite * (1 - ratio_m)

            saldo = saldi_base.get(paese, 0) * mult_migr
            qm = prop_m_paese.get(paese, 0.5)
            m_n += (saldo * qm) * pesi_eta_migr
            f_n += (saldo * (1 - qm)) * pesi_eta_migr

            m_n = np.maximum(0.0, m_n)
            f_n = np.maximum(0.0, f_n)

            for eta in range(101):
                righe_anno.append({
                    'Anno': anno + 1,
                    'Stato di cittadinanza': paese,
                    'Continente': mappa_cont[paese],
                    'Eta': eta,
                    'Maschi': m_n[eta],
                    'Femmine': f_n[eta],
                    'Totale': m_n[eta] + f_n[eta]
                })

        df_curr = pd.DataFrame(righe_anno)
        lista_anni.append(df_curr)

    df_out = pd.concat(lista_anni, ignore_index=True)
    for c in ['Maschi', 'Femmine', 'Totale']:
        df_out[c] = df_out[c].round().astype(int)
    return df_out


# ==============================================================================
# HELPER GRAFICI DARK
# ==============================================================================
def applica_stile_dark(fig, height=480):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0"),
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.06)', zerolinecolor='rgba(255, 255, 255, 0.15)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.06)', zerolinecolor='rgba(255, 255, 255, 0.15)'),
        legend=dict(bgcolor='rgba(15, 23, 42, 0.7)', bordercolor='rgba(255, 255, 255, 0.1)', borderwidth=1)
    )
    return fig


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ **Parametri di Simulazione**")
    st.caption("Modifica le ipotesi: tutto si aggiorna all'istante.")

    st.markdown("#### 🎯 Preset Rapidi")
    col_pre1, col_pre2 = st.columns(2)
    with col_pre1:
        if st.button("📊 Istat Base", use_container_width=True):
            st.session_state['mult_migr'] = 100
            st.session_state['fec_assoluto'] = 1.24
            st.session_state['conv'] = False
            st.session_state['horizon'] = 2050
    with col_pre2:
        if st.button("🛑 Confini Chiusi", use_container_width=True):
            st.session_state['mult_migr'] = 0
            st.session_state['fec_assoluto'] = 1.24
            st.session_state['conv'] = False
            st.session_state['horizon'] = 2050

    col_pre3, col_pre4 = st.columns(2)
    with col_pre3:
        if st.button("🍼 Rimpiazzo (2.1)", use_container_width=True):
            st.session_state['mult_migr'] = 100
            st.session_state['fec_assoluto'] = 2.1
            st.session_state['conv'] = True
            st.session_state['horizon'] = 2100
    with col_pre4:
        if st.button("🚀 Alto Flusso", use_container_width=True):
            st.session_state['mult_migr'] = 180
            st.session_state['fec_assoluto'] = 1.35
            st.session_state['conv'] = True
            st.session_state['horizon'] = 2100

    st.markdown("---")
    
    anni_possibili = list(range(2030, 2201, 5))
    default_h = st.session_state.get('horizon', 2050)
    if default_h not in anni_possibili:
        default_h = 2050

    anno_fine = st.select_slider(
        "Orizzonte Temporale", 
        options=anni_possibili,
        value=default_h
    )

    st.markdown("#### ✈️ Flussi Migratori Netti")
    mult_migr_pct = st.slider(
        "Intensità migrazioni (% su 2024)", 
        0, 200, 
        value=st.session_state.get('mult_migr', 100), 
        step=10
    )
    mult_migr = mult_migr_pct / 100.0

    st.markdown("#### 👶 Fecondità Autoctona")
    tasso_fec_assoluto = st.slider(
        "Figli per donna (TFR)", 
        min_value=0.8, max_value=3.0, 
        value=st.session_state.get('fec_assoluto', 1.24), 
        step=0.05,
        help="2.1 è la soglia di rimpiazzo generazionale naturale."
    )

    check_conv = st.checkbox(
        "Attiva convergenza culturale", 
        value=st.session_state.get('conv', False)
    )
    velocita_conv = st.slider("Velocità convergenza annua (%)", 0.0, 5.0, 2.0, step=0.5) / 100.0 if check_conv else 0.0

    st.markdown("---")
    st.info("💡 **Modello:** Cohort-Component a singole coorti [0-100+].")

df_res_sim = esegui_simulazione(2025, anno_fine, mult_migr, tasso_fec_assoluto, velocita_conv)


# ==============================================================================
# HEADER & HERO
# ==============================================================================
st.markdown(f"""
<div style="margin-bottom: 25px;">
    <h1 style="font-size: 2.3rem; font-weight: 800; margin-bottom: 6px; letter-spacing: -0.03em;">
        🇮🇹 Proiezione Demografica d'Italia <span style="background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">(2025 — {anno_fine})</span>
    </h1>
    <p style="color: #94a3b8; font-size: 1.02rem; margin: 0;">
        Simulatore predittivo matriciale <em>Cohort-Component</em> per coorti di età, sesso e reale discendenza geografica.
    </p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# KPI CARDS
# ==============================================================================
tot_2025 = df_res_sim[df_res_sim['Anno'] == 2025]['Totale'].sum()
tot_fine = df_res_sim[df_res_sim['Anno'] == anno_fine]['Totale'].sum()
diff_pop = tot_fine - tot_2025
pct_pop = (diff_pop / tot_2025) * 100

aut_2025 = df_res_sim[(df_res_sim['Anno'] == 2025) & (df_res_sim['Stato di cittadinanza'] == 'Italia')]['Totale'].sum()
aut_fine = df_res_sim[(df_res_sim['Anno'] == anno_fine) & (df_res_sim['Stato di cittadinanza'] == 'Italia')]['Totale'].sum()
diff_aut = aut_fine - aut_2025

quota_aut_2025 = (aut_2025 / tot_2025) * 100
quota_aut_fine = (aut_fine / tot_fine) * 100

quota_est_fine = 100 - quota_aut_fine
diff_quota_est = quota_est_fine - (100 - quota_aut_2025)

df_fine_sub = df_res_sim[df_res_sim['Anno'] == anno_fine]
cum_sum = df_fine_sub.groupby('Eta')['Totale'].sum().cumsum()
eta_mediana = cum_sum[cum_sum >= tot_fine / 2].index[0]

def render_badge(val, is_pct=False, unit="", reverse=False):
    prefix = "+" if val > 0 else ""
    fmt = f"{prefix}{val:.1f}%" if is_pct else f"{prefix}{val:,.0f}".replace(",", ".")
    is_good = val >= 0 if not reverse else val <= 0
    cls = "badge-pos" if is_good else "badge-neg"
    icon = "▲" if val > 0 else "▼" if val < 0 else "•"
    return f'<div class="kpi-badge {cls}"><span>{icon}</span> {fmt} {unit}</div>'

str_tot = f"{tot_fine:,.0f}".replace(",", ".")
str_aut = f"{aut_fine:,.0f}".replace(",", ".")

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">👥 Popolazione Totale</div>
        <div class="kpi-value">{str_tot}</div>
        {render_badge(pct_pop, is_pct=True, unit="vs 2025")}
    </div>
    <div class="kpi-card">
        <div class="kpi-title">🏛️ Autoctoni Italiani</div>
        <div class="kpi-value">{str_aut}</div>
        {render_badge(diff_aut, is_pct=False, unit="residenti")}
    </div>
    <div class="kpi-card">
        <div class="kpi-title">🌍 Quota Origine Estera</div>
        <div class="kpi-value">{quota_est_fine:.1f}%</div>
        {render_badge(diff_quota_est, is_pct=True, unit="punti")}
    </div>
    <div class="kpi-card">
        <div class="kpi-title">⏳ Età Mediana nel {anno_fine}</div>
        <div class="kpi-value">{eta_mediana} <span style="font-size:1.1rem; color:#94a3b8; font-weight:500;">anni</span></div>
        <div class="kpi-badge badge-neutral"><span>•</span> Indice Invecchiamento</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# TAB PRINCIPALI
# ==============================================================================
tab_piramide, tab_trend, tab_classifica, tab_dati = st.tabs([
    "🏛️ Piramide delle Coorti Animata", 
    "📈 Traiettorie & Scomposizione", 
    "🏆 Rango & Classifica Comunità",
    "📊 Esploratore Dati & Export"
])


# ------------------------------------------------------------------------------
# TAB 1: PIRAMIDE (ANIMATA CON SLIDER NATIVO PLOTLY A 60 FPS)
# ------------------------------------------------------------------------------
with tab_piramide:
    col_p_tit, col_p_ctrl = st.columns([2, 1])
    with col_p_tit:
        st.subheader("Piramide Demografica Dinamica")
        st.caption("Trascina lo slider o premi **Play ▶️** per scorrere gli anni in tempo reale fluido dentro il browser.")
    with col_p_ctrl:
        aggrega_5_anni = st.checkbox("Raggruppa in classi di 5 anni", value=False)

    anni_proiezione = sorted(df_res_sim['Anno'].unique())

    if not aggrega_5_anni:
        eta_axis = np.arange(101)
        sub_init = df_res_sim[df_res_sim['Anno'] == 2025]
        aut_m_init = sub_init[sub_init['Stato di cittadinanza'] == 'Italia'].sort_values('Eta')['Maschi'].values
        aut_f_init = sub_init[sub_init['Stato di cittadinanza'] == 'Italia'].sort_values('Eta')['Femmine'].values
        est_m_init = sub_init[sub_init['Stato di cittadinanza'] != 'Italia'].groupby('Eta')['Maschi'].sum().values
        est_f_init = sub_init[sub_init['Stato di cittadinanza'] != 'Italia'].groupby('Eta')['Femmine'].sum().values

        max_val = max(aut_m_init.max() + est_m_init.max(), aut_f_init.max() + est_f_init.max()) * 1.15

        frames = []
        for y in anni_proiezione:
            sub_y = df_res_sim[df_res_sim['Anno'] == y]
            aut_m = sub_y[sub_y['Stato di cittadinanza'] == 'Italia'].sort_values('Eta')['Maschi'].values
            aut_f = sub_y[sub_y['Stato di cittadinanza'] == 'Italia'].sort_values('Eta')['Femmine'].values
            est_m = sub_y[sub_y['Stato di cittadinanza'] != 'Italia'].groupby('Eta')['Maschi'].sum().values
            est_f = sub_y[sub_y['Stato di cittadinanza'] != 'Italia'].groupby('Eta')['Femmine'].sum().values

            frames.append(go.Frame(
                data=[
                    go.Bar(y=eta_axis, x=-aut_m, customdata=aut_m),
                    go.Bar(y=eta_axis, x=-est_m, customdata=est_m),
                    go.Bar(y=eta_axis, x=aut_f),
                    go.Bar(y=eta_axis, x=est_f)
                ],
                name=str(y),
                layout=go.Layout(title_text=f"Struttura per Età e Genere — Anno {y}")
            ))

        fig_p = go.Figure(
            data=[
                go.Bar(y=eta_axis, x=-aut_m_init, name="Maschi Autoctoni", orientation='h', marker_color='#2563eb', customdata=aut_m_init),
                go.Bar(y=eta_axis, x=-est_m_init, name="Maschi Origine Estera", orientation='h', marker_color='#06b6d4', customdata=est_m_init),
                go.Bar(y=eta_axis, x=aut_f_init, name="Femmine Autoctone", orientation='h', marker_color='#e11d48'),
                go.Bar(y=eta_axis, x=est_f_init, name="Femmine Origine Estera", orientation='h', marker_color='#f59e0b')
            ],
            frames=frames
        )

        slider_steps = [
            {"args": [[str(y)], {"frame": {"duration": 100, "redraw": True}, "mode": "immediate"}], "label": str(y), "method": "animate"}
            for y in anni_proiezione
        ]

        fig_p.update_layout(
            barmode='relative', bargap=0.0,
            xaxis=dict(range=[-max_val, max_val], title="Popolazione"),
            yaxis=dict(title="Età Esatta", dtick=10),
            updatemenus=[{
                "type": "buttons", "showactive": False, "x": 0.05, "y": 1.15,
                "buttons": [
                    {"label": "▶️ Play", "method": "animate", "args": [None, {"frame": {"duration": 120, "redraw": True}, "fromcurrent": True}]},
                    {"label": "⏸️ Pausa", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
                ]
            }],
            sliders=[{
                "active": 0, "yanchor": "top", "xanchor": "left",
                "currentvalue": {"font": {"size": 15, "color": "#38bdf8"}, "prefix": "Anno: ", "visible": True},
                "pad": {"b": 10, "t": 35}, "len": 0.9, "x": 0.05, "y": 0, "steps": slider_steps
            }]
        )
    else:
        df_5 = df_res_sim.copy()
        df_5['Classe_Eta'] = pd.cut(df_5['Eta'], bins=list(range(0, 105, 5)) + [120], right=False, labels=[f"{i}-{i+4}" for i in range(0, 100, 5)] + ["100+"])
        piv_5 = df_5.groupby(['Anno', 'Classe_Eta', 'Stato di cittadinanza'], observed=True)[['Maschi', 'Femmine']].sum().reset_index()
        sub_5 = piv_5[piv_5['Anno'] == anno_fine]
        aut_5 = sub_5[sub_5['Stato di cittadinanza'] == 'Italia']
        est_5 = sub_5[sub_5['Stato di cittadinanza'] != 'Italia'].groupby('Classe_Eta', observed=True)[['Maschi', 'Femmine']].sum().reset_index()

        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(y=aut_5['Classe_Eta'], x=-aut_5['Maschi'], orientation='h', name='M Autoctoni', marker_color='#2563eb'))
        fig_p.add_trace(go.Bar(y=est_5['Classe_Eta'], x=-est_5['Maschi'], orientation='h', name='M Origine Estera', marker_color='#06b6d4'))
        fig_p.add_trace(go.Bar(y=aut_5['Classe_Eta'], x=aut_5['Femmine'], orientation='h', name='F Autoctone', marker_color='#e11d48'))
        fig_p.add_trace(go.Bar(y=est_5['Classe_Eta'], x=est_5['Femmine'], orientation='h', name='F Origine Estera', marker_color='#f59e0b'))
        fig_p.update_layout(barmode='relative', title=f"Piramide in Classi Quinquennali — {anno_fine}")

    applica_stile_dark(fig_p, height=640)
    st.plotly_chart(fig_p, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 2: DINAMICHE TEMPORALI CON SUNBURST GEOGRAFICO A TUTTO SCHERMO
# ------------------------------------------------------------------------------
with tab_trend:
    st.subheader("Traiettorie Demografiche Comparate")

    col_t1, col_t2, col_t3 = st.columns([1.2, 1.2, 2.6])
    with col_t1:
        tipo_metrica = st.radio("Scala metrica:", ["Valore Assoluto", "Quota Percentuale (%)"], horizontal=True)
    with col_t2:
        aggrega_macro = st.toggle("Aggrega per Continente", value=False)
    
    tutti_paesi = df_finale.sort_values(by='Totale', ascending=False)['Stato di cittadinanza'].tolist()
    default_paesi = ['Italia', 'Bangladesh', 'Albania', 'Marocco', 'Romania', 'Pakistan', 'Egitto']
    
    with col_t3:
        if not aggrega_macro:
            paesi_scelti = st.multiselect("Filtra comunità:", tutti_paesi, default=[p for p in default_paesi if p in tutti_paesi])
        else:
            paesi_scelti = []

    if aggrega_macro:
        df_trend = df_res_sim.groupby(['Anno', 'Continente'])['Totale'].sum().reset_index()
        colore_key = 'Continente'
    else:
        df_trend = df_res_sim[df_res_sim['Stato di cittadinanza'].isin(paesi_scelti)].groupby(['Anno', 'Stato di cittadinanza'])['Totale'].sum().reset_index()
        colore_key = 'Stato di cittadinanza'

    if not df_trend.empty:
        if "Quota" in tipo_metrica:
            totali_annui = df_res_sim.groupby('Anno')['Totale'].sum().to_dict()
            df_trend['Y'] = (df_trend['Totale'] / df_trend['Anno'].map(totali_annui)) * 100
            y_label = "Quota sul Totale Nazionale (%)"
            hover_fmt = "%{y:.2f}%"
        else:
            df_trend['Y'] = df_trend['Totale']
            y_label = "Numero Residenti"
            hover_fmt = "%{y:,.0f}"

        fig_line = px.line(
            df_trend, x="Anno", y="Y", color=colore_key,
            color_discrete_sequence=px.colors.qualitative.Plotly + px.colors.qualitative.Set2
        )
        fig_line.update_traces(mode="lines+markers", hovertemplate=f"<b>%{{x}}</b>: {hover_fmt}<extra></extra>")
        fig_line.update_layout(hovermode="x unified", xaxis_title="Anno", yaxis_title=y_label)
        applica_stile_dark(fig_line, height=460)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Seleziona almeno un'origine per tracciare il grafico.")

    st.markdown("---")
    st.subheader("🌐 Mappa Gerarchica Geografica Interattiva")
    st.caption("Esplora la scomposizione della popolazione per Continente e Stato. Trascina lo slider temporale o premi **Play ▶️** per vedere la mappa mutare in tempo reale.")

    # COSTRUZIONE SUNBURST ANIMATO NATIVO PLOTLY A TUTTO SCHERMO
    anni_struttura_list = sorted(df_res_sim['Anno'].unique())
    anno_init_s = anni_struttura_list[0]

    df_sun_init = df_res_sim[df_res_sim['Anno'] == anno_init_s]
    fig_sun_base = px.sunburst(df_sun_init, path=['Continente', 'Stato di cittadinanza'], values='Totale', color='Totale', color_continuous_scale='Tealgrn')

    frames_tab2 = []
    for y in anni_struttura_list:
        df_y = df_res_sim[df_res_sim['Anno'] == y]
        temp_sun = px.sunburst(df_y, path=['Continente', 'Stato di cittadinanza'], values='Totale')
        
        frames_tab2.append(go.Frame(
            data=[go.Sunburst(
                labels=temp_sun.data[0].labels,
                parents=temp_sun.data[0].parents,
                values=temp_sun.data[0].values,
                ids=temp_sun.data[0].ids
            )],
            name=str(y)
        ))

    fig_struct = go.Figure(
        data=[fig_sun_base.data[0]],
        frames=frames_tab2
    )

    slider_steps_tab2 = [
        {"args": [[str(y)], {"frame": {"duration": 100, "redraw": True}, "mode": "immediate"}], "label": str(y), "method": "animate"}
        for y in anni_struttura_list
    ]

    fig_struct.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0"),
        height=620,
        margin=dict(l=20, r=20, t=50, b=20),
        updatemenus=[{
            "type": "buttons", "showactive": False, "x": 0.05, "y": 1.12,
            "buttons": [
                {"label": "▶️ Play", "method": "animate", "args": [None, {"frame": {"duration": 120, "redraw": True}, "fromcurrent": True}]},
                {"label": "⏸️ Pausa", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
            ]
        }],
        sliders=[{
            "active": 0, "yanchor": "top", "xanchor": "left",
            "currentvalue": {"font": {"size": 15, "color": "#38bdf8"}, "prefix": "Anno Strutturale: ", "visible": True},
            "pad": {"b": 10, "t": 35}, "len": 0.9, "x": 0.05, "y": 0, "steps": slider_steps_tab2
        }]
    )

    st.plotly_chart(fig_struct, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 3: CLASSIFICA COMUNITÀ (CON ANIMAZIONE NATIVA PLOTLY PER ANNO)
# ------------------------------------------------------------------------------
with tab_classifica:
    col_r1, col_r2 = st.columns([2, 2])
    with col_r1:
        top_n = st.slider("Numero massimo comunità in classifica:", 5, 25, 12, key="sl_top_n_rank")
    with col_r2:
        continente_filtro = st.multiselect(
            "Filtra per Continente:", 
            options=sorted(df_finale['Continente'].unique()), 
            default=sorted(df_finale['Continente'].unique())
        )

    st.subheader("Classifica Evolutiva delle Comunità Estere")
    st.caption("Usa lo slider temporale integrato sotto il grafico per scorrere gli anni e vedere la classifica riordinarsi fluidamente in tempo reale.")

    anni_rank = sorted(df_res_sim['Anno'].unique())
    anno_init_r = anni_rank[0]

    df_rk_init = df_res_sim[
        (df_res_sim['Anno'] == anno_init_r) & 
        (df_res_sim['Stato di cittadinanza'] != 'Italia') &
        (df_res_sim['Continente'].isin(continente_filtro))
    ].groupby('Stato di cittadinanza')['Totale'].sum().reset_index().sort_values(by='Totale', ascending=True).tail(top_n)

    frames_rank = []
    for y in anni_rank:
        df_y = df_res_sim[
            (df_res_sim['Anno'] == y) & 
            (df_res_sim['Stato di cittadinanza'] != 'Italia') &
            (df_res_sim['Continente'].isin(continente_filtro))
        ].groupby('Stato di cittadinanza')['Totale'].sum().reset_index().sort_values(by='Totale', ascending=True).tail(top_n)

        frames_rank.append(go.Frame(
            data=[go.Bar(
                x=df_y['Totale'],
                y=df_y['Stato di cittadinanza'],
                text=df_y['Totale'],
                orientation='h'
            )],
            name=str(y)
        ))

    fig_rank = go.Figure(
        data=[go.Bar(
            x=df_rk_init['Totale'],
            y=df_rk_init['Stato di cittadinanza'],
            text=df_rk_init['Totale'],
            orientation='h',
            texttemplate='%{text:,.0f}',
            textposition='outside',
            marker=dict(color=df_rk_init['Totale'], colorscale='Tealgrn')
        )],
        frames=frames_rank
    )

    slider_steps_rank = [
        {"args": [[str(y)], {"frame": {"duration": 100, "redraw": True}, "mode": "immediate"}], "label": str(y), "method": "animate"}
        for y in anni_rank
    ]

    fig_rank.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0"),
        height=max(480, top_n * 32),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Residenti", yaxis_title="",
        updatemenus=[{
            "type": "buttons", "showactive": False, "x": 0.05, "y": 1.15,
            "buttons": [
                {"label": "▶️ Play", "method": "animate", "args": [None, {"frame": {"duration": 120, "redraw": True}, "fromcurrent": True}]},
                {"label": "⏸️ Pausa", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
            ]
        }],
        sliders=[{
            "active": 0, "yanchor": "top", "xanchor": "left",
            "currentvalue": {"font": {"size": 15, "color": "#38bdf8"}, "prefix": "Anno Classifica: ", "visible": True},
            "pad": {"b": 10, "t": 35}, "len": 0.9, "x": 0.05, "y": 0, "steps": slider_steps_rank
        }]
    )

    st.plotly_chart(fig_rank, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 4: TABELLA DETTAGLIATA & EXPORT
# ------------------------------------------------------------------------------
with tab_dati:
    st.subheader("Matrice Numerica e Download Proiezioni")

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        ricerca_paese = st.text_input("🔍 Cerca comunità o paese:", placeholder="es. Albania, Marocco, Cina...")
    with col_f2:
        mostra_solo_estero = st.checkbox("Escludi Autoctoni Italiani", value=False)

    piv = df_res_sim.groupby(['Anno', 'Stato di cittadinanza'])['Totale'].sum().unstack(level=0)
    piv['Delta Assoluto'] = piv[anno_fine] - piv[2025]
    piv['Variazione %'] = ((piv['Delta Assoluto'] / piv[2025]) * 100).round(1)
    piv[f'Quota {anno_fine}'] = ((piv[anno_fine] / tot_fine) * 100).round(2)

    colonne_mostrate = [2025, anno_fine, 'Delta Assoluto', 'Variazione %', f'Quota {anno_fine}']
    tab_show = piv.sort_values(by=anno_fine, ascending=False)[colonne_mostrate]

    if mostra_solo_estero and 'Italia' in tab_show.index:
        tab_show = tab_show.drop('Italia')

    if ricerca_paese:
        tab_show = tab_show[tab_show.index.str.contains(ricerca_paese, case=False)]

    st.dataframe(
        tab_show.style
            .format({
                2025: "{:,.0f}",
                anno_fine: "{:,.0f}",
                'Delta Assoluto': "{:+,.0f}",
                'Variazione %': "{:+.1f}%",
                f'Quota {anno_fine}': "{:.2f}%"
            })
            .bar(subset=['Delta Assoluto'], align='mid', color=['#ef4444', '#10b981']),
        use_container_width=True,
        height=520
    )

    st.markdown("---")
    col_dwn1, col_dwn2 = st.columns(2)
    with col_dwn1:
        csv_full = df_res_sim.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Microdati Completi (Anno x Età x Origine)",
            data=csv_full,
            file_name=f"simulazione_demografica_italia_{anno_fine}_dettaglio.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dwn2:
        csv_summary = tab_show.to_csv().encode('utf-8')
        st.download_button(
            label="📊 Scarica Tabella Sintetica di Confronto (CSV)",
            data=csv_summary,
            file_name=f"sintesi_demografica_{anno_fine}.csv",
            mime="text/csv",
            use_container_width=True
        )