#[Clinic_token_generator.py](https://github.com/user-attachments/files/24151307/Clinic_token_generator.py)
import wx
import csv
import os
import re
from datetime import datetime

#Lists
CSV_FILE = "clinic_data_full.csv"
CSV_COLS = ["token", "name", "phone", "dept", "date", "time", "status", "notes"]
DEPARTMENTS = ["General", "Dental", "ENT", "Ortho"]
STATUS = ["Scheduled", "Completed", "Cancelled"]

#listctrl global
list_ctrl = None 


#Functions of csv file
def load_data():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, "r", newline="") as f:
        return list(csv.DictReader(f))

def save_data(rows):
    with open(CSV_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        w.writerows(rows)

def generate_token(date_str):
    rows = load_data()
    todays = [r for r in rows if r['token'].startswith(date_str)]
    count = len(todays) + 1
    return f"{date_str}-{count:03d}"


#Gui
#cross symbol
def on_header_paint(event):
    panel = event.GetEventObject()
    dc = wx.PaintDC(panel)
    dc.SetPen(wx.Pen("ORANGE", 1))
    dc.SetBrush(wx.Brush("ORANGE"))
    dc.DrawRectangle(200, 30, 40, 10)
    dc.DrawRectangle(215, 15, 10, 40)

#Table refresh
def refresh_list(query=None):
    global list_ctrl
    if not list_ctrl: return

    list_ctrl.DeleteAllItems()
    rows = load_data()
    
    if query:
        q = query.lower()
        rows = [r for r in rows if q in r['name'].lower() or q in r['token'].lower()]

    for r in rows:
        idx = list_ctrl.InsertItem(list_ctrl.GetItemCount(), r['token'])
        list_ctrl.SetItem(idx, 1, r['name'])
        list_ctrl.SetItem(idx, 2, r['phone'])
        list_ctrl.SetItem(idx, 3, r['dept'])
        list_ctrl.SetItem(idx, 4, r['status'])
        list_ctrl.SetItem(idx, 5, r['notes'])

        if r['status'] == "Completed":
            list_ctrl.SetItemTextColour(idx, wx.Colour("SEA GREEN"))
        elif r['status'] == "Cancelled":
            list_ctrl.SetItemTextColour(idx, wx.Colour("RED"))


#Dialogs for add/edit
def add_edit_appointment_dialog(parent, title="Appointment", data=None):
    dlg = wx.Dialog(parent, title=title, size=(400, 520))
    panel = wx.Panel(dlg)
    vbox = wx.BoxSizer(wx.VERTICAL)

    #Font
    def add_lbl(label):
        t = wx.StaticText(panel, label=label)
        t.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        return t

    # Inputs
    vbox.Add(add_lbl("Patient Name:"), 0, wx.LEFT|wx.TOP, 10)
    txt_name = wx.TextCtrl(panel)
    vbox.Add(txt_name, 0, wx.EXPAND|wx.ALL, 10)

    vbox.Add(add_lbl("Phone (10 digits):"), 0, wx.LEFT, 10)
    txt_phone = wx.TextCtrl(panel)
    vbox.Add(txt_phone, 0, wx.EXPAND|wx.ALL, 10)

    vbox.Add(add_lbl("Department:"), 0, wx.LEFT, 10)
    cmb_dept = wx.ComboBox(panel, choices=DEPARTMENTS, style=wx.CB_READONLY)
    cmb_dept.SetValue(DEPARTMENTS[0])
    vbox.Add(cmb_dept, 0, wx.EXPAND|wx.ALL, 10)

    # Date and Time
    hbox_dt = wx.BoxSizer(wx.HORIZONTAL)
    txt_date = wx.TextCtrl(panel, value=datetime.now().strftime("%Y-%m-%d"))
    txt_time = wx.TextCtrl(panel, value=datetime.now().strftime("%H:%M"))
    hbox_dt.Add(txt_date, 1, wx.RIGHT, 5)
    hbox_dt.Add(txt_time, 1, wx.LEFT, 5)
    vbox.Add(hbox_dt, 0, wx.EXPAND|wx.ALL, 10)
    
    #Status
    chk_status = wx.ComboBox(panel, choices=STATUS, style=wx.CB_READONLY)
    chk_status.SetValue(STATUS[0])
    vbox.Add(chk_status, 0, wx.EXPAND|wx.ALL, 10)
    
    #Notes
    vbox.Add(add_lbl("Notes:"), 0, wx.LEFT, 10)
    txt_notes = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 60))
    vbox.Add(txt_notes, 0, wx.EXPAND|wx.ALL, 10)

    #Buttons
    btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
    btn_ok = wx.Button(panel, wx.ID_OK, label="Save Record")
    btn_cancel = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
    btn_sizer.Add(btn_ok, 0, wx.RIGHT, 10)
    btn_sizer.Add(btn_cancel, 0)
    vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER|wx.BOTTOM, 20)

    panel.SetSizer(vbox)

    #If data already exists (used for editing)
    if data:
        txt_name.SetValue(data['name'])
        txt_phone.SetValue(data['phone'])
        cmb_dept.SetValue(data['dept'])
        txt_date.SetValue(data['date'])
        txt_time.SetValue(data['time'])
        txt_notes.SetValue(data['notes'])
        chk_status.SetValue(data['status'])

    #Adding new element 
    result_data = None
    if dlg.ShowModal() == wx.ID_OK:
        # Collecting values
        result_data = {
            "name": txt_name.GetValue(),
            "phone": txt_phone.GetValue(),
            "dept": cmb_dept.GetValue(),
            "date": txt_date.GetValue(),
            "time": txt_time.GetValue(),
            "status":chk_status.GetValue(),
            "notes": txt_notes.GetValue()
        }
    
    dlg.Destroy()
    return result_data

#adding appointment
#checking inputs
def check_and_save(parent, new_data, current_token=None):
    try:
        if not new_data['name']: 
            raise ValueError("Name required!")
        if not re.match(r"^\d{10}$", new_data['phone']): 
            raise ValueError("Phone must be 10 digits")
        
        rows = load_data()

        if current_token:
            new_data['token'] = current_token
            for i, r in enumerate(rows):
                if r['token'] == current_token:
                    rows[i] = new_data
                    break
        else:
            new_data['token'] = generate_token(new_data['date'])
            rows.append(new_data)

        save_data(rows)
        return True, new_data['token']
    
    except ValueError as e:
        wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
        return False, None
    
#adding appointment 
def on_add(event):
    parent = event.GetEventObject().GetParent()
    data = add_edit_appointment_dialog(parent, title="Add Appointment")
    if data:
        success, token = check_and_save(parent, data)
        if success:
            refresh_list()
            wx.MessageBox(f"Generated Token: {token}", "Success")
#edit
def on_edit(event):
    global list_ctrl
    selected = list_ctrl.GetFirstSelected()
    if selected == -1:
        wx.MessageBox("No appointment selected.", "Error", wx.ICON_ERROR)
        return
    token = list_ctrl.GetItemText(selected, 0)
    rows = load_data()
    record = next((r for r in rows if r['token'] == token), None)

    if record:
        parent = event.GetEventObject().GetParent()
        new_data = add_edit_appointment_dialog(parent, "Edit Record", data=record)
        
        if new_data:
            success, x = check_and_save(parent, new_data, current_token=token)
            if success:
                refresh_list()
                wx.MessageBox("Record Updated!", "Success") 
#Search
def on_search(event):
    parent = event.GetEventObject().GetParent()
    dlg = wx.TextEntryDialog(parent, "Search by Name or Token:", "Search")
    if dlg.ShowModal() == wx.ID_OK:
        query = dlg.GetValue()
        refresh_list(query)
    dlg.Destroy()

#delete
def on_delete(event):
    global list_ctrl
    parent=event.GetEventObject().GetParent()
    selected = list_ctrl.GetFirstSelected()
    if selected == -1:
        wx.MessageBox("No appointment selected.", "Error", wx.ICON_ERROR)
        return

    token=list_ctrl.GetItemText(selected)
    rows=load_data()
    rows=[r for r in rows if r['token'] != token]
    save_data(rows)
    refresh_list()

#main gui
app=wx.App()
    
# Create Main Frame
frame=wx.Frame(None, title="Clinic App", size=(720, 600))
panel=wx.Panel(frame)
sizer=wx.BoxSizer(wx.VERTICAL)

#Header
header=wx.Panel(panel)
header.SetBackgroundColour("light blue")
header.SetMinSize((-1, 80)) 

# Title
title_lbl = wx.StaticText(header, label="MEDICARE CLINIC", pos=(260, 25))
title_lbl.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

# Bind Paint Event for the Red Cross
header.Bind(wx.EVT_PAINT, on_header_paint)
sizer.Add(header, 0, wx.EXPAND)

# Table
list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL)
list_ctrl.InsertColumn(0, "Token", width=100)
list_ctrl.InsertColumn(1, "Name", width=150)
list_ctrl.InsertColumn(2, "Phone", width=100)
list_ctrl.InsertColumn(3, "Dept", width=80)
list_ctrl.InsertColumn(4, "Status", width=80)
list_ctrl.InsertColumn(5, "Notes", width=150)

sizer.Add(list_ctrl, 1, wx.EXPAND | wx.ALL, 10)

# Buttons
btn_sizer = wx.GridSizer(2, 2, 10, 10)

btn_add = wx.Button(panel, label="Add New")
btn_search = wx.Button(panel, label="Search")
btn_edit = wx.Button(panel, label="Edit")
btn_del = wx.Button(panel, label="Delete")

# Styling
btn_add.SetBackgroundColour("SEA GREEN")
btn_del.SetBackgroundColour("ORANGE")
btn_add.SetForegroundColour("WHITE")
btn_del.SetForegroundColour("WHITE")

# Binding events to buttons
btn_add.Bind(wx.EVT_BUTTON, on_add)
btn_search.Bind(wx.EVT_BUTTON, on_search)
btn_edit.Bind(wx.EVT_BUTTON, on_edit)
btn_del.Bind(wx.EVT_BUTTON, on_delete)

btn_sizer.Add(btn_add, 0, wx.EXPAND)
btn_sizer.Add(btn_search, 0, wx.EXPAND)
btn_sizer.Add(btn_edit, 0, wx.EXPAND)
btn_sizer.Add(btn_del, 0, wx.EXPAND)

sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 20)


panel.SetSizer(sizer)
refresh_list()
frame.Show()
app.MainLoop()
