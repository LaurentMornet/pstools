import os
import subprocess
import numpy as np

class Rect:
    def __init__(self, x, y, dx, dy):
        self.x, self.y, self.dx, self.dy = x, y, dx, dy
    def output(self, output):
        output.write('newpath\n')
        output.write('{} {} moveto\n'.format(self.x, self.y))
        output.write('{} 0 rlineto\n'.format(self.dx))
        output.write('0 {} rlineto\n'.format(self.dy))
        output.write('{} 0 rlineto\n'.format(-self.dx))
        output.write('closepath stroke\n')

class Poly:
    def __init__(self, coords, close=True):
        self.coords, self.close = coords, close
    def output(self, output):
        output.write('newpath\n')
        output.write('{} {} moveto\n'.format(self.coords[0][0], self.coords[0][1]))
        for coords in self.coords[1:]:
            output.write('{} {} lineto\n'.format(coords[0], coords[1]))
        if self.close:
            output.write('closepath\n')
        output.write('stroke\n')

class Line:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
    def output(self, output):
        output.write('newpath\n')
        output.write('{} {} moveto\n'.format(self.x0, self.y0))
        output.write('{} {} lineto\n'.format(self.x1, self.y1))
        output.write('stroke\n')

class Arc:
    def __init__(self, cx, cy, rx, ry, a0, a1):
        self.cx, self.cy, self.rx, self.ry, self.a0, self.a1 = cx, cy, rx, ry, a0, a1
    def output(self, output):
        output.write('newpath\n')
        output.write('1 {} scale\n'.format(self.ry / self.rx))
        output.write('{} {} {} {} {} arc\n'.format(self.cx, self.cy * self.rx / self.ry, self.rx, self.a0, self.a1))
        output.write('1 {} scale\n'.format(self.rx / self.ry))
        output.write('stroke\n')

class Text:
    def __init__(self, x, y, text):
        self.x, self.y, self.text = x, y, text
    def output(self, output):
        output.write('{} {} moveto\n'.format(self.x, self.y))
        output.write('1 -1 scale\n')
        output.write('0 0 1 setrgbcolor\n')
        output.write('({}) show\n'.format(self.text))
        output.write('0 0 0 setrgbcolor\n')
        output.write('1 -1 scale\n')

class Color:
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b
    def output(self, output):
        output.write('{} {} {} setrgbcolor\n'.format(self.r, self.g, self.b))

class Rotate:
    def __init__(self, angle):
        self.angle = angle
    def output(self, output):
        output.write('{} rotate\n'.format(self.angle))

class Translate:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def output(self, output):
        output.write('{} {} translate\n'.format(self.x, self.y))

def entraxe(module, z1, z2 = None):
    if z2 is None:
        return (module * z1) / 2 + 1.25 * module
    else:
        return module * (z1 + z2) / 2

class Cremaillere:
    def __init__(self, pspage, x, y, h, l, m, horizontal=True):
        self.pspage, self.x, self.y, self.h, self.l, self.m, self.horizontal = pspage, x, y, h, l, m, horizontal
    def output(self, output):
        # parametres engrenage
        ha = self.m
        hf = 1.25 * self.m
        alpha = np.radians(20.)
        l0 = (self.m * np.pi) / 2

        # preparation
        z_count = int(self.l / l0)
        z_count = int((z_count + 1) / 2) if z_count % 2 == 1 else int(z_count / 2)
        l_util = z_count * l0 * 2 - l0
        x = self.x + (self.l- l_util) / 2
        y = self.y
        for i in range(z_count):
            self.pspage.add_poly([
                [x, y],
                [x, y - hf],
                [x + ha * np.cos(alpha - np.pi/2), (y - hf) - ha],
                [x + l0 - ha * np.cos(alpha - np.pi/2), (y - hf) - ha],
                [x + l0, y - hf],
                [x + l0, y],
                [x + 2 * l0, y] if i < z_count - 1 else [x + l0, y]
            ], False)
            if i < z_count - 1:
                self.pspage.add_line(x + 3 * l0 / 2 - 1, y - 1, x + 3 * l0 / 2 + 1, y + 1)
                self.pspage.add_line(x + 3 * l0 / 2 + 1, y - 1, x + 3 * l0 / 2 - 1, y + 1)
            x += 2 * l0
        self.pspage.add_poly([
            [self.x + (self.l - l_util) / 2, self.y],
            [self.x, self.y],
            [self.x, self.y + self.h],
            [self.x + self.l, self.y + self.h],
            [self.x + self.l, self.y],
            [self.x + (self.l + l_util) / 2, self.y]
        ], False)
        self.pspage.set_color(.6, .6, .6)
        self.pspage.add_line(self.x, self.y + 10, self.x + self.l, self.y + 10)
        self.pspage.set_color(.0, .0, .0)

class Engrenage:
    def __init__(self, pspage, cx, cy, m, z, initial_rotation=0.):
        self.pspage, self.cx, self.cy, self.m, self.z, self.initial_rotation = pspage, cx, cy, m, z, initial_rotation
    def output(self, output):
        # parametres engrenage
        d0 = self.m * self.z
        da = d0 + 2 * self.m
        df = d0 - 2.5 * self.m
        ha = self.m
        alpha = np.radians(20.)
        rf = df / 2                                         # rayon de fond
        beta = (2 * np.pi) / self.z                         # angle entre 2 dents
        l0 = (d0 * np.pi) / self.z / 2               # largeur de la dent
        largeur_a = l0 - 2 * (ha * np.sin(alpha))    # largeur de tete
        t = np.arctan2(l0 / 2, d0 / 2)               # angle intermédiaire
        # points
        m = [(df / 2) * np.cos(-t), (d0 / 2) * np.sin(-t)]
        n = [(d0 / 2) * np.cos(-t), (d0 / 2) * np.sin(-t)]
        o = [d0 / 2 + ha, -largeur_a / 2]
        p = [d0 / 2 + ha, largeur_a / 2]
        q = [(d0 / 2) * np.cos(+t), (d0 / 2) * np.sin(+t)]
        r = [(df / 2) * np.cos(+t), (d0 / 2) * np.sin(+t)]
        t2 = np.arctan2(m[1], m[0])                          # angle intermédiaire 2
        s = [(df / 2) * np.cos(beta + t2), (df / 2) * np.sin(beta + t2)]
        u = [(m[0] + r[0])/2, (m[1] + r[1])/2]
        # preparation:
        self.pspage.translate(self.cx, self.cy)
        self.pspage.rotate(self.initial_rotation)
        # cerclage
        self.pspage.set_color(.8, .8, .8)
        self.pspage.add_arc(0, 0, d0 / 2, d0 / 2, 0, 360)
        self.pspage.add_arc(0, 0, df / 2, df / 2, 0, 360)
        self.pspage.add_arc(0, 0, da / 2, da / 2, 0, 360)
        self.pspage.set_color(0, 0, 0)
        # centre
        self.pspage.add_line(0, -10, 0, 10)
        self.pspage.add_line(-10, 0, 10, 0)
        for i in range(self.z):
            self.pspage.add_poly([
                m, n, o, p, q, r, s
            ], False)
            self.pspage.add_line(u[0]-1, u[1]-1, u[0]+1, u[1]+1)
            self.pspage.add_line(u[0]+1, u[1]-1, u[0]-1, u[1]+1)
            self.pspage.rotate(np.degrees(beta))
        # finalisation
        self.pspage.rotate(-self.initial_rotation)
        self.pspage.translate(-self.cx, -self.cy)

class PsPage:
    
    def __init__(self):
        self.shapes = []

    def output(self, filepath):
        with open(filepath, 'w') as output:
            output.write('0 842 translate\n')
            output.write('2.84 -2.84 scale\n')
            output.write('0.1 setlinewidth\n')
            output.write('0.9 setgray\n')

            for i in range(0, 2100):
                if i % 10 == 0:
                    output.write('0.7 setgray\n')
                output.write('newpath\n')
                output.write('{} 0 moveto\n'.format(i))
                output.write('{} 2970 lineto\n'.format(i))
                output.write('stroke\n')
                if i % 10 == 0:
                    output.write('0.9 setgray\n')
            for i in range(0, 2970):
                if i % 10 == 0:
                    output.write('0.7 setgray\n')
                output.write('newpath\n')
                output.write('0 {} moveto\n'.format(i))
                output.write('2100 {} lineto\n'.format(i))
                output.write('stroke\n')
                if i % 10 == 0:
                    output.write('0.9 setgray\n')
            output.write('.0 setgray\n')
            # font
            output.write('/Courrier findfont 3 scalefont setfont\n')
            for shape in self.shapes:
                shape.output(output)

        gscommand='gswin64c.exe -o{} -sDEVICE=pdfwrite -c .setpdfwrite <</NeverEmbed []>> setdistillerparams -f{}'.format(filepath.replace('.ps', '.pdf'), filepath)
        print(gscommand)
        subprocess.call(gscommand.split())
        os.remove('{}'.format(filepath))

    def add_rect(self, x, y, dx, dy):
        self.shapes.append(Rect(x, y, dx, dy))

    def add_poly(self, coords, close=True):
        self.shapes.append(Poly(coords, close))

    def add_line(self, x0, y0, x1, y1):
        self.shapes.append(Line(x0, y0, x1, y1))

    def add_arc(self, cx, cy, rx, ry, a0, a1):
        self.shapes.append(Arc(cx, cy, rx, ry, a0, a1))

    def add_text(self, x, y, text):
        self.shapes.append(Text(x, y, text))

    def rotate(self, angle):
        self.shapes.append(Rotate(angle))

    def translate(self, x, y):
        self.shapes.append(Translate(x, y))

    def add_engrenage(self, cx, cy, m, z, initial_rotation=0.):
        self.shapes.append(Engrenage(self, cx, cy, m, z, initial_rotation))

    def add_cremaillere(self, cx, cy, h, l, m, horizontal=True):
        self.shapes.append(Cremaillere(self, cx, cy, h, l, m, horizontal))

    def set_color(self, r, g, b):
        self.shapes.append(Color(r, g, b))

if __name__ == "__main__":
    p = PsPage()
    p.output("empty.ps")
