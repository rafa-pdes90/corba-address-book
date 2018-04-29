import CorbaAddressBook, CorbaAddressBook__POA
from omniORB import CORBA
import CosNaming

class AddressBookImpl (CorbaAddressBook__POA.AddressBook):

	def __init__(self):
		self.contact_list = {}
		self.all_books = []

	def loadBooks(self, naming, index):
		self.naming = naming
		self.index = index

		for i in range(1, 5):
			if (i == self.index):
				self.all_books.append(None)
				continue
			
			self.all_books.append(self.getAddressBook(i))
		
	def getAddressBook(self, i):
		# Resolve the name "test.my_context/AddressBook.#"
		name = [CosNaming.NameComponent("test", "my_context"),
						CosNaming.NameComponent("AddressBook", str(i))]
		try:
			objRef = self.naming.resolve(name)
			objRef._non_existent() # Test if obj exists

		except (CosNaming.NamingContext.NotFound, CORBA.TRANSIENT):
			pass

		else:
			# Narrow the object to an CorbaAddressBook::AddressBook
			return objRef._narrow(CorbaAddressBook.AddressBook)
		
		return None

	def addContact(self, c):
		if (c.name not in self.contact_list):
			self.contact_list[c.name] = c
		else:
			raise CorbaAddressBook.ContactAlreadyExists(self.contact_list[c.name])

	def delContact(self, name):
		if (name in self.contact_list):
			del self.contact_list[name]
		else:
			raise CorbaAddressBook.ContactNotFound()

	def updateContact(self, currentName, updatedContact):
		if (currentName in self.contact_list):
			if (updatedContact.name != currentName):
				try:
					self.delContact(currentName)

				except (CorbaAddressBook.ContactNotFound):
					pass
			
			self.contact_list[updatedContact.name] = updatedContact
		else:
			raise CorbaAddressBook.ContactNotFound()

	def addOrUpdateContact(self, c):
		try:
			self.addContact(c)
		
		except (CorbaAddressBook.ContactAlreadyExists):
			try:
				self.updateContact(c.name, c)
			
			except (CorbaAddressBook.ContactNotFound):
				pass

	def getContacts(self):
		return list(self.contact_list.values())
