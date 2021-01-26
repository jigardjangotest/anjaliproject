from django.shortcuts import render,redirect
from .models import Contact,User,Book,WishList,Cart,Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse

# Create your views here.

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=username).exists()
    }
    return JsonResponse(data)
def validate_login(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=username).exists()
    }
    return JsonResponse(data)

def initiate_payment(request):
	if request.method=="POST":

	    try:
	        amount = int(request.POST['final_amount'])
	        print(amount)
	    except:
	        return render(request, 'mycart.html', context={'error': 'Wrong Accound Details or amount'})

	    transaction = Transaction.objects.create(amount=amount)
	    transaction.save()
	    merchant_key = settings.PAYTM_SECRET_KEY

	    params = (
	        ('MID', settings.PAYTM_MERCHANT_ID),
	        ('ORDER_ID', str(transaction.order_id)),
	        ('CUST_ID', str(request.session['email'])),
	        ('TXN_AMOUNT', str(transaction.amount)),
	        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
	        ('WEBSITE', settings.PAYTM_WEBSITE),
	        # ('EMAIL', request.user.email),
	        # ('MOBILE_N0', '9911223388'),
	        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
	        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
	        # ('PAYMENT_MODE_ONLY', 'NO'),
	    )
	    paytm_params = dict(params)
	    checksum = generate_checksum(paytm_params, merchant_key)
	    transaction.checksum = checksum
	    transaction.save()
	    
	    paytm_params['CHECKSUMHASH'] = checksum
	    print('SENT: ', checksum)
	    user=User.objects.get(email=request.session['email'])
	    carts=Cart.objects.filter(user=user,status="pending")
	    for i in carts:
	    	i.status="completed"
	    	i.save()
	    return render(request, 'redirect.html',context=paytm_params)
	else:
		pass

@csrf_exempt
def callback(request):

	if request.method == 'POST':
		received_data = dict(request.POST)
		print(received_data)
		paytm_params = {}

		paytm_checksum = received_data['CHECKSUMHASH']
		
		for key, value in received_data.items():
			if key == 'CHECKSUMHASH':
				paytm_checksum = value
			else:
				paytm_params[key] = str(value)
		
		is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
		
		if is_valid_checksum:
			
			received_data['message'] = "Checksum Matched"
		else:
			received_data['message'] = "Checksum Mismatched"
			return render(request, 'callback.html', context=received_data)
		
		return render(request, 'callback.html', context=received_data)


def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html')

def add_book(request):
	if request.method=="POST":

		Book.objects.create(
				book_subject=request.POST['book_subject'],
				book_name=request.POST['book_name'],
				book_author=request.POST['book_author'],
				book_price=request.POST['book_price'],
				book_desc=request.POST['book_desc'],
				book_image=request.FILES['book_image'],
				book_seller=User.objects.get(email=request.session['email'],)
			)
		msg="Book Added Successfully"
		return render(request,'add_book.html',{'msg':msg})
	else:
		return render(request,'add_book.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			mobile=request.POST['mobile'],
			remarks=request.POST['remarks']
		)
		contacts=Contact.objects.all().order_by('-id')
		msg="Contact Saved Successfully"
		return render(request,'contact.html',{'msg':msg,'contacts':contacts})

	else:
		contacts=Contact.objects.all().order_by('-id')
		return render(request,'contact.html',{'contacts':contacts})

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
				email=request.POST['email'],
				password=request.POST['password']
			)
			if user.usertype=="user":
				request.session['fname']=user.fname
				request.session['lname']=user.lname
				request.session['email']=user.email
				request.session['user_image']=user.user_image.url
				wishlist=WishList.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlist)
				cart=Cart.objects.filter(user=user)
				request.session['cart_count']=len(cart)
				return render(request,'index.html')
			elif user.usertype=="seller":
				request.session['fname']=user.fname
				request.session['lname']=user.lname
				request.session['email']=user.email
				request.session['user_image']=user.user_image.url
				return render(request,'seller_index.html')
		except Exception as e:
			print(e)
			msg="User Name Or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})	
	else:
		return render(request,'login.html')

def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="EMail Id Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						password=request.POST['password'],
						cpassword=request.POST['cpassword'],
						usertype=request.POST['usertype'],
						user_image=request.FILES['user_image'],
					)
				msg="Signup Successfull"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})		
	else:
		return render(request,'signup.html')

def logout(request):
	try:
		del request.session['fname']
		del request.session['lname']
		del request.session['email']
		del request.session['user_image']
		del request.session['wishlist_count']
		del request.session['cart_count']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.session['email'])
			if user.password==request.POST['old_password']:
				if request.POST['npassword']==request.POST['cnpassword']:
					user.password=request.POST['npassword']
					user.cpassword=request.POST['npassword']
					user.save()
					return redirect('logout')
				else:
					msg="New Password & Confirm New Password Does Not Matched"
					return render(request,'change_password.html',{'msg':msg})
			else:
				msg="Old Password Is Incorrect"
				return render(request,'change_password.html',{'msg':msg})
		except:
			pass
	else:
		return render(request,'change_password.html')

def view_book(request):
	user=User.objects.get(email=request.session['email'])
	books=Book.objects.filter(book_seller=user)
	return render(request,'view_books.html',{'books':books})

def book_detail(request,pk):
	user=User.objects.get(email=request.session['email'])
	book=Book.objects.get(book_seller=user,pk=pk)
	return render(request,'book_detail.html',{'book':book})

def edit_book(request,pk):
	if request.method=="POST":

		user=User.objects.get(email=request.session['email'])
		book=Book.objects.get(book_seller=user,pk=pk)
		book.book_subject=request.POST['book_subject']
		book.book_name=request.POST['book_name']
		book.book_author=request.POST['book_author']
		book.book_price=request.POST['book_price']
		book.book_desc=request.POST['book_desc']

		try:
			book.book_image=request.FILES['book_image']
		except:
			pass
		book.save()
		msg="Book Updated Successfully"
		books=Book.objects.filter(book_seller=user)
		return render(request,'view_books.html',{'books':books,'msg':msg})
	else:

		user=User.objects.get(email=request.session['email'])
		book=Book.objects.get(book_seller=user,pk=pk)
		return render(request,'edit_book.html',{'book':book})

def delete_book(request,pk):
	user=User.objects.get(email=request.session['email'])
	book=Book.objects.get(book_seller=user,pk=pk)
	book.delete()
	msg="Book Deleted Successfully"
	books=Book.objects.filter(book_seller=user)
	return render(request,'view_books.html',{'books':books,'msg':msg})

def book(request,bname):
	books=Book.objects.filter(book_name__contains=bname)
	return render(request,'show_books.html',{'books':books})

def user_book_detail(request,pk):
	flag=False
	flag1=False
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	try:
		wishlist=WishList.objects.get(user=user,book=book)
		flag=True
	except:
		pass
	try:
		cart=Cart.objects.get(user=user,book=book,status="pending")
		flag1=True
	except:
		pass
	return render(request,'user_book_detail.html',{'book':book,'flag':flag,'flag1':flag1})

def add_to_wishlist(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	WishList.objects.create(user=user,book=book)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=WishList.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=WishList.objects.get(user=user,book=book)
	wishlist.delete()
	return redirect('wishlist')

def cart(request):
	final_amount=0
	qty=1
	cart=Cart()
	if request.method=="POST":
		qty=request.POST['quantity']
		pk=request.POST["pk"]
		book=Book.objects.get(pk=pk)
		user=User.objects.get(email=request.session['email'])
		cart=Cart.objects.get(user=user,book=book)
		print("Cart.Book.ID : ",cart.book.id)
		cart.qty=qty
		cart.amount=book.book_price
		cart.net_amount=int(cart.qty)*int(cart.amount)
		cart.save()
	
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status="pending")
	for i in carts:
		final_amount=final_amount+int(i.net_amount)
	request.session['cart_count']=len(carts)
	return render(request,'mycart.html',{'carts':carts,'final_amount':final_amount})

def add_to_cart(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,book=book,qty="1",amount=book.book_price,net_amount=book.book_price)
	return redirect('cart')

def remove_from_cart(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,book=book)
	cart.delete()
	return redirect('cart')

def search(request):
	search=request.POST['search']
	books=Book.objects.filter(book_name__contains=search)
	return render(request,'search_result.html',{'books':books})