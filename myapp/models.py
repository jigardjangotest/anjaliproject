from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	remarks=models.TextField()

	def __str__(self):
		return self.name

class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100,default="user")
	user_image=models.ImageField(upload_to='images/')
	address=models.TextField(default="")
	

	def __str__(self):
		return self.fname+" "+self.lname

class Book(models.Model):

	Choices=(
        ('C','C'),
        ('C++','C++'),
        ('Python','Python'),
        ('Java','Java'),
        ('PHP','PHP'),
    )
	book_seller=models.ForeignKey(User,on_delete=models.CASCADE)
	book_name=models.CharField(max_length=100)
	book_author=models.CharField(max_length=100)
	book_price=models.CharField(max_length=100)
	book_image=models.ImageField(upload_to='images/')
	book_desc=models.TextField()
	book_subject=models.CharField(max_length=100,choices=Choices)

	def __str__(self):
		return self.book_name

class WishList(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	book=models.ForeignKey(Book,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" "+self.book.book_name



class Cart(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	book=models.ForeignKey(Book,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	qty=models.CharField(max_length=100,default="1")
	amount=models.CharField(max_length=100,default="0")
	net_amount=models.CharField(max_length=100,default="0")
	status=models.CharField(max_length=100,default="pending")

	def __str__(self):
		return self.user.fname+" "+self.book.book_name

class Transaction(models.Model):
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)