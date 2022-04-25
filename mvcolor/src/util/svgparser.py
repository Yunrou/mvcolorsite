from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, Close, parse_path
import os
import numpy as np
import numpy.linalg as LA
from xml.dom import minidom

svgfolder = os.path.join("../../media", "screenshot")

def parse_style(s: str):
    style_strings = s.split('; ')
    style = dict()
    for style_string in style_strings:
        ss = style_string.split(": ")
        if ss[1] == 'none': 
            style.update({ss[0]: None})
        else:
            style.update({ss[0]: ss[1]})
    return style

def extract_symmetric(path_strings):
    '''
    Return: diameter
    '''
    for d, style in path_strings:
        path_d = parse_path(d)
        path_style = parse_style(style)
        if 'stroke' not in path_style.keys() and path_style['fill'] == None: continue
        
        for e in path_d:
            if isinstance(e, Arc):
                return  2*e.radius.real

def extract_elongate(path_strings):
    '''
    e.g. barplot
    Return: shortest and longest
    '''
    shortest = np.inf
    longest = 0
    
    for d, style in path_strings:
        
        path_d = parse_path(d)
        path_style = parse_style(style)
        if 'stroke' not in path_style.keys() and path_style['fill'] == None: continue
            
        
        for e in path_d:
            if isinstance(e, Line):
                start = np.array([e.start.real, e.start.imag])
                end   = np.array([e.end.real, e.end.imag])
            
                length = LA.norm(start-end, 2)
                if length == 0: continue
                
                shortest = min(length, shortest)
                longest  = max(length, longest)
                
    return shortest, longest

def extract_asymmetric(path_strings):
    '''
    e.g. lineplot
    Return: thickness
    '''
    for d, style in path_strings:
        path_d = parse_path(d)
        path_style = parse_style(style)
        if 'stroke' not in path_style.keys() and path_style['fill'] == None: continue
        
        return float(path_style['stroke-width'])

def svgparser(marktype, svgfile):
    # Read SVG file
    filename = os.path.join(svgfolder, svgfile)
    doc = minidom.parse(filename)  # parseString also exists
    path_strings = [(path.getAttribute('d'), path.getAttribute('style')[:-1]) for path
                    in doc.getElementsByTagName('path')]

    doc.unlink()
    if marktype in ('circle', 'point'):
        return extract_symmetric(path_strings)
    elif marktype in ('bar'):
        return extract_elongate(path_strings)
    elif marktype in ('line'):
        return extract_asymmetric(path_strings)