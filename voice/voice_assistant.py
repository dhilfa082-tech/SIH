import sqlite3
import pyttsx3
import speech_recognition as sr
import time


# ==========================================
# AGRILINK AI - VOICE ASSISTANT
# ==========================================


# ==========================================
# SPEAK FUNCTION
# ==========================================

def speak(text):
    """
    Every AgriLink AI message is printed
    and spoken through the speaker.
    """

    print(f"\nAgriLink AI: {text}", flush=True)

    try:
        # Create a fresh voice engine
        engine = pyttsx3.init()

        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()

        engine.stop()

        # Small pause before microphone starts
        time.sleep(0.5)

    except Exception as e:
        print(f"\nVoice Error: {e}")


# ==========================================
# LISTEN FUNCTION
# ==========================================

def listen():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("\n🎤 Listening... Please speak.")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=8
            )

        text = recognizer.recognize_google(audio)

        print(f"👨‍🌾 Farmer: {text}")

        return text.lower()

    except sr.WaitTimeoutError:

        speak("I did not hear anything. Please try again.")

        return ""

    except sr.UnknownValueError:

        speak("Sorry, I could not understand your voice. Please try again.")

        return ""

    except Exception as e:

        print(f"\nSystem Error: {e}")

        return ""


# ==========================================
# DATABASE SETUP
# ==========================================

def setup_database():

    conn = sqlite3.connect("agrilink_voice.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT UNIQUE,
            price_per_kg REAL,
            location TEXT
        )
    """)

    sample_data = [
        ("tomato", 25, "Salem"),
        ("onion", 30, "Salem"),
        ("potato", 35, "Salem"),
        ("rice", 45, "Salem"),
        ("carrot", 40, "Salem")
    ]

    for crop, price, location in sample_data:

        cursor.execute("""
            INSERT OR IGNORE INTO market_prices
            (crop_name, price_per_kg, location)
            VALUES (?, ?, ?)
        """, (crop, price, location))

    conn.commit()

    return conn


# ==========================================
# CHECK MARKET PRICE
# ==========================================

def check_market_price(conn, crop):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT price_per_kg, location
        FROM market_prices
        WHERE LOWER(crop_name) LIKE ?
    """, (f"%{crop.lower()}%",))

    result = cursor.fetchone()

    if result:

        price = result[0]
        location = result[1]

        return (
            f"The current demonstration market price for "
            f"{crop} in {location} is {price} rupees per kilogram."
        )

    else:

        return (
            f"Sorry, price information for {crop} "
            f"is not available in this prototype."
        )


# ==========================================
# LOCAL MARKET FLOW
# ==========================================

def local_market_flow(conn):

    # THIS MUST BE SPOKEN 🔊
    speak(
        "Local Market selected. "
        "Would you like to check prices or market information?"
    )

    while True:

        choice = listen()

        if not choice:
            continue

        # PRICE
        if "price" in choice:

            # THIS MUST BE SPOKEN 🔊
            speak("Please say the crop name.")

            while True:

                crop = listen()

                if crop:
                    break

            result = check_market_price(conn, crop)

            # THIS MUST BE SPOKEN 🔊
            speak(result)

            return


        # MARKET INFORMATION
        elif (
            "information" in choice
            or "market information" in choice
            or "stock" in choice
        ):

            # THIS MUST BE SPOKEN 🔊
            speak(
                "Market information selected. "
                "This prototype provides information about "
                "crop availability and local market conditions."
            )

            return


        else:

            # THIS MUST BE SPOKEN 🔊
            speak(
                "Please say check prices "
                "or market information."
            )


# ==========================================
# BIG MARKET FLOW
# ==========================================

def big_market_flow():

    # THIS MUST BE SPOKEN 🔊
    speak("Big Market selected.")

    # THIS MUST BE SPOKEN 🔊
    speak(
        "AgriLink AI helps small farmers combine their produce "
        "and access larger buyers."
    )

    # THIS MUST BE SPOKEN 🔊
    speak("Please say your crop name.")

    crop = ""

    while not crop:
        crop = listen()

    # THIS MUST BE SPOKEN 🔊
    speak(
        f"You selected {crop}. "
        "We will now check for other farmers "
        "with the same crop."
    )

    # Demonstration pooling

    speak(
        "Matching farmers found. "
        "Farmer Ramesh has 500 kilograms, "
        "and Farmer Suresh has 700 kilograms."
    )

    speak(
        "Your produce is being combined into a Smart Farmer Pool."
    )

    speak(
        "The combined quantity can now be offered "
        "to larger wholesale buyers."
    )

    speak(
        "AgriLink AI is checking buyer requirements."
    )

    speak(
        "A suitable buyer match has been found."
    )

    speak(
        "The next step is logistics and delivery coordination."
    )


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    print("\n===================================")
    print("      AGRILINK AI VOICE SYSTEM")
    print("===================================")

    conn = setup_database()

    # --------------------------------------
    # WELCOME
    # --------------------------------------

    speak("Welcome to AgriLink AI.")

    speak(
        "Please choose Local Market "
        "or Big Market."
    )


    # --------------------------------------
    # FIRST CHOICE
    # --------------------------------------

    while True:

        choice = listen()

        if not choice:
            continue


        # ----------------------------------
        # LOCAL MARKET
        # ----------------------------------

        if "local" in choice:

            local_market_flow(conn)

            break


        # ----------------------------------
        # BIG MARKET
        # ----------------------------------

        elif (
            "big" in choice
            or "bulk" in choice
            or "large" in choice
        ):

            big_market_flow()

            break


        # ----------------------------------
        # WRONG RESPONSE
        # ----------------------------------

        else:

            speak(
                "Sorry, I did not understand. "
                "Please say Local Market or Big Market."
            )


    # --------------------------------------
    # END
    # --------------------------------------

    speak("Thank you for using AgriLink AI.")

    conn.close()


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
    