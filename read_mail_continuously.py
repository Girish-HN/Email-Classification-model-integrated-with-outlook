import win32com.client
import pythoncom
#from read_mail import stringcheck
from model_email import return_mail_category

class Handler_Class(object):
    def OnNewMailEx(self, receivedItemsIDs):
        for ID in receivedItemsIDs.split(","):

            mailItem = outlook.Session.GetItemFromID(ID)
            
            mail = return_mail_category()
            request_value = mail.mail_contents(str(mailItem.Body), str('girish.hn@accenture.com'))
            target = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            donebox = target.GetDefaultFolder(6).Folders[request_value]
            mailItem.Move(donebox)
            print('mail is moved to %s folder'%(request_value))
       
outlook = win32com.client.DispatchWithEvents("Outlook.Application", Handler_Class)
pythoncom.PumpMessages()