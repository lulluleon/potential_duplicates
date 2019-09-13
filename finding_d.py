"""To find potential duplicates in HubSpot database with RESTful API"""

import sys
import warnings
from hubspot.connection import APIKey, PortalConnection
from hubspot.contacts.lists import get_all_contacts
import pandas as pd
import wx


# turning error into exceptions
warnings.filterwarnings('error')


# create gui
class MyFrame(wx.Frame):
    """frame for result, finding duplicates from combined data frame df3"""
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='List of Duplicates', size=(500, 500))

        self.main_panel = wx.Panel(self)
        self.vbox1 = wx.BoxSizer(wx.VERTICAL)

    # set text, list, button
        self.text = wx.StaticText(self.main_panel,
                                  label="                            "+"Click RUN"+"                            ")
        self.vbox1.Add(self.text, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 15)

        self.list = wx.ListCtrl(self.main_panel, style=wx.LC_REPORT, pos=(35, 5), size=(500, 440))
        self.list.InsertColumn(0, 'Email Address', width=200)
        self.list.InsertColumn(1, 'First Name', wx.LIST_FORMAT_RIGHT, 110)
        self.list.InsertColumn(2, 'Last Name', wx.LIST_FORMAT_RIGHT, 110)
        self.vbox1.Add(self.list, 1, wx.ALL, 5)

        self.btn = wx.Button(self.main_panel, label="RUN", size=(90, 30))
        self.btn.Bind(wx.EVT_BUTTON, self._on_click)
        self.vbox1.Add(self.btn, 0, wx. ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, 5)

    # other style
        self.main_panel.SetSizer(self.vbox1)
        self.CreateStatusBar()
        self.Center()
        self.Show()

# pull data from HubSpot and fill list
    def _f_process(self):
        authentication_key = APIKey("06f14623-f391-428e-8a15-c285e0350a86")
        connection = PortalConnection(authentication_key, "Forduplicates")
        df1 = pd.DataFrame([contact.email_address for contact in get_all_contacts(connection)])
        df2 = pd.DataFrame([contact.properties for contact in get_all_contacts(connection)])
        df3 = pd.concat([df1, df2], axis=1)

    # cleanse dataframe
        df3.drop(['company', 'lastmodifieddate'], axis=1, inplace=True)
        df4 = df3.dropna(subset=['firstname', 'lastname'], axis=0)
        df4 = df4.apply(lambda x: x.str.lower())

    # find duplicates
        df5 = df4[df4.duplicated(subset=['firstname', 'lastname'], keep=False)]
        df6 = df5.sort_values(by=['firstname', 'lastname'])
        df6.reset_index(drop=True, inplace=True)
        contact_list = df6.values.tolist()
        count_row = df6.shape[0]

        self.text.SetLabel("        Total " + str(count_row) + " contacts are duplicated!")

    # fill list
        for i in contact_list:
            index = self.list.InsertItem(sys.maxint, i[0])
            self.list.SetItem(index, 1, i[1])
            self.list.SetItem(index, 2, i[2])

# define toggle event
    def _on_click(self, event):
        message = event.GetEventObject().GetLabel()
        if message == "RUN":
            self.text.SetLabel("Loading...This can take up to 1 minute.")
            event.GetEventObject().SetLabel("OK")
            self._f_process()

        elif message == "OK":
            self.Close()
            sys.exit()


APP = wx.App(False)
MyFrame(None)
APP.MainLoop()
del APP
