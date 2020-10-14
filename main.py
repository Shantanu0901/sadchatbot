import wikipediaapi
wiki_wiki = wikipediaapi.Wikipedia('en')
import urllib.request
import sys
import time
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
import tkinter
from tkinter import *

# Function and List Definitions

answer_A = ["A", "a", "A.", "a."]
answer_B = ["B", "b", "B.", "b."]
answer_C = ["C", "c", "C.", "c."]
yes = ["Y", "y", "Yes", "yes", "YES"]
no = ["N", "n", "No", "no", "NO"]


# Return Name 
def returnname():
    print("What's your name? (Enter your name only)(If want to exit the room enter 'exit', if want some help enter 'help')")
    global name
    name = input(">>> ")
    if name == "exit":
        print("Goodbye!")
        sys.exit()
    elif name == "help":
        instructions()
    elif name == "return":
        mainmenu()
    else:
        print("Wow! Cool name,", name, "!")


# Instructions
def instructions():
    #Prints instructions on how to operate the chatbot.
    print(
        "I am a robot with a wide feature set!\nFirst off, I returned your name at the beginning of the program!\nFurthermore, I can:"
    )
    print(
        "- Find Information about something you want to learn"
    )
    print("- Just simple CHAT")
    print("- Play an Interactive Story")
    print(
        'Operating me is very simple, from the main menu, type the number that corresponds to the action.\nThen, you can follow the on-screen prompts to tell me what to do.\n If you want to return to the main menu from any action, all you have to say is {"return"} at any time.\nAfter you finish your action, I will automatically prompt you to return to the main menu as well.\nIf you want me to stop running, then just type "exit" from anywhere in the program.\n Don\'t worry if you can\'t memorize all of this.\n Just type "help" if you can\'t remember, and I will give you these instructions again.'
    )


# Main Menu
def main_menu_validate(x):
    #Input validation for mainmenu() function
    if x == "1":
        wikichat()
    elif x == "2":
        chatterbot()
    elif x == "3":
        intro()
    elif x == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif x == "help":
        instructions()
        time.sleep(1)
        mainmenu()
    elif x == "return":
        mainmenu()
    else:
        return False

# Main Function
def mainmenu():  
    #Asks the user what they want to do and redirects accordingly
    print(
        "\nWhat do you want to do? Type the number that corresponds to the action."
    )
    time.sleep(1)
    print(
        "\n\n[1] --> Find Information about something you want to learn"
    )
    print("[2] --> Retrieve the current weather")
    print("[3] --> Play an Interactive story mode")
    x = input(">>> Input Your Choice, My Friend --> ")
    main_menu_result = main_menu_validate(x)
    if main_menu_result == False:
        while main_menu_result == False:
            print("My Friend, Please enter a valid input")
            x = input(">>> here --> ")
            main_menu_result = main_menu_validate(x)


#Chatbot code
def chatterbot():
    intents = json.loads(open('intents.json').read())
    words = pickle.load(open('words.pkl','rb'))
    classes = pickle.load(open('classes.pkl','rb'))


    def clean_up_sentence(sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

    def bow(sentence, words, show_details=True):
            # tokenize the pattern
        sentence_words = clean_up_sentence(sentence)
        # bag of words - matrix of N words, vocabulary matrix
        bag = [0]*len(words)
        for s in sentence_words:
            for i,w in enumerate(words):
                if w == s:
                # assign 1 if current word is in the vocabulary position
                    bag[i] = 1
                    if show_details:
                        print ("found in bag: %s" % w)
        return(np.array(bag))

    def predict_class(sentence, model):
    # filter out predictions below a threshold
        p = bow(sentence, words,show_details=False)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        return return_list

    def getResponse(ints, intents_json):
        tag = ints[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if(i['tag']== tag):
                result = random.choice(i['responses'])
                break
        return result

    def chatbot_response(msg):
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)
        return res

    def send():
        msg = EntryBox.get("1.0",'end-1c').strip()
        EntryBox.delete("0.0",END)

        if msg != '':
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, "You: " + msg + '\n\n')
            ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

            res = chatbot_response(msg)
            ChatLog.insert(END, "Bot: " + res + '\n\n')

            ChatLog.config(state=DISABLED)
            ChatLog.yview(END)


    base = Tk()
    base.title("Hello")
    base.geometry("400x500")
    base.resizable(width=FALSE, height=FALSE)

    #Create Chat window
    ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)

    ChatLog.config(state=DISABLED)

    #Bind scrollbar to Chat window
    scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
    ChatLog['yscrollcommand'] = scrollbar.set

    #Create Button to send message
    SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                    command= send )

    #Create the box to enter message
    EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
    #EntryBox.bind("<Return>", send)


    #Place all components on the screen
    scrollbar.place(x=376,y=6, height=386)
    ChatLog.place(x=6,y=6, height=386, width=370)
    EntryBox.place(x=128, y=401, height=90, width=265)
    SendButton.place(x=6, y=401, height=90)
    
    base.mainloop()


# Return to Main Menu
#Returns to the mainmenu() function from the wikichat() function
def wiki_return():
    print("Do you want to return to the main menu?")
    x = input(">>> ")
    if x == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif x == "help":
        instructions()
    elif x == "return":
        mainmenu()
    elif x in yes:
        mainmenu()
    elif x in no:
        wikichat()
    else:
        print("Please enter a valid input (yes or no):")
        x = input(">>> ")
        wiki_validation_result = wiki_return(x)


#Returns to the mainmenu() function from the weatherchat() function



#Returns to the mainmenu() function from the intro() function
def story_return():
    print("Do you want to return to the main menu?")
    x = input(">>> ")
    if x == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif x == "help":
        instructions()
    elif x == "return":
        mainmenu()
    elif x in yes:
        mainmenu()
    elif x in no:
        intro()
    else:
        print("PLease enter a valid input (yes or no)")
        x = input(">>> ")
        story_validation_result = story_return(x)


# Retrieve Summary of Wikipedia Article
def wiki_article_validate(articlename):
    #Validates the input for the wikichat() function
    page_py = wiki_wiki.page(articlename)
    if page_py.exists() == True:
        print("Here you go,", name, ":")
        print("Page - Title: %s" % page_py.title)  
        print("Page - Summary: %s" % page_py.summary)
    else:
        return False
    return page_py

# Main Function
def wikichat():  
    #Prompts the user to enter the name of a Wikipedia article to retrieve the summary of said article.
    print("What do you want to learn about?")
    x = input(">>> ")
    if x == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif x == "help":
        instructions()
    elif x == "return":
        mainmenu()
    else:
        wiki_validation_result = wiki_article_validate(x)
        if wiki_validation_result == False:
            while wiki_validation_result == False:
                print("Please enter a valid input, My Friend:")
                x = input(">>> ")
                wiki_validation_result = wiki_article_validate(x)
        wiki_return()


#Retrieve Local Weather


# Interactive Story
# -- Grabbing Objects --
flower = 0

# -- Cutting down on Duplication --
required = ("\nUse only A, B, or C\n")

# Story Functions

def intro():
    #Prompts the user to choose whether the character is a boy or a girl.
    print("Would you like to be start?")
    print("yes or no")
    choice = input(">>> ")
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    else:
        if choice in yes:
            boystory()
            return True
        elif choice in no:
            mainmenu()
        else:
            print("Please enter a valid input:")
            story_return()


# The Male Version for the Story 
def boystory_validate(choice):
    #Validates the input for the boystory() function
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    elif choice in answer_A:
        option_rockb()
    elif choice in answer_B:
        print("\nWelp, that was quick.", "\n\n", name, "died.")
        story_return()
    elif choice in answer_C:
        option_runb()
    else:
        print(required)
        return False


def boystory():
    #Introduction to the male interactive story.
    print(
        name,
        ", you are on a vacation with all your friends. You are alone right now because you wanted to take a midnight stroll. THUNK! Something hits you, on the head. Your eyes close and you slumps down. Head spinning and fighting the pain on the head, you manage to wake up. You are in a big dark cave. There are bones all over the place. Now, you are trying to find the exit. Atlast you see a light shining from somewhere. You are now following the light until you reaches this dark room. You hears a groan behind you. Slowly turning, you see a big green ogre with a club. You are scared to death.",
        name, ", What will you will do?")
    time.sleep(1)
    print("A. will grab a nearby rock and throw it at the ogre\n B. will lie down and wait to be mauled\nC. will run")
    choice = input(">>> ")
    boystory_validation_result = boystory_validate(choice)
    if boystory_validation_result == False:
        while boystory_validation_result == False:
            choice = input(">>> ")
            boystory_validation_result = boystory_validate(choice)


# Options for the Male Interactive Story.
def option_rockb_validate(choice):
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    elif choice in answer_A:
        option_runb()
    elif choice in answer_B:
        print(
            "\n You decided to throw another rock, as if the first rock thrown did much damage. The rock flew well over the ogre's head. You missed.\n\n You are died.")
        story_return()
    else:
        print("Use only A or B.")
        return False


def option_rockb():
    print(
        "\nThe ogre is stunned, but regains control. He begins running towards",
        name, ", again. What will you do?")
    time.sleep(1)
    print("A. will run\nB. will throw another rock")
    choice = input(">>> ")
    option_rockb_validation_result = option_rockb_validate(choice)
    if option_rockb_validation_result == False:
        while option_rockb_validation_result == False:
            choice = input(">>> ")
            option_rockb_validation_result = option_rockb_validate(choice)


def option_runb_validate(choice):
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    elif choice in answer_A:
        print("Your are easily spotted.\n\nYou are died.")
        story_return()
    elif choice in answer_B:
        print("\nYou are no match for an ogre.\n\nYou are died.")
        story_return()
    elif choice in answer_C:
        option_run2b()
    else:
        print(required)
        return False


def option_runb():
    print(
        "\nYou run as quickly as possible, but the ogre's speed is too great.",
        name, ", What will you will do?")
    time.sleep(1)
    print("A. will hide behind a boulder\nB. will fight\nC. will run")
    choice = input(">>> ")
    option_runb_validate_result = option_runb_validate(choice)
    if option_runb_validate_result == False:
        while option_runb_validate_result == False:
            choice = input(">>> ")
            option_runb_validate_result = option_runb_validate(choice)


def option_run2b_validate(choice):
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    elif choice in answer_A:
        print(
            "\nYou take the left trusting the arrow. You ends up in a dead end. You look behind to run, but the ogre is there waiting for you. You realizes that the arrow is a trap. The ogre grabs his club and kills him.\n\nYou are died.")
        story_return()
    elif choice in answer_B:
        option_rightb()
    else:
        print("Use only A or B")
        return False


def option_run2b():
    print(
        "\nYou run as fast as you can. You endup in a fork. Now, you can either take a left or a right. You noticed a battered sign with burnt edges. It is point towards the left. You can hear the ogre coming behind you and you has to make a decision fast. Does you choose left or right?")
    time.sleep(1)
    print("A. Left\nB. Right")
    choice = input('>>> ')
    option_run2b_validation_result = option_run2b_validate(choice)
    if option_run2b_validation_result == False:
        while option_run2b_validation_result == False:
            choice = input(">>> ")
            option_run2b_validation_result = option_run2b_validate(choice)


def option_rightb_validate(choice):
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    elif choice in answer_A:
        print(
            "\n You jump off the cliff into the mud. It is a soft landing. You try to get out but you can't, and you slowly starts sinking into the mud. Realizing that it sinking mud, you screams until you sinks fully\n\nYou are died.")
        story_return()
    elif choice in answer_B:
        option_townb()
    elif choice in answer_C:
        print(
            "\nyou take the left into the Cave Entrance. No clue why you would go back into the cave, but you does. You comes back to the fork."
        )
        option_run2b()
    else:
        print(required)
        return False


def option_rightb():
    print(
        "\nYour own instincts tell you that the arrow is a trap so you takes a right. You run as fast as you can. You come to a cliff. When you looks down from the cliff you see a pool of mud. You look to your right and there are steps leading toward a town. On your left is another entrance into the cave. What will",
        name, ", you do?")
    time.sleep(1)
    print("A. you will jump off the cliff into the pool of mud\nB. you run towards the Town\nC. you take the entrance back into the cave")
    choice = input('>>> ')
    option_rightb_validation_result = option_rightb_validate(choice)
    if option_rightb_validation_result == False:
        while option_rightb_validation_result == False:
            choice = input(">>> ")
            option_rightb_validation_result = option_rightb_validate(choice)


def option_townb_validate(choice):
    if choice == "exit":
        print("Thank you! Goodbye!")
        sys.exit()
    elif choice == "help":
        instructions()
    elif choice == "return":
        mainmenu()
    if choice in yes:
        flower = 1
    elif choice not in yes:
        flower = 0
    print(
        "\nyou hear its heavy footsteps and gets ready for the impending ogre. What will you do?")
    time.sleep(1)
    if flower > 0:
        print(
            "\nYou quickly held out the purple flower, somehow hoping it will stop the ogre. It does! The ogre was looking for love.",
            "\n\nThis got weird, but you survived!")
        story_return()
    elif choice in no:  # If the user didn't grab the flower
        print("\nMaybe you should have picked up the flower."
              "\n\nYou are died.")
        story_return()
    else:
        print("Please enter a valid input:")
        return False


def option_townb():
    print(
        "\nWhile frantically running towards the town, you notice a rusted sword lying in the mud. you reache down to grab it, but misses. You try to calm your heavy breathing as you hide behind a boulder, waiting for the ogre to come charging around the corner. You notice a purple flower near your foot. Will you pick it up? Y/N")
    choice = input(">>> ")
    option_townb_validation_result = option_townb_validate(choice)
    if option_townb_validation_result == False:
        while option_townb_validation_result == False:
            choice = input(">>> ")
            option_townb_validation_result = option_townb_validate(choice)

# Main Code
print(
    "Hello, my name is Python SADChatbot!\nConsider me as your friend or the helpful tool."
)
time.sleep(1)
returnname()
instructions()
print("Now, let's get started!")
mainmenu()
