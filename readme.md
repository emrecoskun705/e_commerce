
https://user-images.githubusercontent.com/57330864/127233277-4d24491b-aec0-4d94-86e5-f7883843eafa.mp4

# Django E-Commerce

Simple django e-commertce website.

- Python 3.7.6
- virtualenv
- All other requirments in requirments.txt file



## Tech


- [Python] - backend handling
- [Django] - using Django version 2.2
- [Stripe] - Stripe for payment
- [Google API] - Google OAuth 2.0
- [Template] - MDBootstrap free e-commerce template.


## Installation

You should use minimum [Python 3.7.6](https://docs.anaconda.com/anaconda/packages/py3.7_win-64/) to run.

First clone this repository

```sh
git clone https://github.com/emrecoskun705/e_commerce.git
```

Install and create virtual environment

```sh
pip install virtualenv
virtualenv env
```

Install, create and start virtual environment

```sh
pip install virtualenv
virtualenv env
.\env\Scripts\activate
```

Then install all the requirments for project

```sh
pip install -r requirements.txt
```

Create a file named '.env' then copy the variables in '.env.copy' to '.env' then fill the values for those variables

Now, run the project from command line
```sh
python manage.py runserver
```

Creating superuser
```sh
python manage.py createsuperuser
```

#### Stripe webhook

To test and complete the order, stripe webhook must be working.

First, install [Stripe CLI]
Then run this command
```sh
stripe listen --forward-to localhost:8000/webhooks/stripe/
```




   [Python]: https://www.python.org/downloads/release/python-370/
   [Django]: https://www.djangoproject.com/download/
   [Template]: https://mdbootstrap.com/freebies/jquery/e-commerce/
   [Stripe CLI]: https://stripe.com/docs/stripe-cli#install
   [Stripe]: https://stripe.com/
   [Google API]: https://developers.google.com/identity/protocols/oauth2
  
