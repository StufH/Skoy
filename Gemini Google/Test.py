import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Filnavn ---
FILENAME = 'eksperiment_data.csv'
PNG_FILENAME_ALL = 'graf_alle_grupper_alle_spm.png'
PNG_FILENAME_G1 = 'graf_gruppe_16-21.png'
PNG_FILENAME_G2 = 'graf_gruppe_30-50.png'
PNG_FILENAME_SPM2 = 'graf_alle_grupper_spm2.png'
PNG_FILENAME_SPM3 = 'graf_alle_grupper_spm3.png'
PNG_FILENAME_EMO_MATCH_GRAPH = 'graf_rett_emosjon_prosent.png'
PNG_FILENAME_EMO_MATCH_TABLE = 'tabell_rett_emosjon_status.png'
PNG_FILENAME_KJONN_SPM2 = 'graf_kjonn_spm2.png'
PNG_FILENAME_KJONN_SPM3 = 'graf_kjonn_spm3.png'
PNG_FILENAME_KJONN_EMO_MATCH = 'graf_kjonn_rett_emosjon.png'
PNG_FILENAME_RAADATA_TABLE = 'tabell_raadata.png' # Filnavn for ny rådata-tabell

EXPECTED_COLUMNS = ['AgeGroup', 'ParticipantID', 'ImageType', 'ImageName', 'Spm1', 'Spm2', 'Spm3']

# --- Initial Data (basert på siste input - 8 deltakere x 2 bilder = 16 rader) ---
initial_data = {
    'AgeGroup': ['16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','16-21','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50','30-50'],
    'ParticipantID': ['Jente 18a','Jente 18a','Gutt 18a','Gutt 18a','Gutt 17','Gutt 17','Jente 18b','Jente 18b','Gutt 19','Gutt 19','Gutt 18b','Gutt 18b','Jente 19','Jente 19','Jente 20','Jente 20','Kvinne 36','Kvinne 36','Mann 38','Mann 38','Mann 50','Mann 50','Mann 44','Mann 44','Kvinne 47','Kvinne 47','Mann 35','Mann 35','Kvinne 33','Kvinne 33','Kvinne 42','Kvinne 42'],
    'ImageType': ['Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI','Menneske','KI'],
    'ImageName': ['Kjedsomhet','Kjedsomhet','Nostalgi','Nostalgi','Frykt','Frykt','Tristhet','Tristhet','Glede','Glede','Avsky','Avsky','Overraskelse','Overraskelse','Sinne','Sinne','Kjedsomhet','Kjedsomhet','Sinne','Sinne','Nostalgi','Nostalgi','Frykt','Frykt','Avsky','Avsky','Glede','Glede','Overraskelse','Overraskelse','Tristhet','Tristhet'],
    'Spm1': ['kaos','Fred','ukomfortabel','Glede','sinne','håp','Tristhet','Tristhet','Nostalgi','Glede','Kaos','Kvalme','frykt','Overveldende','Sinne','Frykt','Sinne','Nostalgi','Krig/frykt','Frykt','nysgjerrighet','Avslappende','Frykt','Kaotisk','Forvirring','Avsky','Avslapning','Forvirring','Tristhet','Forvirring','Tristhet','Tristhet'],
    'Spm2': [3,4,6.9,8,6,4,3,7,4,6,4,8,3,7,4,8,5,7,2,2,8,4,5,9,7,10,3,4,7,7,7,9],
    'Spm3': [4,8,3,8,3,8,5,3,5,7,3,1,4,2,5,2,3,9,5,5,2,4,7,2,2,0,7,6,2,5,6,5]
}
initial_df = pd.DataFrame(initial_data)

# --- Definisjon av "Rett Emosjon" ---
correct_emotion_map = {
    'kjedsomhet': ['kjedsomhet', 'kjedelig'], 'nostalgi': ['nostalgi', 'nostalgisk'],
    'sinne': ['sinne'], 'frykt': ['frykt', 'krig/frykt'], 'avsky': ['avsky', 'kvalme'],
    'glede': ['glede', 'glad', 'håp'], 'overraskelse': ['overraskelse', 'overrasket', 'overveldende'],
    'tristhet': ['tristhet', 'trist']
}
correct_matches_log = {}

def is_emotion_correct(row):
    theme = str(row['ImageName']).lower().strip(); perceived = str(row['Spm1']).lower().strip()
    normalized_map = {k.lower(): [v.lower() for v in val] for k, val in correct_emotion_map.items()}
    is_correct = False
    if theme in normalized_map:
        is_correct = perceived in normalized_map[theme]
        if is_correct:
            original_theme = row['ImageName']; original_perceived = row['Spm1']
            if original_theme not in correct_matches_log: correct_matches_log[original_theme] = set()
            correct_matches_log[original_theme].add(original_perceived)
    return 1 if is_correct else 0

def get_gender(participant_id):
    pid_lower = str(participant_id).lower()
    if 'kvinne' in pid_lower or 'jente' in pid_lower: return 'Kvinne/Jente'
    elif 'mann' in pid_lower or 'gutt' in pid_lower: return 'Mann/Gutt'
    else: return 'Ukjent'

# --- Filhåndtering ---
if not os.path.exists(FILENAME):
    print(f"Datafil '{FILENAME}' ikke funnet. Oppretter fil med 16 målinger...")
    try:
        correct_matches_log = {}; initial_df['CorrectEmotion'] = initial_df.apply(is_emotion_correct, axis=1)
        initial_df['Gender'] = initial_df['ParticipantID'].apply(get_gender)
        output_columns = EXPECTED_COLUMNS + ['CorrectEmotion', 'Gender']
        initial_df[output_columns].to_csv(FILENAME, index=False, encoding='utf-8-sig')
        print(f"Fil '{FILENAME}' opprettet.")
    except Exception as e: print(f"FEIL: Kunne ikke skrive til fil '{FILENAME}': {e}"); exit()
else: print(f"Bruker eksisterende datafil: '{FILENAME}'")

# --- Les Data ---
df = pd.DataFrame()
try:
    df = pd.read_csv(FILENAME, encoding='utf-8-sig')
    if df.empty: raise ValueError("Datafilen er tom.")
    check_cols = EXPECTED_COLUMNS + ['Gender']
    missing_cols = [col for col in check_cols if col not in df.columns]
    if missing_cols:
         if 'Gender' in missing_cols and 'ParticipantID' in df.columns:
             print("ADVARSEL: Mangler 'Gender'-kolonne, legger den til basert på ParticipantID.")
             df['Gender'] = df['ParticipantID'].apply(get_gender); missing_cols.remove('Gender')
         if missing_cols: raise ValueError(f"Mangler kolonner: {', '.join(missing_cols)}")
    df['Spm2'] = pd.to_numeric(df['Spm2'], errors='coerce'); df['Spm3'] = pd.to_numeric(df['Spm3'], errors='coerce')
    df['Spm1'] = df['Spm1'].astype(str); df['ImageName'] = df['ImageName'].astype(str); df['Gender'] = df['Gender'].astype(str)
    original_rows = len(df); df.dropna(subset=['Spm2', 'Spm3', 'ImageName', 'Spm1', 'AgeGroup', 'ImageType', 'Gender'], inplace=True)
    removed_rows = original_rows - len(df)
    if removed_rows > 0: print(f"ADVARSEL: Fjernet {removed_rows} rad(er) pga. ugyldige/manglende verdier.")
    if df.empty: raise ValueError("Ingen gyldige datarader igjen.")
    correct_matches_log = {}
    if 'CorrectEmotion' not in df.columns:
        print("Beregner 'CorrectEmotion' kolonne..."); df['CorrectEmotion'] = df.apply(is_emotion_correct, axis=1)
    else:
        df['CorrectEmotion'] = pd.to_numeric(df['CorrectEmotion'], errors='coerce').fillna(0).astype(int)
        print("Bruker eksisterende 'CorrectEmotion' kolonne.")
        for idx, row in df[df['CorrectEmotion'] == 1].iterrows():
             original_theme = row['ImageName']; original_perceived = row['Spm1']
             if original_theme not in correct_matches_log: correct_matches_log[original_theme] = set()
             correct_matches_log[original_theme].add(original_perceived)
except Exception as e: print(f"FEIL under lesing/behandling av '{FILENAME}': {e}"); df = pd.DataFrame()

# --- Databehandling ---
average_scores_grouped_age = pd.DataFrame(); average_scores_grouped_gender = pd.DataFrame()
plot_data_age_spm2 = pd.DataFrame(); plot_data_age_spm3 = pd.DataFrame(); plot_data_age_emo_match = pd.DataFrame()
plot_data_gender_spm2 = pd.DataFrame(); plot_data_gender_spm3 = pd.DataFrame(); plot_data_gender_emo_match = pd.DataFrame()
age_groups_found = []; genders_found_list = []
averages_dict_age = {}; averages_dict_gender = {}

if not df.empty:
    try:
        df_filtered = df[df['ImageType'].isin(['Menneske', 'KI'])]
        if df_filtered.empty: raise ValueError("Ingen rader med ImageType 'Menneske' eller 'KI'.")
        # --- Gjennomsnitt etter ALDER ---
        avg_calc_age = df_filtered.groupby(['AgeGroup', 'ImageType'])[['Spm2', 'Spm3', 'CorrectEmotion']].mean()
        for index, row in avg_calc_age.iterrows(): averages_dict_age.setdefault(index[0], {})[index[1]] = row.to_dict()
        average_scores_grouped_age = avg_calc_age.unstack().fillna(0); average_scores_grouped_age.columns = ['_'.join(col).strip() for col in average_scores_grouped_age.columns.values]; average_scores_grouped_age.reset_index(inplace=True)
        age_groups_found = average_scores_grouped_age['AgeGroup'].tolist()
        if not age_groups_found: raise ValueError("Ingen aldersgrupper funnet (Alder).")
        required_cols = ['Spm2_Menneske','Spm2_KI','Spm3_Menneske','Spm3_KI','CorrectEmotion_Menneske','CorrectEmotion_KI']
        for col in required_cols: average_scores_grouped_age[col] = average_scores_grouped_age.get(col, 0.0)
        plot_data_age_spm2 = average_scores_grouped_age.set_index('AgeGroup')[['Spm2_Menneske', 'Spm2_KI']]; plot_data_age_spm3 = average_scores_grouped_age.set_index('AgeGroup')[['Spm3_Menneske', 'Spm3_KI']]; plot_data_age_emo_match = average_scores_grouped_age.set_index('AgeGroup')[['CorrectEmotion_Menneske', 'CorrectEmotion_KI']]
        print("\nBeregnet gjennomsnitt/andel (etter ALDER):"); print(average_scores_grouped_age.to_string(index=False, float_format='%.2f'))

        # --- Gjennomsnitt etter KJØNN ---
        df_gender_filtered = df_filtered[df_filtered['Gender'] != 'Ukjent']
        if df_gender_filtered.empty: raise ValueError("Ingen rader med gyldig Kjønn funnet.")
        avg_calc_gender = df_gender_filtered.groupby(['Gender', 'ImageType'])[['Spm2', 'Spm3', 'CorrectEmotion']].mean()
        for index, row in avg_calc_gender.iterrows(): averages_dict_gender.setdefault(index[0], {})[index[1]] = row.to_dict()
        average_scores_grouped_gender = avg_calc_gender.unstack().fillna(0); average_scores_grouped_gender.columns = ['_'.join(col).strip() for col in average_scores_grouped_gender.columns.values]; average_scores_grouped_gender.reset_index(inplace=True)
        genders_found_list = average_scores_grouped_gender['Gender'].tolist()
        if not genders_found_list: raise ValueError("Ingen kjønn funnet etter gruppering (Kjønn).")
        for col in required_cols: average_scores_grouped_gender[col] = average_scores_grouped_gender.get(col, 0.0)
        plot_data_gender_spm2 = average_scores_grouped_gender.set_index('Gender')[['Spm2_Menneske', 'Spm2_KI']]; plot_data_gender_spm3 = average_scores_grouped_gender.set_index('Gender')[['Spm3_Menneske', 'Spm3_KI']]; plot_data_gender_emo_match = average_scores_grouped_gender.set_index('Gender')[['CorrectEmotion_Menneske', 'CorrectEmotion_KI']]
        print("\nBeregnet gjennomsnitt/andel (etter KJØNN):"); print(average_scores_grouped_gender.to_string(index=False, float_format='%.2f'))

    except Exception as e:
        print(f"FEIL under beregning av gjennomsnitt: {e}"); average_scores_grouped_age = pd.DataFrame(); average_scores_grouped_gender = pd.DataFrame(); averages_dict_age = {}; averages_dict_gender = {}
else: print("Kan ikke behandle data, DataFrame er tom.")

# --- Plotting ---
plot_counter = 0
if not average_scores_grouped_age.empty and not average_scores_grouped_gender.empty: # Trenger begge for å lage alle plots
    image_types_plot = ['Menneskeskapt', 'KI-generert']
    bar_width = 0.35
    index_groups_age = np.arange(len(age_groups_found))
    index_types = np.arange(len(image_types_plot))
    index_genders = np.arange(len(genders_found_list))

    # --- 1. Lagre Graf 1: Alle ALDERSGRUPPER, Alle spørsmål ---
    try:
        fig1, axes1 = plt.subplots(1, 2, figsize=(14, 6)); fig1.suptitle('Gj.sn. Respons & Behagelighet: Sammenligning av Aldersgrupper (Del 1)', fontsize=16, y=1.03)
        plot_data_age_spm2_reidx = plot_data_age_spm2.reindex(index=age_groups_found); plot_data_age_spm3_reidx = plot_data_age_spm3.reindex(index=age_groups_found)
        rects1 = axes1[0].bar(index_groups_age - bar_width/2, plot_data_age_spm2_reidx['Spm2_Menneske'], bar_width, label='Menneskeskapt', color='skyblue'); rects2 = axes1[0].bar(index_groups_age + bar_width/2, plot_data_age_spm2_reidx['Spm2_KI'], bar_width, label='KI-generert', color='lightcoral')
        axes1[0].set_ylabel('Gjennomsnittlig score (1-10)'); axes1[0].set_title('Gj.sn. Respons/Emosjon Intensitet (Spm 2)'); axes1[0].set_xticks(index_groups_age); axes1[0].set_xticklabels(age_groups_found, rotation=0); axes1[0].set_ylim(0, 11); axes1[0].legend(title="Bildetype"); axes1[0].grid(axis='y', linestyle='--'); axes1[0].bar_label(rects1, padding=3, fmt='%.2f', fontsize=9); axes1[0].bar_label(rects2, padding=3, fmt='%.2f', fontsize=9)
        rects3 = axes1[1].bar(index_groups_age - bar_width/2, plot_data_age_spm3_reidx['Spm3_Menneske'], bar_width, label='Menneskeskapt', color='skyblue'); rects4 = axes1[1].bar(index_groups_age + bar_width/2, plot_data_age_spm3_reidx['Spm3_KI'], bar_width, label='KI-generert', color='lightcoral')
        axes1[1].set_ylabel('Gjennomsnittlig score (1-10)'); axes1[1].set_title('Gj.sn. Behagelighet (Spm 3)'); axes1[1].set_xticks(index_groups_age); axes1[1].set_xticklabels(age_groups_found, rotation=0); axes1[1].set_ylim(0, 11); axes1[1].legend(title="Bildetype"); axes1[1].grid(axis='y', linestyle='--'); axes1[1].bar_label(rects3, padding=3, fmt='%.2f', fontsize=9); axes1[1].bar_label(rects4, padding=3, fmt='%.2f', fontsize=9)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_ALL, format='png', bbox_inches='tight', dpi=150); print(f"\nGraf 1 lagret: {PNG_FILENAME_ALL}"); plot_counter += 1; plt.close(fig1)
    except Exception as e: print(f"FEIL under Graf 1: {e}"); plt.close(fig1)

    # --- 2. Lagre Graf 2: Gruppe 16-21, Begge spørsmål ---
    age_group_1 = "16-21";
    if age_group_1 in averages_dict_age:
        try:
            fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5), sharey=True); fig2.suptitle(f'Gjennomsnittsresponser - Aldersgruppe: {age_group_1}', fontsize=16)
            avg_data = averages_dict_age[age_group_1]
            spm2_m = avg_data.get('Menneske', {}).get('Spm2', np.nan); spm2_k = avg_data.get('KI', {}).get('Spm2', np.nan); spm3_m = avg_data.get('Menneske', {}).get('Spm3', np.nan); spm3_k = avg_data.get('KI', {}).get('Spm3', np.nan)
            if np.isnan([spm2_m, spm2_k, spm3_m, spm3_k]).any(): raise ValueError(f"Manglende snittverdier for {age_group_1}")
            bars1 = axes2[0].bar(image_types_plot, [spm2_m, spm2_k], color=['skyblue', 'lightcoral']); axes2[0].set_title('Gj.sn. Respons/Emosjon Intensitet (Spm 2)'); axes2[0].set_ylabel('Gjennomsnittlig score (1-10)'); axes2[0].set_ylim(0, 11); axes2[0].bar_label(bars1, padding=3, fmt='%.2f', fontsize=9); axes2[0].grid(axis='y', linestyle='--')
            bars2 = axes2[1].bar(image_types_plot, [spm3_m, spm3_k], color=['skyblue', 'lightcoral']); axes2[1].set_title('Gj.sn. Behagelighet (Spm 3)'); axes2[1].set_ylim(0, 11); axes2[1].bar_label(bars2, padding=3, fmt='%.2f', fontsize=9); axes2[1].grid(axis='y', linestyle='--')
            p_count = df[df['AgeGroup'] == age_group_1]['ParticipantID'].nunique() if not df.empty else 0; fig2.text(0.5, 0.01, f'*Merk: Gjennomsnitt basert på {p_count} deltaker(e).', ha='center', va='top', fontsize=9, style='italic')
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_G1, format='png', bbox_inches='tight', dpi=150); print(f"Graf 2 lagret: {PNG_FILENAME_G1}"); plot_counter += 1; plt.close(fig2)
        except Exception as e: print(f"FEIL under Graf 2 ({age_group_1}): {e}"); plt.close(fig2)
    else: print(f"Ingen data å plotte for Graf 2 ({age_group_1}).")

    # --- 3. Lagre Graf 3: Gruppe 30-50, Begge spørsmål ---
    age_group_2 = "30-50";
    if age_group_2 in averages_dict_age:
        try:
            fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5), sharey=True); fig3.suptitle(f'Gjennomsnittsresponser - Aldersgruppe: {age_group_2}', fontsize=16)
            avg_data = averages_dict_age[age_group_2]
            spm2_m = avg_data.get('Menneske', {}).get('Spm2', np.nan); spm2_k = avg_data.get('KI', {}).get('Spm2', np.nan); spm3_m = avg_data.get('Menneske', {}).get('Spm3', np.nan); spm3_k = avg_data.get('KI', {}).get('Spm3', np.nan)
            if np.isnan([spm2_m, spm2_k, spm3_m, spm3_k]).any(): raise ValueError(f"Manglende snittverdier for {age_group_2}")
            bars1 = axes3[0].bar(image_types_plot, [spm2_m, spm2_k], color=['skyblue', 'lightcoral']); axes3[0].set_title('Gj.sn. Respons/Emosjon Intensitet (Spm 2)'); axes3[0].set_ylabel('Gjennomsnittlig score (1-10)'); axes3[0].set_ylim(0, 11); axes3[0].bar_label(bars1, padding=3, fmt='%.2f', fontsize=9); axes3[0].grid(axis='y', linestyle='--')
            bars2 = axes3[1].bar(image_types_plot, [spm3_m, spm3_k], color=['skyblue', 'lightcoral']); axes3[1].set_title('Gj.sn. Behagelighet (Spm 3)'); axes3[1].set_ylim(0, 11); axes3[1].bar_label(bars2, padding=3, fmt='%.2f', fontsize=9); axes3[1].grid(axis='y', linestyle='--')
            p_count = df[df['AgeGroup'] == age_group_2]['ParticipantID'].nunique() if not df.empty else 0; fig3.text(0.5, 0.01, f'*Merk: Gjennomsnitt basert på {p_count} deltaker(e).', ha='center', va='top', fontsize=9, style='italic')
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_G2, format='png', bbox_inches='tight', dpi=150); print(f"Graf 3 lagret: {PNG_FILENAME_G2}"); plot_counter += 1; plt.close(fig3)
        except Exception as e: print(f"FEIL under Graf 3 ({age_group_2}): {e}"); plt.close(fig3)
    else: print(f"Ingen data å plotte for Graf 3 ({age_group_2}).")

    # --- 4. Lagre Graf 4: Alle ALDERSGRUPPER, Kun Spm 2 ---
    try:
        fig4, ax4 = plt.subplots(1, 1, figsize=(7, 6)); fig4.suptitle('Gj.sn. Respons/Intensitet (Spm 2): Sammenligning Alder', fontsize=14, y=1.0)
        plot_data_age_spm2_reidx = plot_data_age_spm2.reindex(index=age_groups_found)
        rects1 = ax4.bar(index_groups_age - bar_width/2, plot_data_age_spm2_reidx['Spm2_Menneske'], bar_width, label='Menneskeskapt', color='skyblue'); rects2 = ax4.bar(index_groups_age + bar_width/2, plot_data_age_spm2_reidx['Spm2_KI'], bar_width, label='KI-generert', color='lightcoral')
        ax4.set_ylabel('Gjennomsnittlig score (1-10)'); ax4.set_title('Spm 2: Respons/Emosjon Intensitet'); ax4.set_xticks(index_groups_age); ax4.set_xticklabels(age_groups_found, rotation=0); ax4.set_ylim(0, 11); ax4.legend(title="Bildetype"); ax4.grid(axis='y', linestyle='--'); ax4.bar_label(rects1, padding=3, fmt='%.2f', fontsize=9); ax4.bar_label(rects2, padding=3, fmt='%.2f', fontsize=9)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_SPM2, format='png', bbox_inches='tight', dpi=150); print(f"Graf 4 lagret: {PNG_FILENAME_SPM2}"); plot_counter += 1; plt.close(fig4)
    except Exception as e: print(f"FEIL under Graf 4 (Alder Spm 2): {e}"); plt.close(fig4)

    # --- 5. Lagre Graf 5: Alle ALDERSGRUPPER, Kun Spm 3 ---
    try:
        fig5, ax5 = plt.subplots(1, 1, figsize=(7, 6)); fig5.suptitle('Gj.sn. Behagelighet (Spm 3): Sammenligning Alder', fontsize=14, y=1.0)
        plot_data_age_spm3_reidx = plot_data_age_spm3.reindex(index=age_groups_found)
        rects3 = ax5.bar(index_groups_age - bar_width/2, plot_data_age_spm3_reidx['Spm3_Menneske'], bar_width, label='Menneskeskapt', color='skyblue'); rects4 = ax5.bar(index_groups_age + bar_width/2, plot_data_age_spm3_reidx['Spm3_KI'], bar_width, label='KI-generert', color='lightcoral')
        ax5.set_ylabel('Gjennomsnittlig score (1-10)'); ax5.set_title('Spm 3: Behagelighet'); ax5.set_xticks(index_groups_age); ax5.set_xticklabels(age_groups_found, rotation=0); ax5.set_ylim(0, 11); ax5.legend(title="Bildetype"); ax5.grid(axis='y', linestyle='--'); ax5.bar_label(rects3, padding=3, fmt='%.2f', fontsize=9); ax5.bar_label(rects4, padding=3, fmt='%.2f', fontsize=9)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_SPM3, format='png', bbox_inches='tight', dpi=150); print(f"Graf 5 lagret: {PNG_FILENAME_SPM3}"); plot_counter += 1; plt.close(fig5)
    except Exception as e: print(f"FEIL under Graf 5 (Alder Spm 3): {e}"); plt.close(fig5)

    # --- 6. Lagre Graf 6: Alle ALDERSGRUPPER, Andel "Rett Emosjon" (%) ---
    try:
        fig6, ax6 = plt.subplots(1, 1, figsize=(7, 6)); fig6.suptitle('Andel "Rett" Emosjon (Spm 1 vs Bildetema): Alder', fontsize=14, y=1.0)
        plot_data_age_emo_match_reidx = plot_data_age_emo_match.reindex(index=age_groups_found)
        correct_emo_m = plot_data_age_emo_match_reidx['CorrectEmotion_Menneske'] * 100; correct_emo_k = plot_data_age_emo_match_reidx['CorrectEmotion_KI'] * 100
        rects5 = ax6.bar(index_groups_age - bar_width/2, correct_emo_m, bar_width, label='Menneskeskapt', color='skyblue'); rects6 = ax6.bar(index_groups_age + bar_width/2, correct_emo_k, bar_width, label='KI-generert', color='lightcoral')
        ax6.set_ylabel('Prosentandel (%)'); ax6.set_title('Andel som opplevde "Rett" Emosjon (Spm 1)'); ax6.set_xticks(index_groups_age); ax6.set_xticklabels(age_groups_found, rotation=0); ax6.set_ylim(0, 105); ax6.legend(title="Bildetype"); ax6.grid(axis='y', linestyle='--'); ax6.bar_label(rects5, padding=3, fmt='%.0f%%', fontsize=9); ax6.bar_label(rects6, padding=3, fmt='%.0f%%', fontsize=9)
        fig6.text(0.5, -0.02, '*Merk: "Rett" emosjon er definert i kodens regler.', ha='center', va='top', fontsize=9, style='italic')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_EMO_MATCH_GRAPH, format='png', bbox_inches='tight', dpi=150); print(f"Graf 6 lagret: {PNG_FILENAME_EMO_MATCH_GRAPH}"); plot_counter += 1; plt.close(fig6)
    except Exception as e: print(f"FEIL under Graf 6 (Alder Rett Emosjon): {e}"); plt.close(fig6)

    # --- 7. Lagre Tabell: Rett Emosjon Status ---
    try:
        table_data = df_filtered[['AgeGroup', 'ParticipantID', 'ImageName', 'ImageType', 'Spm1', 'CorrectEmotion']].copy(); table_data['Status'] = table_data['CorrectEmotion'].apply(lambda x: '✓' if x==1 else '✗'); table_data.sort_values(by=['AgeGroup','ParticipantID','ImageType'], inplace=True)
        table_display_data = table_data[['AgeGroup', 'ParticipantID', 'ImageName', 'ImageType', 'Spm1', 'Status']]; col_labels = ['Aldersgr.', 'Deltaker', 'Bildetema', 'Bildetype', 'Opplevd (Spm1)', 'Rett?']
        row_height = 0.35; fig_height = max(5, len(table_display_data) * row_height + 1.5) # Mer høyde for tittel
        fig_table, ax_table = plt.subplots(figsize=(10, fig_height)); ax_table.axis('tight'); ax_table.axis('off')
        the_table = ax_table.table(cellText=table_display_data.values, colLabels=col_labels, loc='center', cellLoc='left'); the_table.auto_set_font_size(False); the_table.set_fontsize(8); the_table.scale(1.0, 1.1) # Litt større scale
        plt.title("Opplevde Emosjoner (Spm 1) og 'Rett Emosjon' Status", fontsize=14, y=0.98 if fig_height > 6 else 0.95) # Juster y for tittel
        plt.tight_layout(pad=0.5); plt.savefig(PNG_FILENAME_EMO_MATCH_TABLE, format='png', bbox_inches='tight', dpi=150); print(f"Tabell 7 lagret: {PNG_FILENAME_EMO_MATCH_TABLE}"); plot_counter += 1; plt.close(fig_table)
    except Exception as e: print(f"FEIL under Tabell 7: {e}"); plt.close(fig_table)

    # --- 8. Lagre Graf 8: Alle KJØNN, Kun Spm 2 ---
    if not average_scores_grouped_gender.empty:
        print("\nDEBUG: Starter plotting av Graf 8 (Kjønn Spm 2)...")
        try:
            fig8, ax8 = plt.subplots(1, 1, figsize=(7, 6)); fig8.suptitle('Gj.sn. Respons/Intensitet (Spm 2): Kjønnssammenligning', fontsize=14, y=1.0)
            plot_data_gender_spm2_reidx = plot_data_gender_spm2.reindex(index=genders_found_list)
            rects_g1 = ax8.bar(index_genders - bar_width/2, plot_data_gender_spm2_reidx['Spm2_Menneske'], bar_width, label='Menneskeskapt', color='skyblue'); rects_g2 = ax8.bar(index_genders + bar_width/2, plot_data_gender_spm2_reidx['Spm2_KI'], bar_width, label='KI-generert', color='lightcoral')
            ax8.set_ylabel('Gjennomsnittlig score (1-10)'); ax8.set_title('Spm 2: Respons/Emosjon Intensitet'); ax8.set_xticks(index_genders); ax8.set_xticklabels(genders_found_list, rotation=0); ax8.set_ylim(0, 11); ax8.legend(title="Bildetype"); ax8.grid(axis='y', linestyle='--'); ax8.bar_label(rects_g1, padding=3, fmt='%.2f', fontsize=9); ax8.bar_label(rects_g2, padding=3, fmt='%.2f', fontsize=9)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_KJONN_SPM2, format='png', bbox_inches='tight', dpi=150); print(f"Graf 8 lagret: {PNG_FILENAME_KJONN_SPM2}"); plot_counter += 1; plt.close(fig8)
        except Exception as e: print(f"FEIL under Graf 8 (Kjønn Spm 2): {e}"); plt.close(fig8)
    else: print("\nIngen data for kjønnssammenligning (Graf 8).")

    # --- 9. Lagre Graf 9: Alle KJØNN, Kun Spm 3 ---
    if not average_scores_grouped_gender.empty:
        print("\nDEBUG: Starter plotting av Graf 9 (Kjønn Spm 3)...")
        try:
            fig9, ax9 = plt.subplots(1, 1, figsize=(7, 6)); fig9.suptitle('Gj.sn. Behagelighet (Spm 3): Kjønnssammenligning', fontsize=14, y=1.0)
            plot_data_gender_spm3_reidx = plot_data_gender_spm3.reindex(index=genders_found_list)
            rects_g3 = ax9.bar(index_genders - bar_width/2, plot_data_gender_spm3_reidx['Spm3_Menneske'], bar_width, label='Menneskeskapt', color='skyblue'); rects_g4 = ax9.bar(index_genders + bar_width/2, plot_data_gender_spm3_reidx['Spm3_KI'], bar_width, label='KI-generert', color='lightcoral')
            ax9.set_ylabel('Gjennomsnittlig score (1-10)'); ax9.set_title('Spm 3: Behagelighet'); ax9.set_xticks(index_genders); ax9.set_xticklabels(genders_found_list, rotation=0); ax9.set_ylim(0, 11); ax9.legend(title="Bildetype"); ax9.grid(axis='y', linestyle='--'); ax9.bar_label(rects_g3, padding=3, fmt='%.2f', fontsize=9); ax9.bar_label(rects_g4, padding=3, fmt='%.2f', fontsize=9)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_KJONN_SPM3, format='png', bbox_inches='tight', dpi=150); print(f"Graf 9 lagret: {PNG_FILENAME_KJONN_SPM3}"); plot_counter += 1; plt.close(fig9)
        except Exception as e: print(f"FEIL under Graf 9 (Kjønn Spm 3): {e}"); plt.close(fig9)
    else: print("\nIngen data for kjønnssammenligning (Graf 9).")

    # --- 10. Lagre Graf 10: Alle KJØNN, Andel "Rett Emosjon" (%) ---
    if not average_scores_grouped_gender.empty:
        print("\nDEBUG: Starter plotting av Graf 10 (Kjønn Rett Emosjon)...")
        try:
            fig10, ax10 = plt.subplots(1, 1, figsize=(7, 6)); fig10.suptitle('Andel "Rett" Emosjon: Kjønnssammenligning', fontsize=14, y=1.0)
            plot_data_gender_emo_reidx = plot_data_gender_emo_match.reindex(index=genders_found_list)
            correct_emo_m = plot_data_gender_emo_reidx['CorrectEmotion_Menneske'] * 100; correct_emo_k = plot_data_gender_emo_reidx['CorrectEmotion_KI'] * 100
            rects_g5 = ax10.bar(index_genders - bar_width/2, correct_emo_m, bar_width, label='Menneskeskapt', color='skyblue'); rects_g6 = ax10.bar(index_genders + bar_width/2, correct_emo_k, bar_width, label='KI-generert', color='lightcoral')
            ax10.set_ylabel('Prosentandel (%)'); ax10.set_title('Andel som opplevde "Rett" Emosjon (Spm 1)'); ax10.set_xticks(index_genders); ax10.set_xticklabels(genders_found_list, rotation=0); ax10.set_ylim(0, 105); ax10.legend(title="Bildetype"); ax10.grid(axis='y', linestyle='--'); ax10.bar_label(rects_g5, padding=3, fmt='%.0f%%', fontsize=9); ax10.bar_label(rects_g6, padding=3, fmt='%.0f%%', fontsize=9)
            fig10.text(0.5, -0.02, '*Merk: "Rett" emosjon er definert i kodens regler.', ha='center', va='top', fontsize=9, style='italic')
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(PNG_FILENAME_KJONN_EMO_MATCH, format='png', bbox_inches='tight', dpi=150); print(f"Graf 10 lagret: {PNG_FILENAME_KJONN_EMO_MATCH}"); plot_counter += 1; plt.close(fig10)
        except Exception as e: print(f"FEIL under Graf 10 (Kjønn Rett Emosjon): {e}"); plt.close(fig10)
    else: print("\nIngen data for kjønnssammenligning (Graf 10).")

    # --- 11. Lagre Tabell 11: Rådata ---
    print("\nDEBUG: Starter plotting av Tabell 11 (Rådata)...")
    if not df_filtered.empty:
        try:
            table_data_raw = df_filtered[['AgeGroup','ParticipantID','Gender','ImageName','ImageType','Spm1','Spm2','Spm3','CorrectEmotion']].copy()
            table_data_raw['Status'] = table_data_raw['CorrectEmotion'].apply(lambda x: '✓' if x==1 else '✗')
            table_display_raw = table_data_raw[['AgeGroup','ParticipantID','Gender','ImageName','ImageType','Spm1','Spm2','Spm3','Status']]
            col_labels_raw = ['Aldersgr.','Deltaker','Kjønn','Bildetema','Bildetype','Opplevd (Spm1)','Spm2','Spm3','Rett?']
            row_height_raw = 0.3; fig_height_raw = max(6, len(table_display_raw) * row_height_raw + 1.5)
            fig_raw, ax_raw = plt.subplots(figsize=(12, fig_height_raw))
            ax_raw.axis('tight'); ax_raw.axis('off')
            the_raw_table = ax_raw.table(cellText=table_display_raw.values, colLabels=col_labels_raw, loc='center', cellLoc='left')
            the_raw_table.auto_set_font_size(False); the_raw_table.set_fontsize(8); the_raw_table.scale(1.0, 1.0)
            plt.title("Innsamlet Rådata (Del 1)", fontsize=16, y=0.98)
            plt.tight_layout(pad=0.5); plt.savefig(PNG_FILENAME_RAADATA_TABLE, format='png', bbox_inches='tight', dpi=150); print(f"Tabell 11 lagret: {PNG_FILENAME_RAADATA_TABLE}"); plot_counter += 1; plt.close(fig_raw)
        except Exception as e: print(f"FEIL under Tabell 11 (Rådata): {e}"); plt.close(fig_raw)
    else: print("\nKunne ikke lage rådata-tabell, df_filtered var tom.")

    # --- Oppsummering lagring ---
    if plot_counter == 0: print("\nIngen filer ble lagret pga. feil.")
    elif plot_counter < 11: print(f"\nADVARSEL: Kun {plot_counter} av 11 filer ble lagret pga. feil eller manglende data.")
    else: print("\nAlle 11 PNG-filer ble lagret.")

else: print("\nKunne ikke generere noen filer, ingen gyldig data funnet eller beregnet fra filen.")

# --- Utskrift av definisjon "Rett Emosjon" ---
print("\n--- Definisjon av 'Rett Emosjon' brukt ---"); print("Regler brukt (ignorerer store/små bokstaver):")
for theme, allowed_list in correct_emotion_map.items(): print(f"  '{theme.capitalize()}': {allowed_list}")

# --- Utskrift av Spm1 status ---
print("\nFølgende emosjoner ble oppgitt og status for 'rett' (✓ = Rett, ✗ = Ikke rett):")
if not df.empty:
    all_spm1_data_out = df[df['ImageType'].isin(['Menneske', 'KI'])][['AgeGroup','ParticipantID','Gender','ImageType','ImageName','Spm1', 'CorrectEmotion']].copy()
    all_spm1_data_out['Status'] = all_spm1_data_out['CorrectEmotion'].apply(lambda x: '✓' if x==1 else '✗')
    all_spm1_data_out.sort_values(by=['AgeGroup','ParticipantID','ImageType'], inplace=True)
    for idx, row in all_spm1_data_out.iterrows(): print(f"- {row['AgeGroup']}, {row['ParticipantID']} ({row['Gender']}), {row['ImageType']} ({row['ImageName']}): '{row['Spm1']}' ({row['Status']})")
else: print("- Ingen gyldige data å vise.")

# --- Instruksjoner ---
print("\n--- Instruksjoner for å legge til data ---"); print(f"1. Data leses fra '{FILENAME}'."); print(f"2. Hvis filen ble nyopprettet, inneholder den data for 8+8 målinger."); print(f"3. Åpne '{FILENAME}' og legg til nye rader nederst."); print("4. Kolonnene: AgeGroup,ParticipantID,ImageType,ImageName,Spm1,Spm2,Spm3"); print("5. Lagre CSV."); print(f"6. Kjør scriptet på nytt for 11 oppdaterte PNG-filer.")