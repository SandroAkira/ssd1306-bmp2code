# ssd1306-bmp2code
BMP 8/16/24/32 bits to C Code converter. Tested on SSD1306 library. (Tested on Wemos + OLED Shield 64x48 - 0.66 inch)

Example output from [Example file](https://raw.githubusercontent.com/SandroAkira/ssd1306-bmp2code/master/loading.bmp)

```
/* res:  12 x 12   */
PROGMEM const char loading [] = {
   0x00,  0x00,  0x00,  0x00,  0x07,  0x0E,  0x09,  0x09,  0x91,  0x08,  0x61,  0x0C,  0x61,  0x0C,  0x91,  0x08,
   0x09,  0x09,  0x07,  0x0E,  0x00,  0x00,  0x00,  0x00,
}
```

To display the image in the SD1306 OLED just use like the following command.

```
#include <SSD1306.h>                                      // OLED library by Daniel Eichhorn
SSD1306  display(0x3c, D2, D1);                           // Initialize OLED Shield 0.66in
...
display.drawFastImage(86, 18, 12, 12, loading);  
...
```

This will position the image on the top right corner of the OLED Screen.
