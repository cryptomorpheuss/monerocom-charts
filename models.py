from django.db import models

# Create your models here.
class Coin(models.Model):
	name = models.CharField(max_length=4)
	date = models.DateField()
	priceusd = models.FloatField()
	pricebtc = models.FloatField()
	inflation = models.FloatField()
	transactions = models.FloatField()
	stocktoflow = models.FloatField()
	hashrate = models.FloatField()
	supply = models.FloatField()
	fee = models.FloatField(default="0")
	revenue = models.FloatField(default="0")

	def __str__(self):
		return self.priceusd

class Data(models.Model):
	date = models.DateField()
	XMR_price_usd = models.FloatField()
	XMR_price_btc = models.FloatField()
	XMR_color = models.FloatField()
	XMR_stock_to_flow = models.FloatField()
	XMR_grey_line = models.FloatField()

	def __str__(self):
		return self.date

class Transaction(models.Model):
	date = models.DateField()
	xmr = models.FloatField()
	btc = models.FloatField()
	zcash = models.FloatField()
	grin = models.FloatField()
	dash = models.FloatField()

	def __str__(self):
		return self.date