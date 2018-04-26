import sys
from agenda_impl import *
import CosNaming
from omniORB import CORBA, PortableServer


if __name__ == '__main__':
	# Initialise the ORB and find the root POA
	orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
	rootPOA = orb.resolve_initial_references("RootPOA") # No need to narrow to PortableServer.POA

	# Obtain a reference to the root naming context
	obj = orb.resolve_initial_references("NameService")
	naming = obj._narrow(CosNaming.NamingContext)

	if naming is None:
		print ("Failed to narrow the root naming context")
		sys.exit(1)

	# Create an instance of CalculadoraImpl and an Calculadora object reference
	calc = agenda_impl()
	objRef = calc._this()
	
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

	# Bind the Calculadora object to the test context
	name = [CosNaming.NameComponent("MatematicaCalculadora", "Exemplo")]
	try:
			testContext.bind(name, objRef)
			print ("New MatematicaCalculadora object bound")

	except (CosNaming.NamingContext.AlreadyBound):
			testContext.rebind(name, objRef)
			print ("MatematicaCalculadora binding already existed -- rebound")

	# Activate the POA
	poaManager = rootPOA._get_the_POAManager()
	poaManager.activate()

	print ("Servidor Pronto ...")

	# Block for ever (or until the ORB is shut down)
	orb.run()
