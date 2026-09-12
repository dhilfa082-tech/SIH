"""
AgriLink AI - Tamil Voice Assistant
------------------------------------
Two-way Tamil voice assistant for the AgriLink AI project (SIH 2026).

- Speaks every AgriLink response aloud in Tamil (gTTS + pygame playback)
- Prints the same response in the terminal
- Listens to the farmer's Tamil speech via microphone
- Converts farmer speech to text (Google Speech Recognition, ta-IN)
- Waits for AgriLink to finish speaking before listening again
- No overlapping audio, no multiple media player windows

Tested target: Windows 10/11, Python 3.11
"""

import os
import sys
import time
import uuid

try:
    from gtts import gTTS
except ImportError:
    print("Missing package 'gTTS'. Install it with: pip install gTTS")
    sys.exit(1)

try:
    import pygame
except ImportError:
    print("Missing package 'pygame'. Install it with: pip install pygame")
    sys.exit(1)

try:
    import speech_recognition as sr
except ImportError:
    print("Missing package 'SpeechRecognition'. Install it with: pip install SpeechRecognition")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

pygame.mixer.init()

TEMP_DIR = os.path.join(os.getcwd(), "agrilink_temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Speak (Tamil TTS) - prints AND speaks, blocks until audio fully finishes
# ---------------------------------------------------------------------------

def speak(text):
    """Speak `text` aloud in Tamil and print it. Blocks until playback ends.

    This fixes the classic bug where only the first sentence is heard:
    each call uses a UNIQUE temp file, loads it fresh into pygame.mixer,
    waits for pygame to report playback finished (get_busy() == False),
    unloads the file, THEN deletes it. Nothing overlaps and nothing is
    left locked for the next call.
    """
    print(f"AgriLink AI: {text}")

    filename = os.path.join(TEMP_DIR, f"tts_{uuid.uuid4().hex}.mp3")

    try:
        tts = gTTS(text=text, lang="ta")
        tts.save(filename)
    except Exception as e:
        print(f"[TTS error - check your internet connection] {e}")
        return

    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[Audio playback error] {e}")
    finally:
        time.sleep(0.15)  # tiny buffer so Windows releases the file handle
        try:
            os.remove(filename)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Listen (Tamil STT)
# ---------------------------------------------------------------------------

def listen(timeout=6, phrase_time_limit=8):
    """Listen on the microphone and return recognized Tamil text (or "")."""
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("... கேட்கிறேன் (Listening) ...")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            try:
                audio = recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            except sr.WaitTimeoutError:
                print("[No speech detected]")
                return ""
    except OSError as e:
        print(f"[Microphone error - check your mic is connected] {e}")
        return ""

    try:
        text = recognizer.recognize_google(audio, language="ta-IN")
        print(f"Farmer: {text}")
        return text
    except sr.UnknownValueError:
        speak("மன்னிக்கவும், எனக்கு புரியவில்லை. மீண்டும் சொல்லுங்கள்.")
        return ""
    except sr.RequestError as e:
        print(f"[Speech recognition service error] {e}")
        speak("இணைய இணைப்பில் பிரச்சனை இருக்கு. தயவுசெய்து பின்னர் முயற்சி செய்யுங்கள்.")
        return ""


# ---------------------------------------------------------------------------
# Keyword matching helpers
# ---------------------------------------------------------------------------

def contains_any(text, keywords):
    text = text.lower()
    return any(k.lower() in text for k in keywords)


# Primary words are now pure Tamil; old loanwords kept as fallback matches
# in case the farmer still says them in English.
LOCAL_KEYWORDS = ["உள்ளூர்", "உள்ளூர் சந்தை", "லோக்கல்", "local"]
BIG_KEYWORDS = ["பெரிய சந்தை", "பெரிய", "பிக்", "big"]
PRICE_KEYWORDS = ["விலை", "price"]
INFO_KEYWORDS = ["தகவல்", "info", "information", "சந்தை தகவல்"]
TOMATO_KEYWORDS = ["தக்காளி", "tomato"]
EXIT_KEYWORDS = ["வேண்டாம்", "நிறுத்து", "exit", "stop", "பை"]


# ---------------------------------------------------------------------------
# Conversation branches
# ---------------------------------------------------------------------------

def handle_local_market():
    speak(
        "சரி, உள்ளூர் சந்தை தேர்வு பண்ணிட்டீங்க. "
        "உங்களுக்கு விலை தெரிஞ்சுக்கணுமா, இல்ல சந்தை தகவல் வேணுமா?"
    )
    reply = listen()

    if contains_any(reply, PRICE_KEYWORDS):
        speak("சரி. எந்த பயிரின் விலை தெரிஞ்சுக்கணும்?")
        crop = listen()

        if contains_any(crop, TOMATO_KEYWORDS):
            speak(
                "சரி. இந்த டெமோவில் சேலம் சந்தையில் "
                "தக்காளி ஒரு கிலோ இருபத்தைந்து ரூபாய்."
            )
        elif crop:
            speak(
                f"மன்னிக்கவும், {crop} விலை தகவல் இந்த டெமோவில் இல்லை. "
                "தக்காளி விலையை மட்டும் இப்போ காட்ட முடியும்."
            )
        else:
            speak("பயிர் பெயர் தெளிவா கேக்கல. மீண்டும் முயற்சி செய்யுங்கள்.")

    elif contains_any(reply, INFO_KEYWORDS):
        speak(
            "உள்ளூர் சந்தையில் இன்று நல்ல கிராக்கி இருக்கு. "
            "காய்கறி விலைகள் ஸ்திரமா இருக்கு."
        )
    else:
        speak("புரியவில்லை. விலை அல்லது சந்தை தகவல் என்று சொல்லுங்கள்.")


def handle_big_market():
    speak(
        "சரி, பெரிய சந்தை தேர்வு பண்ணிட்டீங்க. "
        "நீங்க எந்த பயிரை விற்க விரும்புறீங்க?"
    )
    crop = listen()  # captured for future use / logging

    speak("AgriLink AI உங்க பகுதியில் இதே பயிரை விற்கிற மற்ற விவசாயிகளை கண்டுபிடிக்கும்.")
    speak("உதாரணத்துக்கு, ஒரு விவசாயி கிட்ட ஐநூறு கிலோ தக்காளி இருக்கு.")
    speak("இன்னொரு விவசாயி கிட்ட எழுநூறு கிலோ தக்காளி இருக்கு.")
    speak("AgriLink AI இந்த இரண்டு விவசாயிகளையும் ஒன்றாக இணைக்கும்.")
    speak("இப்போ மொத்தம் ஆயிரத்து இருநூறு கிலோ தக்காளி கிடைக்கும்.")
    speak("இந்த மொத்த அளவை பெரிய வாங்குபவர் கிட்ட விற்க முடியும்.")
    speak("AgriLink AI பொருத்தமான வாங்குபவரை கண்டுபிடித்து போக்குவரத்து வாய்ப்புகளையும் பரிந்துரை செய்யும்.")
    speak("இதனால் சின்ன விவசாயிகளுக்கும் பெரிய சந்தையில் விற்க வாய்ப்பு கிடைக்கும்.")


def run_intro():
    speak("வணக்கம். AgriLink AI க்கு உங்களை வரவேற்கிறோம்.")
    speak(
        "நான் உங்களுக்கு உள்ளூர் சந்தை விலை, சந்தை தகவல், "
        "மற்றும் பெரிய சந்தையில் விற்க உதவுவேன்."
    )
    speak("நீங்க உள்ளூர் சந்தை அல்லது பெரிய சந்தை என்று சொல்லலாம்.")


# ---------------------------------------------------------------------------
# Main conversation loop
# ---------------------------------------------------------------------------

def main():
    run_intro()

    while True:
        speak("நான் உங்களுக்கு எப்படி உதவலாம்?")
        reply = listen()

        if not reply:
            continue

        if contains_any(reply, EXIT_KEYWORDS):
            speak("நன்றி. AgriLink AI-ஐ பயன்படுத்தியதற்கு நன்றி. இனிய நாள்.")
            break

        if contains_any(reply, LOCAL_KEYWORDS):
            handle_local_market()
        elif contains_any(reply, BIG_KEYWORDS):
            handle_big_market()
        else:
            speak("தயவுசெய்து உள்ளூர் சந்தை அல்லது பெரிய சந்தை என்று சொல்லுங்கள்.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Program stopped by user]")
    finally:
        pygame.mixer.quit()