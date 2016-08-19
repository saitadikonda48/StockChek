from django import forms

symbolfile = open("analyze/symbols_with_names.txt")
symbolslist = symbolfile.read()
realsymbolslist = symbolslist.split("\n")
stocklengthlist = []
newsymbolslist = zip(realsymbolslist,realsymbolslist)

class StockChoiceForm(forms.Form):
	stock_choice = forms.ChoiceField(label="",choices=newsymbolslist)

	