from PIL import Image
from PIL import ImageDraw
import urllib2 as urllib
import io
import os
import shutil
import common_data as cd

CHAMP_ICONS_ROOT_FOLDER = "app/static/img/champ_icons"
FOLDER_FORMAT = CHAMP_ICONS_ROOT_FOLDER + os.sep + "{0}"
CHAMP_ICONS_FOLDER = FOLDER_FORMAT.format("latest")

def main():
    if not os.path.exists(CHAMP_ICONS_ROOT_FOLDER):
        os.makedirs(CHAMP_ICONS_ROOT_FOLDER)

    versions = [name for name in os.listdir(CHAMP_ICONS_ROOT_FOLDER)]
    if str(cd.CHAMPS_BY_ID["version"]) not in versions:
        for v in versions:
            shutil.rmtree(FOLDER_FORMAT.format(v))
            
        os.makedirs(FOLDER_FORMAT.format(cd.CHAMPS_BY_ID["version"]))
            
        for id, name in cd.CHAMPS_BY_ID["keys"].iteritems():
            dir = 'http://ddragon.leagueoflegends.com/cdn/{v}/img/champion/{n}.png'.format(
                v=cd.CHAMPS_BY_ID["version"], n=name)
                
            fd = urllib.urlopen(dir)
            image_file = io.BytesIO(fd.read())
            im = Image.open(image_file)

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
                draw.ellipse(circle, outline=c)
                filename = FOLDER_FORMAT.format("{v}{sep}{n}_{color}.png")
                im.save(filename.format(
                    v=cd.CHAMPS_BY_ID["version"], sep=os.sep, n=name, color=c))
                    
        shutil.copytree(FOLDER_FORMAT.format(cd.CHAMPS_BY_ID["version"]),
                        CHAMP_ICONS_FOLDER)
                    
main()