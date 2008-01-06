# -*- coding: utf-8 -*-

__authors__ = ['Egor Zindy <EZindy@gmail.com>']
__contributors__ = []
__date__ = '2007-12-01'
__copyright__ = """
Copyright (c) 2007 Egor Zindy
"""

__license__ = """
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, 
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, 
      this list of conditions and the following disclaimer in the documentation 
      and/or other materials provided with the distribution.
    * Neither the name of Egor Zindy nor the names of his contributors 
      may be used to endorse or promote products derived from this software 
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__changelog__ = """
2007-12-01 Released to Google Code under a BSD license.
"""

#This is a simple test harness to check the lutctrl.py functionality

import wx
import wx.lib.newevent

from lutdata import LutData

LutEvent, EVT_LUT = wx.lib.newevent.NewEvent()

class LutPanel(wx.Panel,LutData):
    def __init__(self, parent,lut_index=0):
        wx.Panel.__init__(self, parent, -1,size=(10,24),style=wx.SUNKEN_BORDER)
        LutData.__init__(self)

        if lut_index >= self.get_count():
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

        self.sb.SetToolTip(wx.ToolTip(self._names[self.lut_index]))
        self.sb.SetBitmap(self.img.Scale(w,h).ConvertToBitmap())
        self.Refresh()

    def GetLutCount(self):
        return len(self._names)

    def GetLutIndex(self):
        return self.lut_index

    def GetLutNames(self):
        return self._names

    def GetLutName(self):
        return self.get_name(self.lut_index)

    #returns an interleaved "RGBRGBRGB..." string, 768 bytes long.
    def GetLut(self):
        return self.get_lut(self.lut_index)

    #returns 3 strings R,G,B 256 bytes long.
    #These are easy to convert to numarray, Numeric or numpy...
    #
    #r,g,b = event.GetLutRGB()
    #r_array = Numeric.array(r)
    #g_array = Numeric.array(r)
    #b_array = Numeric.array(r)
    def GetLutRGB(self):
        return self.get_rgb(self.lut_index)

    #select a LUT to display
    def SetLutIndex(self,lut_index,redraw=1):
        self.lut_index=lut_index

        s=self.get_lut(lut_index)

        image = wx.EmptyImage(256,1)
        image.SetData(s)

        self.img=image

        if redraw:
            self.Redraw()

class LutChoice(wx.Panel):
    def __init__(self, parent,lut_index=0,height=20):
        wx.Panel.__init__(self, parent, -1)

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.lp=LutPanel(self,lut_index)
        self.lut_index=lut_index

        self.ch=wx.Choice(self, -1, size=wx.Size(110, -1), choices = self.lp.GetLutNames())
        self.ch.SetSelection(lut_index)

        self.box.Add(self.ch,0)
        self.box.Add(self.lp,1,wx.EXPAND)
        self.box.Layout()
        self.SetSizer(self.box)

        self.Bind(wx.EVT_CHOICE,self.OnChoice,self.ch)

        self.GetLutCount=self.lp.GetLutCount
        self.GetLutIndex=self.lp.GetLutIndex
        self.GetLutRGB=self.lp.GetLutRGB
        self.GetLutName=self.lp.GetLutName

    def SetLutIndex(self,lut_index):
        self.SetLutIndex=self.lp.SetLutIndex(lut_index,redraw=1)
        self.ch.SetSelection(lut_index)

    def OnChoice(self, event):
        lut_index=self.ch.GetSelection()
        if lut_index!=self.lut_index:
            self.lut_index=lut_index
            self.lp.SetLutIndex(lut_index,redraw=1)

            lut_event = LutEvent(
                    GetLutCount=self.GetLutCount,
                    GetLutIndex=self.GetLutIndex,
                    GetLutRGB=self.GetLutRGB,
                    GetLutName=self.GetLutName)
            wx.PostEvent(self, lut_event)

class LutSpin(wx.Panel):
    def __init__(self, parent,lut_index=0,height=20):
        wx.Panel.__init__(self, parent, -1)

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.lp=LutPanel(self,lut_index)
        self.lp.SetToolTipString(self.lp.GetLutName())

        self.lut_index=lut_index

        self.spin = wx.SpinButton(self, -1, size=(height*.75, height), style=wx.SP_VERTICAL)
        self.spin.SetRange(0, self.lp.GetLutCount()-1)
        self.spin.SetValue(lut_index)

        self.box.Add(self.lp,1,wx.EXPAND)
        self.box.Add(self.spin,0)
        self.box.Layout()
        self.SetSizer(self.box)

        self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)

        self.GetLutCount=self.lp.GetLutCount
        self.GetLutIndex=self.lp.GetLutIndex
        self.GetLutRGB=self.lp.GetLutRGB
        self.GetLutName=self.lp.GetLutName

    def SetLutIndex(self,lut_index):
        self.SetLutIndex=self.lp.SetLutIndex(lut_index,redraw=1)
        self.spin.SetValue(lut_index)

    def OnSpin(self, event):
        lut_index=event.GetPosition()
        if lut_index!=self.lut_index:
            self.lut_index=lut_index
            self.lp.SetLutIndex(lut_index,redraw=1)
            self.lp.SetToolTipString(self.lp.GetLutName())

            lut_event = LutEvent(
                    GetLutCount=self.GetLutCount,
                    GetLutIndex=self.GetLutIndex,
                    GetLutRGB=self.GetLutRGB,
                    GetLutName=self.GetLutName)
            wx.PostEvent(self, lut_event)

if __name__ == "__main__":

    class MyFrame(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, -1, "Lut Control", size=(350,120))
            self.CreateStatusBar()

            p = wx.Panel(self,-1)
            cl=LutChoice(p,0)
            sl=LutSpin(p,28)
            pl=LutPanel(p,13)

            box = wx.BoxSizer(wx.VERTICAL)
            box.Add(cl,0,wx.EXPAND|wx.ALL,2)
            box.Add(sl,0,wx.EXPAND|wx.ALL,2)
            box.Add(pl,1,wx.EXPAND|wx.ALL,2)
            box.Layout()
            p.SetSizer(box)

            cl.Bind(EVT_LUT, self.OnLut)
            sl.Bind(EVT_LUT, self.OnLut)

            self.pl = pl

        def OnLut(self,event):
            s = "LUT %d of %d is '%s'" % (
                event.GetLutIndex(),
                event.GetLutCount(),
                event.GetLutName())

            #The event.GetLUT() and event.GetLUTRGB() are also available.
            #They return and RGB string (interleaved) or separate R,G,B strings
            #These are easy to convert to numarray, Numeric or numpy...
            #
            #r,g,b = event.GetLutRGB()
            #r_array = Numeric.array(r)
            #g_array = Numeric.array(r)
            #b_array = Numeric.array(r)

            self.SetStatusText(s)
            self.pl.SetLutIndex(event.GetLutIndex())

    app = wx.PySimpleApp()
    f = MyFrame()
    f.Show()
    app.MainLoop()

