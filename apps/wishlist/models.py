from __future__ import unicode_literals

from django.db import models
import re
from django.contrib import messages
import bcrypt
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# name cannot contain numbers
NAME_REGEX = re.compile(r'^[^0-9]+$')
# requires a password to have at least 1 uppercase letter and 1 numeric value.
PASS_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d).+$')

# Create your models here.

class WishManager(models.Manager):
	def add_wish(self, item, userId):
		errors = {}

		errors['new-item-error'] = []

		if len(item) == 0:
			errors['new-item-error'].append('Item/Product\'s Name cannot be empty!')

		elif len(item) < 4:
			errors['new-item-error'].append('Item/Product needs to have at least 4 characters!')

		if len(errors['new-item-error']) != 0:
			return (False, errors)

		else:

			users= User.userMgr.filter(id=userId)

			if users:
				user = users[0]
				print "user from wish manager is", user.name
			else:
				errors['new-item-error'].append('No user exists to associate item')
				return (False, errors)

			wishes = Wish.wishMgr.filter(item=item)
			if wishes:
				wish = wishes[0]
			else:
				wish = Wish.wishMgr.create(item=item, creator=user.name)

			wish.users.add(user)
			return (True, wish)

	def add_to_list(self, userID, itemID):
		errors = {}
		errors['list-add-error'] = []
		wish = Wish.wishMgr.get(id = itemID)
		users = User.userMgr.filter(id=userID)

		if users:
			user = users[0]
		else:
			errors['list-add-error'].append('No user exists to add to list')
			return (False, errors)

		wish.users.add(user)


		return (True, wish)

	def delete(self, itemID):
		errors = {}
		errors['list-delete-error'] = []
		wishes = Wish.wishMgr.filter(id = itemID)
		if wishes:
			wish = wishes[0]
		else:
			errors['list-delete-error'].append('No user exists to delete from list')
			return (False, errors)
		wish.delete()
		return (True, wish)

	def remove_from_list(self, userID, itemID):
		errors = {}
		errors['list-remove-error'] = []
		users = User.userMgr.filter(id=userID)

		if users:
			user = users[0]
		else:
			errors['list-remove-error'].append('No user exists to remove item from list')
			return (False, errors)

		wish = Wish.wishMgr.get(id = itemID)

		wish.users.remove(user)
		return (True, wish)


class UserManager(models.Manager):
	def login(self, username, password):
		errors = {}

		errors['username-error'] = []
		errors['password-error'] = []

		if len(username) < 1:
			errors['username-error'].append("Username cannot be empty!")

		if len(password) < 1:
			errors['password-error'].append("Password cannot be empty!")

		elif len(password) < 8:
			errors['password-error'].append("Password\'s length has to be more than 8 characters!")


		if len(errors['username-error']) != 0 or len(errors['password-error']) != 0:
			return (False, errors)
	
		else:
			try:
				user = User.userMgr.get(username=username)

				if not bcrypt.hashpw(password, user.password.encode('utf-8')) == user.password:
					print "login check - password DO NOT MATCH"
					errors['password-error'].append("Either email/pw is incorrect")	
					return (False, errors)
				elif bcrypt.hashpw(password, user.password.encode('utf-8')) == user.password:
					print "login check - passwords match"
					return (True, user)


			except User.DoesNotExist:
				errors['username-error'].append("Username cannot be found")
				return (False, errors)


	def register(self, name, username, password, passwordconfirm, date_hired):
		errors = {}
		present = datetime.now()
		errors['name-error'] = []
		errors['username-error'] = []
		errors['date-hire-error'] = []
		errors['password-error'] = []
		errors['password-confirm-error'] = []


		if len(name) < 1:
			errors['name-error'].append("Name cannot be empty!")

		elif len(name) < 3:
			errors['name-error'].append("Name has to be at least 3 characters!")

		elif not NAME_REGEX.match(name):
			errors['name-error'].append("Name cannot contain a number!")

		if len(username) < 1:
			errors['username-error'].append("Username cannot be empty!")

		elif len(username) < 3:
			errors['username-error'].append("Username has to be at least 3 characters!")

		elif not self.is_date(date_hired):
			errors['date-hire-error'].append("Date hired entered is not valid!!")
		elif datetime.strptime(date_hired, "%Y-%m-%d") > present:
			errors['date-hire-error'].append("Date hired cannot be from the future!")

		if len(password) < 1:
			errors['password-error'].append("Password cannot be empty!")

		elif len(password) < 8:
			errors['password-error'].append("Password's length has to be more than 8 characters!")

		if len(passwordconfirm) < 1:
			errors['password-confirm-error'].append("Password Confirmation cannot be empty!")
		
		elif len(passwordconfirm) < 8:
			errors['password-confirm-error'].append("Password confirmation's length has to be more than 8 characters!")
		
		if password != passwordconfirm:
			errors['password-confirm-error'].append("Password and password's confirmation must match!")


		if len(errors['password-error']) != 0 or len(errors['password-confirm-error']) != 0 or len(errors['date-hire-error']) != 0 or len(errors['username-error']) != 0 or len(errors['name-error']) != 0:
			return (False, errors)
		
		else:				
			user = User.userMgr.filter(username = username)
			if (user):
				errors['username-error'].append("Username already exists. Please proceed to login or choose another one")
				return (False, errors)
			else:
				hashed = bcrypt.hashpw(password, bcrypt.gensalt().encode('utf-8'))
				user = User.userMgr.create(name=name, username=username, password=hashed, date_hired=date_hired)
				user.save()
				return (True, user)

	def is_date(self, date_hired):
		try:
			if date_hired != datetime.strptime(date_hired, "%Y-%m-%d").strftime('%Y-%m-%d'):
				raise ValueError
			return True
		except ValueError:
			return False

class User(models.Model):
	name = models.CharField(max_length=255)
	username = models.CharField(max_length=255)
	password = models.CharField(max_length=255)
	date_hired = models.CharField(max_length=10, null=True)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	userMgr = UserManager()


class Wish(models.Model):
	item = models.CharField(max_length=255)
	users = models.ManyToManyField(User)
	creator = models.CharField(max_length=255, null=True)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	wishMgr = WishManager()