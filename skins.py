import sys
import random

skins = {'malphite': ['Shamrock', 'Coral Reef', 'Marble', 'Obsidian',
                      'Glacial', 'Mecha'],
         'warwick': ['Big Bad', 'Tundra Hunter', 'Feral', 'Firefang',
                     'Hyena'],
         'singed': ['Hextech', 'Surfer', 'Mad Scientist', 'Augmented']
         }

def get_skin_list(champ_name):
    # Returns list of all available skins, including Normal
    # TODO: Is there a cleaner way to do this? IE less than 3 lines?
    choices = skins[champ_name.lower()]
    choices.append('Normal')
    return choices

def pick_skin(champ_name):
    choices = get_skin_list(champ_name)
    skin = random.choice(choices)
    return skin

if __name__== "__main__":
    if len(sys.argv) < 2:
        champ = random.choice(skins.keys())
        skin = pick_skin(champ)
        print("{0} {1}".format(skin, champ.capitalize()))
    else:
        champ_name = sys.argv[1]
        skin = pick_skin(champ_name)
        print(skin)
