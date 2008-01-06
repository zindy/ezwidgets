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
import lutctrl

class MyFrame(wx.Frame):
def __init__(self):
        wx.Frame.__init__(self, None, -1, "Lut Control", size=(350,120))
        self.CreateStatusBar()

        p = wx.Panel(self,-1)
        cl=lutctrl.LutChoice(p,0)
        sl=lutctrl.LutSpin(p,28)
        pl=lutctrl.LutPanel(p,13)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(cl,0,wx.EXPAND|wx.ALL,2)
        box.Add(sl,0,wx.EXPAND|wx.ALL,2)
        box.Add(pl,1,wx.EXPAND|wx.ALL,2)
        box.Layout()
        p.SetSizer(box)

        cl.Bind(lutctrl.EVT_LUT, self.OnLut)
        sl.Bind(lutctrl.EVT_LUT, self.OnLut)

        self.pl = pl

    def OnLut(self,event):
        s = "LUT %d of %d is '%s'" % (
            event.GetLutIndex(),
            event.GetLutCount(),
            event.GetLutName())

        self.SetStatusText(s)
        self.pl.SetLutIndex(event.GetLutIndex())

if __name__ == "__main__":
    app = wx.PySimpleApp()
    f = MyFrame()
    f.Show()
    app.MainLoop()
