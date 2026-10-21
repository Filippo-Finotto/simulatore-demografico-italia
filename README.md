# 🇮🇹 Simulatore demografico Italia

**Un modello di simulazione demografica per studiare l'evoluzione della popolazione residente in Italia attraverso età, sesso e origine geografica.**

🌐 **[Prova il simulatore online](https://simulatore-demografico-italia.streamlit.app/)** · 📂 **[Repository GitHub](https://github.com/Filippo-Finotto/simulatore-demografico-italia)**

## 📌 Descrizione del progetto

Il progetto sviluppa un modello di simulazione demografica dell'Italia basato sul metodo *Cohort-Component*, con l'obiettivo di analizzare come la popolazione possa evolvere nel lungo periodo in funzione delle dinamiche di natalità, mortalità e migrazione.

A differenza delle tradizionali statistiche demografiche basate sulla cittadinanza giuridica, il modello adotta una classificazione per **origine geografica e discendenza**, cercando di tracciare separatamente la popolazione di origine italiana e le principali comunità di origine estera, comprese le generazioni nate in Italia.

La simulazione parte dalla struttura demografica del 2025 e applica annualmente le componenti fondamentali del cambiamento della popolazione. Il codice attualmente imposta un orizzonte temporale fino al 2200.

Il progetto utilizza dati demografici ufficiali dell'ISTAT, elaborati e armonizzati attraverso Python e Pandas, per costruire una matrice iniziale della popolazione e proiettarne l'evoluzione nel tempo.

## 🎯 Obiettivi

- Analizzare la struttura della popolazione residente per età, sesso e origine geografica.
- Ricostruire una popolazione iniziale distinta per gruppi di origine.
- Modellare l'evoluzione delle diverse coorti demografiche.
- Simulare gli effetti della fecondità, della mortalità e dei flussi migratori internazionali.
- Confrontare le variazioni assolute e percentuali della popolazione tra gruppi geografici.
- Esplorare le conseguenze di lungo periodo delle dinamiche demografiche attuali.

## ⚙️ Metodologia

Il modello si articola in quattro fasi principali.

### 1. Ricostruzione della popolazione di partenza

I dati ISTAT riferiti al 2025 vengono puliti e armonizzati per costruire una base demografica coerente.

Le principali operazioni comprendono:

- separazione della popolazione con cittadinanza italiana da quella con cittadinanza straniera;
- rielaborazione della serie storica delle acquisizioni di cittadinanza dal 2012 al 2024;
- riallocazione delle acquisizioni ai gruppi di origine utilizzati nel modello;
- mantenimento individuale dei principali Paesi di origine con almeno 50.000 residenti e aggregazione degli altri in cinque gruppi continentali;
- ricostruzione delle distribuzioni per età e sesso.

La popolazione viene rappresentata attraverso una matrice che incrocia gruppi geografici e singole età, da 0 a 100 anni e oltre.

### 2. Mortalità e invecchiamento

A ogni iterazione annuale, le coorti avanzano di un anno e vengono applicate le probabilità di sopravvivenza distinte per età e sesso, ricavate dalle tavole di mortalità.

La classe aperta dei 100 anni e oltre viene mantenuta attraverso la somma dei sopravvissuti della classe precedente e di quelli già appartenenti alla classe terminale.

### 3. Natalità e fecondità

Le nascite vengono calcolate sulla base della popolazione femminile in età riproduttiva, compresa tra 15 e 49 anni, e di un tasso di fecondità specifico per ciascun gruppo.

I nuovi nati vengono distribuiti tra maschi e femmine secondo il rapporto alla nascita ricavato dai dati utilizzati nel modello.

Il gruppo di origine della madre viene mantenuto come riferimento per l'attribuzione demografica dei figli.

### 4. Migrazioni internazionali

Il saldo migratorio netto viene calcolato come differenza tra immigrati ed emigrati, utilizzando le tavole ISTAT riferite al 2024.

I flussi vengono attribuiti ai principali gruppi geografici e ripartiti tra sesso ed età. Per la distribuzione anagrafica dei migranti viene utilizzata una curva a campana concentrata tra 18 e 38 anni, con un picco a 26 anni.

Nello scenario di base, i tassi di fecondità, le probabilità di sopravvivenza e i saldi migratori vengono mantenuti costanti nel tempo.

## 📊 Dati utilizzati

Il modello utilizza le seguenti fonti di dati in formato CSV e XLSX:

| File | Contenuto |
|---|---|
| `Dati_cittadinanza_2025.csv` | Popolazione residente per cittadinanza, sesso e continente |
| `acquisizioni_cittadinanza.csv` | Acquisizioni della cittadinanza italiana, 2012–2024 |
| `Popolazione residente.csv` | Distribuzione della popolazione residente per età e sesso |
| `Popolazione straniera residente.csv` | Distribuzione della popolazione straniera per età e sesso |
| `Decessi2025.csv` | Tavole di mortalità e probabilità di sopravvivenza |
| `Nascite2024.csv` | Nascite registrate sul territorio italiano |
| `migrazioni_italiani.xlsx` | Bilancio migratorio internazionale complessivo |
| `immigrati_per_paese.xlsx` | Iscrizioni dall'estero per Paese di provenienza |
| `emigrati_per_paese.xlsx` | Cancellazioni anagrafiche per l'estero |

**Fonte principale:** [ISTAT — Istituto Nazionale di Statistica](https://www.istat.it/).

## 🛠️ Tecnologie utilizzate

- **Python** — implementazione del modello e gestione dei dati.
- **NumPy** — calcolo numerico e operazioni vettoriali.
- **Pandas** — pulizia, trasformazione e aggregazione dei dataset.
- **Matplotlib** — visualizzazione grafica e analisi demografica.
- **OpenPyXL** — lettura dei file Excel.
- **Jupyter Notebook** — sviluppo, documentazione e analisi del modello.
- **Streamlit** — interfaccia web interattiva del progetto.

## 🚀 Esecuzione in locale

### Prerequisiti

- Python installato sul sistema.
- Git.
- I dataset utilizzati dal notebook.

### Installazione

Clona la repository:

```bash
git clone https://github.com/Filippo-Finotto/simulatore-demografico-italia.git
cd simulatore-demografico-italia
```

Crea e attiva un ambiente virtuale:

```bash
python -m venv .venv
```

Su Linux e macOS:

```bash
source .venv/bin/activate
```

Su Windows:

```bash
.venv\Scripts\activate
```

Installa le dipendenze:

```bash
pip install pandas numpy matplotlib openpyxl jupyter
```

Avvia Jupyter Notebook:

```bash
jupyter notebook
```

Apri `simulazione.ipynb` ed esegui le celle in ordine, assicurandoti che tutti i file di input siano disponibili nei percorsi previsti dal notebook.

Per utilizzare l'interfaccia web pubblicata, visita direttamente il [simulatore online](https://simulatore-demografico-italia.streamlit.app/).

## 📈 Risultati e analisi

Il modello produce una serie longitudinale della popolazione, organizzata per anno, gruppo geografico, età e sesso.

I risultati consentono di analizzare:

- l'evoluzione della popolazione complessiva;
- le variazioni assolute e percentuali rispetto all'anno iniziale;
- il peso relativo dei diversi gruppi geografici;
- i cambiamenti nella struttura per età e sesso;
- le differenze tra le traiettorie demografiche delle diverse comunità.

Le tabelle finali del notebook confrontano la popolazione iniziale e quella proiettata, includendo le variazioni assolute, le percentuali di crescita e le quote sul totale nazionale.

## ⚠️ Assunzioni e limiti

I risultati devono essere interpretati alla luce delle ipotesi e delle semplificazioni adottate.

In particolare:

- **Parametri costanti:** fecondità, sopravvivenza e saldi migratori vengono mantenuti ai livelli di riferimento.
- **Attribuzione per origine materna:** i figli vengono assegnati al gruppo di origine della madre, senza modellare esplicitamente i matrimoni misti.
- **Naturalizzazioni future non simulate:** il modello non rappresenta le successive acquisizioni della cittadinanza italiana come transizioni tra gruppi.
- **Aggregazione geografica:** i Paesi sotto la soglia demografica stabilita vengono riuniti in gruppi continentali.
- **Migrazioni semplificate:** i flussi netti vengono distribuiti attraverso una curva anagrafica prestabilita.

La classificazione per origine geografica è una scelta modellistica del progetto e non coincide con le classificazioni ufficiali della popolazione per cittadinanza. Non rappresenta necessariamente l'identità personale, culturale o nazionale degli individui.

Le proiezioni sono scenari condizionati alle ipotesi del modello, non previsioni certe del futuro. L'incertezza cresce con l'estensione dell'orizzonte temporale.

## 📄 Licenza

La licenza del progetto deve essere specificata nella repository. In assenza di una licenza esplicita, non si deve presumere che il codice possa essere riutilizzato senza restrizioni.

---

**Autore:** [Filippo Finotto](https://github.com/Filippo-Finotto)

**Demo:** [Simulatore demografico Italia](https://simulatore-demografico-italia.streamlit.app/)
