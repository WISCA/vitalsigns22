"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, vecSize=2048):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Vector Max Angle',   # will show up in GRC
            in_sig=[(np.complex64, vecSize)],
            out_sig=[np.float32]
        )

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        for vectorIndex in range(len(input_items[0])):
            maxValue = (180/np.pi)*np.angle(np.max(input_items[0][vectorIndex]))
            output_items[0][vectorIndex] = maxValue
        return len(output_items[0])
