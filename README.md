# MoviePosterGenerator

This script creates posters from a movie file. To do this it takes the average color of a frame every second.
This data can then be processed in the three functions create_line_poster, create_wave_poster and create_average poster.
Just play around with the variables until you get a result you like, since every color set needs some different constants.
The runtime of the analyse_frames() method is polynomial in regards to the image resolution, so try to use low-res movies for faster results with the same results.

Examples from the movie the End of Evangelion:

<img src="/Examples/barcode.png" width="50%" height="50%">
<img src="/Examples/wave.png" width="50%" height="50%">
<img src="/Examples/average.png" width="50%" height="50%">
