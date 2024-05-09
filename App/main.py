import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import speech_recognition as sr
import pyttsx3
import datetime
import re

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

# Funkcija za dobivanje trenutacnog vremena
def tell_current_time():
   current_time = datetime.datetime.now()
   current_hours = current_time.strftime("%H")
   current_minutes = current_time.strftime("%M")
   if current_hours[0] == "0":
      current_hours = current_hours[1]
   if current_minutes[0] == "0":
      current_minutes = current_minutes[1]
   print(f"Bot: It is {current_hours} hours and {current_minutes} minutes.")
   speak(f"It is {current_hours} hours and {current_minutes} minutes.")

# Funkcija za dobivanja trenutacnog dana u tjednu
def tell_day_of_week():
   current_date = datetime.datetime.now()
   day = current_date.strftime("%A")
   print(f"Bot: It is {day}")
   speak(f"It is {day}")

# Funkcija za dobivanja trenutacnog datuma
def tell_current_date():
   current_date = datetime.datetime.today()
   formatted_date = current_date.strftime("%Y-%m-%d")
   print(f"Bot: Today is {formatted_date}")
   speak(f"Today is {formatted_date}")
   
# Funkcija za pretvaranje teksta u matematicki izraz
def text_to_expression(text):
   pattern = r'(\d+|\+|\-|\*|\/)'
   tokens = re.findall(pattern, text)
   
   word_to_symbol = {
      "plus": "+",
      "minus": "-",
      "times": "*",
      "divided by": "/"
   }
   
   tokens = [word_to_symbol.get(token, token) for token in tokens]
   expression = "".join(tokens)
   return expression

# Funkcija za evaluiranje matematickog izraza
def calculate_expression(expression):
   try:
      result = eval(expression)
      return result
   except Exception as e:
      return str(e)
   
# Main
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
   print("Bot: Hello! I am your assistant, what can I do for you?")
   speak("Hello! I am your assistant, what can I do for you?")
   
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
               if random_choice != "none":
                  print(f"{bot_name}: {random_choice}")
                  speak(random_choice)
         if tag == "goodbye":
            break
         if tag == "tell-current-time":
            tell_current_time()
         if tag == "day_of_week":
            tell_day_of_week()
         if tag == "current_date":
            tell_current_date()
         if tag == "mathematical_expression":
            expression = text_to_expression(command)
            result = calculate_expression(expression)
            speak(f"Answer is {result}")
            print(f"Answer is {result}")
            
         # ODE NASTAVIT DODAVAT UVJETE A GORE DEFINIRAT VISE FUNKCIJA KOJE IZVRSAVAJU POSLOVE-----------------------------------------------------------
      else:
         print(f"{bot_name}: I do not understand...")     
           
# Runnaj main      
if __name__ == "__main__":
    main()