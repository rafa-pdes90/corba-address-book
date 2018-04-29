import sys, traceback
from CorbaAddressBook import *
from omniORB import CORBA
import CosNaming
import random
from appJar import gui


class CorbaClient():

	def __init__(self, argv):
		# Initialise the ORB
		orb = CORBA.ORB_init(argv, CORBA.ORB_ID)

		# Obtain a reference to the root naming context
		obj = orb.resolve_initial_references("NameService")
		self.naming = obj._narrow(CosNaming.NamingContext)

		if self.naming is None:
			print ("Failed to narrow the root naming context")
			sys.exit(1)

		self.app = None
		self.renewAddressBook()
		self.loadApp()
		
	def getAddressBook(self):
		# Resolve the name "test.my_context/AddressBook.#"
		for i in random.sample(range(1, 4), 3):
			name = [CosNaming.NameComponent("test", "my_context"),
							CosNaming.NameComponent("AddressBook", str(i))]
			try:
				objRef = self.naming.resolve(name)
				objRef._non_existent() # Test if obj exists

			except (CosNaming.NamingContext.NotFound):
				print ("AddressBook" + str(i) + " not found")

			except (CORBA.TRANSIENT):
				print ("AddressBook" + str(i) + " is offline")

			else:
				print ("AddressBook" + str(i) + " found")
				self.connected_to = "AddressBook" + str(i)

				# Narrow the object to an CorbaAddressBook::AddressBook
				return objRef._narrow(AddressBook)
		
		return None

	def renewAddressBook(self):
		self.address_book = None
		while self.address_book == None:
			self.address_book = self.getAddressBook()
		
		if (self.app != None):
			self.app.setLabel("title", "Connected to " + self.connected_to)

	def loadApp(self):
		# create a GUI variable called app
		self.app = gui()
		self.app.setSticky("ew")
		self.app.setStretch("column")

		# add & configure widgets - widgets get a name, to help referencing them later
		row = self.app.getRow()
		self.app.setInPadding([10,10])
		self.app.addLabel("title", "Connected to " + self.connected_to, row=row)
		self.app.setLabelBg("title", "lightgreen")

		row = self.app.getRow()
		self.app.startFrame("buttons", row=row)
		self.app.setSticky("ew")
		self.app.setStretch("column")
		self.app.setPadding([10,10])
		self.app.setInPadding([10,0])
		self.app.addButton("Add Contact", self.addContact, row=0, column=0)
		self.app.addButton("Del Contact", self.delContact, row=0, column=1)
		self.app.addButton("Update Contact", self.updateContact, row=0, column=2)
		self.app.stopFrame()

		row = self.app.getRow()
		self.app.startFrame("labels", row=row)
		self.app.setSticky("ew")
		self.app.setStretch("column")
		self.app.setPadding([10,10])
		self.app.setInPadding([10,0])
		self.app.addLabelEntry("Name", row=0, column=0)
		self.app.addLabelEntry("Phone Number", row=0, column=1)
		self.app.stopFrame()

		row = self.app.getRow()
		self.app.setPadding([10,10])
		self.app.setInPadding([10,10])
		self.app.addButton("Get Contacts", self.getContacts, row=row)

		row = self.app.getRow()
		self.app.setSticky("nsew")
		self.app.setStretch("both")
		self.app.startFrame("listbox", row=row)
		self.app.setSticky("nsew")
		self.app.setStretch("both")
		self.app.setPadding([10,10])
		self.app.setInPadding([10,10])
		self.app.addListBox("ContactName", values=[], row=0, column=0)
		self.app.setListBoxChangeFunction("ContactName", self.selectContact)
		self.app.setListBoxGroup("ContactName", group=True)
		self.app.addListBox("ContactPhoneNumber", values=[], row=0, column=1)
		self.app.setListBoxChangeFunction("ContactPhoneNumber", self.selectContact)
		self.app.setListBoxGroup("ContactPhoneNumber", group=True)
		self.app.stopFrame()

		# start the GUI
		self.app.setLocation("CENTER")
		self.app.go()

	def selectContact(self, selectedList):
		try:
			selected = self.app.getListBox(selectedList)[0]
			pos = self.app.getAllListItems(selectedList).index(selected)

			if (selectedList == "ContactName"):
				name = selected
				self.app.selectListItemAtPos("ContactPhoneNumber", pos, callFunction=False)
				pnumber = self.app.getListBox("ContactPhoneNumber")[0]
			else:
				pnumber = selected
				self.app.selectListItemAtPos("ContactName", pos, callFunction=False)
				name = self.app.getListBox("ContactName")[0]

			self.app.setEntry("Name", name)
			self.app.setEntry("Phone Number", pnumber)
		except (IndexError):
			pass
		
	def printContact(self, c):
		return "Name: " + c.name + " - Phone Number: " + c.pnumber

	def addContact(self):
		name = self.app.getEntry("Name")
		pnumber = self.app.getEntry("Phone Number")

		if (name == "" or pnumber == ""):
			return

		newContact = Contact(name, pnumber)
		updated = True
		while (True):
			try:
				try:
					self.address_book.addContact(newContact)

				except (ContactAlreadyExists) as ex:
					print ('Contact already exists: "' + self.printContact(ex.c) + '"')

					if (ex.c.pnumber != pnumber):
						msg = "Contact already exists as:\r\n" + self.printContact(ex.c) + "\r\n\r\nWould your like to update it?"
						if (self.app.yesNoBox("Warning", msg)):
							try:
								self.address_book.updateContact(ex.c.name, newContact)
							
							except (ContactNotFound):
								updated = False
						else:
							updated = False

				if (updated):
					print ('Contact saved: "' + self.printContact(newContact) + '"')
				self.app.clearEntry("Name", "")
				self.app.clearEntry("Phone Number", "")
				return

			except (CORBA.TRANSIENT):
				self.renewAddressBook()

	def delContact(self):
		name = self.app.getEntry("Name")

		if (name == ""):
			return

		while (True):
			try:
				try:
					self.address_book.delContact(name)

				except (ContactNotFound):
					print ("Contact already deleted")

				else:
					print ('Contact "' + name + '" deleted')
				
				self.app.clearEntry("Name", "")
				self.app.clearEntry("Phone Number", "")
				return

			except (CORBA.TRANSIENT):
				self.renewAddressBook()
	
	def updateContact(self):
		currentName = self.app.getListBox("ContactName")[0]
		name = self.app.getEntry("Name")
		pnumber = self.app.getEntry("Phone Number")

		if (name == "" or pnumber == ""):
			return

		newContact = Contact(name, pnumber)
		updated = True
		while (True):
			try:
				try:
					self.address_book.updateContact(currentName, newContact)

				except (ContactNotFound):
					print ('Contact "' + name + '" does not exist')

					msg = 'Contact "' + name + '" does not exist\r\n\r\nWould your like to add it?'
					if (self.app.yesNoBox("Warning", msg)):
						try:
							self.address_book.addContact(newContact)
						
						except (ContactAlreadyExists):
							updated = False
					else:
						updated = False
				
				if (updated):
					print ('Contact saved: "' + self.printContact(newContact) + '"')
				
				self.app.clearEntry("Name", "")
				self.app.clearEntry("Phone Number", "")
				return

			except (CORBA.TRANSIENT):
				self.renewAddressBook()

	
	def getContacts(self):
		contact_list = []

		while (True):
			try:
				contact_list = self.address_book.getContacts()
				break

			except (CORBA.TRANSIENT):
				self.renewAddressBook()
		

		names = []
		pnumbers = []
		for c in contact_list:
			names.append(c.name)
			pnumbers.append(c.pnumber)

		self.app.clearListBox("ContactName", callFunction=False)
		self.app.addListItems("ContactName", sorted(names, key=str.lower), select=False)

		self.app.clearListBox("ContactPhoneNumber", callFunction=False)
		self.app.addListItems("ContactPhoneNumber", sorted(pnumbers, key=str.lower), select=False)


if __name__ == '__main__':
	try:		
		client = CorbaClient(sys.argv)
	
	except Exception as inst:
		print("Unknown Error : " + str(inst))
		traceback.print_exc()
