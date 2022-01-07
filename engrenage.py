import numpy as np
from pstools import *
'''

      +--+          +--+            ^    ^      -- diametre de tete da
     /    \        /    \           | ha |
    +      +      +      +   -------x    | h    -- diametre primitif d
    |      |      |      |          | hf |
----+------+------+------+----  ----v    v      -- diametre de fond df
        pas (°)
    <------------->

d = m.Z
da = d + 2.m
df = d - 2.5.m
ha = m
hf = 1.25.m
h = 2.25.m
pas = pi.m
epaisseur = (pi.m)/2

'''

if __name__ == '__main__':
    pspage = PsPage()
    module = 5
    pspage.add_engrenage(50, 60, module, 15, initial_rotation = 36.)
    pspage.add_engrenage(50 + entraxe(module, 15, 20), 60, module, 20)
    pspage.add_text(50 + entraxe(module, 15, 20) - 15, 45, "entraxe = " + str(entraxe(module, 15, 20)))
    pspage.add_cremaillere(11, 75 + entraxe(module, 20), 25, 190, module)
    pspage.add_text(50 + entraxe(module, 15, 20) - 15, 80 + entraxe(module, 20), "entraxe = " + str(entraxe(module, 20)))
    pspage.add_text(40, 80 + entraxe(module, 20), "entraxe = " + str(entraxe(module, 15)))

    pspage.add_engrenage(50, 210, module, 15)
    pspage.add_engrenage(148, 220, module, 20)

    pspage.output('pspage.ps')
