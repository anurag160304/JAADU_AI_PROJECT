import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests
import threading
import pyttsx3 # For TTS on desktop testing
import speech_recognition as sr # For STT on desktop testing

# --- Replace with mobile-specific libraries when packaging ---
# from kivy.core.audio import SoundLoader
# from android.speech import RecognizerIntent, SpeechRecognizer
# ---

class JaaduApp(App):
    def build(self):
        self.user_id = None
        self.server_ip = "192.168.1.10" # IMPORTANT: CHANGE THIS TO YOUR PC's IP ADDRESS

        layout = BoxLayout(orientation='vertical', padding=30, spacing=10)

        self.status_label = Label(text="Please enter your username to login.", size_hint_y=None, height=40)
        self.username_input = TextInput(hint_text='Username', multiline=False, size_hint_y=None, height=40)
        self.login_button = Button(text='Login / Register', on_press=self.login_user, size_hint_y=None, height=40)

        self.conversation_label = Label(text="Jaadu is waiting...")
        self.listen_button = Button(text='Tap and Speak', on_press=self.start_listening_thread, disabled=True)

        layout.add_widget(self.status_label)
        layout.add_widget(self.username_input)
        layout.add_widget(self.login_button)
        layout.add_widget(self.conversation_label)
        layout.add_widget(self.listen_button)

        return layout

    def login_user(self, instance):
        username = self.username_input.text.strip()
        if not username:
            self.status_label.text = "Username cannot be empty."
            return

        try:
            response = requests.post(f"http://{self.server_ip}:5000/api/login", json={'username': username})
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('userId')
                self.status_label.text = data.get('message')
                self.listen_button.disabled = False
                self.login_button.disabled = True
                self.username_input.disabled = True
            else:
                self.status_label.text = "Error: Could not log in."
        except requests.exceptions.ConnectionError:
            self.status_label.text = "Error: Cannot connect to the server."

    def start_listening_thread(self, instance):
        # Run listening in a separate thread to not freeze the UI
        threading.Thread(target=self.listen_and_process).start()

    def listen_and_process(self):
        self.conversation_label.text = "Listening..."
        # This uses desktop libraries for testing.
        # For a real mobile app, you'd replace this with Android/iOS APIs.
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                query = r.recognize_google(audio)
                self.conversation_label.text = f"You: {query}"
                self.send_query_to_server(query)
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                self.conversation_label.text = "Could not understand. Try again."
            except Exception as e:
                self.conversation_label.text = f"Error: {e}"


    def send_query_to_server(self, query):
        try:
            response = requests.post(
                f"http://{self.server_ip}:5000/api/interact",
                json={'userId': self.user_id, 'query': query}
            )
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response')
                self.conversation_label.text = f"Jaadu: {response_text}"
                self.speak(response_text)
            else:
                self.conversation_label.text = "Error receiving response from server."
        except requests.exceptions.ConnectionError:
            self.conversation_label.text = "Error: Cannot connect to the server."

    def speak(self, text):
        # This uses desktop libraries for testing.
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

if __name__ == '__main__':
    JaaduApp().run()