# Games-Captures-Organizer

The sole purpose of this python code is to help me order my XboxGameBar screenshots into folder.

As I am taking screenshot in 4K HDR, it tends to give me big files (10/20MB per file), one in PNG, one in JXR (HDR support).

My folder was starting to lag a lot just to load previews/order file by date so I decided to order all of that into folders and subfolders

The resulting folder structure is the following :
	- OUTPUT_FOLDER
		  - GAME_NAME
          - PNG
          - JXR
          - Conv
         
As you may have spotted, the folder structure is quite easy, the Conv folder is a folder that output JXR converted to JXR using a custom exe (hdrfix.exe). 
It give better result than the PNG files created by default by the XboxGameBar
