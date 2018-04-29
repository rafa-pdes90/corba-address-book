import CorbaAddressBook, CorbaAddressBook__POA
from omniORB import CORBA
import CosNaming


class AddressBookImpl (CorbaAddressBook__POA.AddressBook):

	def __init__(self):
		self.contact_list = {}

	def loadBooks(self, naming, index):
		self.naming = naming
		self.index = index
		self.all_refs = []
		self.all_books = []

		loaded = False

		for i in range(1, 4):
			if (i == self.index):
				self.all_refs.append(None)
				self.all_books.append(None)
				continue

			ref, address_book = self.getAddressBookWithRef(i)
			self.all_refs.append(ref)
			self.all_books.append(address_book)
			
			if (not loaded and self.all_books[i-1] != None):
				try:
					for c in self.all_books[i-1].getContacts():
						self.contact_list[c.name] = c

				except (CORBA.TRANSIENT):
					continue

				loaded = True

		
	def getAddressBookWithRef(self, i):
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
			return objRef, objRef._narrow(CorbaAddressBook.AddressBook)
		
		return None, None

	def getNextBook(self):
		for i in range(0, 3):
			if (i+1 == self.index):
				continue
			
			if (self.all_refs[i] == None):
				self.all_refs[i], self.all_books[i] = self.getAddressBookWithRef(i+1)

				if (self.all_refs[i] == None):
					continue

			else:
				try:
					self.all_refs[i]._non_existent()
				
				except (CORBA.TRANSIENT):
					self.all_refs[i], self.all_books[i] = self.getAddressBookWithRef(i+1)

					if (self.all_refs[i] == None):
						continue

			yield self.all_books[i]

	def addContact(self, c):
		if (c.name not in self.contact_list):
			self.contact_list[c.name] = c

			for address_book in self.getNextBook():
				try:
					address_book.addOrUpdateContact(c)
				
				except (CORBA.TRANSIENT):
					continue

		else:
			raise CorbaAddressBook.ContactAlreadyExists(self.contact_list[c.name])

	def delContact(self, name):
		if (name in self.contact_list):
			del self.contact_list[name]

			for address_book in self.getNextBook():
				try:
					address_book.delContact(name)
				
				except (CORBA.TRANSIENT, CorbaAddressBook.ContactNotFound):
					continue
			
		else:
			raise CorbaAddressBook.ContactNotFound()

	def updateContact(self, currentName, updatedContact):
		if (currentName in self.contact_list):
			if (updatedContact.name != currentName):
				del self.contact_list[currentName]
			
			self.contact_list[updatedContact.name] = updatedContact

			for address_book in self.getNextBook():
				try:
					address_book.updateContact(currentName, updatedContact)
				
				except (CORBA.TRANSIENT, CorbaAddressBook.ContactNotFound):
					continue
			
		else:
			raise CorbaAddressBook.ContactNotFound()

	def addOrUpdateContact(self, c):
		self.contact_list[c.name] = c

	def getContacts(self):
		return list(self.contact_list.values())
