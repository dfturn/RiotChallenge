# OBSOLETE.
Demo is no longer running.

# Map Control Analysis
My submission for the Riot Developer challenge is a sort of replay system utilizing the timeline data from
match data retrieved from the Riot API. This is more of a concept application to explore the potential of
this timeline data to visualize and analyze map and vision control. There are several limitations in the
timeline data, some of which are intentionally left out. We only have player position data once per
minute, though position data is also provided for some major events like champion kills. Ward positions are
intentionally not provided, and so we attempt to extrapolate additional data based on the player positions
we're provided.

## Demo
The demo can be seen here: http://flask-phoclabian.rhcloud.com
The default visualization is a randomly selected URF game which was found using the api-challenge-1.4 endpoint.
There is also support for selecting the latest match found through this endpoint, but since this endpoint is
no longer functional now that URF isn't running, we are forced to use a static game. However, it is also possible
to search for a new game. This can be done manually with a match ID, or by typing in a summoner name (only on the NA
region currently). If a summoner name is typed in, it will display the visualization for their last ranked match.

## Challenges
As described above, there are several challenges in this type of visualization based on the data provided. Since we
only have position data once per minute in the worst case, we used an A-Star search algorithm to extrapolate position
data between every known location. This was done to make the "replay" more realistic so that players wouldn't constantly
run through walls. Also, since the goal is to estimate ward positions based on these estimated player positions
(admittedly a lofty goal given the scarcity of data), this provides a more accurate estimate, assuming the players
generally take the optimal route from point to point. Using these estimated positions, we estimate the ward positions.
To use this to visualize map control, we used a convex hull composed of towers and active wards. Optimally we would
use a visualization technique which allowed finer granularity (since obviously with a ward in enemy jungle doesn't
directly imply control of the river in between), but it was quickly seen that the ward position estimation is not
accurate enough to make these more advanced visualizations useful.

## Future Work
There are some more techniques which could be used to somewhat improve the ward position estimation, such as
using bush locations as a higher probability location for wards to be placed, but it simply is not enough. Of course
this is intentional on Riot's part, as they've stated they do not want this information available. And as mentioned
in the Challenges section, there are some other visualization techniques which could be used to more accurately
describe the vision control based on our points.

## End Goal
In the end, I do not want a tool like this to be used against other specific players. I envision a map control tool
like this one to assist a player in their own (or their team's) deficiencies in map control. By examining their team's
map control at various points in the game, they would be able to more quickly pinpoint bad habits, such as 
overextending, not clearing enough enemy vision, not preparing vision control around neutral objectives, and more.
To accomplish something like this, it might be possible to allow additional information to players for their own games.
By doing this, they could take advantage of the additional information to improve themselves, while making it more
difficult to take advantage of this data to exploit tendencies of specific enemy summoners.

## Technologies Used
* Python
* Flask
* MongoDB
* d3 Javascript library
