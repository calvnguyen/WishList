from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import User, Wish


# Create your views here.
def index(request):
  if 'user_id' in request.session:
    return redirect("/listing")
    request.session['status'] = "logged"
  else:
    return redirect("/login") 

def login(request):

  if request.method == "POST": 
    print "im in Login - Post"
    password = request.POST['password'].encode('utf-8')
    result = User.userMgr.login(request.POST['username'], password)

    if result[0]:
      print result[1]
      request.session['user_id'] = result[1].id
      request.session['status'] = "logged"
      return redirect("/listing")
    else:
 
      if 'username-error' in result[1]:
        for msg in result[1]['username-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='username-error')
      if 'password-error' in result[1]:
        for msg in result[1]['password-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='password-error')

    	return redirect("/login")

  elif request.method == "GET":
    	return render(request, 'wishlist/login.html')


def create_user(request):

  if (request.method == "GET"):
    return render(request, "wishlist/index.html")

  elif (request.method == "POST"):
    print "Got Post Info"
    password = request.POST['password'].encode('utf-8')
    result = User.userMgr.register(request.POST['name'], request.POST['username'], password, request.POST['passwordconfirm'], request.POST['date_hired'])
    print "Got out of register"
    if result[0]:
      print "Able to create ok"
      request.session['user_id'] = result[1].id
      request.session['status'] = "registered"
      return redirect('/listing')
    else:
      print result[1]
      if 'name-error' in result[1]:
        for msg in result[1]['name-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='name-error')
      if 'username-error' in result[1]:
        for msg in result[1]['username-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='login-error')
      if 'password-error' in result[1]:
        for msg in result[1]['password-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='password-error')
      if 'password-confirm-error' in result[1]:
        for msg in result[1]['password-confirm-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='password-confirm-error')
      if 'date-hire-error' in result[1]:
        for msg in result[1]['date-hire-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='datehire-error')

      return redirect('/register')
  else:
    return redirect('/register')

def create_item(request):
  if (request.method == "GET"):
    return render(request, "wishlist/add.html")
  elif (request.method == "POST"):
    print "Got Post Info"

    result = Wish.wishMgr.add_wish(request.POST['item'], request.session['user_id'])
    
    if (result[0]):
      # return redirect('/listing')
      print "created item ok"
      # user = User.userMgr.filter(id=request.session['user_id'])
      # if user:
      #   wishes= Wish.wishMgr.filter(users=user)
      #   print user.query
      #   print wishes.query
      return redirect('/listing')
        
    else:
      if 'new-item-error' in result[1]:
        for msg in result[1]['new-item-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='new-item-error')
      return redirect('/wish_items/add')
  else:
    return redirect('/login')

def list_items(request):

  if 'user_id' in request.session:
    print "my user id", request.session['user_id']
    user = User.userMgr.get(id = request.session['user_id'])
   
    print "user id", user.id

    #wishitems = Wish.wishMgr.filter(creator__isnull=True).update(creator="John Do")

    #Wish.wishMgr.filter(item = "").update(creator="John Do")

    others_items = Wish.wishMgr.exclude(users__id = user.id)
    print "Everyone's wish items are:"
    for item in others_items:
      print item.item
    
    user_items = user.wish_set.all()
    # print user_items.query
    print "\nuser "  + user.name + " items are: "
    for useritem in user_items:
      item_users = useritem.users.all()
      print "\nitem is:", useritem.item
      print "\nthis item is Added by:", item_users[0].name  + "\n"

    context = {'user_wish_listing': user_items,
              'user_account': user,
              'others_wish_listing': others_items
              }

    return render(request, 'wishlist/listing.html', context)

  else:
    return redirect("/login")
def show(request, wish_id):

  wish = Wish.wishMgr.get(id = wish_id)

  item_users = wish.users.all()

  context = {'item_user_list': item_users, 'wish_item': wish}

  return render(request, 'wishlist/show.html', context)

def add_to_list(request, wish_id):

  result = Wish.wishMgr.add_to_list(request.session['user_id'], wish_id)
  if (result[0]):
    return redirect('/listing')
        
  else:
    if 'new-item-error' in result[1]:
      for msg in result[1]['list-add-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='list-add-error')
      return redirect('/listing')

def delete_wish(request, wish_id):

  result = Wish.wishMgr.delete(wish_id)

  if (result[0]):
    return redirect('/listing')
  else:
    if 'list-delete-error' in result[1]:
      for msg in result[1]['list-delete-error']:
        messages.add_message(request, messages.ERROR, msg, extra_tags='list-delete-error')
      return redirect('/listing')


def remove_wish(request, wish_id):

  result = Wish.wishMgr.remove_from_list(request.session['user_id'], wish_id)

  if (result[0]):
    return redirect('/listing')

def logout(request):
  request.session.pop('user_id')
  return redirect('/login')