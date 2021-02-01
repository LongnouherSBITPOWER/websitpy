from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login
from .models import Allproduct

# HttpResponse คือ ฟังชั่นสำหลับทำให้โชว์ข้อความหน้าเว็บได้
def Home(request):
	product = Allproduct.objects.all().order_by('id').reverse()[:3] #ดึงข้อมูลมาทั้งหมด
	preorder = Allproduct.objects.filter(quantity__lte=0)
	#quantity__lte=0 (หาค่าที่ quantity <= 0 - lte is <=) (underscore 2 ตัว)
	#quantity__gt=0 (หาค่าที่ quantity > 0 - gt is >)
	#quantity__gte=5 (หาค่าที่ quantity >= 5 - gte is >=)
	context = {'product':product,'preorder':preorder}
	return render(request, 'myapp/home.html',context)
	#return HttpResponse('<marquee>ສະບາຍດີ<h1>สวัสดี hello world</h1></marquee>')
def About(request):
	return render(request, 'myapp/about.html')


def Contact(request):
	return render(request, 'myapp/contact.html')



def AddProduct(request):
	if request.user.profile.usertype != 'admin':
		return redirect('home-page')
	if request.method == 'POST' and request.FILES['imageupload']:
		data = request.POST.copy()
		name = data.get('name')
		price = data.get('price')
		detail = data.get('detail')
		imageurl = data.get('imageurl')
		quantity = data.get('quantity')
		unit = data.get('unit')

		new = Allproduct()
		new.name = name
		new.price = price
		new.detail = detail
		new.imageurl = imageurl
		new.quantity = quantity
		new.unit = unit
		################################
		file_image = request.FILES['imageupload']
		files_image_name = request.FILES['imageupload'].name.replace(' ' ,'')
		print('FILES_IMAGE:',file_image)
		print('IMAGE_NAME:',files_image_name)
		fs = filesSystemStorage()
		filename = fs.save(files_image_name,file_image)
		upload_file_url = fs.url(filename)
		new.image = upload_file_url[6:]
		#################################
		new.save()



	return render(request, 'myapp/addproduct.html')


def Product(request):
	product = Allproduct.objects.all().order_by('id').reverse() #ดืงข้อมูลมาทั้งหมด
	context = {'product':product}
	return render(request, 'myapp/allproduct.html',context)


def Register(request):
	if request.method == 'POST':
		data = request.POST.copy()
		first_name = data.get('first_name')
		last_name = data.get('last_name')
		email = data.get('email')
		password = data.get('password')
		#ยังไม่ใส่ try except เพือป้องกันการสมัครชํ้า
		#+ alert ไหน้าสมัครเเล้วว่าอิเมวล์นี้เคียสมัครเเล้ว
		#สอน คู่กับหัวข้อ reset password


		newuser = User()
		newuser.username = email
		newuser.email = email
		newuser.first_name = first_name
		newuser.last_name = last_name
		newuser.set_password(password)
		newuser.save()

		profile = Profile()
		profile.user = User.objects.get(username=email)
		profile.save()
		#from django.contrib.auth import authenticate,login
		user = authenticate(username=email,password=password)
		login(request,user)

	return render(request,'myapp/register.html')


def AddtoCart(request,pid):
	#localhost:8000/addtocart/3
	#{% url 'addtocart-page' pd.id %}
	print('CURRENT USER:',request.user)
	username = request.user.username
	user = User.objects.get(username=username)
	check = Allproduct.objects.get(id=pid)

	try:
		#กรณีที่สีนค้ามีชํ้า
		newcart = Cart.objects.get(user=user,productid=str(pid))
		#print('EXISTS: ',pcheck.exists())
		newquan = newcart.quantity + 1 
		newcart.quantity = newquan 
		calculate = newcart.price * newquan
		newcart.total = calculate
		newcart.save()


        ## update จำนวนของตระกร้าสินค้า ณ ตอนนี้
		count = Cart.objects.filter(user=user)
		count = sum([ c.quantity for c in count])
		updatequan = Profile.objects.get(user=user)
		updatequan.cartquan = count
		updatequan.save()


		return redirect('allproduct-page') 
	except:
		newcart = Cart()
		newcart.user = user
		newcart.productid = pid 
		newcart.productname = check.name
		newcart.price = int(check.price)
		newcart.quantity = 1
		calculate = int(check.price) * 1
		newcart.total = calculate
		newcart.save()



		count = Cart.objects.filter(user=user)
		count = sum([ c.quantity for c in count])
		updatequan = Profile.objects.get(user=user)
		updatequan.cartquan = count
		updatequan.save()


		return redirect('allproduct-page')

def MyCart(request):
	username = request.user.username
	user = User.objects.get(username=username)

	context = {}

	if request.method == 'POST':
		#ใช้สำหลับการดึงเท่านั้น
		data = request.POST.copy()
		productid = data.get('productid')
		print('PID',productid)
		item = Cart.objects.get(user=user,productid=productid)
		item.delete()
		context['status'] = 'delete'

		count = Cart.objects.filter(user=user)
		count = sum([ c.quantity for c in count])
		updatequan = Profile.objects.get(user=user)
		updatequan.cartquan = count
		updatequan.save()


	mycart = Cart.objects.filter(user=user)
	count = sum([ c.quantity for c in mycart])
	total = sum([ c.total for c in mycart])
	context['mycart'] = mycart
	context['count'] = count
	context['total'] = total
	
	return render(request,'myapp/mycart.html',context)



def MyCartEdit(request):
	username = request.user.username
	user = User.objects.get(username=username)
	context = {}

	if request.method == 'POST':
		data = request.POST.copy()
		#print(data)

		if data.get('clear') == 'clear':
			print(data.get('clear'))
			Cart.objects.filter(user=user).delete()
			updatequan = Profile.objects.get(user=user)
			updatequan.cartquan = 0
			updatequan.save()
			return redirect('mycart-page')

		editlist = []
		
		for k,v in data.items():
				#print([k,v])
				#pv_7
				if k[:2] == 'pd':
					pid = int(k.split('_')[1])
					dt = [pid,int(v)]
					editlist.append(dt)
		#print('EDITLIST:',editlist)

		for ed in editlist:
			edit = Cart.objects.get(productid=ed[0],user=user) # productid
			edit.quantity = ed[1]#quan
			calculate = edit.price * ed[1]
			edit.total = calculate
			edit.save()


		count = Cart.objects.filter(user=user)
		count = sum([ c.quantity for c in count])
		updatequan = Profile.objects.get(user=user)
		updatequan.cartquan = count
		updatequan.save()
		return redirect('mycart-page')


		#if data.get('checksave') == 'checksave':
		#return redirect('mycart-page')

	mycart = Cart.objects.filter(user=user)
	context['mycart'] = mycart

	return render(request,'myapp/mycartedit.html',context)


def Checkout(request):
	if request.method == 'POST':
		data = request.POST.copy()
		name = data.get('name')
		tel = data.get('tel')
		address = data.get('address')
		shipping = data.get('shipping')
		payment = data.get('payment')
		other = data.get('other')
		page = data.get('page')
		if page == 'informaton':
			context = {}
			context['name'] = name
			context['tel'] = tel
			context['address'] = address
			context['shipping'] = shipping
			context['payment'] = payment
			context['other'] = other
			return render(request, 'myapp/checkout2.html',context)

	return render(request, 'myapp/checkout1.html')


