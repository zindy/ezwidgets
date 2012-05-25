# This file was automatically generated by pywxrc.
# -*- coding: UTF-8 -*-

import wx
import wx.xrc as xrc

__res = None

def get_resources():
    """ This function provides access to the XML resources in this module."""
    global __res
    if __res == None:
        __init_resources()
    return __res




class xrcmypanel(wx.Panel):
#!XRCED:begin-block:xrcmypanel.PreCreate
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
#!XRCED:end-block:xrcmypanel.PreCreate

    def __init__(self, parent):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PrePanel()
        self.PreCreate(pre)
        get_resources().LoadOnPanel(pre, parent, "mypanel")
        self.PostCreate(pre)

        # Define variables for the controls, bind event handlers

        self.Bind(wx.EVT_TEXT_ENTER, self.OnText_enter_text1, id=xrc.XRCID('text1'))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnText_enter_text2, id=xrc.XRCID('text2'))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_ch1, id=xrc.XRCID('ch1'))
        self.Bind(wx.EVT_SCROLL, self.OnScroll_slider1, id=xrc.XRCID('slider1'))
        self.Bind(wx.EVT_LISTBOX, self.OnListbox_listbox1, id=xrc.XRCID('listbox1'))
        self.Bind(wx.EVT_COMBOBOX, self.OnCombobox_combo1, id=xrc.XRCID('combo1'))
        self.Bind(wx.EVT_TEXT, self.OnText_combo1, id=xrc.XRCID('combo1'))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnText_enter_combo1, id=xrc.XRCID('combo1'))
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinctrl_sp1, id=xrc.XRCID('sp1'))
        self.Bind(wx.EVT_BUTTON, self.OnButton_button, id=xrc.XRCID('button'))

#!XRCED:begin-block:xrcmypanel.OnText_enter_text1
    def OnText_enter_text1(self, evt):
        # Replace with event handler code
        print "OnText_enter_text1()"
#!XRCED:end-block:xrcmypanel.OnText_enter_text1        

#!XRCED:begin-block:xrcmypanel.OnText_enter_text2
    def OnText_enter_text2(self, evt):
        # Replace with event handler code
        print "OnText_enter_text2()"
#!XRCED:end-block:xrcmypanel.OnText_enter_text2        

#!XRCED:begin-block:xrcmypanel.OnCheckbox_ch1
    def OnCheckbox_ch1(self, evt):
        # Replace with event handler code
        print "OnCheckbox_ch1()"
#!XRCED:end-block:xrcmypanel.OnCheckbox_ch1        

#!XRCED:begin-block:xrcmypanel.OnScroll_slider1
    def OnScroll_slider1(self, evt):
        # Replace with event handler code
        print "OnScroll_slider1()"
#!XRCED:end-block:xrcmypanel.OnScroll_slider1        

#!XRCED:begin-block:xrcmypanel.OnListbox_listbox1
    def OnListbox_listbox1(self, evt):
        # Replace with event handler code
        print "OnListbox_listbox1()"
#!XRCED:end-block:xrcmypanel.OnListbox_listbox1        

#!XRCED:begin-block:xrcmypanel.OnCombobox_combo1
    def OnCombobox_combo1(self, evt):
        # Replace with event handler code
        print "OnCombobox_combo1()"
#!XRCED:end-block:xrcmypanel.OnCombobox_combo1        

#!XRCED:begin-block:xrcmypanel.OnText_combo1
    def OnText_combo1(self, evt):
        # Replace with event handler code
        print "OnText_combo1()"
#!XRCED:end-block:xrcmypanel.OnText_combo1        

#!XRCED:begin-block:xrcmypanel.OnText_enter_combo1
    def OnText_enter_combo1(self, evt):
        # Replace with event handler code
        print "OnText_enter_combo1()"
#!XRCED:end-block:xrcmypanel.OnText_enter_combo1        

#!XRCED:begin-block:xrcmypanel.OnSpinctrl_sp1
    def OnSpinctrl_sp1(self, evt):
        # Replace with event handler code
        print "OnSpinctrl_sp1()"
#!XRCED:end-block:xrcmypanel.OnSpinctrl_sp1        

#!XRCED:begin-block:xrcmypanel.OnButton_button
    def OnButton_button(self, evt):
        # Replace with event handler code
        print "OnButton_button()"
#!XRCED:end-block:xrcmypanel.OnButton_button        




# ------------------------ Resource data ----------------------

def __init_resources():
    global __res
    __res = xrc.EmptyXmlResource()

    __res.Load('gui.xrc')