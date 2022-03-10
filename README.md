# MoviePosterGenerator

This script creates posters from a movie file. To do this it takes the average color of a frame every second. For this you can either use sample_avg_color() or full_avg_color(), where sampling is much quicker and returns a color within ±0.5% of the actual average (for a sample rate of 0.01).

This data can then be processed in the three functions create_line_poster, create_wave_poster and create_average_poster.

The runtime of the analyse_frames() function is in O(number_of_frames\*frame_height\*frame_width), so try to use low-res movies for faster results.

To install necessary packages run:

```
pip3 install -r requirements.txt
```
Can either be used with GUI or CLI arguments, example:

```
python3 movie_poster_generator.py --gui='false' --video_path='movie.mkv' --randomized_selection='false'
```

Examples from the movie "The End of Evangelion":

Output of create_average_poster():

<img src="/Examples/average.png" width="50%" height="50%">
Output of create_wave_poster():

<img src="/Examples/wave.png" width="50%" height="50%">
Output of create_line_poster():

<img src="/Examples/barcode.png" width="50%" height="50%">
