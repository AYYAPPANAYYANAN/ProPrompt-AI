import pyttsx3

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    text = 'Hello Ayyappan, I am your autonomous AI'
    speak_text(text)

if __name__ == "__main__":
    main()