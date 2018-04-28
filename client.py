import sys, traceback
from CorbaAddressBook import *
from omniORB import CORBA
import CosNaming
import random


if __name__ == '__main__':
	try:
		# Initialise the ORB
		orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

		# Obtain a reference to the root naming context
		obj = orb.resolve_initial_references("NameService")
		naming = obj._narrow(CosNaming.NamingContext)

		if naming is None:
			print ("Failed to narrow the root naming context")
			sys.exit(1)

		# Resolve the name "test.my_context/AddressBook.#"
		for i in random.sample(range(1, 2), 1):
			name = [CosNaming.NameComponent("test", "my_context"),
							CosNaming.NameComponent("AddressBook", str(i))]
			try:
				objRef = naming.resolve(name)
				print ("AddressBook" + str(i) + " found")
				break

			except (CosNaming.NamingContext.NotFound) as ex:
				print ("AddressBook" + str(i) + " not found")

		# Narrow the object to an CorbaAddressBook::AddressBook
		address_book = objRef._narrow(AddressBook)

		if address_book is None:
			print ("Object reference is not an CorbaAddressBook::AddressBook")
			sys.exit(1)

		try:
			c = Contact("Rafael", "985287902")
			address_book.addContact(c)
			print (str(address_book.getContacts()))
			address_book.updateContact("Rafael", Contact("Rafael Parente", "981035078"))
			print (str(address_book.getContacts()))
		
		except (ContactAlreadyExists):
			print ("Contact already exists")
			address_book.delContact("Rafael")

		except (CORBA.TRANSIENT):
			print ("Server offline")
	
	except Exception as inst:
		print("Unknown Error : " + str(inst))
		traceback.print_exc()
