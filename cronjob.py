import pymysql as pm
from mobile import Item, core, get_url, get_all_items, Wishlist
from mail_sender import send_email
from details import db, User, Wishlist as wl, verified, Item as it



def database_query():
	mailing_list = {}
	try:

		# db = pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE)
		# cur = db.cursor(pm.cursors.DictCursor)

		all_items = {}
		# query = "select email from users"
		# res = cur.execute(query)

		res = db.session.query(verified).filter_by(confirmed=True).all()
		for user in res:
			# print(email)
			email = user.email
			# query1 = "select `wishlist_id` from `wishlists` where `email` = %s"
			# res1 = cur.execute(query1, (email['email'],))

			res1 = db.session.query(wl).filter_by(email=email).all()

			for wl_id in res1:
				# print(wl_id)
				all_items = core(wl_id.wishlist_id)

				n = len(all_items)
				# cur.execute("update `wishlists` set `num_of_items` = %s where `wishlist_id` = %s", (n, wl_id['wishlist_id']))
				wl_id.num_of_items = n
				db.session.commit()
				db.session.close()

				update_db(email, all_items, mailing_list)

		# db.commit()
		# db.close()
		# print(mailing_list)
		send_email(mailing_list)
	except Exception as e:
		print(e)
	



def update_db(email, all_items, mailing_list):

	try:
		for item_id in all_items:

			item = all_items[item_id]
			# res = cur.execute("select * from `items` where `item_asin` = %s", (item.item_asin,))
			res = db.session.query(it).filter_by(item_asin=item.item_asin).first()
			if res:
				# item found in database
				# res1 = cur.fetchone()
				# price = res1['cur_price']
				price = res.cur_price
				if item.availability:
					if not res.availability or item.cur_price < res1.cur_price :
						mailing_list[email] = mailing_list.get(email, [])
						mailing_list[email].append(item)
						price = item.cur_price
				# print(price)
				# query = "update `items` set `cur_price` = %s, `availability` = %s, `least_price` = %s where `item_asin` = %s"
				# cur.execute(query, (item.cur_price, item.availability, price, item.item_asin))
				res.cur_price = item.cur_price
				res.availability = item.availability
				res.least_price = price
				db.session.commit()
				db.session.close()

			else:
				# item not found in database
				# query = "insert into items(`item_asin`, `name`, `cur_price`, `availability`, `least_price`) values(%s,%s,%s,%s,%s)"
				# cur.execute(query, (item.item_asin, item.name, item.cur_price, item.availability, item.least_price))

				new_item = it(item_asin=item.item_asin, name=item.name, cur_price=item.cur_price, availability=item.availability, least_price=item.least_price)
				db.session.add(new_item)
				db.session.commit()
				db.session.close()

			# db.commit()
	except:
		pass


if __name__ == '__main__':
	database_query()