from django.shortcuts import render
import urllib
import requests
from bs4 import BeautifulSoup
import re
from .forms import StockChoiceForm
from datetime import datetime
from time import mktime

def analyze_stock(request):
	# Make Your Default Apple or Tesla Later
	stock_choice_made="Stock Name"
	price="$0.00"
	daily_change = "0.00"
	# Dates
	dates=[]
	# Ratios
	gross_margin_ratios=[]
	gp_e_ratios=[]
	interest_coverage_ratios=[]
	operating_margins=[]
	net_profit_margins=[]
	operating_activities=[]
	financing_activities=[]
	investment_activities=[]
	inventory_turnover_ratios=[]
	current_ratios=[]
	quick_ratios=[]
	pe_stat=0
	pe_date=0
	pb_stat=0
	pb_date=0
	return_on_assets=[]
	return_on_equities=[]
	article_names = []
	article_links = []
	article_combos = {}
	co_article_names = []
	co_article_links = []
	co_article_combos = {}
	first_table_headers = []
	first_table_data = []
	second_table_headers = []
	second_table_data = []
	competitors = []
	# Stock Name and Value
	stock_choice_made = 'AAPL'
	co_name = "aapl"
	# Competitors
	comp_url = "http://www.nasdaq.com/symbol/"+co_name+"/stock-comparison"
	htmlfile = urllib.urlopen(comp_url)
	htmltext = htmlfile.read()
	r = requests.get(comp_url)
	soup = BeautifulSoup(r.content, "html.parser")
	comp_div = soup.find_all('div',{'id':'quotes_content_left_SC_CompanyPanel'})
	comp_symb_names = soup.find_all('div',{'align':'center'})
	for thing in comp_symb_names:
		competitors.append(thing.text)
	try:
		competitors.pop()
	except:
		pass
	try:
		# Insider Trading
		insider_url = "http://www.nasdaq.com/symbol/"+co_name+"/insider-trades"
		htmlfile = urllib.urlopen(insider_url)
		htmltext = htmlfile.read()
		r = requests.get(insider_url)
		soup = BeautifulSoup(r.content, "html.parser")
		insider_divs = soup.find_all('div',{'class':'infoTable'})
		first_table_rows = insider_divs[0].find_all('tr')
		for tr in first_table_rows:
			# table headers
			headers = tr.find_all('th')
			for header in headers:
				first_table_headers.append(header.text)
			# table data
			data = tr.find_all('td')
			for datum in data:
				first_table_data.append(datum.text)
		second_table_rows = insider_divs[1].find_all('tr')
		for tr in second_table_rows:
			# table headers
			headers = tr.find_all('th')
			for header in headers:
				second_table_headers.append(header.text)
			# table data
			data = tr.find_all('td')
			for datum in data:
				second_table_data.append(datum.text)
	except:
		pass
	try:
		# Company Headines
		co_source_url = "http://www.nasdaq.com/symbol/"+co_name+"/news-headlines"
		htmlfile = urllib.urlopen(co_source_url)
		htmltext = htmlfile.read()
		r = requests.get(co_source_url)
		soup = BeautifulSoup(r.content, "html.parser")
		articles = soup.find_all('div',{'class':'news-headlines'})[0]
		article_headlines = articles.find_all('a')
		counter = 1
		for name in article_headlines:
			counter = counter + 1
			if counter%2 == 0:
				co_article_links.append(name.attrs['href'])
				co_article_names.append(name.text)
			else:
				pass
		if len(co_article_links) > 10:
			co_article_links = co_article_links[:10]
			co_article_names = co_article_names[:10]
		co_article_combos = zip(co_article_names, co_article_links)
		# Press Releases
		source_url = "http://www.nasdaq.com/symbol/"+co_name+"/press-releases"
		htmlfile = urllib.urlopen(source_url)
		htmltext = htmlfile.read()
		r = requests.get(source_url)
		soup = BeautifulSoup(r.content, "html.parser")
		articles = soup.find_all('div',{'class':'news-headlines'})[0]
		article_headlines = articles.find_all('a')
		for name in article_headlines:
			article_links.append(name.attrs['href'])
			article_names.append(name.text)
		if len(article_links) > 10:
			article_links = article_links[:10]
			article_names = article_names[:10]
		article_combos = zip(article_names, article_links)
	except:
		pass
	try:
		# Stock Data (Income Statement)
		income_statement_url = "http://www.nasdaq.com/symbol/"+co_name+"/financials?query=income-statement" 
		dates = []
		income_statement_data = []
		r = requests.get(income_statement_url)
		soup = BeautifulSoup(r.content, "html.parser")
		income_table_dates = soup.find('thead')
		htmlfile = urllib.urlopen(income_statement_url)
		htmltext = htmlfile.read()
		regex = '<div id="qwidget_lastsale" class="qwidget-dollar">(.+?)</div>'
		sec_regex = '<div id="qwidget_netchange" class="qwidget-cents qwidget-Red">(.+?)</div>'
		third_regex = '<div id="qwidget_netchange" class="qwidget-cents qwidget-Green">(.+?)</div>'
		pattern = re.compile(regex)
		sec_pattern = re.compile(sec_regex)
		third_pattern = re.compile(third_regex)
		price = re.findall(pattern, htmltext)[0]
		if len(re.findall(sec_pattern, htmltext)) != 0:
			daily_change = re.findall(sec_pattern, htmltext)[0]
			daily_change = "-"+str(daily_change)
		elif len(re.findall(third_pattern, htmltext)) != 0:
			daily_change = re.findall(third_pattern, htmltext)[0]
			daily_change = "+"+str(daily_change)
		else:
			daily_change = "+0.00"
		for th in income_table_dates.find_all('th')[2:]:
			the_date = str(th.text)
			if the_date is not "":
				dates.append(the_date)
		for td in soup.find_all('td',{"class":None}):
			if '$' in td.text:
				num = (td.text).replace("$","")
				num = num.replace(",", "")
				num = num.replace(")", "")
				num = num.replace("(","-")
				num = int(str(num))
				income_statement_data.append(num)
	except:
		pass
	try:
		# Stock Data (Cash Flow)
		cash_flow_url = "http://www.nasdaq.com/symbol/"+co_name+"/financials?query=cash-flow" 
		cash_flow_data = []
		r = requests.get(cash_flow_url)
		soup = BeautifulSoup(r.content, "html.parser")
		for td in soup.find_all('td',{"class":None}):
			if '$' in td.text:
				num = (td.text).replace("$","")
				num = num.replace(",", "")
				num = num.replace(")", "")
				num = num.replace("(","-")
				num = str(num)
				cash_flow_data.append(num)
	except:
		pass
	try:
		# Balance Sheet Data
		balance_sheet_url = "http://www.nasdaq.com/symbol/"+co_name+"/financials?query=balance-sheet" 
		balance_sheet_data = []
		r = requests.get(balance_sheet_url)
		soup = BeautifulSoup(r.content, "html.parser")
		for td in soup.find_all('td',{"class":None}):
			if '$' in td.text:
				num = (td.text).replace("$","")
				num = num.replace(",", "")
				num = num.replace(")", "")
				num = num.replace("(","-")
				num = int(str(num))
				balance_sheet_data.append(num)
	except:
		pass
	try:
		# Price/Earnings Ratio
		pe_url = "https://ycharts.com/companies/"+str(stock_choice_made)+"/pe_ratio"
		htmlfile = urllib.urlopen(pe_url)
		htmltext = htmlfile.read()
		regex = '<span id="pgNameVal">(.+?)</span>'
		pattern = re.compile(regex)
		pe_info = re.findall(pattern, htmltext)[0]
		pe_stat,pe_date = str(pe_info).split(" for ")
		# Price/Book Ratio
		pb_url = "https://ycharts.com/companies/"+str(stock_choice_made)+"/price_to_book_value"
		htmlfile = urllib.urlopen(pb_url)
		htmltext = htmlfile.read()
		regex = '<span id="pgNameVal">(.+?)</span>'
		pattern = re.compile(regex)
		pb_info = re.findall(pattern, htmltext)[0]
		pb_stat,pb_date = str(pb_info).split(" for ")
	except:
		pass
	try:
		# Gross Margin Ratio
		gross_margin_ratios.append(round((1.0*income_statement_data[8]/income_statement_data[0])*100,1))
		gross_margin_ratios.append(round((1.0*income_statement_data[9]/income_statement_data[1])*100,1))
		gross_margin_ratios.append(round((1.0*income_statement_data[10]/income_statement_data[2])*100,1))
		gross_margin_ratios.append(round((1.0*income_statement_data[11]/income_statement_data[3])*100,1))
		# Gross Profit / Expense Ratio
		try:
			gp_e_ratios.append(round((1.0*income_statement_data[8]/income_statement_data[16])*100,1))
		except:
			gp_e_ratios.append(float("inf"))
		try:
			gp_e_ratios.append(round((1.0*income_statement_data[9]/income_statement_data[17])*100,1))
		except:
			gp_e_ratios.append(float("inf"))
		try:
			gp_e_ratios.append(round((1.0*income_statement_data[10]/income_statement_data[18])*100,1))
		except:
			gp_e_ratios.append(float("inf"))
		try:
			gp_e_ratios.append(round((1.0*income_statement_data[11]/income_statement_data[19])*100,1))
		except:
			gp_e_ratios.append(float("inf"))
			
		# Interest Coverage Ratio
		try:
			interest_coverage_ratios.append(round((1.0*income_statement_data[18]/income_statement_data[22]),1))
		except:
			interest_coverage_ratios.append(float("inf"))
		try:
			interest_coverage_ratios.append(round((1.0*income_statement_data[19]/income_statement_data[23]),1))
		except:
			interest_coverage_ratios.append(float("inf"))
		try:	
			interest_coverage_ratios.append(round((1.0*income_statement_data[20]/income_statement_data[24]),1))
		except:
			interest_coverage_ratios.append(float("inf"))
		try:
			interest_coverage_ratios.append(round((1.0*income_statement_data[21]/income_statement_data[25]),1))
		except:
			interest_coverage_ratios.append(float("inf"))

		# Operating Margin
		try:
			operating_margins.append(round((1.0*income_statement_data[28]/income_statement_data[8])*100,1))
		except:
			operating_margins.append(float("inf"))
		try:
			operating_margins.append(round((1.0*income_statement_data[29]/income_statement_data[9])*100,1))
		except:
			operating_margins.append(float("inf"))
		try:
			operating_margins.append(round((1.0*income_statement_data[30]/income_statement_data[10])*100,1))
		except:
			operating_margins.append(float("inf"))
		try:
			operating_margins.append(round((1.0*income_statement_data[31]/income_statement_data[11])*100,1))
		except:
			operating_margins.append(float("inf"))

		# Net Profit Margins
		try:
			net_profit_margins.append(round((1.0*income_statement_data[60]/income_statement_data[8])*100,1))
		except:
			net_profit_margins.append(float("inf"))
		try:
			net_profit_margins.append(round((1.0*income_statement_data[61]/income_statement_data[9])*100,1))
		except:
			net_profit_margins.append(float("inf"))
		try:
			net_profit_margins.append(round((1.0*income_statement_data[62]/income_statement_data[10])*100,1))
		except:
			net_profit_margins.append(float("inf"))
		try:
			net_profit_margins.append(round((1.0*income_statement_data[63]/income_statement_data[11])*100,1))
		except:
			net_profit_margins.append(float("inf"))

		# Cash Flow Data
		operating_activities.append(cash_flow_data[28])
		operating_activities.append(cash_flow_data[29])
		operating_activities.append(cash_flow_data[30])
		operating_activities.append(cash_flow_data[31])
		financing_activities.append(cash_flow_data[68])
		financing_activities.append(cash_flow_data[69])
		financing_activities.append(cash_flow_data[70])
		financing_activities.append(cash_flow_data[71])
		investment_activities.append(cash_flow_data[44])
		investment_activities.append(cash_flow_data[45])
		investment_activities.append(cash_flow_data[46])
		investment_activities.append(cash_flow_data[47])

		# Inventory Turnover Ratio
		inventory_turnover_ratios.append(round((1.0*income_statement_data[4]/balance_sheet_data[12])/100,2))
		inventory_turnover_ratios.append(round((1.0*income_statement_data[5]/balance_sheet_data[13])/100,2))
		inventory_turnover_ratios.append(round((1.0*income_statement_data[6]/balance_sheet_data[14])/100,2))
		inventory_turnover_ratios.append(round((1.0*income_statement_data[7]/balance_sheet_data[15])/100,2))
		# Current Ratio
		current_ratios.append(round(100.0*balance_sheet_data[20]/balance_sheet_data[64],1))
		current_ratios.append(round(100.0*balance_sheet_data[21]/balance_sheet_data[65],1))
		current_ratios.append(round(100.0*balance_sheet_data[22]/balance_sheet_data[66],1))
		current_ratios.append(round(100.0*balance_sheet_data[23]/balance_sheet_data[67],1))
		# Quick Ratio
		quick_ratios.append(round(100.0*(balance_sheet_data[20]-balance_sheet_data[12])/balance_sheet_data[64],1))
		quick_ratios.append(round(100.0*(balance_sheet_data[21]-balance_sheet_data[13])/balance_sheet_data[65],1))
		quick_ratios.append(round(100.0*(balance_sheet_data[22]-balance_sheet_data[14])/balance_sheet_data[66],1))
		quick_ratios.append(round(100.0*(balance_sheet_data[23]-balance_sheet_data[15])/balance_sheet_data[67],1))
		# Return On Assets
		return_on_assets.append(round(100.0*income_statement_data[64]/balance_sheet_data[48],1))
		return_on_assets.append(round(100.0*income_statement_data[65]/balance_sheet_data[49],1))
		return_on_assets.append(round(100.0*income_statement_data[66]/balance_sheet_data[50],1))
		return_on_assets.append(round(100.0*income_statement_data[67]/balance_sheet_data[51],1))
		# Return On Equity
		return_on_equities.append(round(100.0*income_statement_data[64]/balance_sheet_data[112],1))
		return_on_equities.append(round(100.0*income_statement_data[65]/balance_sheet_data[113],1))
		return_on_equities.append(round(100.0*income_statement_data[66]/balance_sheet_data[114],1))
		return_on_equities.append(round(100.0*income_statement_data[67]/balance_sheet_data[115],1))
	except:
		pass
	# Pick your stock
	stockChoiceForm = StockChoiceForm(request.POST or None )
	if stockChoiceForm.is_valid():
		# Dates
		dates=[]
		# Ratios
		gross_margin_ratios=[]
		gp_e_ratios=[]
		interest_coverage_ratios=[]
		operating_margins=[]
		net_profit_margins=[]
		operating_activities=[]
		financing_activities=[]
		investment_activities=[]
		inventory_turnover_ratios=[]
		current_ratios=[]
		quick_ratios=[]
		pe_stat=0
		pe_date=0
		pb_stat=0
		pb_date=0
		return_on_assets=[]
		return_on_equities=[]
		article_names = []
		article_links = []
		article_combos = {}
		co_article_names = []
		co_article_links = []
		co_article_combos = {}
		first_table_headers = []
		first_table_data = []
		second_table_headers = []
		second_table_data = []
		competitors = []
		# Stock Name and Value
		stock_choice_made = stockChoiceForm.cleaned_data.get('stock_choice')
		stock_choice_made = stock_choice_made.split("	")[0]
		co_name = str(stock_choice_made.lower())
		# Insider Trading
		insider_url = "http://www.nasdaq.com/symbol/"+co_name+"/insider-trades"
		htmlfile = urllib.urlopen(insider_url)
		htmltext = htmlfile.read()
		r = requests.get(insider_url)
		soup = BeautifulSoup(r.content, "html.parser")
		insider_divs = soup.find_all('div',{'class':'infoTable'})
		first_table_rows = insider_divs[0].find_all('tr')
		for tr in first_table_rows:
			# table headers
			headers = tr.find_all('th')
			for header in headers:
				first_table_headers.append(header.text)
			# table data
			data = tr.find_all('td')
			for datum in data:
				first_table_data.append(datum.text)
		second_table_rows = insider_divs[1].find_all('tr')
		for tr in second_table_rows:
			# table headers
			headers = tr.find_all('th')
			for header in headers:
				second_table_headers.append(header.text)
			# table data
			data = tr.find_all('td')
			for datum in data:
				second_table_data.append(datum.text)
		# Company Headines
		co_source_url = "http://www.nasdaq.com/symbol/"+co_name+"/news-headlines"
		htmlfile = urllib.urlopen(co_source_url)
		htmltext = htmlfile.read()
		r = requests.get(co_source_url)
		soup = BeautifulSoup(r.content, "html.parser")
		articles = soup.find_all('div',{'class':'news-headlines'})[0]
		article_headlines = articles.find_all('a')
		counter = 1
		for name in article_headlines:
			counter = counter + 1
			if counter%2 == 0:
				co_article_links.append(name.attrs['href'])
				co_article_names.append(name.text)
			else:
				pass
		if len(co_article_links) > 10:
			co_article_links = co_article_links[:10]
			co_article_names = co_article_names[:10]
		co_article_combos = zip(co_article_names, co_article_links)
		# Press Releases
		source_url = "http://www.nasdaq.com/symbol/"+co_name+"/press-releases"
		htmlfile = urllib.urlopen(source_url)
		htmltext = htmlfile.read()
		r = requests.get(source_url)
		soup = BeautifulSoup(r.content, "html.parser")
		articles = soup.find_all('div',{'class':'news-headlines'})[0]
		article_headlines = articles.find_all('a')
		for name in article_headlines:
			article_links.append(name.attrs['href'])
			article_names.append(name.text)
		if len(article_links) > 10:
			article_links = article_links[:10]
			article_names = article_names[:10]
		article_combos = zip(article_names, article_links)
		try:
			# Competitors
			comp_url = "http://www.nasdaq.com/symbol/"+co_name+"/stock-comparison"
			htmlfile = urllib.urlopen(comp_url)
			htmltext = htmlfile.read()
			r = requests.get(comp_url)
			soup = BeautifulSoup(r.content, "html.parser")
			comp_div = soup.find_all('div',{'id':'quotes_content_left_SC_CompanyPanel'})
			comp_symb_names = soup.find_all('div',{'align':'center'})
			for thing in comp_symb_names:
				competitors.append(thing.text)
			try:
				competitors.pop()
			except:
				pass
			# Stock Data (Income Statement)
			income_statement_url = "http://www.nasdaq.com/symbol/"+co_name+"/financials?query=income-statement" 
			dates = []
			income_statement_data = []
			r = requests.get(income_statement_url)
			soup = BeautifulSoup(r.content, "html.parser")
			income_table_dates = soup.find('thead')
			htmlfile = urllib.urlopen(income_statement_url)
			htmltext = htmlfile.read()
			regex = '<div id="qwidget_lastsale" class="qwidget-dollar">(.+?)</div>'
			sec_regex = '<div id="qwidget_netchange" class="qwidget-cents qwidget-Red">(.+?)</div>'
			third_regex = '<div id="qwidget_netchange" class="qwidget-cents qwidget-Green">(.+?)</div>'
			pattern = re.compile(regex)
			sec_pattern = re.compile(sec_regex)
			third_pattern = re.compile(third_regex)
			price = re.findall(pattern, htmltext)[0]
			if len(re.findall(sec_pattern, htmltext)) != 0:
				daily_change = re.findall(sec_pattern, htmltext)[0]
				daily_change = "-"+str(daily_change)
			elif len(re.findall(third_pattern, htmltext)) != 0:
				daily_change = re.findall(third_pattern, htmltext)[0]
				daily_change = "+"+str(daily_change)
			else:
				daily_change = "+0.00"
			for th in income_table_dates.find_all('th')[2:]:
				the_date = str(th.text)
				if the_date is not "":
					dates.append(the_date)
			for td in soup.find_all('td',{"class":None}):
				if '$' in td.text:
					num = (td.text).replace("$","")
					num = num.replace(",", "")
					num = num.replace(")", "")
					num = num.replace("(","-")
					num = int(str(num))
					income_statement_data.append(num)
			# Stock Data (Cash Flow)
			cash_flow_url = "http://www.nasdaq.com/symbol/"+co_name+"/financials?query=cash-flow" 
			cash_flow_data = []
			r = requests.get(cash_flow_url)
			soup = BeautifulSoup(r.content, "html.parser")
			for td in soup.find_all('td',{"class":None}):
				if '$' in td.text:
					num = (td.text).replace("$","")
					num = num.replace(",", "")
					num = num.replace(")", "")
					num = num.replace("(","-")
					num = str(num)
					cash_flow_data.append(num)
			# Balance Sheet Data
			balance_sheet_url = "http://www.nasdaq.com/symbol/"+co_name+"/financials?query=balance-sheet" 
			balance_sheet_data = []
			r = requests.get(balance_sheet_url)
			soup = BeautifulSoup(r.content, "html.parser")
			for td in soup.find_all('td',{"class":None}):
				if '$' in td.text:
					num = (td.text).replace("$","")
					num = num.replace(",", "")
					num = num.replace(")", "")
					num = num.replace("(","-")
					num = int(str(num))
					balance_sheet_data.append(num)
			# Price/Earnings Ratio
			try:
				pe_url = "https://ycharts.com/companies/"+str(stock_choice_made)+"/pe_ratio"
				htmlfile = urllib.urlopen(pe_url)
				htmltext = htmlfile.read()
				regex = '<span id="pgNameVal">(.+?)</span>'
				pattern = re.compile(regex)
				pe_info=re.findall(pattern, htmltext)[0]
				pe_stat,pe_date = str(pe_info).split(" for ")
				# Price/Book Ratio
				pb_url = "https://ycharts.com/companies/"+str(stock_choice_made)+"/price_to_book_value"
				htmlfile = urllib.urlopen(pb_url)
				htmltext = htmlfile.read()
				regex = '<span id="pgNameVal">(.+?)</span>'
				pattern = re.compile(regex)
				pb_info = re.findall(pattern, htmltext)[0]
				pb_stat,pb_date = str(pb_info).split(" for ")
			except:
				pe_stat,pe_date,pb_stat,pb_date="N/A","N/A","N/A","N/A"

			if len(dates) == 3:

				# Gross Margin Ratio
				gross_margin_ratios.append(round((1.0*income_statement_data[6]/income_statement_data[0])*100,1))
				gross_margin_ratios.append(round((1.0*income_statement_data[7]/income_statement_data[1])*100,1))
				gross_margin_ratios.append(round((1.0*income_statement_data[8]/income_statement_data[2])*100,1))
				# Gross Profit / Expense Ratio
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[6]/income_statement_data[12])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[7]/income_statement_data[13])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[8]/income_statement_data[14])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
				# Interest Coverage Ratio
				try:
					interest_coverage_ratios.append(round((1.0*income_statement_data[27]/income_statement_data[30]),1))
				except:
					interest_coverage_ratios.append(float("inf"))
				try:
					interest_coverage_ratios.append(round((1.0*income_statement_data[28]/income_statement_data[31]),1))
				except:
					interest_coverage_ratios.append(float("inf"))
				try:	
					interest_coverage_ratios.append(round((1.0*income_statement_data[29]/income_statement_data[32]),1))
				except:
					interest_coverage_ratios.append(float("inf"))
				# Operating Margin
				try:
					operating_margins.append(round((1.0*income_statement_data[24]/income_statement_data[6])*100,1))
				except:
					operating_margins.append(float("inf"))
				try:
					operating_margins.append(round((1.0*income_statement_data[25]/income_statement_data[7])*100,1))
				except:
					operating_margins.append(float("inf"))
				try:
					operating_margins.append(round((1.0*income_statement_data[26]/income_statement_data[8])*100,1))
				except:
					operating_margins.append(float("inf"))
				# Net Profit Margins
				try:
					net_profit_margins.append(round((1.0*income_statement_data[48]/income_statement_data[6])*100,1))
				except:
					net_profit_margins.append(float("inf"))
				try:
					net_profit_margins.append(round((1.0*income_statement_data[49]/income_statement_data[7])*100,1))
				except:
					net_profit_margins.append(float("inf"))
				try:
					net_profit_margins.append(round((1.0*income_statement_data[50]/income_statement_data[8])*100,1))
				except:
					net_profit_margins.append(float("inf"))
				# Cash Flow Data
				operating_activities.append(cash_flow_data[21])
				operating_activities.append(cash_flow_data[22])
				operating_activities.append(cash_flow_data[23])
				financing_activities.append(cash_flow_data[51])
				financing_activities.append(cash_flow_data[52])
				financing_activities.append(cash_flow_data[53])
				investment_activities.append(cash_flow_data[33])
				investment_activities.append(cash_flow_data[34])
				investment_activities.append(cash_flow_data[35])
				# Inventory Turnover Ratio
				try:
					inventory_turnover_ratios.append(round((1.0*income_statement_data[3]/balance_sheet_data[9])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				try:	
					inventory_turnover_ratios.append(round((1.0*income_statement_data[4]/balance_sheet_data[10])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				try:
					inventory_turnover_ratios.append(round((1.0*income_statement_data[6]/balance_sheet_data[11])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				# Current Ratio
				try:
					current_ratios.append(round(100.0*balance_sheet_data[15]/balance_sheet_data[48],1))
				except:
					current_ratios.append(float("inf"))
				try:
					current_ratios.append(round(100.0*balance_sheet_data[16]/balance_sheet_data[49],1))
				except:
					current_ratios.append(float("inf"))
				try:
					current_ratios.append(round(100.0*balance_sheet_data[17]/balance_sheet_data[50],1))
				except:
					current_ratios.append(float("inf"))
				# Quick Ratio
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[15]-balance_sheet_data[9])/balance_sheet_data[48],1))
				except:
					quick_ratios.append(float("inf"))
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[16]-balance_sheet_data[10])/balance_sheet_data[49],1))
				except:
					quick_ratios.append(float("inf"))
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[17]-balance_sheet_data[11])/balance_sheet_data[50],1))
				except:
					quick_ratios.append(float("inf"))
				# Return On Assets
				try:
					return_on_assets.append(round(100.0*income_statement_data[48]/balance_sheet_data[36],1))
				except:
					return_on_assets.append(float("inf"))
				try:
					return_on_assets.append(round(100.0*income_statement_data[49]/balance_sheet_data[35],1))
				except:
					return_on_assets.append(float("inf"))
				try:
					return_on_assets.append(round(100.0*income_statement_data[50]/balance_sheet_data[34],1))
				except:
					return_on_assets.append(float("inf"))
				# Return On Equity
				try:
					return_on_equities.append(round(100.0*income_statement_data[48]/balance_sheet_data[84],1))
				except:
					return_on_equities.append(float("inf"))
				try:
					return_on_equities.append(round(100.0*income_statement_data[49]/balance_sheet_data[85],1))
				except:
					return_on_equities.append(float("inf"))
				try:
					return_on_equities.append(round(100.0*income_statement_data[50]/balance_sheet_data[86],1))			
				except:
					return_on_equities.append(float("inf"))
			if len(dates) == 4:
				# Gross Margin Ratio
				gross_margin_ratios.append(round((1.0*income_statement_data[8]/income_statement_data[0])*100,1))
				gross_margin_ratios.append(round((1.0*income_statement_data[9]/income_statement_data[1])*100,1))
				gross_margin_ratios.append(round((1.0*income_statement_data[10]/income_statement_data[2])*100,1))
				gross_margin_ratios.append(round((1.0*income_statement_data[11]/income_statement_data[3])*100,1))

				# Gross Profit / Expense Ratio
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[8]/income_statement_data[16])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[9]/income_statement_data[17])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[10]/income_statement_data[18])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
				try:
					gp_e_ratios.append(round((1.0*income_statement_data[11]/income_statement_data[19])*100,1))
				except:
					gp_e_ratios.append(float("inf"))
					
				# Interest Coverage Ratio
				try:
					interest_coverage_ratios.append(round((1.0*income_statement_data[18]/income_statement_data[22]),1))
				except:
					interest_coverage_ratios.append(float("inf"))
				try:
					interest_coverage_ratios.append(round((1.0*income_statement_data[19]/income_statement_data[23]),1))
				except:
					interest_coverage_ratios.append(float("inf"))
				try:	
					interest_coverage_ratios.append(round((1.0*income_statement_data[20]/income_statement_data[24]),1))
				except:
					interest_coverage_ratios.append(float("inf"))
				try:
					interest_coverage_ratios.append(round((1.0*income_statement_data[21]/income_statement_data[25]),1))
				except:
					interest_coverage_ratios.append(float("inf"))

				# Operating Margin
				try:
					operating_margins.append(round((1.0*income_statement_data[28]/income_statement_data[8])*100,1))
				except:
					operating_margins.append(float("inf"))
				try:
					operating_margins.append(round((1.0*income_statement_data[29]/income_statement_data[9])*100,1))
				except:
					operating_margins.append(float("inf"))
				try:
					operating_margins.append(round((1.0*income_statement_data[30]/income_statement_data[10])*100,1))
				except:
					operating_margins.append(float("inf"))
				try:
					operating_margins.append(round((1.0*income_statement_data[31]/income_statement_data[11])*100,1))
				except:
					operating_margins.append(float("inf"))

				# Net Profit Margins
				try:
					net_profit_margins.append(round((1.0*income_statement_data[60]/income_statement_data[8])*100,1))
				except:
					net_profit_margins.append(float("inf"))
				try:
					net_profit_margins.append(round((1.0*income_statement_data[61]/income_statement_data[9])*100,1))
				except:
					net_profit_margins.append(float("inf"))
				try:
					net_profit_margins.append(round((1.0*income_statement_data[62]/income_statement_data[10])*100,1))
				except:
					net_profit_margins.append(float("inf"))
				try:
					net_profit_margins.append(round((1.0*income_statement_data[63]/income_statement_data[11])*100,1))
				except:
					net_profit_margins.append(float("inf"))

				# Cash Flow Data
				operating_activities.append(cash_flow_data[28])
				operating_activities.append(cash_flow_data[29])
				operating_activities.append(cash_flow_data[30])
				operating_activities.append(cash_flow_data[31])
				financing_activities.append(cash_flow_data[68])
				financing_activities.append(cash_flow_data[69])
				financing_activities.append(cash_flow_data[70])
				financing_activities.append(cash_flow_data[71])
				investment_activities.append(cash_flow_data[44])
				investment_activities.append(cash_flow_data[45])
				investment_activities.append(cash_flow_data[46])
				investment_activities.append(cash_flow_data[47])
				# Inventory Turnover Ratio
				try:
					inventory_turnover_ratios.append(round((1.0*income_statement_data[4]/balance_sheet_data[12])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				try:	
					inventory_turnover_ratios.append(round((1.0*income_statement_data[5]/balance_sheet_data[13])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				try:
					inventory_turnover_ratios.append(round((1.0*income_statement_data[6]/balance_sheet_data[14])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				try:
					inventory_turnover_ratios.append(round((1.0*income_statement_data[7]/balance_sheet_data[15])/100,2))
				except:
					inventory_turnover_ratios.append(float("inf"))
				# Current Ratio
				try:
					current_ratios.append(round(100.0*balance_sheet_data[20]/balance_sheet_data[64],1))
				except:
					current_ratios.append(float("inf"))
				try:
					current_ratios.append(round(100.0*balance_sheet_data[21]/balance_sheet_data[65],1))
				except:
					current_ratios.append(float("inf"))
				try:
					current_ratios.append(round(100.0*balance_sheet_data[22]/balance_sheet_data[66],1))
				except:
					current_ratios.append(float("inf"))
				try:
					current_ratios.append(round(100.0*balance_sheet_data[23]/balance_sheet_data[67],1))
				except:
					current_ratios.append(float("inf"))
				# Quick Ratio
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[20]-balance_sheet_data[12])/balance_sheet_data[64],1))
				except:
					quick_ratios.append(float("inf"))
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[21]-balance_sheet_data[13])/balance_sheet_data[65],1))
				except:
					quick_ratios.append(float("inf"))
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[22]-balance_sheet_data[14])/balance_sheet_data[66],1))
				except:
					quick_ratios.append(float("inf"))
				try:
					quick_ratios.append(round(100.0*(balance_sheet_data[23]-balance_sheet_data[15])/balance_sheet_data[67],1))
				except:
					quick_ratios.append(float("inf"))
				# Return On Assets
				return_on_assets.append(round(100.0*income_statement_data[64]/balance_sheet_data[48],1))
				return_on_assets.append(round(100.0*income_statement_data[65]/balance_sheet_data[49],1))
				return_on_assets.append(round(100.0*income_statement_data[66]/balance_sheet_data[50],1))
				return_on_assets.append(round(100.0*income_statement_data[67]/balance_sheet_data[51],1))
				# Return On Equity
				return_on_equities.append(round(100.0*income_statement_data[64]/balance_sheet_data[112],1))
				return_on_equities.append(round(100.0*income_statement_data[65]/balance_sheet_data[113],1))
				return_on_equities.append(round(100.0*income_statement_data[66]/balance_sheet_data[114],1))
				return_on_equities.append(round(100.0*income_statement_data[67]/balance_sheet_data[115],1))
		except:
			pass
		
	content = {
		"stock_choice_made":stock_choice_made,
		"price":price,
		"stockChoiceForm":stockChoiceForm,
		"dates":dates,
		"gross_margin_ratios":gross_margin_ratios,
		"gp_e_ratios":gp_e_ratios,
		"interest_coverage_ratios":interest_coverage_ratios,
		"operating_margins":operating_margins,
		"net_profit_margins":net_profit_margins,
		"operating_activities":operating_activities,
		"financing_activities":financing_activities,
		"investment_activities":investment_activities,
		"inventory_turnover_ratios":inventory_turnover_ratios,
		"current_ratios":current_ratios,
		"quick_ratios":quick_ratios,
		"pe_date":pe_date,
		"pe_stat":pe_stat,
		"daily_change":daily_change,
		"pb_date":pb_date,
		"pb_stat":pb_stat,
		"return_on_assets":return_on_assets,
		"return_on_equities":return_on_equities,
		"article_combos":article_combos,
		"co_article_combos":co_article_combos,
		"first_table_headers":first_table_headers,
		"first_table_data":first_table_data,
		"second_table_headers":second_table_headers,
		"second_table_data":second_table_data,
		"competitors":competitors,
	}
	return render(request,'analyze_stock.html',content)

def barchart(request):
	stock_picks = []
	barchart_link = "http://www.barchart.com/stocks/signals/top100?s=sm"
	r = requests.get(barchart_link)
	soup = BeautifulSoup(r.content, "html.parser")
	tables = soup.find_all('table',{"id":"dt1"})
	main_table = tables[0]
	table_data = main_table.find_all('tr')
	for tr in table_data[1:]:
		percents = tr.find_all('td')
		int_percents = []
		if "Buy" in str(percents[4].text):
			int_percents.append(int(str(percents[4].text).replace("% Buy","")))
		elif "Sell" in str(percents[4].text):
			int_percents.append(int(str(percents[4].text).replace("% Sell","")))
		else:
			pass
		if "Buy" in str(percents[5].text):
			int_percents.append(int(str(percents[5].text).replace("% Buy","")))
		elif "Sell" in str(percents[5].text):
			int_percents.append(int(str(percents[5].text).replace("% Sell","")))
		else:
			pass
		if "Buy" in str(percents[6].text):
			int_percents.append(int(str(percents[6].text).replace("% Buy","")))
		elif "Sell" in str(percents[6].text):
			int_percents.append(int(str(percents[6].text).replace("% Sell","")))
		else:
			pass
		if "Buy" in str(percents[7].text):
			int_percents.append(int(str(percents[7].text).replace("% Buy","")))
		elif "Sell" in str(percents[7].text):
			int_percents.append(int(str(percents[7].text).replace("% Sell","")))
		else:
			pass
		arr_len = len(int_percents)
		for percentage in int_percents:
			if percentage > 84:
				arr_len = arr_len - 1
		if arr_len == 0:
			change = str(percents[3].text)
			avg = round(1.0*sum(int_percents)/len(int_percents),1)-90
			if change == 'unch':
				change = '0.00'
			else:
				pass
			made_cut = str(percents[0].text),str(percents[1].text),str(percents[2].text),change,avg
			stock_picks.append(made_cut)

	return render(request, 'hotlist.html',{"stock_picks":stock_picks})
