import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

FILENAME = 'eksperiment_data.csv'
PNG_FILENAME = 'gjennomsnitt_grafer.png' # Navn på PNG-filen
EXPECTED_COLUMNS = ['AgeGroup', 'ParticipantID', 'ImageType', 'ImageName', 'Spm1', 'Spm2', 'Spm3']

# --- NY Initial Data (kun basert på siste input) ---
initial_data = {
    'AgeGroup': ['16-21', '16-21', '30-50', '30-50', '30-50', '30-50'],
    'ParticipantID': ['Jente 18', 'Jente 18', 'Kvinne 36', 'Kvinne 36', 'Mann 38', 'Mann 38'],
    'ImageType': ['Menneske', 'KI', 'Menneske', 'KI', 'Menneske', 'KI'],
    'ImageName': ['Kjedsomhet', 'Kjedsomhet', 'Kjedsomhet', 'Kjedsomhet', 'Sinne', 'Sinne'], # Forenklet navn
    'Spm1': ['kaos', 'Fred', 'Sinne', 'Nostalgi', 'Krig/frykt', 'Frykt'],
    'Spm2': [3, 4, 5, 7, 2, 2], # Respons/Intensitet
    'Spm3': [4, 8, 3, 9, 5, 5]  # Behagelighet
}
initial_df = pd.DataFrame(initial_data)

# --- Filhåndtering ---
if not os.path.exists(FILENAME):
    print(f"Datafil '{FILENAME}' ikke funnet. Oppretter fil med de 3 spesifiserte deltakerne...")
    try:
        initial_df[EXPECTED_COLUMNS].to_csv(FILENAME, index=False, encoding='utf-8-sig')
        print(f"Fil '{FILENAME}' opprettet.")
    except Exception as e:
        print(f"FEIL: Kunne ikke skrive til fil '{FILENAME}': {e}")
        exit()
else:
    print(f"Bruker eksisterende datafil: '{FILENAME}'")

# --- Les Data ---
try:
    df = pd.read_csv(FILENAME, encoding='utf-8-sig')
    if df.empty:
        raise ValueError("Datafilen er tom.")
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Mangler følgende kolonner i filen: {', '.join(missing_cols)}")
    df['Spm2'] = pd.to_numeric(df['Spm2'], errors='coerce')
    df['Spm3'] = pd.to_numeric(df['Spm3'], errors='coerce')
    original_rows = len(df)
    df.dropna(subset=['Spm2', 'Spm3'], inplace=True)
    removed_rows = original_rows - len(df)
    if removed_rows > 0:
        print(f"ADVARSEL: Fjernet {removed_rows} rad(er) pga. ugyldige scorer.")
    if df.empty:
      raise ValueError("Ingen gyldige datarader igjen.")
except Exception as e:
    print(f"FEIL under lesing/behandling av '{FILENAME}': {e}")
    df = pd.DataFrame()

# --- Databehandling (Beregn Gjennomsnitt med Pandas) ---
average_scores = pd.DataFrame()
plot_data_spm2 = pd.DataFrame()
plot_data_spm3 = pd.DataFrame()
age_groups_found = []

if not df.empty:
    try:
        df_filtered = df[df['ImageType'].isin(['Menneske', 'KI'])]
        if df_filtered.empty:
             raise ValueError("Ingen rader med ImageType 'Menneske' eller 'KI' funnet.")

        # Grupper etter Aldersgruppe og Bildetype, beregn gjennomsnitt (mean) for Spm2 og Spm3
        average_scores_calc = df_filtered.groupby(['AgeGroup', 'ImageType'])[['Spm2', 'Spm3']].mean()
        print("\nRå gjennomsnittsberegning:\n", average_scores_calc) # Debug print

        average_scores = average_scores_calc.unstack() # Gjør om fra multi-index til kolonner
        average_scores.columns = ['_'.join(col).strip() for col in average_scores.columns.values]
        average_scores.reset_index(inplace=True)

        age_groups_found = average_scores['AgeGroup'].tolist()
        if len(age_groups_found) == 0:
             raise ValueError("Ingen aldersgrupper funnet etter gruppering.")

        plot_data_spm2 = average_scores[['AgeGroup', 'Spm2_Menneske', 'Spm2_KI']].set_index('AgeGroup')
        plot_data_spm3 = average_scores[['AgeGroup', 'Spm3_Menneske', 'Spm3_KI']].set_index('AgeGroup')

        print("\nBeregnet gjennomsnitt (formatert for plot):")
        print(average_scores.to_string(index=False, float_format='%.2f'))

    except KeyError as ke:
        print(f"FEIL under klargjøring av plot-data (mangler kanskje data for en gruppe/imagetype?): {ke}")
        average_scores = pd.DataFrame()
    except Exception as e:
        print(f"FEIL under beregning av gjennomsnitt: {e}")
        average_scores = pd.DataFrame()
else:
    print("Kan ikke behandle data, DataFrame er tom.")

# --- Plotting ---
if not average_scores.empty:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Gjennomsnittsresponser: Sammenligning av Aldersgrupper (Del 1)', fontsize=16, y=1.03)

    bar_width = 0.35
    index = np.arange(len(age_groups_found))

    # Graf 1: Respons/Emosjon Intensitet (Spm 2)
    rects1 = axes[0].bar(index - bar_width/2, plot_data_spm2['Spm2_Menneske'], bar_width, label='Menneskeskapt', color='skyblue')
    rects2 = axes[0].bar(index + bar_width/2, plot_data_spm2['Spm2_KI'], bar_width, label='KI-generert', color='lightcoral')
    axes[0].set_ylabel('Gjennomsnittlig score (1-10)')
    axes[0].set_title('Gj.sn. Respons/Emosjon Intensitet (Spm 2)')
    axes[0].set_xticks(index)
    axes[0].set_xticklabels(age_groups_found, rotation=0)
    axes[0].set_ylim(0, 11)
    axes[0].legend(title="Bildetype")
    axes[0].grid(axis='y', linestyle='--')
    axes[0].bar_label(rects1, padding=3, fmt='%.2f', fontsize=9)
    axes[0].bar_label(rects2, padding=3, fmt='%.2f', fontsize=9)

    # Graf 2: Behagelighet (Spm 3)
    rects3 = axes[1].bar(index - bar_width/2, plot_data_spm3['Spm3_Menneske'], bar_width, label='Menneskeskapt', color='skyblue')
    rects4 = axes[1].bar(index + bar_width/2, plot_data_spm3['Spm3_KI'], bar_width, label='KI-generert', color='lightcoral')
    axes[1].set_ylabel('Gjennomsnittlig score (1-10)')
    axes[1].set_title('Gj.sn. Behagelighet (Spm 3)')
    axes[1].set_xticks(index)
    axes[1].set_xticklabels(age_groups_found, rotation=0)
    axes[1].set_ylim(0, 11)
    axes[1].legend(title="Bildetype")
    axes[1].grid(axis='y', linestyle='--')
    axes[1].bar_label(rects3, padding=3, fmt='%.2f', fontsize=9)
    axes[1].bar_label(rects4, padding=3, fmt='%.2f', fontsize=9)

    # Legg til fotnote om ulike bilder
    if "16-21" in age_groups_found and "30-50" in age_groups_found:
         fig.text(0.5, -0.02, '*Merk: Aldersgruppene vurderte ulike bilder (Kjedsomhet vs. Sinne).',
                  ha='center', va='top', fontsize=9, style='italic')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # --- Lagre figuren som en PNG ---
    try:
        plt.savefig(PNG_FILENAME, format='png', bbox_inches='tight', dpi=150)
        print(f"\nGrafen ble lagret som '{PNG_FILENAME}'")
    except Exception as e:
        print(f"FEIL under lagring til PNG '{PNG_FILENAME}': {e}")

    # --- Vis grafen (kommentert ut) ---
    # plt.show()

    plt.close(fig) # Lukk figuren for å frigjøre minne

else:
    print("\nKunne ikke generere plot, ingen gyldig data funnet eller beregnet fra filen.")

print("\n--- Instruksjoner for å legge til data ---")
print(f"1. Data leses fra '{FILENAME}'.")
print(f"2. Hvis filen ble nyopprettet, inneholder den KUN data for Jente 18, Kvinne 36, Mann 38.")
print(f"3. Åpne '{FILENAME}' og legg til nye rader nederst for flere deltakere.")
print("4. Kolonnene må være: AgeGroup,ParticipantID,ImageType,ImageName,Spm1,Spm2,Spm3")
print("5. Lagre CSV-filen.")
print(f"6. Kjør dette scriptet på nytt for å lage en oppdatert '{PNG_FILENAME}'.")