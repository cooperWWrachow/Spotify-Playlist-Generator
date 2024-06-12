<h1>Spotify Color Playlist Generator</h1>

I worked with Spotify's API and Python's Spotipy library to develop an application that builds a 
unique playlist based on user preferences. The way it works is... the user specifies what artists they 
want to be in the playlist. Then, the program finds those artists and displays all their albums for the 
user to choose from. All the user has to do is select their favorite albums (as many as they want), and then they input 
one of the color options to define the "sound" of their new playlist. Each color is assigned to specific bounds
within the different sound aspects of individual songs. If the song succeeds the aspects of the color, then it is placed 
into the playlist.

This application is mobile friendly and works with all screen dimensions due to its mediaqueries.

<h1>Demos</h1>

First, a video will be shown of a simple creation of a playlist consisting of four popular artists. While the demo
is sped up for the sake of your time, once the user reaches the success page, they will be redirected back to the beginning
after 10 seconds. The final result is showcasing the way playlist covers (the color) and titles (a string
of the first letter in each artist's name) are seen.

![ezgif com-resize (2)](https://github.com/cooperWWrachow/Spotify-Playlist-Generator/assets/135729317/d57ea6a2-864c-469b-abab-a0898177968b)

<br>

![image](https://github.com/cooperWWrachow/Spotify-Playlist-Generator/assets/135729317/e8e7c999-e4de-4d55-ab2d-e8ef4028353b)




Another set of videos are shown below that show the functionality of scoll features in case of a large amount of artists
requested by the user.

![ezgif com-resize](https://github.com/cooperWWrachow/Spotify-Playlist-Generator/assets/135729317/797ff04e-a0fa-48ef-8108-d8eb70b18054)


Lastly, I wanted to show how the user is redirected in case of an error. They will be redirected to the error page 
briefly explaining the error, and then redirecting them back to the beginning after 15 seconds. [The error is generated 
by not selecting any albums from the artists. Will not make a playlist without songs.]

![ezgif com-video-to-gif-converter (1)](https://github.com/cooperWWrachow/Spotify-Playlist-Generator/assets/135729317/8c9d7fee-4610-4460-ab9c-0af525cc4942)




