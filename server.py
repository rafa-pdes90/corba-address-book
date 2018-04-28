import sys
from address_book_impl import AddressBookImpl
from omniORB import CORBA, PortableServer
import CosNaming


if __name__ == '__main__':
	try:
		# Initialise the ORB and find the root POA
		orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
		rootPOA = orb.resolve_initial_references("RootPOA") # No need to narrow to PortableServer.POA

		# Obtain a reference to the root naming context
		obj = orb.resolve_initial_references("NameService")
		naming = obj._narrow(CosNaming.NamingContext)

		if naming is None:
			print ("Failed to narrow the root naming context")
			sys.exit(1)

		# Create an instance of AddressBookImpl and an AddressBook object reference
		address_book = AddressBookImpl()
		objRef = address_book._this()
		
		# Bind a context named "test.my_context" to the root context
		name = [CosNaming.NameComponent("test", "my_context")]
		try:
			testContext = naming.bind_new_context(name)
			print ("New test context bound")

		except (CosNaming.NamingContext.AlreadyBound) as ex:
			print ("Test context already exists")
			obj = naming.resolve(name)
			testContext = obj._narrow(CosNaming.NamingContext)
			if testContext is None:
					print ("test.mycontext exists but is not a NamingContext")
					sys.exit(1)

		# Bind the AddressBook object to the test context
		i = 1
		while (i > 0 and i < 4): # Limited to 3 by specification of the assignment
			name_component = CosNaming.NameComponent("AddressBook", str(i))
			name = [name_component]

			try:
				testContext.bind(name, objRef)
				print ("AddressBook" + str(i) + " object bound")
				i = 0

			except (CosNaming.NamingContext.AlreadyBound):
				try:
					bound_name = [CosNaming.NameComponent("test", "my_context"), name_component]
					bound_objRef = naming.resolve(bound_name)
					bound_objRef._non_existent() # Test if obj exists
					i += 1

				except (CORBA.TRANSIENT):
					testContext.rebind(name, objRef)
					print ("AddressBook" + str(i) + " binding already existed -- rebound")
					i = 0

		if (i != 4): # Limited to 3 by specification of the assignment
			# Activate the POA
			poaManager = rootPOA._get_the_POAManager()
			poaManager.activate()

			print ("Server is Ready ...")

			# Block for ever (or until the ORB is shut down)
			orb.run()
	
	except Exception as inst:
		print("Unknown Error : " + str(inst))
		traceback.print_exc()
