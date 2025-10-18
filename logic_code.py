import random

color = ['Yellow','Red','Blue','Green','Black']

wild_cards = ['0','+4']

cards = ['1','2','3','4','5','6','7','8','9','0','+2']

player_cards = []
main_deck=[]
current_card=[]
initial_deck=[]


def bold(text):
  return "\\033[1m" + text + "\\033[0m"

for x in range(0,7):
    r = random.randint(0,4)
    s = random.randint(0,10)
    f = random.randint(0,1) 
    if r == 4:
        main_deck.append(wild_cards[f]+color[4])
    else:
        main_deck.append(cards[s]+color[r])



for z in range(0,108):
    r = random.randint(0,3)
    s = random.randint(0,9)
    initial_deck.append(cards[s]+color[r])


current_card = random.choice(initial_deck)



while True:
    print(main_deck)
    print('current_card : ',current_card)
    user_choice = int(input("Enter the no of card you want to keep : "))
    if user_choice > len(main_deck):
        print("Value is not in range")
        pass
    else:

        if current_card[1:] == main_deck[user_choice-1][1:]:
            current_card = main_deck[user_choice-1]
            main_deck.remove(main_deck[user_choice-1])
        else:    
            print("Invalid card selected")




