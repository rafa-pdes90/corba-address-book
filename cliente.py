import sys, traceback
from Matematica import *
from omniORB import CORBA
import CosNaming


if __name__ == '__main__':
	# Initialise the ORB
	orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

	# Obtain a reference to the root naming context
	obj = orb.resolve_initial_references("NameService")
	naming = obj._narrow(CosNaming.NamingContext)

	if naming is None:
		print ("Failed to narrow the root naming context")
		sys.exit(1)

	# Resolve the name "test.my_context/MatematicaCalculadora.Exemplo"
	name = [CosNaming.NameComponent("test", "my_context"),
					CosNaming.NameComponent("MatematicaCalculadora", "Exemplo")]
	try:
		objRef = naming.resolve(name)

	except (CosNaming.NamingContext.NotFound) as ex:
		print ("Name not found")
		sys.exit(1)

	# Narrow the object to an Matematica::Calculadora
	calc = objRef._narrow(Calculadora)

	if calc is None:
		print ("Object reference is not an Matematica::Calculadora")
		sys.exit(1)

	try:
		print ("5+3=" + str(calc.soma(5,3)))
		print ("5/0=" + str(calc.divisao(5,0)))
	
	except (DivisaoPorZero) as ex:
		print ("Divisao Por Zero")
		print ("A Divisao foi " + str(ex.arg1) + "/ " + str(ex.arg2))
	
	except Exception as inst:
		print("Outro Erro : " + str(inst))
		traceback.print_exc()

