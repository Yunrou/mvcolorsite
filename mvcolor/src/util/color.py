import numpy as np
from numpy import ndarray
import cv2

from .ciede2000 import ciede2000

class Color():
    '''
    classmethods
    '''
    # --------------------------------------------------------------------------
    @classmethod
    def hex2rgb(cls, _hex: str):
        return np.array([int(_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)])
    # --------------------------------------------------------------------------
    @classmethod
    def rgb2hex(cls, rgb: ndarray):
        return '#%02x%02x%02x' % tuple(rgb)
    # --------------------------------------------------------------------------
    @classmethod
    def rgb2hsv(cls, rgb: ndarray):
        '''
        Parameters
        ----------
        rgb : ndarray
              [r, g, b] where r,g,b in range [0, 255].
        
        Results
        -------
        hsv : ndarray
              [h, s, v] where h in range [0, 360] and s,v in range [0, 100].
        '''

        rgb = np.divide(rgb, 255)
        [r, g, b] = rgb
        
        delta = rgb.max() - rgb.min()

        v = rgb.max()*100
        if delta == 0:
            return [0, 0, int(v)]
        
        if rgb.max() == r:
            h = 60 * (((g - b) / delta) % 6)
        elif rgb.max() == g:
            h = 60 * (((b - r) / delta) + 2.0)
        else:
            h = 60 * (((r - g) / delta) + 4.0)
        s = 100 * (delta / rgb.max())
        
        return np.array([h, s, v])
    # --------------------------------------------------------------------------
    @classmethod
    def hsv2rgb(cls, hsv: ndarray):
        (h, s, v) = hsv[0]/60, hsv[1]/100, hsv[2]/100
        f = h - np.floor(h)
        m = v*(1-s)
        n = v*(1-(s*f))
        k = v*(1-(s*(1-f)))

        rgb = (0, 0, 0)
        if h < 1:
            rgb = (v, k, m)
        elif 1 <= h < 2:
            rgb = (n, v, m)
        elif 2 <= h < 3:
            rgb = (m, v, k)
        elif 3 <= h < 4:
            rgb = (m, n, v)
        elif 4 <= h < 5:
            rgb = (k, m, v)
        elif 5 <= h < 6:
            rgb = (v, m, n)

        # convert rgb from range [0, 1] to [0, 255]
        rgb = np.rint(np.multiply(rgb,255))

        R = int(max(0, min(rgb[0], 255)))
        G = int(max(0, min(rgb[1], 255)))
        B = int(max(0, min(rgb[2], 255)))

        return np.array([R, G, B])
    # --------------------------------------------------------------------------
    @classmethod
    def rgb2lab(cls, rgb: ndarray):
        '''
        Under illuminant D65

        Parameters
        ----------
        rgb : ndarray
              [r, g, b] where r,g,b in range [0, 255].

        Results
        -------
        lab : ndarray
              [l, a, b] where l in range [0, 100] and a, b in range [−110, +110].
        ''' 

        # delta = 6/29
        # delta^3 = 0.008856451679035631, delta^2/3 = 7.787037037037036, 16/116 = 0.13793103448275862
        f = lambda t: np.power(t,1/3) if t > 0.008856451679035631 else t*7.787037037037036 + 0.13793103448275862 # (4/29)
        g = lambda u: u/12.92 if u <= 0.04045 else np.power((u+0.055)/1.055, 2.4) 
        
        rgblinear = np.apply_along_axis(g, axis=0, arr=np.array([np.divide(rgb, 255)]))[0]

        A = np.array([[0.4124564, 0.3575761, 0.1804375],
                      [0.2126729, 0.7151522, 0.0721750], 
                      [0.0193339, 0.1191920, 0.9503041]])

        # sRGB to CIE XYZ
        XYZ = np.dot(A, rgblinear)
        
        # D65 white
        XYZn = np.array([0.950489, 1.0, 1.088840])

        tn = np.divide(XYZ, XYZn)
        
        # CIE XYZ to CIE Lab
        L = 116*f(tn[1])-16
        a = 500*(f(tn[0])-f(tn[1]))
        b = 200*(f(tn[1])-f(tn[2]))
        
        # return Lab
        return np.array([L, a, b])
    # --------------------------------------------------------------------------
    @classmethod
    def lab2rgb(cls, lab: ndarray):
        '''
        Under illuminant D65

        Parameters
        ----------
        lab : ndarray
              [l, a, b] where l in range [0, 100] and a, b in range [−110, +110].

        Results
        -------
        rgb : ndarray
              [r, g, b] where r,g,b in range [0, 255].
        ''' 
        (L, a, b) = lab

        # D65 white
        XYZn = np.array([0.950489, 1.0, 1.088840])

        # CIE Lab to CIE XYZ
        fy = (L + 16) / 116
        fx = fy + a/500
        fz = fy - b/200

        delta = 0.20689655172413793 #(6/29) (3*delta**2) = 0.12841854934601665

        f = lambda t: np.power(t, 3) if t > delta else (t-0.13793103448275862)*0.12841854934601665
        XYZ = np.multiply(XYZn, np.apply_along_axis(f, axis=0, arr=np.array([[fx, fy, fz]]))[0])

        # CIE XYZ to sRGB
        A = np.array([[ 3.2404542, -1.5371385, -0.4985314],
                      [-0.9692660,  1.8760108,  0.0415560],
                      [ 0.0556434, -0.2040259,  1.0572252]])

        rgb = np.dot(A, XYZ)
        
        # gamma correction
        g = lambda u: u*12.92 if u <= 0.0031308 else (1.055 * np.power(u,5/12) - 0.055) 
        rgb = np.apply_along_axis(g, axis=0, arr=np.array([rgb]))[0]

        # convert rgb from range [0, 1] to [0, 255]
        rgb = np.rint(np.multiply(rgb,255))

        R = int(max(0, min(rgb[0], 255)))
        G = int(max(0, min(rgb[1], 255)))
        B = int(max(0, min(rgb[2], 255)))

        return np.array([R, G, B])
    # --------------------------------------------------------------------------
    @classmethod
    def hex2lab(cls, _hex: str):
        return cls.rgb2lab(cls.hex2rgb(_hex))
    # --------------------------------------------------------------------------
    @classmethod
    def lab2hex(cls, lab: ndarray):
        return cls.rgb2hex(cls.lab2rgb(lab))
    # --------------------------------------------------------------------------
    @classmethod
    def hex2hsv(cls, _hex: str):
        return cls.rgb2hsv(cls.hex2rgb(_hex))
    # --------------------------------------------------------------------------
    @classmethod
    def hsv2hex(cls, hsv: ndarray):
        return cls.rgb2hex(cls.hsv2rgb(hsv))
    # --------------------------------------------------------------------------
    @classmethod
    def ciede2000(cls, lab1: ndarray, lab2: ndarray):
        return ciede2000(lab1[0], lab1[1], lab1[2], lab2[0], lab2[1], lab2[2])
    # --------------------------------------------------------------------------
    @classmethod
    def auto_gradient(cls, hexcolor, n_colors):
        '''
        ref: https://github.com/gka/palettes/blob/master/src/PalettePreview.svelte
        '''
        if n_colors == 1:
            return [hexcolor]
        lab = cls.hex2lab(hexcolor)
        l_range = 100 * (0.8 - 1/n_colors)
        l_step = l_range / (n_colors - 1)
        l_start = (100 - l_range) * 0.5
        _range = np.arange(l_start, l_start+n_colors*l_step, l_step)
        offset = 9999
        for i in range(n_colors):
            diff = lab[0] - _range[i]
            if np.abs(diff) < np.abs(offset):
                offset = diff
        return [cls.lab2hex([l+offset, lab[1], lab[2]]) for l in _range][::-1]
    # --------------------------------------------------------------------------
    @classmethod
    def interpolation(cls, control_points: tuple, n: int):
        '''
        Parameters
        ----------
        control_points : tuple of hexcolor

        n : integer
            number of interpolations between two control points
              
        Results
        -------
        colors : list of hexcolor
        '''
        colors = [control_points[0]]
        
        for i in range(len(control_points)-1):
            
            lab1 = cls.hex2lab(control_points[i])
            lab2 = cls.hex2lab(control_points[i+1])
            
            
            for j in range(1, n+1):
                color = lab1 + (lab2-lab1)*(j/(n+1))
                colors.append(cls.lab2hex(color))
            colors.append(control_points[i+1])
            
        return colors
    # --------------------------------------------------------------------------
    @classmethod
    def find_control_colors(cls, mainhex):
        mainlab   = cls.hex2lab(mainhex)
        L, a, b = mainlab
        brightlab = mainlab + (np.array([100, 0.01, -0.01]) - mainlab) * (95-L)/(100-L)
        darklab   = np.array([40, a, b])
        brighthex = cls.lab2hex(brightlab)
        darkhex   = cls.lab2hex(darklab)
        return brighthex, darkhex 
    # --------------------------------------------------------------------------
    @classmethod
    def hsv2colorterm(cls, hsvcolor):
        h, s, v = hsvcolor
        if s < 30:
            return 'black and white'
        if h == 0: return 'black and white'
        elif h > 345 or h <= 15: return 'red'
        elif 15 < h <= 45: return 'orange and brown'
        elif 45 < h <= 75: return 'yellow'
        elif 75 < h <= 105: return 'lime'
        elif 105 < h <= 135: return 'green'
        elif 135 < h <= 165: return 'turqoise'
        elif 165 < h <= 195: return 'cyan'
        elif 195 < h <= 225: return 'cobalt'
        elif 225 < h <= 255: return 'blue'
        elif 255 < h <= 285: return 'violet'
        elif 285 < h <= 315: return 'magentas'
        elif 315 < h <= 345: return 'crimson'
    # --------------------------------------------------------------------------
    @classmethod
    def n_distinct(cls, colorscheme):
        '''
        Number of distinct colors
        '''
        distinctcolors = {'red': [], 'orange and brown': [], 'yellow': [], 'lime': [], 
                          'green': [], 'turqoise': [], 'cyan': [], 'cobalt': [], 
                          'blue': [], 'violet': [], 'magentas': [], 'crimson': [], 
                          'black and white': []}
        for hexcolor in colorscheme:
            hsvcolor = cls.hex2hsv(hexcolor)
            colorterm = cls.hsv2colorterm(hsvcolor)
            distinctcolors[colorterm].append(hexcolor)
        n = 0
        for k, v in distinctcolors.items():
            if v: n += 1
        return n
    # --------------------------------------------------------------------------
    @classmethod
    def scheme_extension(cls, colorscheme, max_ramp_size=5):
        '''
        Parameters
        ----------
        colorscheme : list
        
        max_ramp_size : integer

        Results
        -------
        all_colors : ndarray
                     key1 is colorhue, key2 is ramp size (#colorhue x max_ramp_size)
        '''
        all_colors = np.zeros(shape=(len(colorscheme), max_ramp_size), dtype=object)
        i = 0
        for colorhue in colorscheme:
            for j in range(1, max_ramp_size+1):
                colorlab = cls.hex2lab(colorhue)
                if j == 1:
                    all_colors[i, 0] = np.array([colorlab])
                else:
                    all_colors[i, j-1] = cls.ramp_generation(colorlab, j, output_type='Lab')
            i += 1
        return all_colors
    # --------------------------------------------------------------------------
    @classmethod
    def ramp_generation(cls, mainlab, n, output_type='Lab'):
        brightness_lookup = {2: 80, 3: 80, 4: 85, 5: 85}
        darkness_lookup = {2: 45, 3: 45, 4: 45, 5: 45}

        L, a, b = mainlab[0], mainlab[1], mainlab[2]
        bright_l, dark_l = brightness_lookup[n], darkness_lookup[n]
        brightlab = mainlab + (np.array([100, 0.01, -0.01])-mainlab) * (bright_l-L)/(100-L)
        darklab   = mainlab + (np.array([100, a, b])-mainlab) * (dark_l-L)/(100-L)

        if output_type == 'Lab':
            if n == 2:
                if L-(dark_l+bright_l)/2 > 0: # bright side
                    return np.array([darklab, mainlab])
                else: # dark side
                    return np.array([mainlab, brightlab])

            # color interpolation for n > 2
            order = int(round((L-dark_l)/((bright_l-dark_l)/(n-1))))
            colors = np.zeros((n,3))
            colors[order] = mainlab

            for i in range(n):
                if i == order: continue
                elif i-order < 0: # dark side
                    colors[i,:] = mainlab + (darklab-mainlab)*(order-i)/order
                else: # bright side
                    colors[i,:] = mainlab + (brightlab-mainlab)*(i-order)/(n-order-1)
            colors[colors > 90] = 90
            colors[colors < -90] = -90
            return colors

        elif output_type == 'hex':
            if n == 2:
                if L-(dark_l+bright_l)/2 > 0: # bright side
                    return np.array([cls.lab2hex(darklab), mainhex])
                else: # dark side
                    return np.array([mainhex, cls.lab2hex(brightlab)])

            # color interpolation for n > 2
            order = int(round((L-dark_l)/((bright_l-dark_l)/(n-1))))
            colors = np.zeros((n,))
            colors[order] = mainhex
            
            for i in range(n):
                if i == order: continue
                if i-order < 0: # dark side
                    colorlab = mainlab + (darklab-mainlab)*(order-i)/order
                    colors[i] = cls.lab2hex(colorlab)
                else: # bright side
                    colorlab = mainlab + (brightlab-mainlab)*(i-order)/(n-order-1)
                    colors[i] = cls.lab2hex(colorlab)

            return colors
    # --------------------------------------------------------------------------
    @classmethod
    def ND(cls, p, size):
        '''
        Notice difference
        '''
        pass
    # --------------------------------------------------------------------------
    @classmethod
    def ND_by_mark(cls, marktype, p, _size):
        if marktype == 'symmetric':
            diameter = _size[0]
            return ND_symmetric(p, diameter)
        elif marktype == 'elongate':
            shortest_edge, longest_edge = _size
            return ND_elongate(p, shortest_edge, longest_edge)
        elif marktype == 'asymmetric':
            thickness = _size[0]
            return ND_assymmetric(p, thickness)
    # --------------------------------------------------------------------------
    @classmethod
    def ND_symmetric(cls, p, diameter):
        # ND_L = p / (0.0937 - 0.0085/diameter)
        # ND_a = p / (0.0775 - 0.0121/diameter)
        # ND_b = p / (0.0611 - 0.0096/diameter)
        w0 = np.array([0.0937, 0.0775, 0.0611])
        w1 = np.array([0.0085, 0.0121, 0.0096])
        ND_Lab = p / (w0 - w1/diameter)
        return ND_Lab

    # --------------------------------------------------------------------------
    @classmethod
    def ND_elongate(cls, p, shortest_edge, longest_edge):
        # ND_L = p / (0.1056 - 0.0061/shortest_edge - 0.0134/longest_edge)
        # ND_a = p / (0.0881 - 0.0067/shortest_edge - 0.0117/longest_edge)
        # ND_b = p / (0.0719 - 0.0059/shortest_edge - 0.0105/longest_edge)
        w0 = np.array([0.1056, 0.0881, 0.0719])
        w1 = np.array([0.0061, 0.0067, 0.0059])
        w2 = np.array([0.0134, 0.0117, 0.0105])
        ND_Lab = p / (w0 - w1/shortest_edge - w2/longest_edge)
        return ND_Lab
    # --------------------------------------------------------------------------
    @classmethod
    def ND_assymmetric(cls, p, thickness):
        # ND_L = p / (0.0742 - 0.0023/thickness)
        # ND_a = p / (0.0623 - 0.0015/thickness)
        # ND_b = p / (0.0425 - 0.0009/thickness)
        w0 = np.array([0.0742, 0.0623, 0.0425])
        w1 = np.array([0.0023, 0.0015, 0.0009])
        ND_Lab = p / (w0 - w1/thickness)
        return ND_Lab
    # --------------------------------------------------------------------------
    @classmethod
    def colordifference(cls, lab1:ndarray, lab2:ndarray, ND_Lab:ndarray):
        return np.sqrt(np.square((lab1-lab2)/ND_Lab).sum())