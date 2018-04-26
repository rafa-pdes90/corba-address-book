import Matematica, Matematica__POA

class CalculadoraImpl (Matematica__POA.Calculadora):
	def soma(self, arg1, arg2):
		print ("Soma = " + str(arg1) + " + " + str(arg2))
		return arg1 + arg2

	def divisao(self, arg1, arg2):
		print ("Divisao=" + str(arg1) + "/" + str(arg2))
		if (arg2 == 0):
			raise Matematica.DivisaoPorZero(arg1,arg2)
		return arg1 / arg2
