
import random
import time

def fake_coordinates():
    # Generate a fake latitude and longitude
    lat = round(random.uniform(-90.0, 90.0), 6)
    lon = round(random.uniform(-180.0, 180.0), 6)
    return lat, lon

def change_location_loop():
    print("[LocationObfuscator] Real-time GPS/IP spoofing activated.")
    for _ in range(20000):
        lat, lon = fake_coordinates()
        print(f"[OBFUSCATE] Faked Location: Lat {lat}, Lon {lon}")
        time.sleep(0.5)

if __name__ == "__main__":
    change_location_loop()
