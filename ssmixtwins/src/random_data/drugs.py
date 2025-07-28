presc_keywords = [
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
    "皮下注",
    "テープ",
    "ワセリン",
    "内服",
    "内用",
]

# Codes compatible with merit_9_4
NAME_TO_PRESCRIPTION_UNIT = {
    # 錠
    "TAB": ["錠"],
    # カプセル
    "CAP": ["カプセル", "cap", "Cap"],
    # 包
    "PCK": ["原末", "粉末", "顆粒", "散"],
    # 本
    "HON": [
        "クリーム",
        "点眼",
        "点耳",
        "点鼻",
        "うがい液",
        "噴霧",
    ],
}

# For prescription only
# NOTE: Units are selected from merit_9_4
NAME_TO_DOSE_FORM = {
    "TAB": {
        "keywords": ["錠"],
        "dose_unit_code": "TAB",
        "dispense_unit_code": "TAB",
    },
    "CAP": {
        "keywords": ["カプセル", "Cap", "cap"],
        "dose_unit_code": "CAP",
        "dispense_unit_code": "CAP",
    },
    "PWD": {
        "keywords": ["散", "原末", "粉末", "顆粒"],
        "dose_unit_code": "PAC",
        "dispense_unit_code": "PAC",
    },
    "SYR": {
        "keywords": ["シロップ"],
        "dose_unit_code": "DOSE",  # 〜回分
        "dispense_unit_code": "DOSE",
    },
    "SUP": {
        "keywords": ["坐"],
        "dose_unit_code": "KO",  # 個
        "dispense_unit_code": "KO",
    },
    "OIT": {
        "keywords": ["膏"],
        "dose_unit_code": '""',  # Ointment dose unit is hard to define, so use '""'.
        "dispense_unit_code": "HON",
    },
    "CRM": {
        "keywords": ["クリーム"],
        "dose_unit_code": '""',
        "dispense_unit_code": "HON",
    },
    "TPE": {
        "keywords": ["テープ", "貼付", "パッチ"],
        "dose_unit_code": "SHT",  # 枚
        "dispense_unit_code": "SHT",
    },
    "LQD": {
        "keywords": ["うがい液"],
        "dose_unit_code": '""',
        "dispense_unit_code": "HON",
    },
    "INJ": {
        "keywords": ["注"],
        "dose_unit_code": '""',
        "dispense_unit_code": "HON",
    },
}


# Compatible with udt_0162
# NOTE: その他 is 'OTH'. The order matters!!. The program serches for the first match.
NAME_TO_PRESCRIPTION_ROUTE = {
    "AP": ["膏", "クリーム"],
    "PR": ["坐"],
    "OP": ["眼"],
    "OT": ["耳"],
    "IH": ["吸入", "噴霧"],
    "SC": ["皮下"],
    "SL": ["舌下"],
    "VG": ["膣"],
    "PO": [
        "錠",
        "カプセル",
        "cap",
        "Cap",
        "原末",
        "粉末",
        "顆粒",
        "散",
        "シロップ",
        "内服",
        "内用",
    ],
}


# Compatible with jhsi_0002
NAME_TO_INJECTION_TYPE = {
    "00": "一般",
    "01": ["血小板", "凍結血漿", "赤血球"],  # "血液製剤",
}

# Random prescription repeat pattern forms
ROUTE_TO_PRESC_REPEST_PATTERNS = {
    # NOTE: daily_dose x minimum_dose = total_daily_dose
    # NOTE: Drugs without fixed minumu_dose (e.g., ointment) must not use total_daily_dose (RXE-3) and dose_unit (RXE-5).
    #       Therefore, ignore daily_dose for these drugs.
    # Oral route (The second number in the 16 digits is '0' for oral)
    "PO": [
        {
            "repeat_pattern_code": "1011040000000000",
            "repeat_pattern_name": "内服・経口・１日１回朝食後",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        },
        {
            "repeat_pattern_code": "1012040400000000",
            "repeat_pattern_name": "内服・経口・１日２回朝夕食後",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "2",
        },
        {
            "repeat_pattern_code": "1013044400000000",
            "repeat_pattern_name": "内服・経口・１日３回朝昼夕食後",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "3",
        },
    ],
    # Sublingual route (The second number in the 16 digits is '1' for sublingual)
    "SL": [
        {
            "repeat_pattern_code": "1111040000000000",
            "repeat_pattern_name": "内服・舌下・１日１回朝食後",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        }
    ],
    # Transvaginal route (The second number in the 16 digits is 'T' for vaginal)
    "VG": [
        {
            "repeat_pattern_code": "2T71000000000000",
            "repeat_pattern_name": "外用・経膣・１日１回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        }
    ],
    # 　Inhalation route (The second number in the 16 digits is 'L' for inhalation)
    "IH": [
        {
            "repeat_pattern_code": "2L71000000000000",
            "repeat_pattern_name": "外用・吸入・１日１回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        },
        {
            "repeat_pattern_code": "2L72000000000000",
            "repeat_pattern_name": "外用・吸入・１日２回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "2",
        },
    ],
    # Ocular route (The second number in the 16 digits is 'O' for ocular)
    "OT": [
        {
            "repeat_pattern_code": "2G71000000000000",
            "repeat_pattern_name": "外用・点耳・１日１回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        },
        {
            "repeat_pattern_code": "2G72000000000000",
            "repeat_pattern_name": "外用・点耳・１日２回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "2",
        },
    ],
    # Ophthalmic route (The second number in the 16 digits is 'H' for ophthalmic)
    "OP": [
        {
            "repeat_pattern_code": "2H71000000000000",
            "repeat_pattern_name": "外用・点眼・１日１回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        },
        {
            "repeat_pattern_code": "2H72000000000000",
            "repeat_pattern_name": "外用・点眼・１日２回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "2",
        },
    ],
    # Rectal route (The second number in the 16 digits is 'R' for rectal)
    "PR": [
        {
            "repeat_pattern_code": "2R71000000000000",
            "repeat_pattern_name": "外用・肛門挿入・１日１回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        },
        {
            "repeat_pattern_code": "2R72000000000000",
            "repeat_pattern_name": "外用・肛門挿入・１日２回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "2",
        },
    ],
    # Transdermal route (NOTE: We use local codes for this because 'AP' can be mapped to several JAMISDP01 codes.)
    "AP": [
        {
            "repeat_pattern_code": "9999000000000000",
            "repeat_pattern_name": "外用・１日１回",
            "repeat_pattern_code_system": "99xyz",
            "daily_dose": "1",
        },
        {
            "repeat_pattern_code": "9999000000000000",
            "repeat_pattern_name": "外用・１日２回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "2",
        },
    ],
    # Subcutaneous route (The second number in the 16 digits is '2' for subcutaneous)
    "SC": [
        {
            "repeat_pattern_code": "3271000000000012",
            "repeat_pattern_name": "注射・皮下・１日１回",
            "repeat_pattern_code_system": "JAMISDP01",
            "daily_dose": "1",
        }
    ],
}
