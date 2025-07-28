
import os
import json

# Postal codes
# NOTE: This file is loaded from a JSON file containing postal codes. Make sure you specify this in setup.py
JA_POSTAL_CODES = None
with open(os.path.join(os.path.dirname(__file__), "ja_postal_codes.json"), "r", encoding="utf-8") as f:
    JA_POSTAL_CODES = json.load(f)

# ABO blood types
RANDOM_ABO_BLOOD_TYPES = {
    "choices": ["A", "B", "AB", "O", ""],
    "weights": [0.4, 0.3, 0.1, 0.2, 0.0],  # Weights for ABO blood types
}

# We use 99XYZ for local codes
RANDOM_ALLERGIES = [
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "1",  # Penicillin
        "allergen_name": "ペニシリン",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "2",  # Aspirin
        "allergen_name": "アスピリン",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "3",  # Sulfa Drugs
        "allergen_name": "スルファ剤",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "4",  # Cephalosporins
        "allergen_name": "セフェム系抗生物質",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
    {
        "allergy_type_code": "FA",  # Food Allergy
        "allergen_code": "J9FA21180000",  # Peanuts
        "allergen_name": "ピーナッツ",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "LA",  # Pollen Allergy
        "allergen_code": "J9NK12000000",  # Pollen
        "allergen_name": "花粉",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "AA",  # Animal Allergy
        "allergen_code": "J9NJ12150000",  # Cat Dander
        "allergen_name": "猫",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "AA",  # Animal Allergy
        "allergen_code": "J9NJ12110000",
        "allergen_name": "犬",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "PA",  # Plant Allergy
        "allergen_code": "J9NK12150000",  # Ragweed
        "allergen_name": "ブタクサ",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "MA",  # Miscellaneous Allergy
        "allergen_code": "J9NP14110000",  # Latex
        "allergen_name": "ラテックス",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "MC",  # Miscellaneous Contraindication
        "allergen_code": "J9NT11000000",  # Alcohol
        "allergen_name": "アルコール",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "EA",  # Environmental Allergy
        "allergen_code": "J9NM12000000",  # Dust Mites
        "allergen_name": "ダニ",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "EA",  # Environmental Allergy
        "allergen_code": "J9NM13110000",  # Dust Mites
        "allergen_name": "ハウスタスト",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "FA",  # Food Allergy
        "allergen_code": "J9FC12000000",
        "allergen_name": "貝類",
        "allergen_code_system": "J-FAGY",  # Default code system for allergens
    },
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "13",  # Non-Steroidal Anti-Inflammatory Drugs (NSAIDs)
        "allergen_name": "非ステロイド性抗炎症薬",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "14",  # Antibiotics
        "allergen_name": "アセトアミノフェン",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
    {
        "allergy_type_code": "DA",  # Drug Allergy
        "allergen_code": "15",  # Anticonvulsants
        "allergen_name": "フロセミド",
        "allergen_code_system": "99XYZ",  # Default code system for allergens
    },
]


RANDOM_DEPARTMENT_CODES = {
    "01": "内科",
    "011": "第１内科",
    "012": "第２内科",
    "013": "第３内科",
    "014": "第４内科",
    "018": "一般内科",
    "02": "精神科",
    "03": "神経科",
    "04": "神経内科",
    "05": "呼吸器科",
    "051": "呼吸器・アレルギー科",
    "052": "呼吸器・感染症内科",
    "06": "消化器科",
    "061": "肝臓内科",
    "062": "肝胆膵科",
    "063": "膵臓内科",
    "064": "胆道・膵臓内科",
    "06A": "肝臓病科",
    "08": "循環器科",
    "081": "循環器内科",
    "082": "冠動脈疾患治療部",
    "09": "小児科",
    "091": "小児科周産母子",
    "092": "新生児科",
    "093": "小児循環器科",
    "094": "小児神経科",
    "09A": "成長発達外来",
    "10": "外科",
    "101": "第１外科",
    "102": "第２外科",
    "103": "第３外科",
    "105": "一般外科",
    "106": "総合外科",
    "107": "病態外科",
    "11": "整形外科",
    "111": "整形外科・脊椎外科",
    "112": "脊椎外科",
}


RANDOM_WARDS = [
    "1A",
    "1B",
    "2A",
    "2B",
    "3A",
    "3B",
    "4A",
    "4B",
    "5A",
    "5B",
    "6A",
    "6B",
    "7A",
    "7B",
    "8A",
    "8B",
    "9A",
    "9B",
    "10A",
    "10B",
    "11A",
    "11B",
    "12A",
    "12B",
]
RANDOM_BEDS = ["1", "2", "3", "4"]
RANDOM_ROOMS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
