import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import speech_recognition as sr
import pyttsx3

# Inicijalizacija potrebnih stvari 
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Funkcija za output glasa
def speak(text):
   engine.say(text)
   engine.runAndWait()
    
# Funkcija za uzimanje korisničkog inputa 
def get_audio():
   with sr.Microphone() as source:
      print("Listening...")
      recognizer.adjust_for_ambient_noise(source)
      audio = recognizer.listen(source) 

      try:
         print("Recognizing...")
         command = recognizer.recognize_google(audio)
         print(f"User said: {command}")
         return command.lower()
      except Exception as e:
         print("Exception: " + str(e))
         return ""
         

def main():
   device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

   with open("intents.json", "r") as f:
      intents = json.load(f)
   
   FILE = "data.pth"
   data = torch.load(FILE)

   input_size = data["input_size"]
   hidden_size = data["hidden_size"]
   output_size = data["output_size"]
   all_words = data["all_words"]
   tags = data["tags"]
   model_state = data["model_state"]

   model = NeuralNet(input_size, hidden_size, output_size).to(device)
   model.load_state_dict(model_state)
   model.eval()

   bot_name = "Bot"
   print("Hello! I am your assistant, what can I do?")
   speak("Hello! I am your assistant, what can I do?")
   
   with sr.Microphone() as source:
      recognizer.adjust_for_ambient_noise(source)
      
   while(True):
      command = get_audio()
      if command is None:
         continue
      
      command = tokenize(command)
      X = bag_of_words(command, all_words)
      X = X.reshape(1, X.shape[0])
      X = torch.from_numpy(X)
   
      output = model(X)
      _, predicted = torch.max(output, dim = 1)
      tag = tags[predicted.item()]
   
      probs = torch.softmax(output, dim = 1)
      prob = probs[0][predicted.item()]
   
      if prob.item() > 0.75:
         for intent in intents["intents"]:
            if tag == intent["tag"]:
               random_choice = random.choice(intent['responses'])
               print(f"{bot_name}: {random_choice}")
               speak(random_choice)
         if tag == "goodbye":
            break
         # ODE NASTAVIT DODAVAT UVJETE A GORE DEFINIRAT VISE FUNKCIJA KOJE IZVRSAVAJU POSLOVE-----------------------------------------------------------
      else:
         print(f"{bot_name}: I do not understand...")     
           
# Runnaj main      
if __name__ == "__main__":
    main()