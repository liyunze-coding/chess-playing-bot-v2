# chess puzzle solving bot

### version 2.0

---

install requirements via

`pip install -r requirements.txt`

in terminal / command prompt.

---

## How to use

1. Before we start:

-    Size of template images in `piece_templates` must not be larger than the squares in the board.
-    I suggest turning off highlight on check + moving animations so the script can work properly

2. Use Paint or other software to find the correct coordinates

     ![screenshot1](example.jpg)

     ![screenshot2](example2.jpg)

3. Input the coordinates into the variable `board_bbox` such as
   `board_bbox = (555, 200, 1276, 921)`

4. Run the script, go to lichess and put your mouse on the left side of the screen (not top left or else it will trigger PyAutoGUI's FAIL SAFE)

---

## License & copyright

© Ryan Lee In Zer, student

Licensed under the [MIT License](LICENSE).
