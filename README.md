# game-blink
A tiny emergent behavior toy.

The inspiration for this project is [here](https://www.youtube.com/watch?v=ix66tQ93bdU).

Music by [Ulrike](ulrike.bandcamp.com), [@ulrikemusic on twitter](https://twitter.com/ulrikemusic)
and [@ulrikemusic on instagram](https://www.instagram.com/ulrikemusic/?hl=en).


## Development Instructions

To run locally, create a virtual environment and install briefcase (included in
`requirements.txt`). Primary development was done in Python 3.8.


To run in development mode:

    briefcase dev

## Packaging instructions

To package, if you haven't done so, first run:

    briefcase create

This will create a build directory for your platform.

If you make changes to the code, you must run

    briefcase update

To create a distributable package run:

    briefcase package