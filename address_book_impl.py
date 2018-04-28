import CorbaAddressBook, CorbaAddressBook__POA

class AddressBookImpl (CorbaAddressBook__POA.AddressBook):

	def __init__(self):
		self.contact_list = {}

	def addContact(self, c):
		if (c.name not in self.contact_list):
			self.contact_list[c.name] = c
		else:
			raise CorbaAddressBook.ContactAlreadyExists()

	def delContact(self, name):
		if (name in self.contact_list):
			del self.contact_list[name]
		else:
			raise CorbaAddressBook.ContactNotFound()

	def updateContact(self, currentName, updatedContact):
		if (currentName in self.contact_list):
			if (updatedContact.name != currentName):
				self.delContact(currentName)
			
			self.contact_list[updatedContact.name] = updatedContact

	def getContacts(self):
		return list(self.contact_list.values())
