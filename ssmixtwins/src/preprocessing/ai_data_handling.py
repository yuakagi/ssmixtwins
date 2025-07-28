import os
import glob
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd
import numpy as np
from ..config import BASE_TIMESTAMP_FORMAT
from ..utils import to_datetime_anything

MAX_FILES_PER_DIR = 100
INJEC_THRESHOLD = 15  # Threshold for determining injection vs prescription
# Keywords to detect prescription drug prodcut names
PRESC_KEYWORDS = [
    "錠",
    "カプセル",
    "cap",
    "Cap",
    "原末",
    "粉末",
    "顆粒",
    "散",
    "シロップ",
    "膏",
    "クリーム",
    "貼付",
    "パッチ",
    "坐剤",
    "坐薬",
    "吸入",
    "うがい液",
    "点眼",
    "点耳",
    "点鼻",
    "噴霧",
    "ゼリー",
    "皮下",
    "テープ",
    "ワセリン",
    "内服",
    "内用",
]


def clean_drug_names(drug_names: pd.Series) -> pd.Series:
    """Crop drug names.

    This cleans drug product names like the example shown below:
        'テスト薬剤 100mg (メーカー名)' -> 'テスト薬剤'

    Args:
        drug_names (pd.Series): Series of drug names
    Returns:
        cropped (pd.Series): Cleaned drug names.
    """
    # Fill nan with empty strings for string operations
    cropped = drug_names.fillna("")
    # Remove white spaces from product names
    cropped = cropped.str.replace(r"\s+", "", regex=True)
    # Remove other unnecessary characters
    cropped = cropped.str.replace(
        r"(※|・|×|\*|＊|,|\"|＂|”|“||\'|＇|’|‘|′|-|−)", "", regex=True
    )
    # Remove bracketed parts (e.g, '(麻)', '「メーカー」 etc.) from product names
    cropped = cropped.str.replace(
        r"\[.*?\]|\(.*?\)|\{.*?\}|<.*?>|（.*?）|【.*?】|〈.*?〉|〔.*?〕|「.*?」|『.*?』",
        "",
        regex=True,
    )
    # Remove common units from product names
    cropped = cropped.str.replace(
        r"((\d+\.\d+|\d+)(\%|((m|μ|n|p)?g|(m|μ|)?(l|L)|(c|m)(m|M))|Eq|mEq|[一二三四五六七八九十百千万]*(((国際|国内)(標準)?)?単位|(I)?U)))|(/((\d+\.\d+|\d+))?((m|μ|n|p)?g|(m|μ|)?(l|L)|(c|m)(m|M)|包))|((\d+\.\d+|\d+))/((\d+\.\d+|\d+))",
        "",
        regex=True,
    )
    # Remove unnecessary trail characters
    cropped = cropped.str.replace(
        r"(\d+\.\d*|\d+|([一二三四五六七八九十百千万]+))$", "", regex=True
    )

    return cropped


def extract_numeric_from_text(col: pd.Series) -> pd.Series:
    """Extracts leading numeric values from text.

    Originally designed for lab test results such as:
        "145.2 mEq/L" -> 145.2

    Returns a Series of floats. Non-numeric rows become NaN.
    """
    num_regex = r"^([+-]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
    extracted = col.str.extract(num_regex, expand=False)
    extracted = pd.to_numeric(extracted, errors="coerce")
    non_numeric_mask = extracted.isna()
    extracted = extracted.astype(str)
    extracted[non_numeric_mask] = ""  # Replace non-numeric with empty string

    return extracted


def map_codes(df: pd.DataFrame, src_col: str, dst_col: str, map: str) -> pd.DataFrame:
    """
    Maps codes in a DataFrame from one column to another using a mapping file.
    Args:
        df (pd.DataFrame): The DataFrame containing the source column to be mapped.
        src_col (str): The name of the source column in `df` that contains the codes to be mapped.
        dst_col (str): The name of the destination column in `df` where the mapped codes will be stored.
        map (str): Path to the mapping file, which should contain three columns:
            `src_col`, `dst_col` and 'text'.
            'text' is optional, but if present, it will be used to fill the `text` column in `df`.
    Returns:
        pd.DataFrame: The original DataFrame with an additional column `dst_col` containing the mapped codes.
    """
    # Clean map
    if ("text" in map.columns) and (dst_col != "text"):
        clean_map = map[[src_col, dst_col, "text"]].copy()
    else:
        clean_map = map[[src_col, dst_col]].copy()
    clean_map = clean_map.sample(frac=1, replace=False).reset_index(
        drop=True
    )  # Shuffle the map
    clean_map = clean_map.drop_duplicates(subset=src_col).reset_index(
        drop=True
    )  # Ensure on-to-one
    # Add 'dst_col' ± 'text' col by merge
    indexes = df.index.copy()
    df = df.merge(clean_map, how="left", left_on=src_col, right_on=src_col, sort=False)
    df.index = indexes  # Restore original index

    # Fill NaN values in the destination column with empty strings
    df[dst_col] = df[dst_col].fillna("")
    if "text" in df:
        df["text"] = df["text"].fillna("")  # Fill 'text' if exists
    return df


def _clean_dx(df: pd.DataFrame, dx_type: int, icd10_to_mdcdx2_map: pd.DataFrame):
    # Map ICD10 -> MDCDX2 and texts
    dx_mask = df["type"] == dx_type
    dx_table = df.loc[dx_mask].copy()
    # Add columns for ICD10, MDCDX2, text, and provisional
    df["icd10"] = ""
    df["mdcdx2"] = ""
    df["provisional"] = ""
    # Process
    if not dx_table.empty:
        # Provisional
        prov_mask = dx_table["code"].str.contains("(prov.)", regex=False)
        dx_table["code"] = dx_table["code"].str.replace("(prov.)", "").str.strip()
        dx_table["provisional"] = ""
        dx_table.loc[prov_mask, "provisional"] = "1"
        # Text and code mapping
        dx_table = dx_table.drop(
            columns=["text"], errors="ignore"
        )  # Remove 'text' if exists, because it will be replaced
        dx_table = dx_table.rename(
            columns={"code": "icd10"}
        )  # Rename 'code' to 'icd10'
        dx_table = map_codes(dx_table, "icd10", "mdcdx2", icd10_to_mdcdx2_map)
        # Fill nan with empty strings
        dx_table["icd10"] = dx_table["icd10"].fillna("")
        dx_table["mdcdx2"] = dx_table["mdcdx2"].fillna("")
        dx_table["text"] = dx_table["text"].fillna("")
        # Assign
        df.loc[dx_mask, "icd10"] = dx_table["icd10"].copy()  # Add ICD10
        df.loc[dx_mask, "mdcdx2"] = dx_table["mdcdx2"].copy()  # Add MDCDX2
        df.loc[dx_mask, "text"] = dx_table["text"].copy()  # Add text for MDCDX2
        df.loc[dx_mask, "provisional"] = dx_table[
            "provisional"
        ].copy()  # Add provisional

    return df


def _clean_drug_orders(
    df: pd.DataFrame,
    med_type: int,  # 4
    presc_type: int,  # 4
    injec_type: int,  # 5
    atc_to_yj_map: pd.DataFrame,  # Should have columns ['atc', 'yj']
    yj_to_hot_map: pd.DataFrame,  # Should have columns ['yj', 'hot', 'text']
    atc_to_hot_map: pd.DataFrame = None,  # Should have columns ['atc', 'hot', 'text']
) -> pd.DataFrame:
    # Map ATC
    med_mask = df["type"] == med_type
    med_table = df.loc[med_mask].copy()
    # Add columns for ATC, YJ, HOT
    df["atc"] = ""
    df["yj"] = ""
    df["hot"] = ""

    # Process
    if not med_table.empty:
        # Drop text colmun first (This is texts for ATC, therefore, dropping it is safe)
        med_table = med_table.drop(
            columns=["text"], errors="ignore"
        )  # Remove 'text' if exists
        # Set patterns
        presc_keywords_pattern = "|".join(PRESC_KEYWORDS)
        # Create maps for prescription and injection orders separately
        atc_yj_presc_mask = atc_to_yj_map["text"].str.contains(
            presc_keywords_pattern, regex=True
        )
        atc_yj_injec_mask = ~atc_yj_presc_mask
        atc_yj_presc_map = atc_to_yj_map[atc_yj_presc_mask].copy()
        atc_yj_injec_map = atc_to_yj_map[atc_yj_injec_mask].copy()
        atc_yj_presc_map = atc_yj_presc_map.rename(columns={"yj": "yj_presc"})
        atc_yj_injec_map = atc_yj_injec_map.rename(columns={"yj": "yj_injec"})
        yj_hot_presc_mask = yj_to_hot_map["text"].str.contains(
            presc_keywords_pattern, regex=True
        )
        yj_hot_injec_mask = ~yj_hot_presc_mask
        yj_hot_presc_map = yj_to_hot_map[yj_hot_presc_mask].copy()
        yj_hot_injec_map = yj_to_hot_map[yj_hot_injec_mask].copy()
        yj_hot_presc_map = yj_hot_presc_map.rename(
            columns={"yj": "yj_presc", "hot": "hot_presc"}
        )
        yj_hot_injec_map = yj_hot_injec_map.rename(
            columns={"yj": "yj_injec", "hot": "hot_injec"}
        )
        atc_hot_prsc_mask = atc_to_hot_map["text"].str.contains(
            presc_keywords_pattern, regex=True
        )
        atc_hot_injec_mask = ~atc_hot_prsc_mask
        atc_hot_presc_map = atc_to_hot_map[atc_hot_prsc_mask].copy()
        atc_hot_injec_map = atc_to_hot_map[atc_hot_injec_mask].copy()
        atc_hot_presc_map = atc_hot_presc_map.rename(columns={"hot": "hot_presc_sub"})
        atc_hot_injec_map = atc_hot_injec_map.rename(columns={"hot": "hot_injec_sub"})
        atc_to_hot_map = atc_to_hot_map.rename(columns={"hot": "hot_sub"})

        # Map ATC -> YJ and texts
        # NOTE: This is redundant, but we need possible naming candidates both for prescriptions and injections.
        #      This is not perfect. This can still include some injection prodocts in the prescription orders, and vice versa.
        med_table = med_table.rename(columns={"code": "atc"})  # Rename 'code' to 'atc'
        med_table = map_codes(med_table, "atc", "yj_presc", atc_yj_presc_map)
        med_table = med_table.rename(columns={"text": "text_from_yj_presc"})
        med_table = map_codes(med_table, "atc", "yj_injec", atc_yj_injec_map)
        med_table = med_table.rename(columns={"text": "text_from_yj_injec"})
        med_table = map_codes(med_table, "atc", "yj", atc_to_yj_map)
        med_table = med_table.rename(
            columns={"text": "text_from_yj_random"}
        )  # 'yj' stays here

        # Map YJ -> Hot
        med_table = map_codes(med_table, "yj_presc", "hot_presc", yj_hot_presc_map)
        med_table = med_table.rename(columns={"text": "text_from_hot_presc"})
        med_table = map_codes(med_table, "yj_injec", "hot_injec", yj_hot_injec_map)
        med_table = med_table.rename(columns={"text": "text_from_hot_injec"})
        med_table = map_codes(med_table, "yj", "hot", yj_to_hot_map)
        med_table = med_table.rename(
            columns={"text": "text_from_hot_random"}
        )  # 'hot' stays here
        # MAP ATC -> Hot to fill missing HOT after mapping YJ
        # NOTE: In this step, 'text' and 'hot' columns are dropped after filing missing values.
        med_table = map_codes(med_table, "atc", "hot_presc_sub", atc_hot_presc_map)
        med_table["text_from_hot_presc"] = med_table["text_from_hot_presc"].mask(
            med_table["text_from_hot_presc"] == "", med_table["text"]
        )
        med_table["hot_presc"] = med_table["hot_presc"].mask(
            med_table["hot_presc"] == "", med_table["hot_presc_sub"]
        )
        med_table = med_table.drop(["text", "hot_presc_sub"], axis=1)
        med_table = map_codes(med_table, "atc", "hot_injec_sub", atc_hot_injec_map)
        med_table["text_from_hot_injec"] = med_table["text_from_hot_injec"].mask(
            med_table["text_from_hot_injec"] == "", med_table["text"]
        )
        med_table["hot_injec"] = med_table["hot_injec"].mask(
            med_table["hot_injec"] == "", med_table["hot_injec_sub"]
        )
        med_table = med_table.drop(["text", "hot_injec_sub"], axis=1)
        med_table = map_codes(med_table, "atc", "hot_sub", atc_to_hot_map)
        med_table["text_from_hot_random"] = med_table["text_from_hot_random"].mask(
            med_table["text_from_hot_random"] == "", med_table["text"]
        )
        med_table["hot"] = med_table["hot"].mask(
            med_table["hot"] == "", med_table["hot_sub"]
        )
        med_table = med_table.drop(["text", "hot_sub"], axis=1)
        # Fill missings
        med_table["yj_presc"] = med_table["yj_presc"].mask(
            med_table["yj_presc"] == "", med_table["yj"]
        )
        med_table["yj_injec"] = med_table["yj_injec"].mask(
            med_table["yj_injec"] == "", med_table["yj"]
        )
        med_table["hot_presc"] = med_table["hot_presc"].mask(
            med_table["hot_presc"] == "", med_table["hot"]
        )
        med_table["hot_injec"] = med_table["hot_injec"].mask(
            med_table["hot_injec"] == "", med_table["hot"]
        )
        med_table = med_table.rename(
            columns={"yj": "yj_random", "hot": "hot_random"}
        )  # Rename 'yj' and 'hot' to 'yj_random' and 'hot_random'

        # Text
        # NOTE: Because map_codes() fills nan with empty strings, you should not use fillna() here.
        med_table["text_presc"] = med_table["text_from_yj_presc"].mask(
            med_table["text_from_yj_presc"] == "", med_table["text_from_hot_presc"]
        )
        med_table["text_injec"] = med_table["text_from_yj_injec"].mask(
            med_table["text_from_yj_injec"] == "", med_table["text_from_hot_injec"]
        )
        med_table["text_random"] = med_table["text_from_yj_random"].mask(
            med_table["text_from_yj_random"] == "", med_table["text_from_hot_random"]
        )
        # Borrwow text from injection to prescription and vice versa, if empty
        # But, to avoid placing confusing product names (like, "注射薬" in prescriptions),
        # we clean the drug names first.
        med_table["text_presc"] = med_table["text_presc"].mask(
            med_table["text_presc"] == "", clean_drug_names(med_table["text_injec"])
        )
        med_table["text_injec"] = med_table["text_injec"].mask(
            med_table["text_injec"] == "", clean_drug_names(med_table["text_presc"])
        )

        # --- Speparate prescriptions and injections ---
        # Set flags for prescriptions vs injections
        med_table["is_injection"] = False
        # Iterate through groups of the same timestamp
        for _, group in med_table.groupby("timestamp"):
            # No1. If many ordersare made, it is usually injections.
            if len(group) >= INJEC_THRESHOLD:
                med_table.loc[group.index, "is_injection"] = True
            # No2. If ATC begins with 'B', it is usually injections.
            elif group["atc"].str.startswith("B").any():
                med_table.loc[group.index, "is_injection"] = True
            # No3. Poll by randomly mapped drug names
            n_votes_for_presc = (
                group["text_random"]
                .str.contains(presc_keywords_pattern, regex=True)
                .sum()
            )
            if n_votes_for_presc < len(group) / 2:
                med_table.loc[group.index, "is_injection"] = True

        # Set type
        med_table.loc[med_table["is_injection"], "type"] = injec_type
        med_table.loc[~med_table["is_injection"], "type"] = presc_type
        # Set texts
        med_table["text"] = ""
        med_table.loc[med_table["is_injection"], "text"] = med_table["text_injec"]
        med_table.loc[~med_table["is_injection"], "text"] = med_table["text_presc"]
        # Set HOT, YJ
        med_table["hot"] = ""
        med_table.loc[med_table["is_injection"], "hot"] = med_table["hot_injec"]
        med_table.loc[~med_table["is_injection"], "hot"] = med_table["hot_presc"]
        med_table["yj"] = ""
        med_table.loc[med_table["is_injection"], "yj"] = med_table["yj_injec"]
        med_table.loc[~med_table["is_injection"], "yj"] = med_table["yj_presc"]
        # -----------------------------------------------

        # Replace nan with empty strings
        med_table["yj"] = med_table["yj"].fillna("")
        med_table["hot"] = med_table["hot"].fillna("")
        med_table["atc"] = med_table["atc"].fillna("")
        med_table["text"] = med_table["text"].fillna("")
        # Assign
        df.loc[med_mask, "atc"] = df.loc[med_mask, "code"].copy()
        df.loc[med_mask, "yj"] = med_table["yj"].copy()
        df.loc[med_mask, "hot"] = med_table["hot"].copy()
        df.loc[med_mask, "text"] = med_table["text"].copy()
        df.loc[med_mask, "type"] = med_table["type"].copy()  # Update type

    return df


def _clean_lab(df: pd.DataFrame, lab_type: int, jlac10_segment_map: pd.DataFrame):

    # Clean lab
    lab_mask = df["type"] == lab_type
    lab_table = df.loc[lab_mask].copy()
    # Add columns for lab value, unit, and JLAC10
    df["lab_value"] = ""
    df["unit"] = ""
    df["jlac10"] = ""
    if not lab_table.empty:
        # Extract numeric values
        lab_table["numeric"] = extract_numeric_from_text(lab_table["result"])
        num_mask = lab_table["numeric"] != ""  # Mask for numeric results
        # Non-numerics
        lab_table["nonnumeric"] = lab_table["result"].values
        lab_table.loc[num_mask, "nonnumeric"] = (
            ""  # Remove numerics from non-numeric results
        )
        # Lab value
        lab_table["lab_value"] = lab_table["numeric"]
        lab_table.loc[~num_mask, "lab_value"] = lab_table.loc[
            ~num_mask, "nonnumeric"
        ].values
        # Unit
        lab_table["unit"] = ""
        lab_table.loc[num_mask, "unit"] = (
            lab_table.loc[num_mask, "result"].str.split(" ", expand=True).get(1, "")
        )
        lab_table.loc[lab_table["unit"] == "no_unit", "unit"] = (
            ""  # Remove 'no_unit' from unit
        )

        # Segment code
        lab_table["analyte"] = (
            lab_table["code"].str.slice(0, 5) + "*" * 12
        )  # Extract analyte code
        lab_table["identification"] = (
            "*" * 5 + lab_table["code"].str.slice(5, 9) + "*" * 8
        )  # Extract identification code
        lab_table["specimen"] = (
            "*" * 9 + lab_table["code"].str.slice(9, 12) + "*" * 5
        )  # Extract specimen code
        lab_table["method"] = (
            "*" * 12 + lab_table["code"].str.slice(12, 15) + "*" * 2
        )  # Extract method code (分析物固有結果識別)
        lab_table["result_idenfitication"] = "*" * 15 + lab_table["code"].str.slice(
            15, 17
        )  # Extract result identification code
        lab_table["unique_result_identification"] = (
            lab_table["code"].str.slice(0, 9)
            + "*" * 6
            + lab_table["code"].str.slice(15, 17)
        )
        # Map segments to text
        lab_table = lab_table.drop(
            "text", axis=1, errors="ignore"
        )  # Remove 'text' if exists
        for col in [
            "analyte",
            "identification",
            "specimen",
            "method",
            "result_idenfitication",
            "unique_result_identification",
        ]:

            lab_table = lab_table.rename(columns={col: "segment"})
            lab_table = map_codes(lab_table, "segment", "text", jlac10_segment_map)
            lab_table = lab_table.rename(columns={"text": col + "_text"})
            lab_table = lab_table.drop(columns=["segment"])  # Drop the segment column
        # Override result identification
        has_unique_result = lab_table["unique_result_identification_text"] != ""
        lab_table.loc[has_unique_result, "result_idenfitication_text"] = lab_table.loc[
            has_unique_result, "unique_result_identification_text"
        ]
        # Combine texts
        lab_table["text"] = (
            lab_table["specimen_text"]
            + lab_table["analyte_text"]
            + lab_table["identification_text"]
            + lab_table["result_idenfitication_text"]
            # Currently, method is not used in the text
        )  # Combine texts from segments
        # Fill nan with empty strings
        lab_table["text"] = lab_table["text"].fillna("")
        lab_table["unit"] = lab_table["unit"].fillna("")
        lab_table["lab_value"] = lab_table["lab_value"].fillna("")
        lab_table["code"] = lab_table["code"].fillna("")  # Fill code
        # Assign
        df.loc[lab_mask, "lab_value"] = lab_table["lab_value"].values  # Lab values
        df.loc[lab_mask, "unit"] = lab_table[
            "unit"
        ].values  # Units are for numeric only
        df.loc[lab_mask, "jlac10"] = lab_table["code"].values  # Add JLAC10
        df.loc[lab_mask, "text"] = lab_table[
            "text"
        ].values  # Add Japanese texts for JLAC10

    return df


def clean_base_table(
    file: str,
    output_dir: str,
    start_date: str,  # YYYYMMDD
    icd10_to_mdcdx2_map: pd.DataFrame,  # Should have columns ['icd10', 'mdcdx2', 'text']
    atc_to_yj_map: pd.DataFrame,  # Should have columns ['atc', 'yj'],
    atc_to_hot_map: pd.DataFrame,  # Should have columns ['atc', 'hot', 'text']
    yj_to_hot_map: pd.DataFrame,  # Should have columns ['yj', 'hot', 'text']
    jlac10_segment_map: pd.DataFrame,  # Should have columns ['jlac10', 'text']
    end_date: str=None,  # YYYYMMDD
    presc_type: int = 4,  # 4 is for prescriptions
    injec_type: int = 5,  # 5 is for injections
    # NOTE: Type below is the type numbers used in the AI-generated data.
    #      These are replaced with the actual types in the final DataFrame.
    dmg_type: int = 0,
    adm_type: int = 1,
    dsc_type: int = 2,
    dx_type: int = 3,
    med_type: int = 4,  # 4 is both for prescriptions and injections in the original form
    lab_type: int = 6,
    eot_type: int = 7,  # End of trajectory (EOT) type, currently unused
) -> tuple[pd.DataFrame, str, str]:
    # Load
    df = pd.read_pickle(file)  # Load the base DataFrame
    # Normalize texts
    icd10_to_mdcdx2_map["text"] = (
        icd10_to_mdcdx2_map["text"].str.strip().str.normalize("NFKC")
    )
    yj_to_hot_map["text"] = yj_to_hot_map["text"].str.strip().str.normalize("NFKC")
    jlac10_segment_map["text"] = (
        jlac10_segment_map["text"].str.strip().str.normalize("NFKC")
    )
    # Normalize DataFrame
    # Ensure sortng
    df = df.sort_values(by=["age", "type"], ascending=[True, True]).reset_index(
        drop=True
    )
    # Clean dates
    df["age"] = pd.to_timedelta(df["age"], errors="coerce")
    start_age = df["age"].min().floor("D")  # Get the oldest age in days
    dob = to_datetime_anything(start_date) - start_age  # Simulated DOB
    df["timestamp"] = df["age"] + dob  # Calculate timestamp from age and DOB

    # == Check rows with irregular rows ===
    irregular_mask = ~df["type"].isin(
        [dmg_type, eot_type, adm_type, dsc_type, dx_type, med_type, lab_type]
    )  # Irregular rows are demographics and EOT
    if irregular_mask.any():
        print(f"Warning: Some irregular rows are found in {file}. Aborting.")
        # NOTE: If irregular rows are found, we do not process the file.
        return
    # ======================

    # == Demographics ===
    # After collecting demographic data, demographic rows are dropped.
    dmg_mask = df["type"] == dmg_type  # Set type to demographics
    dmg_df = df.loc[dmg_mask].copy()
    # Determine sex
    if "[F]" in dmg_df["code"].values:
        sex = "F"
    elif "[M]" in dmg_df["code"].values:
        sex = "M"
    else:
        sex = "O"  # Other if neither F nor M is present
    del dmg_df
    # Delete demographics records from the main DataFrame
    # NOTE: Sex is included in the file name, so we do not need to store it in the DataFrame.
    df = df[~dmg_mask].reset_index(drop=True)  # Remove demographics records
    # ======================

    # === Drop EOT ===
    eot_mask = df["type"] == eot_type
    if eot_mask.any():
        df = df[~eot_mask].reset_index(drop=True)  # Remove EOT records if any
    # ======================

    # === Clean diagnoses ===
    # Map ICD10 -> MDCDX2 and texts
    df = _clean_dx(
        df=df,
        dx_type=dx_type,
        icd10_to_mdcdx2_map=icd10_to_mdcdx2_map,
    )
    # ========================

    # === Clean prescriptions and injections ===
    # NOTE: This step is complex. You separate prescriptions and injections in this step.
    df = _clean_drug_orders(
        df,
        med_type=med_type,
        presc_type=presc_type,
        injec_type=injec_type,
        atc_to_yj_map=atc_to_yj_map,
        atc_to_hot_map=atc_to_hot_map,
        yj_to_hot_map=yj_to_hot_map,
    )
    # ========================

    # === Clean lab ===
    df = _clean_lab(df=df, lab_type=lab_type, jlac10_segment_map=jlac10_segment_map)
    # Check missing lab values
    if (df.loc[df["type"] == lab_type, "lab_value"] == "").any():
        print(f"Warning: Some lab values are missing in {file}. Aborting.")
        return
    # ========================

    # === Clean discharge ===
    df["discharge_disposition"] = ""
    df.loc[df["result"] == "[DSC_ALV]", "discharge_disposition"] = (
        "01"  # Set '01' for all survivors
    )
    df.loc[df["result"] == "[DSC_EXP]", "discharge_disposition"] = (
        "20"  # Set '20' for all expired
    )
    # Check missing or irregular discharge dispositions
    valid_discharge_codes = ["01", "20"]
    valid_discharges = df.loc[df["type"] == dsc_type, "discharge_disposition"].isin(
        valid_discharge_codes
    )
    if (~valid_discharges).any():
        print(
            f"Warning: Some discharge dispositions are missing or irregular in {file}. Aborting."
        )
        return
    # =========================

    # === Finalize the DataFrame ===
    # Convert timestamp to string
    # Converting all timestamps to the same format
    df["timestamp"] = df["timestamp"].dt.strftime(BASE_TIMESTAMP_FORMAT)
    # Type mapping
    # NOTE: For easy understanding, change types using continuous integers
    type_mapping = {
        adm_type: 0,  # Admission
        dsc_type: 1,  # Discharge
        dx_type: 2,  # Diagnosis
        presc_type: 3,  # Prescription
        injec_type: 4,  # Injection
        lab_type: 5,  # Lab test
    }
    df["type"] = df["type"].map(type_mapping)
    if df["type"].isna().any():
        print(f"Warning: Some types are not mapped in {file}. They will be dropped.")
        raise ValueError(
            f"Some types are not mapped in {file}. Please check the type mapping."
        )
    df["type"] = df["type"].astype(int)
    df = df[
        [
            "timestamp",  # str
            "type",  # int
            "text",  # str
            "icd10",  # str
            "mdcdx2",  # str
            "provisional",  # str
            "hot",  # str
            "jlac10",  # str
            "lab_value",  # str
            "unit",  # str
            "discharge_disposition",  # str
            # NOTE: 'yj' is created, but currently not used in the final DataFrame.
            # NOTE: 'atc' is created, but currently not used in the final DataFrame.
        ]
    ]

    # ⏱ Truncate all future data
    if end_date is not None:
        end_datetime = to_datetime_anything(end_date)
        end_datetime += pd.Timedelta(days=1)  # Include the end date
        df = df[df["timestamp"] < end_datetime].reset_index(drop=True)

    # Save file (File name: {start_age}_{sex}.csv)
    if len(df) == 0:
        print(
            f"Warning: The DataFrame is empty after cleaning. No file will be saved for {file}."
        )
        return

    else:
        # File name pattern
        start_age_str = str(int(start_age.days / 365.25))  # Convert start age to string
        uuid_hex = (
            uuid.uuid4().hex
        )  # Generate a random hex string to avoid file name collision
        file_name = (
            "<start_age>_<sex>_<hex>.csv".replace("<start_age>", start_age_str)
            .replace("<sex>", sex)
            .replace("<hex>", uuid_hex)
        )
        # Sub directory
        pid = str(os.getpid())  # Get process ID for uniqueness
        sub_dir = os.path.join(output_dir, pid)
        os.makedirs(sub_dir, exist_ok=True)
        n_child_dirs = len(os.listdir(sub_dir))
        if not n_child_dirs:
            child_dir = os.path.join(sub_dir, "0")  # Create a sub directory if empty
        else:
            latest_child_dir = os.path.join(sub_dir, str(n_child_dirs - 1))
            if len(os.listdir(latest_child_dir)) >= MAX_FILES_PER_DIR:
                child_dir = os.path.join(sub_dir, str(n_child_dirs))
            else:
                child_dir = latest_child_dir  # Use the latest sub directory
        os.makedirs(child_dir, exist_ok=True)  # Create the sub directory if not exists
        # Save the DataFrame to CSV
        dist_file = os.path.join(child_dir, file_name)
        df.to_csv(dist_file, index=False, encoding="utf-8")

        return


def prepare_csv_from_ai_data(
    file_pattern: str,
    output_dir: str,
    period_start: str,
    period_end: str,
    icd10_to_mdcdx2_map_path: str,
    atc_to_yj_map_path: str,
    atc_to_hot_map_path: str,
    yj_to_hot_map_path: str,
    jlac10_segment_map_path: str,
    mak_workers: int = 1,
    end_date: str = None, # YYYYMMDD, all data beyond this date will be removed
):
    """Prepares CSV files from AI-generated data.
    
    Args:
        file_pattern (str): Pattern to match AI-generated data files.
        output_dir (str): Directory to save the cleaned CSV files.
        period_start (str): Start date for the timeline to start, in YYYYMMDD format.
        period_end (str): End date for the timeline to start, in YYYYMMDD format.
        icd10_to_mdcdx2_map_path (str): Path to the ICD10 to MDCDX2 mapping file.
        atc_to_yj_map_path (str): Path to the ATC to YJ mapping file.
        atc_to_hot_map_path (str): Path to the ATC to HOT mapping file.
        yj_to_hot_map_path (str): Path to the YJ to HOT mapping file.
        jlac10_segment_map_path (str): Path to the JLAC10 segment mapping file.
        mak_workers (int): Number of parallel workers to use for processing.
        end_date (str): End date for the data to be processed, in YYYYMMDD format.
            If None, no end date is applied.

    Returns:
        None: The function saves cleaned CSV files to the specified output directory.
    """


    if not os.path.exists(output_dir):
        raise FileNotFoundError(
            f"Output directory {output_dir} does not exist. Please create it first."
        )
    # Prepare CSV files from AI data.
    files = glob.glob(file_pattern, recursive="**" in file_pattern)
    start_dt = to_datetime_anything(period_start)
    end_dt = to_datetime_anything(period_end)

    # Task generator
    def _task_gen(files):
        for file in files:
            # Generate a random time
            random_time = start_dt + (end_dt - start_dt) * np.random.rand()
            # Convert to string in the format YYYYMMDD
            start_date = random_time.strftime("%Y%m%d")
            yield file, start_date

    task_gen = _task_gen(files)
    # Maps
    icd10_to_mdcdx2_map = pd.read_csv(
        icd10_to_mdcdx2_map_path, header=0, encoding="utf-8", dtype=str
    )
    atc_to_yj_map = pd.read_csv(
        atc_to_yj_map_path, header=0, encoding="utf-8", dtype=str
    )
    atc_to_hot_map = pd.read_csv(
        atc_to_hot_map_path, header=0, encoding="utf-8", dtype=str
    )
    yj_to_hot_map = pd.read_csv(
        yj_to_hot_map_path, header=0, encoding="utf-8", dtype=str
    )
    jlac10_segment_map = pd.read_csv(
        jlac10_segment_map_path, header=0, encoding="utf-8", dtype=str
    )

    # parallel processing
    with ProcessPoolExecutor(max_workers=mak_workers) as executor:
        futures = [
            executor.submit(
                clean_base_table,
                file=file,
                output_dir=output_dir,
                start_date=start_date,
                icd10_to_mdcdx2_map=icd10_to_mdcdx2_map,
                atc_to_yj_map=atc_to_yj_map,
                atc_to_hot_map=atc_to_hot_map,
                yj_to_hot_map=yj_to_hot_map,
                jlac10_segment_map=jlac10_segment_map,
                end_date=end_date,
            )
            for file, start_date in task_gen
        ]
        for future in tqdm(
            as_completed(futures), total=len(files), desc="Processing files"
        ):
            _ = future.result()

        print("All files processed successfully.")
