#!/usr/bin/env python

"""
LUT Controls

These controls deal with Look-up table selection, histogram display and
opacity interactive selection

* LutPanel: A dumb widget for displaying a LUT

* LutCtrl: LUT selection widget
Use the spin or drop down selector to choose a new LUT. An event is
generated.

* HistogramCtrl: Displays a histogram with LUT overlayed
This widget displays a histogram and allows min/max selection.
Right click displays a list of LUTs. Double click inside the selection
expands the selection to min/max. Clicking and dragging the left or
right handle modifies the selection. Clicking and dragging inside both
handles simultaneously.

* OpacityCtrl: Opacity function definition
Opacity is combined with LUT selection to provide full interactive
RGBA selection. This can then be used with VTK or any other module that
requires RGBA Look-up tables.
- A look-up table is displayed on top of a checker background image.
  Dragging the nodes up increases opacity, down decreases. Depending on
  opacity, the background may or may not be visible through the look-up
  table image.
- Double click adds or removes a node.
- At the moment, right click displays an add/remove node menu
- The +/= or - keys can also be used.


Original LUT data located on http://rsb.info.nih.gov/ij/download/luts/
Rasband, W.S., ImageJ, U. S. National Institutes of Health, Bethesda,
Maryland, USA, http://rsb.info.nih.gov/ij/, 1997-2005.

The latest version of this file is stored in my google code repository:
    http://code.google.com/p/ezwidgets/

Copyright (c) 2007 Egor Zindy <ezindy@gmail.com>

Released under the MIT licence.
"""
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

__author__ = "Egor Zindy <ezindy@gmail.com>"
__copyright__ = "Copyright (c) 2007 Egor Zindy"
__license__ = "MIT"
__version__ = "1.1"
__date= "2010-01-10"
__status__ = "Production"

import wx
import wx.lib.newevent
import numpy
import math

RangeEvent, EVT_RANGE = wx.lib.newevent.NewEvent()
UpdateEvent, EVT_UPDATE = wx.lib.newevent.NewEvent()
LutEvent, EVT_LUT = wx.lib.newevent.NewEvent()
SubmitEvent, EVT_SUBMIT = wx.lib.newevent.NewEvent()

#styles for LutCtrl
LUT_CHOICE = 1
LUT_SPIN = 2

#alternate d black and d white and return he x,y image
def make_checker(w,h,d,col1=1,col2=0):
    if w == 0 or h == 0:
        return None

    nx = int(math.ceil(w / 2. / d))
    ny = int(math.ceil(h / 2. / d))

    a1 = numpy.zeros((d,d),numpy.uint8)+col1
    a2 = numpy.zeros((d,d),numpy.uint8)+col2

    row1 = numpy.hstack([a1,a2]*nx)
    row2 = numpy.hstack([a2,a1]*nx)

    image = numpy.vstack([row1,row2]*ny)
    return image[:h,:w]

class LutPanel(wx.Panel):
    def __init__(self, parent,LutData,lut_index=0,size=(-1,24)):
        wx.Panel.__init__(self, parent, -1,size=size,style=wx.SUNKEN_BORDER)

        self.LutData = LutData

        if lut_index >= self.LutData.get_count():
            lut_index = 0

        self.SetLutIndex(lut_index,redraw=0)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.sb=wx.StaticBitmap(self, -1)
        self.box.Add(self.sb,1,wx.EXPAND)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.box.Layout()
        self.SetSizer(self.box)

    def OnSize(self,event):
        self.Redraw()

    def Redraw(self):
        w,h=self.GetClientSize()
        if self.img is None or w<=0 or h<=0:
            return

        self.sb.SetToolTip(wx.ToolTip(self.LutData._names[self.lut_index]+" (%d)" % self.lut_index))
        self.sb.SetBitmap(self.img.Scale(w,h).ConvertToBitmap())
        self.Refresh()

    def GetLutCount(self):
        return len(self.LutData._names)

    def GetLutIndex(self):
        return self.lut_index

    def GetLutNames(self):
        return self.LutData._names

    def GetLutName(self):
        return self.LutData.get_name(self.lut_index)

    #returns an interleaved "RGBRGBRGB..." string, 768 bytes long.
    #to convert to an array, use rgb_array = numpy.fromstring(rgb,numpy.uint8).reshape((256,3))
    def GetLut(self):
        return self.LutData.get_lut(self.lut_index)

    #returns 3 strings R,G,B 256 bytes long.
    #These are easy to convert to numpy...
    #
    #r,g,b = event.GetLutRGB()
    #r_array = numpy.fromstring(r,numpy.uint8)
    #g_array = numpy.fromstring(g,numpy.uint8)
    #b_array = numpy.fromstring(b,numpy.uint8)
    def GetLutRGB(self):
        return self.LutData.get_rgb(self.lut_index)

    #select a LUT to display
    def SetLutIndex(self,lut_index,redraw=1):
        self.lut_index=lut_index

        self.SetToolTipString(self.GetLutName())

        s=self.LutData.get_lut(lut_index)
        image = wx.EmptyImage(256,1)
        image.SetData(s)

        self.img=image

        if redraw:
            self.Redraw()

class LutCtrl(wx.Panel):
    def __init__(self, parent,LutData,lut_index=0,size=(-1,24),style=LUT_SPIN):
        wx.Panel.__init__(self, parent, -1)

        self.LutData = LutData

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.lp=LutPanel(self,LutData,lut_index,size=size)
        self.lut_index=lut_index
        self.spin = None
        self.ch = None

        #do the choice style...
        if style & LUT_CHOICE > 0:
            self.ch=wx.Choice(self, -1, size=wx.Size(90, -1), choices = self.lp.GetLutNames())
            self.ch.SetSelection(lut_index)
            self.box.Add(self.ch,0)
            self.Bind(wx.EVT_CHOICE,self.OnChoice,self.ch)

        self.box.Add(self.lp,1,wx.EXPAND)

        #do the spin style
        if style & LUT_SPIN > 0:
            height = size[1]
            self.spin = wx.SpinButton(self, -1, size=(height*.67, height), style=wx.SP_VERTICAL)
            self.spin.SetRange(0, self.lp.GetLutCount()-1)
            self.spin.SetValue(lut_index)
            self.box.Add(self.spin,0,wx.EXPAND)
            self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)

        self.box.Layout()
        self.SetSizer(self.box)

        self.GetLutCount=self.lp.GetLutCount
        self.GetLutIndex=self.lp.GetLutIndex
        self.GetLutRGB=self.lp.GetLutRGB
        self.GetLut=self.lp.GetLut
        self.GetLutName=self.lp.GetLutName

    def GetValue(self):
        return self.GetLutIndex()

    def SetValue(self,lut_index):
        self.SetLutIndex(lut_index)

    def SetLutIndex(self,lut_index,redraw=1):
        self.lp.SetLutIndex(lut_index,redraw)
        if self.ch is not None:
            self.ch.SetSelection(lut_index)

    def OnChoice(self, event):
        lut_index=self.ch.GetSelection()
        self.DoEvent(lut_index)
        self.Update(lut_index)

    def OnSpin(self, event):
        lut_index=event.GetPosition()
        self.DoEvent(lut_index)
        self.Update(lut_index)

    def DoEvent(self,lut_index):
        if lut_index!=self.lut_index:
            self.lut_index=lut_index
            self.SetLutIndex(lut_index,redraw=1)

            lut_event = LutEvent(
                    GetLut=self.GetLut,
                    GetLutCount=self.GetLutCount,
                    GetLutIndex=self.GetLutIndex,
                    GetLutRGB=self.GetLutRGB,
                    GetLutName=self.GetLutName)
            wx.PostEvent(self, lut_event)

    def Update(self,lut_index=None):
        if lut_index is None:
            lut_index = self.lut_index

        if self.spin is not None:
            self.spin.SetValue(lut_index)

        if self.ch is not None:
            self.ch.SetSelection(lut_index)

class HistogramCtrl(wx.ScrolledWindow):
    '''\brief The histogram control, a scrolled window'''

    histogram = None
    bmp_histogram = None
    img_lut = None
    img_bg = None

    buffer = None
    wx.InitAllImageHandlers()


    left_absolute_range = 0
    right_absolute_range = 255

    left_current_range = 0
    right_current_range = 255

    left_dc = 0
    right_dc = 255

    min_span = 0.01

    x_delta = 0
    y_delta = 0

    active_bar = None

    def __init__(self, parent, LutData, lut_index = 0, histogram=None,absrange=(0,255),currentrange=(0,255),minspan=0.01,size=(-1,100)):
        wx.ScrolledWindow.__init__(self, parent, -1, size=size, style=wx.SUNKEN_BORDER)

        self.LutData = LutData
        if lut_index >= LutData.get_count():
            lut_index = 0

        #set the absolute range...
        self.SetAbsoluteRange(absrange[0],absrange[1])
        self.SetCurrentRange(absrange[0],absrange[1])

        self.SetLutIndex(lut_index,redraw=0)
        self.SetHistogram(histogram)

        self.potential_bar = -1
        self.flag_clicked = 0

        self.min_span = minspan
        self.x = self.y = 0
        self.drawing = False
        self.tt = wx.ToolTip("")
        self.SetToolTip(self.tt)

        self.SetSelCursor()

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvent)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClickEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnMouseEvent)
        self.Bind(wx.EVT_RIGHT_UP,   self.OnRightUpEvent)
        self.Bind(wx.EVT_MOTION,    self.OnMouseEvent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

    def SetData(self,data,nbins=20,absrange=None,currentrange=None):
        h,b = numpy.histogram(data,nbins,absrange) #,normed=1)
        h = h.astype(numpy.float)/max(h)

        if absrange is None:
            ami = min(b)
            ama = max(b)
            absrange = (ami,ama)

        if currentrange is None:
            currentrange = absrange

        self.SetHistogram(h,absrange,currentrange)

    def SetHistogram(self,histogram=None,absrange=None,currentrange=None):
        if histogram is None or absrange is None or currentrange is None:
            return

        self.left_absolute_range = absrange[0]
        self.right_absolute_range = absrange[1]
        self.left_current_range = currentrange[0]
        self.right_current_range = currentrange[1]

        self.histogram = histogram
        self.bins = histogram

        self.MakeBgBmp()
        self.MakeHistogramBmp()
        self.UpdateDrawing()

    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def GetLeft(self):
        return self.left

    def GetRight(self):
        return self.right

    def OnSize(self, event):
        dc_size = self.GetClientSize()
        dc_w,dc_h=dc_size

        if dc_w != 0 and dc_h !=0:
            self.maxWidth = dc_w
            self.maxHeight = dc_h

            self.MakeLeftRightDC(dc_size)
            self.MakeHistogramBmp(dc_size)
            self.MakeLutBmp(dc_size)
            self.MakeBgBmp(dc_size)

            # Initialize the buffer bitmap.  No real DC is needed at this point.
            self.buffer = wx.EmptyBitmapRGBA(dc_w,dc_h,0,0,0,255)
            #dc = wx.BufferedDC(None, self.buffer)
            self.UpdateDrawing()

    def OnLeaveWindow(self,event):
        if not self.drawing:
            self.active_bar = -2
            self.potential_bar = -2
            self.UpdateDrawing()

    def OnPaint(self, event):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_CLIENT_AREA)

    def DoDrawing(self, dc, printing=False):
        dc.Clear()
        self.DrawLut(dc)
        self.DrawBars(dc)
        dc.EndDrawing()

    def MakeBgBmp(self, size=None):
        if size is None:
            w,h=self.GetClientSize()
        else:
            w,h = size

        if w == 0 or h == 0:
            return

        bg = make_checker(w,h,16,150,220)

        array = numpy.zeros( (h, w, 3),numpy.uint8)
        array[:,:,0] = bg
        array[:,:,1] = bg
        array[:,:,2] = bg

        self.img_bg = wx.EmptyImage(w,h)
        self.img_bg.SetData(array.tostring())

    def MakeLeftRightDC(self,size=None):
        if size is None:
            w,h=self.GetClientSize()
        else:
            w,h = size

        absolute_width = self.right_absolute_range - self.left_absolute_range
        current_width = self.right_current_range - self.left_current_range

        factor = w / float(absolute_width)
        self.left_dc = (self.left_current_range - self.left_absolute_range) * factor
        self.right_dc = (self.right_current_range - self.left_absolute_range) * factor

        if self.left_dc < 0:
            self.left_dc = 0

        if self.right_dc > w-1:
            self.right_dc = w-1

    def MakeHistogramBmp(self, size=None):
        #need to expand the number of points to fill the client size...
        if self.histogram is None:
            return

        if size is None:
            w,h=self.GetClientSize()
        else:
            w,h = size

        n_bins = self.histogram.shape[0]

        rect_list = numpy.zeros((n_bins,4))
        w_rect = int(float(w)/(n_bins))
        missing = w-w_rect*n_bins

        hist = self.histogram * h
        y = h
        x = 0
        for i in range(n_bins):
            w_temp = w_rect
            if missing > 0:
                w_temp+=1
                missing-=1

            rect_list[i,:]=[x,h-hist[i],w_temp,h]
            x += w_temp

        buffer = wx.EmptyBitmapRGBA(w,h,0,0,0,255)

        dc = wx.BufferedDC(None, buffer)
        dc.SetPen( wx.Pen("RED",0) )
        dc.SetBrush( wx.Brush("WHITE") )
        dc.DrawRectangleList(rect_list)
        dc.EndDrawing()

        self.bmp_histogram = buffer

    def MakeLutBmp(self, size=None):
        if size is None:
            w,h=self.GetClientSize()
        else:
            w,h = size

        s=self.LutData.get_lut(self.lut_index)
        image = wx.EmptyImage(256,1)
        image.SetData(s)

        self.img_lut = image

    def DrawHistogram(self,dc):
        bmp = self.bmp_histogram
        dc.DrawBitmap(bmp,0,0)

    def DrawBars(self,dc):
        w,h = self.GetClientSize()

        if self.flag_clicked == 1:
            if self.active_bar == 1 or self.active_bar == 0:
                pen_left = wx.Pen("RED", 2)
            else:
                pen_left = wx.Pen("BLACK", 1)

            if self.active_bar == 1 or self.active_bar == 2:
                pen_right = wx.Pen("RED", 2)
            else:
                pen_right = wx.Pen("BLACK", 1)
        else:
            if self.potential_bar == 1 or self.potential_bar == 0:
                pen_left = wx.Pen("RED", 1)
            else:
                pen_left = wx.Pen("BLACK", 1)

            if self.potential_bar == 1 or self.potential_bar == 2:
                pen_right = wx.Pen("RED", 1)
            else:
                pen_right = wx.Pen("BLACK", 1)

        dc.SetPen(pen_left)
        dc.DrawLine(self.left_dc,0, self.left_dc,h)
        dc.SetPen(pen_right)
        dc.DrawLine(self.right_dc,0, self.right_dc,h)

    def DrawLut(self,dc):
        if self.img_lut is None or self.bmp_histogram is None or self.img_bg is None:
            return

        w,h = self.GetClientSize()

        bmp = self.img_bg.ConvertToBitmap()

        if 1:
            bmp_histogram = self.bmp_histogram
            mask = wx.Mask(bmp_histogram)
            bmp.SetMask(mask)

        mdc = wx.MemoryDC()
        mdc.SelectObject(bmp)

        absolute_width = self.right_absolute_range - self.left_absolute_range
        current_width = self.right_current_range - self.left_current_range
        factor = w / float(absolute_width)
        dc_width = math.ceil(current_width * factor)

        img_scaled = self.img_lut.Scale(dc_width,h)
        mdc.DrawBitmap(img_scaled.ConvertToBitmap(),self.left_dc,0)

        dc.Blit(0,0, w,h, mdc, 0,0, wx.COPY, True)

    def DrawCheckerBoard(self,dc, box=5):
        """
        Draws a checkerboard on a wx.DC.
        Used for the Alpha channel control and the colour panels.
        """

        bmp = self.img_bg.ConvertToBitmap()
        dc.DrawBitmap(bmp,0,0)


    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        return newpos

    def OnLeftDClickEvent(self, event):
        if self.potential_bar == 1:
            mi,ma = self.GetAbsoluteRange()
            self.SetCurrentRange(mi,ma)

            #do an event...
            range_event = RangeEvent(
                    GetAbsoluteRange = self.GetAbsoluteRange,
                    GetRange = self.GetRange,
                    )
            wx.PostEvent(self, range_event)

    def OnRightUpEvent(self, event):
        coords = [self.x, self.y]
        if self.drawing:
            return

        menu = wx.Menu()
        popup = wx.NewId()
        self._popup = popup
        for i in range(self.LutData.get_count()):
            self.Bind(wx.EVT_MENU, self.OnLutMenu, id=popup+i)
            s = self.LutData._names[i]+" (%d)" % i
            menu.Append(popup+i, s)
    
        self.PopupMenu(menu, coords)
        menu.Destroy()

        lut_event = LutEvent(
                GetLut=self.GetLut,
                GetLutName=self.GetLutName)
        wx.PostEvent(self, lut_event)

    def OnMouseEvent(self, event):
        self.SetXY(event)
        coords = [self.x, self.y]
        w,h = self.GetClientSize()

        old_active = self.active_bar
        n = self.hit_bars(coords)

        if n != self.potential_bar:
            self.potential_bar = n
            self.UpdateDrawing()

        if event.Moving and not self.drawing:
            if n == 0 or n == 2:
                self.SetCursor(self._CursorSel)
            elif n == 1:
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
            else:
                self.SetCursor(wx.NullCursor)

        if event.LeftDown():
            self.SetFocus()
            if n == 0 or n == 2 or n == 1:
                self.active_bar = n
                self.flag_clicked=1
                self.CaptureMouse()
                self.drawing = True
                self.click_coords = coords
                self.UpdateDrawing()

        elif event.Dragging() and self.drawing:
            if self.flag_clicked == 1:
                self.drag_bars(coords)
                self.UpdateDrawing()

                #do an event...
                range_event = RangeEvent(
                        GetAbsoluteRange = self.GetAbsoluteRange,
                        GetRange = self.GetRange,
                        )
                wx.PostEvent(self, range_event)
                
        elif event.LeftUp() and self.drawing:
            self.ReleaseMouse()
            self.drawing = False
            self.flag_clicked = 0
            self.UpdateDrawing()

        #do the tooltip
        if self.flag_clicked == 1:
            if self.active_bar == 1:
                s = "%.2f , %.2f" % (self.left_current_range,self.right_current_range)
            else:
                factor = (self.right_absolute_range-self.left_absolute_range)
                s = "%.2f" % (factor*self.x/float(w)+self.left_absolute_range)
        else:
            factor = (self.right_absolute_range-self.left_absolute_range)
            s = "%.2f" % (factor*self.x/float(w)+self.left_absolute_range)

        self.tt.SetTip(s)

    def OnLutMenu(self,evt):
        self.SetLutIndex(evt.GetId()-self._popup,redraw=1)

    def GetAbsoluteRange(self):
        return self.left_absolute_range,self.right_absolute_range

    def GetRange(self):
        return self.left_current_range,self.right_current_range

    def UpdateDrawing(self):
        if self.buffer is not None:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            self.DoDrawing(dc)

    def SetCurrentRange(self,mi,ma,redraw=1):
        self.left_current_range = mi
        self.right_current_range = ma
        self.MakeLeftRightDC()

        if redraw:
            self.UpdateDrawing()

    def SetAbsoluteRange(self,mi,ma):
        self.left_absolute_range = mi
        self.right_absolute_range = ma

    def GetLut(self):
        return self.LutData.get_lut(self.lut_index)

    def GetLutName(self):
        return self.LutData.get_name(self.lut_index)

    def GetLutIndex(self):
        return self.lut_index

    def SetLutIndex(self,lut_index,redraw=1):
        self.lut_index=lut_index
        s=self.LutData.get_lut(lut_index)

        image = wx.EmptyImage(256,1)
        image.SetData(s)

        self.img=image
        self.MakeLutBmp()

        w,h = self.GetClientSize()
        self.buffer = wx.EmptyBitmapRGBA(w,h,0,0,0,1)
        #img = wx.EmptyImage(w,h,clear=True)
        #img.SetData("\xff\xff\xff")
        #w,h = self.GetClientSize()
        #img_scaled = img.Scale(w,h)
        #self.buffer = img_scaled.ConvertToBitmap()

        dc = wx.BufferedDC(None, self.buffer)

        if redraw:
            self.UpdateDrawing()

    def SetSelCursor(self, cur=wx.CURSOR_SIZEWE):
        """ Sets link cursor properties. """        
        self._CursorSel = wx.StockCursor(cur)


    def GetSelCursor(self):
        """ Gets the link cursor. """        
        return self._CursorSel

    #return -1, 0, 1 for no bar, left or right
    def hit_bars(self,coords):
        #hit
        hx,hy=coords

        l_hit = hx - self.left_dc
        r_hit = hx - self.right_dc

        if abs(l_hit)<3:
            n = 0
        elif abs(r_hit)<3:
            n = 2
        elif l_hit < 0:
            n = -1
        elif r_hit > 0:
            n = 3
        else:
            n = 1

        #if n < 0:
        #    self.active_bar = None
        #else:
        #    self.active_bar = n

        return n

    def drag_bars(self,coords):
        w,h = self.GetClientSize()
        if w <= 0 or self.active_bar == -1 or self.active_bar == 3:
            return

        absolute_width = self.right_absolute_range - self.left_absolute_range
        factor = float(absolute_width) / w

        if self.active_bar == 0 or self.active_bar == 2:
            #use the center...
            cx = coords[0] - self.x_delta
            cy = coords[1] - self.y_delta

            #convert cx to ...
            rx = cx * factor +self.left_absolute_range

            if self.active_bar == 0:
                if cx <=0:
                    self.left_dc = 0
                    self.left_current_range = self.left_absolute_range
                elif self.right_current_range - rx > self.min_span:
                    self.left_dc = cx
                    self.left_current_range = rx
                else:
                    self.left_dc = self.right_dc - self.min_span * w / float(absolute_width)
                    self.left_current_range = self.right_current_range - self.min_span

            elif self.active_bar == 2:
                if cx >= w:
                    self.right_dc = w-1
                    self.right_current_range = self.right_absolute_range
                elif rx - self.left_current_range > self.min_span:
                    self.right_dc = cx
                    self.right_current_range = rx
                else:
                    self.right_dc = self.left_dc + self.min_span * w / float(absolute_width)
                    self.right_current_range = self.left_current_range + self.min_span
        else:
            #how far from click?
            d = coords[0] - self.click_coords[0]
            range_dc = self.right_dc - self.left_dc
            range_current = self.right_current_range - self.left_current_range

            left_dc = self.left_dc + d
            right_dc = self.right_dc + d

            if left_dc <= 0:
                self.left_dc = 0
                self.right_dc = range_dc
                self.left_current_range = self.left_absolute_range
                self.right_current_range = self.left_absolute_range + range_current
            elif right_dc >= w:
                self.right_dc = w-1
                self.left_dc = w-1 - range_dc
                self.right_current_range = self.right_absolute_range
                self.left_current_range = self.right_absolute_range - range_current
            else:
                self.right_dc = right_dc
                self.left_dc = left_dc
                self.right_current_range = right_dc * factor + self.left_absolute_range
                self.left_current_range = left_dc * factor + self.left_absolute_range

            self.click_coords = coords

    def SetMinimumSpan(self,ms):
        self.min_span = ms


class OpacityCtrl(wx.ScrolledWindow):
    '''\brief The canvas object, a scrolled window'''

    buffer = None
    n_nodes = None
    nodes_array = None
    nodes_screen = None
    active_node = None
    node_size = 9
    x_delta = 0
    y_delta = 0
    left_range = 0
    right_range = 255
    nlpt = (.2,.5) #Non-linearity point: at 30% up, 80% of the opacity...

    def __init__(self, parent, LutData, lut_index = 0, nodes_array=None,size=(-1,100)):
        wx.ScrolledWindow.__init__(self, parent, -1, size=size, style=wx.SUNKEN_BORDER)

        self.LutData = LutData
        if lut_index >= LutData.get_count():
            lut_index = 0

        self.SetLutIndex(lut_index,redraw=0)
        self.SetNodes(nodes_array)

        self.x = self.y = 0
        self.drawing = False
        self.tt = wx.ToolTip("")
        self.SetToolTip(self.tt)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnMouseEvent)
        self.Bind(wx.EVT_RIGHT_UP,   self.OnMouseEvent)
        self.Bind(wx.EVT_MOTION,    self.OnMouseEvent)
        self.Bind(wx.EVT_LEFT_DCLICK,    self.OnMouseEvent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        self.MakeLutBmp()

    def SetNodes(self,nodes_array=None):
        w,h = self.GetClientSize()

        if nodes_array is None:
            nodes_array = self.nodes_array

        if nodes_array is None:
            n_nodes = 2
            nodes_array = numpy.zeros((n_nodes,2),numpy.float)
            nodes_array[:,0] = numpy.arange(n_nodes)/float(n_nodes-1)
            nodes_array[:,1] = 1 
            self.nodes_array = nodes_array
            self.n_nodes = n_nodes
        else:
            self.nodes_array = numpy.array(nodes_array,numpy.float)
            self.n_nodes = self.nodes_array.shape[0]

        self.CalcScreenNodes()

    def CalcScreenNodes(self):
        w,h = self.GetClientSize()
        nodes_array = self.nodes_array
        n_nodes = self.n_nodes

        nodes_screen = numpy.zeros((n_nodes,2))
        nodes_screen[:,0] = nodes_array[:,0]*float(w)
        nodes_screen[:,1] = h - nodes_array[:,1]*float(h)
        self.nodes_screen = nodes_screen

    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def OnPopupRemove(self,event):
        self.RemoveNode(self.active_node)
        self.CalcScreenNodes()
        self.MakeLutBmp()
        self.UpdateDrawing()

    def OnPopupAdd(self,event):
        l,r = self.GetLeftRight(self.x)
        self.AddNode(l,r,(self.x,self.y))
        self.CalcScreenNodes()
        self.MakeLutBmp()
        self.UpdateDrawing()

    def OnKeyDown(self,event):
        k=event.GetKeyCode()
        av = self.active_node
        coords = [self.x, self.y]

        if k == 45:
            if av!=0 and av!=self.n_nodes-1 and av is not None:
                self.RemoveNode(av)
                self.CalcScreenNodes()
                self.MakeLutBmp()
                self.UpdateDrawing()

        elif k == 61 or k == 43:
            if self.hit_node(coords)==-1:
                l,r = self.GetLeftRight(self.x)
                self.AddNode(l,r,(self.x,self.y))
                self.CalcScreenNodes()
                self.MakeLutBmp()
                self.hit_node(coords)
                self.UpdateDrawing()

        event.Skip()

    def GetActiveOpacity(self):
        return self.nodes_array[self.active_node,1]

    def GetActivePosition(self):
        return (self.right_range-self.left_range)*self.nodes_array[self.active_node,0]+self.left_range

    def GetActiveIndex(self):
        return self.active_node

    def OnLeaveWindow(self,event):
        if not self.drawing:
            #if drawing and dragging then fine, there's no problem with identifying the node
            self.active_node = None
            self.UpdateDrawing()

    def SetOpacity(self,arr):
        self.nodes_array = arr
        self.n_nodes = arr.shape[0]
        self.active_node = None
        self.CalcScreenNodes()
        self.UpdateDrawing()

    def GetOpacity(self,r=None):
        na = self.nodes_array.copy()

        if r is None:
            lr = self.left_range
            rr = self.right_range
        else:
            lr,rr = r

        t = na[:,0]
        t = (t*(rr-lr))+float(lr)

        na[:,0]=t

        return na

    def GetLeftRight(self,x):
        w,h = self.GetClientSize()
        x = x / float(w)
        for i in range(0,self.n_nodes-1):
            if x >= self.nodes_array[i,0] and x <= self.nodes_array[i+1,0]:
                break

        l = i
        r = i+1

        return l,r

    def RemoveNode(self,i):
        #On rare occasion, the node can be unselected while the menu is up.
        #This prevents the function from doing anything stupid.
        if i is None:
            return

        self.nodes_array=numpy.vstack([self.nodes_array[:i,:],self.nodes_array[i+1:,:]])
        self.n_nodes = self.nodes_array.shape[0]
        self.active_node = None

        self.DoEvent()

    def AddNode(self,l,r,pt=None):
        self.n_nodes+=1
        if pt is None:
            xnew = (self.nodes_array[l,0]+self.nodes_array[r,0])/2.
            ynew = (self.nodes_array[l,1]+self.nodes_array[r,1])/2.
        else:
            w,h = self.GetClientSize()
            x,y = pt
            xnew = float(x)/w
            ynew = 1.-float(y)/h

        self.nodes_array = numpy.vstack([self.nodes_array[:l+1,:],[xnew,ynew],self.nodes_array[r:,:]])
        self.active_node = l+1

        self.DoEvent()


    def OnSize(self, event):
        dc_size = self.GetClientSize()
        dc_w,dc_h=dc_size

        if dc_w != 0 and dc_h !=0:
            self.maxWidth = dc_w
            self.maxHeight = dc_h

            self.SetNodes()

            self.MakeLutBmp()
            self.MakeBgBmp()

            # Initialize the buffer bitmap.  No real DC is needed at this point.
            self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
            dc = wx.BufferedDC(None, self.buffer)
            self.UpdateDrawing()

    def OnPaint(self, event):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        #sys.exit()
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_CLIENT_AREA)

    def DoDrawing(self, dc, printing=False):
        self.DrawCheckerBoard(dc)
        self.DrawLut(dc)
        self.DrawNodes(dc)
        dc.EndDrawing()

    def MakeBgBmp(self):
        w,h = self.GetClientSize()
        bg = make_checker(w,h,16,150,220)

        array = numpy.zeros( (h, w, 3),numpy.uint8)
        array[:,:,0] = bg
        array[:,:,1] = bg
        array[:,:,2] = bg

        self.img_bg = wx.EmptyImage(w,h)
        self.img_bg.SetData(array.tostring())

    def MakeLutBmp(self):
        if self.nodes_array is None:
            return

        w,h = self.GetClientSize()

        s=self.LutData.get_lut(self.lut_index)
        image = wx.EmptyImage(256,1)

        image.SetData(s)

        #Original LUT data is 256x1
        ax256 = numpy.arange(256)/255.
        oi = numpy.interp(ax256,self.nodes_array[:,0],self.nodes_array[:,1]*255.)
        ois = oi.astype(numpy.uint8).tostring()
        image.SetAlphaData(ois)

        img_scaled = image.Scale(w,h)
        self.img_lut = img_scaled

    def DrawLut(self,dc):
        bmp = self.img_lut.ConvertToBitmap()
        dc.DrawBitmap(bmp,0,0)

    def DrawCheckerBoard(self,dc, box=5):
        """
        Draws a checkerboard on a wx.DC.
        Used for the Alpha channel control and the colour panels.
        """

        if 0:
            checkColour = wx.Colour(200, 200, 200)

            w,h=dc.GetSize()

            y = 0
            checkPen = wx.Pen(checkColour)
            checkBrush = wx.Brush(checkColour)

            dc.SetPen(checkPen) 
            dc.SetBrush(checkBrush)
            
            while y < h:
                x = box*((y/box)%2)
                while x < w: 
                    dc.DrawRectangle(x, y, box, box) 
                    x += box*2 
                y += box
        else:
            bmp = self.img_bg.ConvertToBitmap()
            dc.DrawBitmap(bmp,0,0)


    def DrawNodes(self,dc):
        s = self.node_size

        nodes_screen = numpy.zeros((self.n_nodes,4))
        nodes_screen[:,0] = self.nodes_screen[:,0]-s/2.
        nodes_screen[:,1] = self.nodes_screen[:,1]-s/2.
        nodes_screen[:,2] = s
        nodes_screen[:,3] = s
        brushes=[wx.TRANSPARENT_BRUSH] * self.n_nodes

        if self.active_node is not None:
            if self.drawing:
                brushes[self.active_node] = wx.Brush(wx.NamedColour('RED'),style=wx.SOLID)
            else:
                brushes[self.active_node] = wx.Brush(wx.NamedColour('WHITE'),style=wx.SOLID)

        dc.DrawRectangleList(nodes_screen,pens = wx.Pen(wx.NamedColour('BLACK'),1,style=wx.SOLID), brushes=brushes)

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen( wx.Pen("RED",1) )
        dc.DrawLines(self.nodes_screen)
        
    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        return newpos

    def OnMouseEvent(self, event):
        self.SetXY(event)
        coords = [self.x, self.y]
        w,h = self.GetClientSize()

        if event.Moving and not self.drawing:
            old_active = self.active_node
            self.hit_node(coords)

            if self.active_node!=old_active:
                self.UpdateDrawing()

        if event.RightUp():
            if self.active_node==0 or self.active_node == self.n_nodes-1:
                return

            #with this, node stays active when pointer moves to the menu...
            self.drawing = 1

            menu = wx.Menu()
            popup = wx.NewId()
            if self.active_node is not None:
                self.Bind(wx.EVT_MENU, self.OnPopupRemove, id=popup)
                menu.Append(popup, "Remove node")
            else:
                self.Bind(wx.EVT_MENU, self.OnPopupAdd, id=popup)
                menu.Append(popup, "Add node")
            self.PopupMenu(menu, coords)
            menu.Destroy()
            self.drawing = 0

        if event.LeftDown():
            self.SetFocus()
            if self.hit_node(coords)>-1:
                self.flag_clicked=1

                self.CaptureMouse()
                self.drawing = True
                self.UpdateDrawing()

        elif event.Dragging() and self.drawing:
            if self.flag_clicked == 1:
                if self.active_node == 0:
                    #calculate left limit
                    coords[0] = self.x_delta
                elif self.active_node == self.n_nodes-1:
                    #calculate right limit
                    coords[0] = w+self.x_delta
                else:
                    if coords[0]-self.x_delta < self.nodes_screen[self.active_node-1,0]+1:
                        coords[0] = self.nodes_screen[self.active_node-1,0]+self.x_delta+1
                    elif coords[0]-self.x_delta > self.nodes_screen[self.active_node+1,0]-1:
                        coords[0] = self.nodes_screen[self.active_node+1,0]+self.x_delta-1
                    elif coords[0]-self.x_delta < 0:
                        coords[0] = self.x_delta
                    elif coords[0]-self.x_delta > w:
                        coords[0] = w+self.x_delta

                #do up and down...
                if coords[1]-self.y_delta < 0:
                    coords[1] = self.y_delta
                elif coords[1]-self.y_delta > h:
                    coords[1] = h+self.y_delta

                self.drag_node(coords)
                self.UpdateDrawing()

                self.DoEvent()
                
        elif event.LeftUp() and self.drawing:
            self.ReleaseMouse()
            self.drawing = False
            self.hit_node(coords)
            self.UpdateDrawing()
            self.flag_clicked = 0

        elif event.LeftDClick():
            hn = self.hit_node(coords)
            if hn == 0 or hn == self.n_nodes-1:
                return
            
            if hn>-1:
                self.RemoveNode(self.active_node)
            else:
                l,r = self.GetLeftRight(self.x)
                self.AddNode(l,r,(self.x,self.y))
                self.flag_clicked=1
                self.drawing = True
                self.CaptureMouse()
            self.CalcScreenNodes()
            self.MakeLutBmp()
            self.UpdateDrawing()

        if self.active_node is not None:
            s = "%.2f , %d%%" % (self.nodes_array[self.active_node,0],self.nodes_array[self.active_node,1]*100)
        else:
            opa_percent = 100-(self.y * 100. / h) 
            if opa_percent < 0:
                opa_percent = 0
            elif opa_percent > 100:
                opa_percent = 100

            s = "%.2f , %d%%" % ((self.right_range-self.left_range)*self.x/float(w)+self.left_range, opa_percent)

        self.tt.SetTip(s)

    def UpdateDrawing(self):
        if self.buffer is not None:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            self.DoDrawing(dc)

    def SetRange(self,mi,ma,redraw=1):
        self.left_range = mi
        self.right_range = ma

        if redraw:
            self.UpdateDrawing()

    def SetLutIndex(self,lut_index,redraw=1):
        self.lut_index=lut_index

        s=self.LutData.get_lut(lut_index)

        image = wx.EmptyImage(256,1)
        image.SetData(s)

        self.img=image
        self.MakeLutBmp()

        if redraw:
            self.UpdateDrawing()

    def drag_node(self,coords):
        active_node = self.active_node
        w,h = self.GetClientSize()

        #use the center...
        cx = coords[0] - self.x_delta
        cy = coords[1] - self.y_delta

        #put the node back in the screen array...
        self.nodes_screen[active_node,0]=cx
        self.nodes_screen[active_node,1]=cy

        #now do nodes_arr...
        self.nodes_array[active_node,0]=cx/float(w)
        self.nodes_array[active_node,1]= (h-cy)/float(h)

        self.MakeLutBmp()

    def hit_node(self,coords):
        #first get the hull points...
        s =self.node_size
        n_nodes = self.n_nodes

        #hit
        hx,hy=coords

        n=-1
        for i in range(n_nodes):
            cx = self.nodes_screen[i,0]
            cy = self.nodes_screen[i,1]
            rect = wx.Rect(cx-s/2,cy-s/2,s,s)

            if rect.InsideXY(hx, hy):
                self.active_node=i
                self.x_delta,self.y_delta=hx-cx,hy-cy
                n = i
                break

        if n == -1:
            self.active_node = None

        return n

    def DoEvent(self):
        ev = UpdateEvent(
                GetOpacity = self.GetOpacity,
                GetActiveIndex = self.GetActiveIndex,
                GetActivePosition = self.GetActivePosition,
                GetActiveOpacity= self.GetActiveOpacity
                )
        wx.PostEvent(self, ev)

