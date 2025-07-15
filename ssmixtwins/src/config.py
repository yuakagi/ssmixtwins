# SSMIX2 guideline version (Used in MSH segment)
SSMIX_GUIDELINE_VERSION = "h"  # Originally, this is 'h'
BASE_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S%f"


# Cancel messages are not included
SSMIX_DATA_TYPES = {
    "ADT-00": "ADT^A08",
    "ADT-01": "ADT^A54",
    "ADT-12": "ADT^A04",
    "ADT-21": "ADT^A14",
    "ADT-22": "ADT^A01",
    "ADT-31": "ADT^A21",
    "ADT-32": "ADT^A22",
    "ADT-41": "ADT^A15",
    "ADT-42": "ADT^A02",
    "ADT-51": "ADT^A16",
    "ADT-52": "ADT^A03",
    "ADT-61": "ADT^A60",
    "PPR-01": "PPR^ZD1",
    "OMD": "OMD^O03",
    "OMP-01": "RDE^O11",
    "OMP-11": "RAS^O17",
    "OMP-02": "RDE^O11",
    "OMP-12": "RAS^O17",
    "OML-01": "OML^O33",
    "OML-11": "OUL^R22",
    "OMG-01": "OMG^O19",
    "OMG-11": "OMI^Z23",
    "OMG-02": "OMG^O19",
    "OMG-12": "OMI^Z23",
    "OMG-03": "OMG^O19",
    "OMG-13": "ORU^R01",
}
