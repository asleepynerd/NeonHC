# uhh neon hackclub submission

## files

flow.py - idk some kind of animation i made

gifconv.py - Converts GIF animations into Python code that can be run on the matrix. Supports optional frame limit argument to control output size

gifstream.py - Streams a GIF from a URL and displays it on the matrix

output.py - The generated Python code containing frame data and display logic for running animations on the matrix

xbox.py - Example animation file showing the Xbox logo (broken bc the site to run it doesnt work above 8 frames)

asc.gif and asc.py - testing gif conversion

thistest-test.gif and output.py - testing gif conversion

## how to use

Convert a GIF to matrix code:

```
python gifconv.py input.gif output.py [frame_limit]
```

show the floy animation:

```
python flow.py
```

stream a gif from a url:

```
take the contents of gifstream.py and run it on https://neon.hackclub.dev/editor
```

Run any generated animation:
take the contents of output.py and run it on https://neon.hackclub.dev/editor
