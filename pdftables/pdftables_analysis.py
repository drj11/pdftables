#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-20
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

"""
Analysis and visualisation library for pdftables
"""


import pdftables as pt
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable



FilterOptions = ['LTPage','LTTextBoxHorizontal','LTFigure','LTLine','LTRect','LTImage','LTTextLineHorizontal','LTCurve', 'LTChar', 'LTAnon']
Colours       = ['black' ,'green'              ,'black'   ,'red'   ,'red'   ,'black'  ,'blue'                ,'red'    , 'red'   , 'White']

ColourTable = dict(zip(FilterOptions, Colours))

LEFT = 0
TOP = 3
RIGHT = 2
BOTTOM = 1


def plotpage(d):
#def plotpage(BoxList,xhistleft,xhistright,yhisttop,yhistbottom,xComb,yComb):
#    global ColourTable
    """This is from pdftables"""
    #columnProjectionThreshold = threshold_above(columnProjection,columnThreshold)
    #colDispHeight = max(columnProjection.values())*0.8
    #columnProj = dict(zip(columnProjectionThreshold, [colDispHeight]*len(columnProjectionThreshold)))
    """End display only code"""

    """This is from pdftables"""
    #rowProjectionThreshold = threshold_above(rowProjection,rowThreshold)
    # rowDispHeight = max(rowProjection.values())*0.8
    # rowProj = dict(zip(rowProjectionThreshold, [rowDispHeight]*len(rowProjectionThreshold)))
    """End display only code"""

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.axis('equal')
    for boxstruct in d.box_list:
        box = boxstruct.bbox
        thiscolour = ColourTable[boxstruct.classname]
        ax1.plot([box[0],box[2],box[2],box[0],box[0]],[box[1],box[1],box[3],box[3],box[1]],color = thiscolour )

    # fig.suptitle(title, fontsize=15)

    divider = make_axes_locatable(ax1)
    axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=ax1)
    axHisty = divider.append_axes("left", 1.2, pad=0.1, sharey=ax1)

    plt.setp(ax1.get_yticklabels(),visible=False)

    axHistx.plot(map(float,d.top_plot.keys()),map(float,d.top_plot.values()), color = 'red')
    #axHistx.scatter(map(float,xhistright.keys()),map(float,xhistright.values()), color = 'red')
    axHisty.plot(map(float,d.left_plot.values()),map(float,d.left_plot.keys()), color = 'red')
    #axHisty.scatter(map(float,yhistbottom.values()),map(float,yhistbottom.keys()), color = 'red')
    #fig.suptitle('%s : Page %d' % (SelectedPDF,pagenumber), fontsize=15)
    # plt.draw()

    if d.y_comb:
        miny = min(d.y_comb)
        maxy = max(d.y_comb)

        for x in d.x_comb:
            ax1.plot([x,x],[miny,maxy],color = "black")
            #axHistx.plot([x,x],[0,35],color = "black")
            axHistx.scatter(x,0,color = "black")

    if d.x_comb:
        #minx = min([box.left for box in d.BoxList])
        #maxx = max([box.right for box in d.BoxList])
        minx = min(d.x_comb)
        maxx = max(d.x_comb)

        for y in d.y_comb:
            ax1.plot([minx,maxx],[y,y],color = "black")
            #axHisty.plot([0,8],[y,y],color = "black")
            axHisty.scatter(1,y,color = "black")

    plt.draw()
    plt.show(block = False)

    return fig, ax1

def plothistogram(hist):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # ax1.axis('equal')
    ax1.scatter(map(float,hist.keys()),map(float,hist.values()))
    #fig.suptitle('%s : Page %d' % (SelectedPDF,pagenumber), fontsize=15)
    plt.draw()
    return fig

def plotAllPages(fh):
    tol = 5 # This is the tolerance for histogram rounding
    doc, interpreter, device = pt.InitializePDFminer(fh)
    print SelectedPDF
    Creator = doc.info[0]['Creator']
    print "Created by: %s" % Creator
    #flt = 'LTTextLineHorizontal'
    flt = ['LTPage','LTTextLineHorizontal']
    for i,page in enumerate(doc.get_pages()):
        # page = next(doc.get_pages())

        interpreter.process_page(page)
    # receive the LTPage object for the page.
        layout = device.get_result()
        BoxList, ElementCount = pt.getbboxes(layout)

        ModalHeight = pt.calcModalHeight(BoxList)
        # index 0 = left, 1 = top, 2 = right, 3 = bottom
        xhistleft = pt.histogramFromBoxList(BoxList,flt,LEFT,tol)
        xhistright = pt.histogramFromBoxList(BoxList,flt,RIGHT,tol)
        yhisttop = pt.histogramFromBoxList(BoxList,flt,TOP,tol)
        yhistbottom = pt.histogramFromBoxList(BoxList,flt,BOTTOM,tol)

        title = "%s : page %d" %(SelectedPDF,i+1)
        plotpage(BoxList,xhistleft,xhistright,yhisttop, yhistbottom, title,flt)
        print "Page %d" % (i+1), ElementCount
        print "Modal character height: %d" % ModalHeight
        # plothistogram(xhist)
        # plothistogram(yhist)
        plt.show()

    return BoxList
