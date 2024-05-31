from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, abort
from flask_login import login_required, current_user
from flask_uploads import UploadNotAllowed
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from .models import Listings, Messages
from . import db, locator
import json, os, re, requests
from .__init__ import photos
from geopy.distance import geodesic
from datetime import datetime



views = Blueprint('views', __name__)



@views.route('/', methods=['GET', 'POST'])
def home():
    listings = Listings.query.all() 

    sort_by = request.args.get('sort_by', '')
    if sort_by == 'distance':
        if current_user.is_authenticated:
            if current_user.postcode and current_user.address:
            
                user_address = f"{current_user.address} {current_user.postcode}"
                print(user_address)
                lat, long = validate_address(user_address)
                

                listings = sorted(Listings.query.all(), key=lambda listing: geodesic((listing.latitude, listing.longitude), (lat, long)).km)

            else:
                flash("User address unknown. Please update", category='error')
                return redirect(url_for('views.settings',username=current_user.first_name, id=current_user.id))
        else:
            flash("Please login", category='error')
    
    
    return render_template("home.html", user=current_user, listings=listings)





#listings for all users
@views.route('/listing/<int:listing_id>', methods=['GET','POST'])
def listing(listing_id):

    listing = next((listing for listing in Listings.query.all() if listing.id == listing_id), None)

    return render_template("listing.html", listing=listing, user=current_user)






@views.route('/<id>/my-account', methods=['POST', 'GET'])
@login_required
def widget_page(id):
    return render_template('account.html', id=id, user=current_user)

#return redirect(url_for('views.settings', username=username, id=id))






#user's listings
@views.route('<id>/my-listing/<int:listing_id>')
@login_required
def listing_page(listing_id, id):

    listing = next((listing for listing in current_user.listings if listing.id == listing_id), None)

    if not listing:
        abort(404)
  
    return render_template('user-listing.html', listing=listing, id=id, user=current_user)






@views.route('/edit-listing/<int:listing_id>', methods=['POST', 'GET'])
@login_required
def edit_listing(listing_id):

    listing = next((listing for listing in current_user.listings if listing.id == listing_id), None)

    if not listing:
        abort(404)

    if request.method == 'POST':
        print('posted')

  
    return render_template('edit-listing.html', listing=listing, user=current_user)






@views.route('/submit-edit', methods=['POST','GET'])
@login_required
def submit_edit():
    if request.method == "POST":

        listing_id = request.form.get('listing_id')
        listing = Listings.query.get(listing_id)

        if not listing:
            abort(404)

        

        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')


        if 'photo' in request.files:
            file = request.files['photo']

            print(file.filename)
        

            if file.filename != '':

                print('photo')
                filename = photos.save(file)
                listing.image_path = filename
  

        listing.title = title  
        listing.description = description  
        listing.price = price

        db.session.commit()  
        
        
        flash("Your edits are now live!")
        return redirect(url_for('views.widget_page'))
        # return redirect(url_for('views.edit_listing', listing_id=listing_id))

    return jsonify







@views.route('<id>/new-listing', methods=['POST','GET'])
@login_required
def upload_photo(id):
    if request.method == "POST":
        
        if 'photo' in request.files:

            file = request.files['photo']
            title = request.form.get('title')
            description = request.form.get('bio')
            price = request.form.get('price')
            address = request.form.get('address')
            city = request.form.get('city')
            postcode = request.form.get('postcode')

            full_address = f"{address}, {postcode}, {city}"

         
            if title:
                pass
            else:
                flash('Enter listing title', category='error')
                return redirect(url_for('views.upload_photo', id=id))
            
            if description:
                pass
            else:
                flash('Enter listing description', category='error')
                return redirect(url_for('views.upload_photo', id=id))
            
            if price:
                pass
            else:
                flash('Enter listing price (£)', category='error')
                return redirect(url_for('views.upload_photo', id=id))
            
            coordinates = validate_address(full_address)
            if coordinates:
                latitude, longitude = coordinates
                print(f"latitude: {latitude}")
            else:
                flash('Invalid address', category='error')
                return redirect(url_for('views.upload_photo', id=id))
              

            if file.filename != '':
                try:
                    filename = photos.save(file)
                    

                    new_listing = Listings(image_path=filename, title=title, description=description, price=price, latitude=latitude, longitude=longitude, address=address, postcode=postcode, city=city, user_id=current_user.id)
                    

                    db.session.add(new_listing)
                    db.session.commit()
                    flash('Success! Listing uploaded', category='success')
                    return redirect(url_for('views.widget_page', id=id))
                except UploadNotAllowed:
                    flash('Invalid file format', category='error')
                return render_template('new-listing.html', user=current_user, id=id)
    return render_template('new-listing.html', user=current_user, id=id)





def validate_address(address):
    api_key = "AIzaSyBvw9hDkkMFaPR8gxtai5x72H2fJ5KuNV0" 
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()

        if data["status"] == "OK":
            # Address is valid
            location = data["results"][0]["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            return (lat, lon)
        else:
            # Address is invalid
            print(f"Error: {data['status']}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Error: {e}")
        return None
    except ValueError as e:
        # Handle JSON parsing errors
        print(f"Error: {e}")
        return None







@views.route('/delete-listing', methods={'POST'})
@login_required
def delete_listing():
    listing = json.loads(request.data)
    listingId = listing['listingId']
    userId = listing['user_id']

    if current_user.id == userId:

        listing = Listings.query.get(listingId)
        if listing:
            if listing.user_id == current_user.id:
                db.session.delete(listing)
                db.session.commit()
        return jsonify
    else:
        return jsonify





@views.route('/<id>/settings', methods=['GET','POST'])
@login_required
def settings( id):
    if current_user.is_authenticated:
        
        if request.method == 'POST':

            email = request.form.get('email')
            username = request.form.get('firstname')
            postcode = request.form.get('postcode')
            address = request.form.get('address')

            if email:
                current_user.email = email
                db.session.commit()
            else:
                flash("Postcode field must have a value")
            
            if username:
                current_user.username = username
                db.session.commit()
            else:
                flash("Username field must have a value")
            


            if postcode:
                current_user.postcode = postcode
                db.session.commit()
            else:
                flash("Postcode field must have a value")
            

            if address:
                current_user.address = address
                db.session.commit()
            else:
                flash("Address field must have a value")
           
            return redirect(url_for('views.settings', username=username, id=id))

       
        return render_template('settings.html', user=current_user)
    else:
        
        return "Unauthorized access or wrong username"



@views.route('/messages', methods=['GET','POST'])
def messages():
    if request.method == 'POST':
        if current_user.is_authenticated:

            message = request.form.get('message')
            timestamp = datetime.now()
            recipient_id = current_user.id #for now - other is me

            if message:
                new_message = Messages(user_id=current_user.id, message=message, recipient_id=recipient_id, timestamp=timestamp)
                db.session.add(new_message)
                db.session.commit()

            print(message)
        
        else:
            return redirect(url_for('auth.login'))

    return render_template('messages.html', user=current_user)




@views.route('/process-messages')
@login_required
def process_messages():
    return render_template('process-messages.html', user=current_user)




#change first name to user name
# handle urls to make unique for each user
#allow users to send messages

