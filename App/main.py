import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import speech_recognition as sr
import pyttsx3
import datetime
import re
import requests

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
   list_of_words = []
   math_operations = {"+", "-", "x", "/"}
   expression = ""
   for item in text:
      list_of_words.append(item)
   
   number_of_operations = 1
   for i in range(len(list_of_words)):
      if list_of_words[i] in math_operations:
         if number_of_operations == 1:
            expression += f"{list_of_words[i - 1]} {list_of_words[i]} {list_of_words[i + 1]}"
            number_of_operations += 1
         else:
            expression += f" {list_of_words[i]} {list_of_words[i + 1]}"
   return expression  

# Funkcija za evaluiranje matematickog izraza
def calculate_expression(expression):
   try:
      if "x" in expression:
         expression = expression.replace("x", "*")
      result = eval(expression)
      return result
   except Exception as e:
      return "I can't evaluate given expression. "

# Funkcija koja preko api-ja dobiva trenutacno vrijeme za odredenu lokaciju   
def weather(command, cities):
   for city in cities:
      if city in command:
         try:
            city_search = city
            api_key = "your_weather_api_key_from_openweather.org"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_search}&appid={api_key}"
            response = requests.get(url)
            weather_data = response.json()

            temperature_kelvin = weather_data["main"]["temp"]
            temperature_celsius = round(temperature_kelvin - 272.15, 2)
            wind_speed = weather_data["wind"]["speed"]
            sky_condition = weather_data["weather"][0]["id"]
            humidity = weather_data["main"]["humidity"]
         except Exception  as e:
            print("Bot: Something went wrong.")
            speak("Something went wrong.")
            break

         if sky_condition >= 200 and sky_condition <= 499:
            print("Bot: It is raining a little bit. I would cover my head.")
            speak("It is raining a little bit. I would cover my head.")
         elif sky_condition >= 500 and sky_condition <= 599:
            print("Bot: Weather is rainy. I would take an umbrella.")
            speak("Weather is rainy. I would take an umbrella.")
         elif sky_condition >= 600 and sky_condition <= 699:
            print("Bot: Weather is snowy.")
            speak("Weather is snowy.")
         elif sky_condition >= 801 and sky_condition <= 899:
            print("Bot: Weather is cloudy.")
            speak("Weather is cloudy.")
         elif sky_condition == 800:
            print("Bot: Weather is clear.")
            speak("Weather is clear.")
         else:
            print("Bot: Weather is undefined.")
            speak("Weather is undefined.")
         
         print(f"Bot: Temperature is {temperature_celsius} degrees Celsius.")
         speak(f"Temperature is {temperature_celsius} degrees Celsius.")

         print(f"Bot: Wind speed is {wind_speed} km/h.")
         speak(f"Wind speed is {wind_speed} km/h.")

         print(f"Bot: Humidity is {humidity}%.")
         speak(f"Humidity is {humidity}%.")

def read_todo_list():
   with open("data.txt", "r") as file:
      todo_list = []
      current_line = file.readline().strip("\n")
      while(current_line != "todo_list_start"):
         current_line = file.readline().strip("\n")
      current_line = file.readline().strip("\n")
      while(current_line != "todo_list_end"):
         todo_list.append(current_line)
         current_line = file.readline().strip("\n")
   return todo_list

def add_item_to_todo_list(task):
   todo_list = read_todo_list()
   todo_list.append(task)
   with open("data.txt", "r") as file:
      lines = file.readlines()
   todo_list_end_index = lines.index("todo_list_end\n")
   del lines[todo_list_end_index:]
   lines.append(f"{task}\n")
   lines.append("todo_list_end\n")
   with open('data.txt', 'w') as file:
      file.writelines(lines)

def remove_item_from_todo_list(task):
   pass

def find_task_in_command_add(raw_command):
   words_in_command = raw_command.split()
   index_of_add = words_in_command.index("add") if "add" in words_in_command else 0
   index_of_to = words_in_command.index("to") if "to" in words_in_command else 0
   index_of_called = words_in_command.index("called") if "called" in words_in_command else 0
   if index_of_called and index_of_called > index_of_to:
      task = words_in_command[index_of_called + 1:]
      task = " ".join(task)
   elif index_of_called and index_of_called < index_of_to: 
      task = words_in_command[index_of_called + 1:index_of_to]
      task = " ".join(task)
   else:
      task = words_in_command[index_of_add + 1:index_of_to]
      task = " ".join(task)
   return task

def find_task_in_command_remove(raw_command):
   pass

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
      
      raw_command = command
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
            print(f"Bot: Answer is {result}")
            speak(f"Answer is {result}")
         if tag == "weather":
            with open("data.txt", "r") as file:
               cities = []
               current_line = file.readline().strip("\n")
               while(current_line != "cities_end"):
                  cities.append(current_line)
                  current_line = file.readline().strip("\n")
            weather(raw_command, cities)
         if tag == "read_todo_list":
            todo_list = read_todo_list()
            print(f"Bot: {", ".join(todo_list)}.")
            for item in todo_list:
               speak(item)
         if tag == "add_item_to_todo_list":
            task = find_task_in_command_add(raw_command)
            add_item_to_todo_list(task)
         if tag == "remove_item_from_todo_list":
            task = find_task_in_command_remove(raw_command)
            remove_item_from_todo_list(task)
            #DOVRSIT OVO 





         # ODE NASTAVIT DODAVAT UVJETE A GORE DEFINIRAT VISE FUNKCIJA KOJE IZVRSAVAJU POSLOVE-----------------------------------------------------------
      else:
         print(f"{bot_name}: I do not understand...")     
           
# Runnaj main      
if __name__ == "__main__":
    main()