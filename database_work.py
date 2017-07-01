import pymysql as pm
from mobile import Item, core, get_url, get_all_items, Wishlist
from details import db, Wishlist as wl
mailing_list = {}


def get_all_wishlists(email):
	wishlists = {}
	try:
		# db = pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE)
		# cur = db.cursor(pm.cursors.DictCursor)

		# query = "select * from wishlists where email = %s"
		
		# res = cur.execute(query, (email,))
		res = db.session.query(wl).filter_by(email=email).all()
		for wishlist in res:
			wl_id = wishlist.wishlist_id
			name = wishlist.name
			all_items = {}
			all_items = core(str(wl_id))
			
			# cur.execute('update wishlists set `num_of_items` = %s where `wishlist_id` = %s', (len(all_items), wl_id))
			# db.commit()
			
			wishlist.num_of_items = len(all_items)
			
			wishlists[wl_id] = Wishlist(wl_id, email, name, len(all_items))
			
			# print(wishlist['name'], len(all_items))
		db.session.commit()
		db.session.close()
		# print(wishlists)

		# db.commit()
		# db.close()
		
	except Exception as e:
		print(e)
		# pass
	finally:
		return wishlists
	



def add_wishlist(email, wishlist_id, name="Amazon wishlist"):
	

	try:
		# db = pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE)
		# cur = db.cursor()

		# query = "select * from wishlists where `wishlist_id` = %s and `email` = %s"

		# res = cur.execute(query, (wishlist_id,email))
		res = db.session.query(wl).filter_by(email=email, wishlist_id=wishlist_id).first()
		db.session.close()

		print("res = ", res)
		if not res:

			# query = "insert into wishlists(`email`, `wishlist_id`, `name`) values(%s, %s, %s)"
			# cur.execute(query, (email, wishlist_id, name))

			# db.commit()
			# db.close()
			new_wl = wl(email=email, wishlist_id=wishlist_id, name=name)
			db.session.add(new_wl)
			db.session.commit()
			db.session.close()
			get_all_wishlists(email)
			
			return 1
		else:
			# db.close()
			return -1
	except Exception as e:
		print(e)
		return -2



if __name__ == '__main__':
	

	email ='akshayachaar@gmail.com'
	get_all_wishlists(email)