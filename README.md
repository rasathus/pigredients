# Pi'gredients

Pi'gredients aims to provide a source of 'ingredients' for all your Raspberry Pi related projects.  There are a number of existing projects that focus on providing easy to implement access to the Raspberry Pi's GPIO, i2c and SPI I/O, but this is still relativly low level.

Pi'gredients aims to provide a higher level, component based interface for Raspberry Pi programming.
  This allows you to get started right away, without having to understand the underlying communications between the Raspberry Pi's bus, and the component you're working with.  

Adafruit have already done some very useful work over at their repo, with implementations for a number of their products, and products they sell.

https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

We are hoping to go beyond this, and provide robust implementations for a diverse range of components, available from a variety of vendors, with consistent and familiar interfaces.  Additionally, you'll find many of the component implementations come with usage examples, and even fritzing diagrams to show you how to correctly lay out the circuit used in the example. 


## Getting Started 

We have layed out the repository in the following structure ...

    .
    ├── ics           # Contains all the Integrate Circuit modules.
    ├── displays      # Contains all the Display driving modules.
    ├── sensors       # Contains all our sensing modules.
    └── examples      # Example implementations for all modules.

Its still early days, and we've yet to evaluate our packaging options.  Currently you have two options ...

* clone the repository into an folder, and create a softlink to allow its import into your python environment. eg. 'sudo ln -s ~/src/pigredients/ /usr/lib/python2.7/dist-packages/pigredients'
* clone the repository directly into your python dist-packages path. like so ... 'git clone https://github.com/rasathus/pigredients.git /usr/lib/python2.7/dist-packages/pigredients'

## Naming Convention Notes

Please note that due to some component identifiers starting with numbers eg. 74HC595, some modules are prefixed with a relevant prefix, 'ic' for integrated circuits, 'sen' for sensors, 'disp' for displays etc..  This aleviates issues with imports, and allows the use of all standard conventions when importing modules.


