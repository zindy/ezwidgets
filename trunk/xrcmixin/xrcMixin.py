#!/usr/bin/env python

"""@package xrcMixin
xrcMixin, an XRC mixin.

Copyright (c) 2009 Egor Zindy <ezindy@gmail.com>

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
__copyright__ = "Copyright (c) 2009 Egor Zindy"
__license__ = "MIT"
__version__ = "1.0"
__date= "2009-12-09"
__status__ = "Production"

import wx
import wx.lib.newevent
DebugEvent, EVT_DEBUG = wx.lib.newevent.NewEvent()

class xrcMixin():
    def __init__(self,debug=False):
        self.debug = debug

        self.dict = {}
        for ctrl in self.GetChildren():
            name = ctrl.GetName()

            if name != "-1":
                if debug:
                    ctrl.SetToolTip(wx.ToolTip(name))
                    if name in self.dict.keys():
                        print "Multiple instance of: %s" % name

                setattr(self,name,ctrl)
                self.dict[name]=ctrl

        if debug:
            self.Bind(wx.EVT_LEFT_DCLICK,self.OnDebug)

    def GetValues(self):
        """Values from panel controls

        Scans controls in the panels and returns the values as a dictionary
        @return a dictionary of the control values
        """
        dict = {}
        for key,ctrl in self.dict.items():
            methods = ctrl.__class__.__dict__.keys()
            if 'GetValue' in methods:
                dict[key]=ctrl.GetValue()
            elif 'GetSelections' in methods:
                dict[key]=ctrl.GetSelections()
            elif 'GetSelection' in methods:
                dict[key]=ctrl.GetSelection()
            elif 'GetCurrentSelection' in methods:
                dict[key]=ctrl.GetCurrentSelection()

        return dict

    def OnDebug(self,evt):
        s = "Control values:\n\n"
        for key,value in self.GetValues().items():
            s+="%s: %s\n" % (key,str(value))

        wx.MessageBox(s, 'Debug')

        debug_event = DebugEvent( GetValues = self.GetValues)
        wx.PostEvent(self, debug_event)

        evt.Skip()

