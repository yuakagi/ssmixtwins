import random
from ..random_data import JA_POSTAL_CODES

def generate_random_phone(prefix:str="099") -> str:
    """Generates a random phone number.

    NOTE: Avoid using fake.phone_number() directly. 

    Args:
        prefix (str): The prefix for the phone number, default is "099".s

    Returns:
        str: A random phone number that starts with the prefix.
    """
    number = f"{prefix}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    return number

def generate_random_address(fake, prefecture:str|None=None, add_building_name:bool=False) -> tuple[str, str]:
    """Generates a random address.

    Args:
        fake: A Faker instance.
        prefecture (str|None): The prefecture to use, if None, a random prefecture is chosen from JA_POSTAL_CODES.
        add_building_name (bool): Whether to add a building name to the address.    

    Returns:
        str: A random address and its corresponding postal code.
    """

    if prefecture is None:
        prefecture = random.choice(list(JA_POSTAL_CODES.keys()))
    
    sub_dict = JA_POSTAL_CODES[prefecture]
    city = random.choice(list(sub_dict.keys()))
    town = random.choice(list(sub_dict[city].keys()))
    # Postal code
    postal_code = sub_dict[city][town]
    # Address 
    chome = "99丁目" # We seet a fixed chome to avoid real addresses, instead of using fake.chome()
    ban = fake.ban()  # Random ban like '13番'
    gou = fake.gou()  # Random gou like '1号'
    address = f"{prefecture}{city}{town}{chome}{ban}{gou}"
    if add_building_name:
        building_name = fake.building_name()
        building_number = fake.building_number()
        address += f" 仮{building_name}{building_number}"

    return address, postal_code