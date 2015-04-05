from PIL import Image
from PIL import ImageDraw
import os
import shutil

CHAMP_ICONS_ROOT_FOLDER = "images/champ_icons"
FOLDER_FORMAT = CHAMP_ICONS_ROOT_FOLDER + os.sep + "{0}"
CHAMP_ICONS_FOLDER = FOLDER_FORMAT.format("latest")

def main():
    # TODO: Get static champion data and for every champ do this
    # Possibly have a methodology to automatically handle updated images referring to the version
    rw = riotwatcher()
    champs = rw.get_champ_list(data_by_id=True)

    versions = [name for name in os.listdir(CHAMP_ICONS_ROOT_FOLDER) if os.path.isdir(name)]
    if champs["version"] not in versions:
        for v in versions:
            shutil.rmtree(FOLDER_FORMAT.format(v))
            
        for id, name in champs["keys"].iteritems():
            dir = 'http://ddragon.leagueoflegends.com/cdn/{v}/img/champion/{n}.png'.format(
                v=champs["version"], n=name)
            im = Image.open(dir)

            new_size = 20, 20
            im.thumbnail(new_size)

            transparent_area = (0, 0, new_size)
            circle = (1, 1, new_size[0] - 2, new_size[1] - 2)

            mask=Image.new('L', im.size, color=255)
            draw=ImageDraw.Draw(mask) 
            draw.rectangle(transparent_area, fill=0)
            draw.ellipse(circle, fill=255)
            im.putalpha(mask)
            draw=ImageDraw.Draw(im)
            
            colors = ["red", "blue"]
            for c in colors:
                draw.ellipse(circle, outline="red")
                im.save('example_data/champs/{n}_{color}.png'.format(
                    n=name, color=c))
                    
    shutil.copytree(FOLDER_FORMAT.format(champs["version"]),
                    CHAMP_ICONS_FOLDER)