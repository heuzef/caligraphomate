import requests
import time

# base_url = "http://heuzef.com:8020"
base_url = "http://192.168.0.37"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

# Init
endpoint_init = "/move/init"
url_init = f"{base_url}{endpoint_init}"

# Joints write
endpoint_write = "/joints/write?robot_id=0"
url_write = f"{base_url}{endpoint_write}"

try:
    # Init
    response_init = requests.post(url_init)
    print(f"INIT")
    print(f"Réponse: {response_init.text}")

    time.sleep(2)

    # Center
    data_center = {
    "angles": [
        0.00,
        1.20,
        0.00,
        -1.00,
        -1.57,
        -1.10
    ],
    "unit": "rad"
    }

    response_write = requests.post(url_write, headers=headers, json=data_center)
    print(f"CENTER")
    print(f"Réponse: {response_init.text}")

    time.sleep(2)

    # Top right
    data_top_right = {
    "angles": [
        -0.36,
        1.80,
        -1.15,
        -0.46,
        -1.57,
        -1.10
    ],
    "unit": "rad"
    }

    response_write = requests.post(url_write, headers=headers, json=data_top_right)
    print(f"TOP RIGHT")
    print(f"Réponse: {response_init.text}")

    time.sleep(2)

    # Top left
    data_top_left = {
    "angles": [
        0.36,
        1.80,
        -1.15,
        -0.46,
        -1.57,
        -1.10
    ],
    "unit": "rad"
    }

    response_write = requests.post(url_write, headers=headers, json=data_top_left)
    print(f"TOP_LEFT")
    print(f"Réponse: {response_init.text}")

    time.sleep(2)

    # Bottom right
    data_bottom_right = {
    "angles": [
        -0.46,
        1.00,
        0.50,
        -1.00,
        -1.57,
        -1.10
    ],
    "unit": "rad"
    }

    response_write = requests.post(url_write, headers=headers, json=data_bottom_right)
    print(f"BOTTOM RIGHT")
    print(f"Réponse: {response_init.text}")

    time.sleep(2)

    # Bottom left
    data_bottom_left = {
    "angles": [
        0.46,
        1.00,
        0.50,
        -1.00,
        -1.57,
        -1.10
    ],
    "unit": "rad"
    }

    response_write = requests.post(url_write, headers=headers, json=data_bottom_left)
    print(f"BOTTOM LEFT")
    print(f"Réponse: {response_init.text}")

    time.sleep(2)


except requests.exceptions.RequestException as e:
    print(f"Erreur lors des requêtes: {e}")