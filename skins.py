import sys
import random

skins = {'malphite': ['Shamrock', 'Coral Reef', 'Marble', 'Obsidian',
                      'Glacial', 'Mecha'],
         'warwick': ['Big Bad', 'Tundra Hunter', 'Feral', 'Firefang',
                     'Hyena'],
         'singed': ['Hextech', 'Surfer', 'Mad Scientist', 'Augmented']
         }
    
if len(sys.argv) < 2:
    # TODO: random skin amongst all champs
    pass
else:
    champ_name = sys.argv[1]
    choices = skins[champ_name.lower()]
    # TODO: Is there a cleaner way to do this? IE less than 3 lines?
    choices.append('Normal')
    skin = random.choice(choices)
    print(skin)

if __name__== "__main__":
    pass
