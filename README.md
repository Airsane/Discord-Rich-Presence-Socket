# Kodi Addon - Discord Rich Presence Socket

## Preview
This addon is a slightly modified Discord Rich Presence addon for Kodi. I have added a socket to make this addon work for example on android tv kodi. 

Episode Paused  | Episode Playing| Movie Playing
----------------|----------------|--------------
![Screenshot_1](https://i.imgur.com/Yd5h8jx.png)|![Screenshot_2](https://i.imgur.com/e5bGekT.png)|![Screenshot_3](https://i.imgur.com/06y8aoP.png)

## Info
Media types:
- [x] Episodes
- [x] Movies
- [ ] Other types of video
- [ ] Music
- [ ] Games

Features:
- [x] Display what is playing
- [ ] Allow user to edit what is displayed and where (partialy done)
- [ ] Image updating depending on media

## Download and Installation

You download this repository and modify the SERVER variable in service.discord.richpresencesocket\default.py to the IP of the device where you have the kodi.
![Screenshot_4](https://i.imgur.com/uozRqmN.png)
You then make the same change in client\main.py. You then zip the service.discord.richpresencesocket folder and install it on kodi. 
Once you turn on kodi and then the client kodi should communicate with the client and set up discord rich presence.

## Bug submitting and features
You can open an issue or message me on Discord (Airsane#777)

# Acknowledgements
Thanks to...
- [@Hiumee](https://github.com/Hiumee) for making Discord Rich Presence for kodi. Without him i wouldnt make this modification.