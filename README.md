# NutriForce B2C Online Shop
B2C introduction

<img src='static/images/readme/amiresponsive.webp' alt='Am I Responsive Image'>

1. [User Experience](#user-experience)
   

## User Experience - TO BE UPDATED

### Visitor Goals

#### First-Time Visitor Goals


#### Returning Visitor Goals 


#### Frequent Visitor Goals 


### User Stories

### Design

#### Colour Palette

#### Typography

#### Imagery

### Site Planning

#### Lucidchart


#### Wireframes
Wireframes were used to plan out the pages for the site. Minor adjustments were made throughout, as the pages were being created. The navigation menu was reorganised in the final site iteration, and differs from the wireframes below as follows:
1. The Newsletter Signup option was added next to the Support Contact details
2. The site logo and user action buttons (view cart, log in, create account) have swapped sides
3. The user action buttons all have icons added (instead of only the Cart button)

##### <ins>Login / Create Account</ins>
**Login:**
_Social media signup options have not yet been implemented. This is planned for release 1.1. [See user story here](https://github.com/crazycooky77/ci_project5/issues/20#issue-2248986787)._
<img src='media/readme/wf-login.webp' alt='Log in page wireframe'>

**Create Account:**
_Social media signup options have not yet been implemented. This is planned for release 1.1. [See user story here](https://github.com/crazycooky77/ci_project5/issues/20#issue-2248986787)._
<img src='media/readme/wf-create-acc.webp' alt='Create account wireframe'>

#### <ins>Profile Pages</ins>
**Account Details:**
<img src='media/readme/wf-profile-details.webp' alt='Profile account details wireframe'>

**Addresses:**
_The Add New Address (now Add Address) button was moved, but otherwise the style has stayed the same._
<img src='media/readme/wf-profile-addr.webp' alt='Profile addresses wireframe'>

**Orders:**
<img src='media/readme/wf-profile-orders.webp' alt='Profile orders wireframe'>

**Order Details:**
<img src='media/readme/wf-profile-order-details.webp' alt='Profile order details wireframe'>

**Saved Items:**
_Saved Items have not yet been implemented. Therefore, the menu item (on the left) and the page itself is not yet available. This is planned for release 1.1. [See user story here](https://github.com/crazycooky77/ci_project5/issues/27#issue-2250330614)._
<img src='media/readme/wf-profile-saved-items.webp' alt='Profile saved items wireframe'>

**Watchlist:**
_The Watchlist has not yet been implemented. Therefore, the menu item (on the left) and the page itself is not yet available. This is planned for release 1.1. [See user story here](https://github.com/crazycooky77/ci_project5/issues/25#issue-2250321761)._
<img src='media/readme/wf-profile-watchlist.webp' alt='Profile watchlist wireframe'>

#### <ins>Product Pages</ins>
**Homepage (Featured Products):**
<img src='media/readme/wf-prod-homepage.webp' alt='Homepage (Featured Products) wireframe'>

**Product Browser:**
<img src='media/readme/wf-prod-browser.webp' alt='Product browser wireframe'>

**Product Page:**
_Add to Watchlist is not yet available. This is planned for release 1.1. [See user story here](https://github.com/crazycooky77/ci_project5/issues/25#issue-2250321761)._
<img src='media/readme/wf-prod-page.webp' alt='Product page wireframe'>

#### <ins>Checkout</ins>
**Cart:**
_Save for Later is not currently available. This is planned for release 1.1. [See user story here](https://github.com/crazycooky77/ci_project5/issues/27#issue-2250330614)._
<img src='media/readme/wf-checkout-cart.webp' alt='Cart view wireframe'>

**Login / Guest Checkout:**
_This view was slightly updated. Social media login options are not available ([planned for 1.1](https://github.com/crazycooky77/ci_project5/issues/20#issue-2248986787)), Forgot Password was added to the login section, and Create Account was added below Login as an option._
<img src='media/readme/wf-checkout-login.webp' alt='Checkout login and guest checkout wireframe'>

**Addresses:**
_A "Back to Cart" button was added at the bottom left of this page._
<img src='media/readme/wf-checkout-addr.webp' alt='Checkout addresses wireframe'>

**Payment Options:**
_This page was completely removed. Also, only stripe payment is currently available. Additional payment options (GooglePay, ApplePay, and PayPal) [are planned for release 1.1](https://github.com/crazycooky77/ci_project5/issues/38#issue-2381801096)._
<img src='media/readme/wf-checkout-pay.webp' alt='Payment options wireframe'>

**Confirmation:**
_Show/Hide Cart and Edit Address links were added to this page. A Note to Seller is now also available at checkout. Text indicating that the customer will be charged once they confirm the purchase is now present. Finally, a "Back to Cart" button was added at the bottom left of this page._
<img src='media/readme/wf-checkout-confirm.webp' alt='Checkout confirmation wireframe'>

## Features - TO BE UPDATED


### To Be Implemented


### Closed Enhancements


## Technologies - TO BE UPDATED


## Testing - TO BE UPDATED

### Manual Testing


### Automated Testing
Automated testing has not yet been implemented. This has been postponed to the 1.1 release.

### Validator Testing

#### HTML


#### CSS


#### JSHint


#### PEP8


#### WAVE


#### Lighthouse



### Bugs


## Deployment
The site was deployed on Heroku. ElephantSQL was used for the database, as end of life is only in January 2025. PyCharm and GitHub Desktop were used for local development.

### Heroku
1. Cloned the basic repository from [Code Institute](https://github.com/Code-Institute-Org/ci-full-template)
   1. Code > Open with GitHub Desktop
2. Created new repository in [own GitHub](https://github.com/crazycooky77/ci_project5) for the cloned repository
3. Created new app on [Heroku](https://dashboard.heroku.com/apps)
   1. New > Create new app
   2. Provide app name and select region > Create app
4. Linked Heroku to cloned GitHub repository
   1. Click GitHub in the Deployment method section
   2. Log into GitHub, provide access to Heroku, and type in the repository name
   3. Search
   4. Connect
5. Enabled automatic deploys
   1. Tick the box for Automatic deploys in the corresponding section
6. Added python buildpack in the Settings > Buildpacks section
7. Added necessary Config Vars

### ElephantSQL
1. Logged into [ElephantSQL](https://www.elephantsql.com/) and Create New Instance
2. Added a name for the instance
3. Selected the Tiny Turtle (Free) plan (should be pre-selected)
4. Selected Region (bottom right)
5. Selected the closest Data center
6. Reviewed selections and Create instance
7. Opened the newly created instance
8. Selected "ADMIN" in the left sidebar (not editable, but can be viewed)
9. Under "Nodes", ensured the PostgreSQL version is 12+ (this is required for Django)
10. Initially it was not, so deleted and recreated the instance to get a different Host assigned
    1. These seem to be randomly assigned, and each has a different PostgreSQL version installed
    2. For example, "kandula" will **not** work (version 11.9), but trumpet (13.9) and flora (15.4) will

### PyCharm
1. File > New Project
2. Selected Django from the left sidebar
3. Gave the project a name
4. For Location, selected the local GitHub repository folder

### Django Project
1. Opened the Terminal in PyCharm (View > Tool Windows > Terminal)
2. If not already installed: `pip3 install django==4.2.1`
3. Created the Django project: `django-admin startproject XX_PROJECT_NAME_XX .`
4. Created the gitignore file: `touch .gitignore`
5. Added details [as here](https://github.com/crazycooky77/ci_project5/blob/main/.gitignore)
6. `python3 manage.py migrate` for the initial migration
7. Installed packages as in [the requirements file](https://github.com/crazycooky77/ci_project5/blob/main/requirements.txt)
8. Added necessary variables locally, as in Heroku
    1. PyCharm > Settings > Tools > Terminal > Environment variables
9. Updated settings.py, e.g. for ALLOWED_HOSTS, DEBUG, DATABASES, and directories (static, media, and templates)
10. The final iteration of this app uses AWS S3 for static and media storage, so the necessary changes needed to be made to [settings.py](https://github.com/crazycooky77/ci_project5/blob/main/nutriforce/settings.py) for this as well

### Important Extras
Heroku re-uploads the entirety of the static files to AWS with every commit, which causes the free tier limit to be reached within days. To avoid this, addED DISABLE_COLLECTSTATIC = 1 to Config Vars on Heroku. Then needed to manually python3 manage.py collectstatic locally with USE_AWS set to True in local environment variables (based on [settings.py](https://github.com/crazycooky77/ci_project5/blob/main/nutriforce/settings.py) in this project). Set this variable back to False when developing locally and using python3 manage.py runserver to see local static file changes. Otherwise the files (CSS, images...) already uploaded to AWS S3 would be used in runserver and no local changes are visible.

---

This project additionally uses fixtures to populate initial data into some of the Django models. As these use a primary key of 0, the following needed to be run in Terminal before fixtures could loaded:

`ALTER SEQUENCE XX_TABLE_PKFIELD_SEQ_XX MINVALUE 0 START 1 RESTART 0`

Then: `python3 manage.py loaddata XX_FIXTURESFILE.yaml_XX` as in [Django docs](https://docs.djangoproject.com/en/5.0/howto/initial-data/)


## Credits
The base template was cloned from the [Code Institute GitHub repository](https://github.com/Code-Institute-Org/ci-full-template). Various other resources were used for different features. They are all listed below, categorised accordingly.

#### Database Objects
- [Product images and text](https://www.theedge-sports.com/)
- [More product images and text](https://www.hollandandbarrett.ie/)
- [Django fixtures](https://docs.djangoproject.com/en/5.0/howto/initial-data/)

#### JSON Data
- [Django JSON serializer](https://stackoverflow.com/questions/10358803/is-it-possible-to-use-javascript-to-get-data-from-django-models-db)
- [Javascript JSON array loops](https://stackoverflow.com/questions/18238173/javascript-loop-through-json-array)
- [Sorting Javascript JSON array](https://www.geeksforgeeks.org/how-to-sort-json-array-in-javascript-by-value/)
- [Sort Javascript JSON array by multiple fields](https://medium.com/developer-rants/sorting-json-structures-by-multiple-fields-in-javascript-60ed96704df7)
- [Splitting JSON arrays (removed from final code)](https://stackoverflow.com/questions/33786400/break-array-into-multiple-arrays-based-on-first-character-in-values)

#### Sorting and Filtering
- [Sorting select options](https://stackoverflow.com/questions/278089/javascript-to-sort-contents-of-select-element)
- [Sorting select options (2)](https://gist.github.com/cschlyter/5187131)
- [Django Q objects](https://stackoverflow.com/questions/15045101/how-to-get-more-than-one-field-with-django-filter-icontains)
- [Keep list sorting for Django query](https://gist.github.com/balazs-endresz/fd4efda41d4581631f4c)
- [Filter query if parameter exists](https://stackoverflow.com/questions/59413613/django-filter-query-if-filter-parameter-exists)
- [Django Admin sorting](https://stackoverflow.com/questions/4571916/sort-order-of-django-admin-records)

#### POST Requests
- [Append data to Django POST request](https://stackoverflow.com/questions/65047248/append-extra-data-to-request-post-in-django)
- [Javascript POST request](https://www.geeksforgeeks.org/javascript-post-request-like-a-form-submit/)
- [Javascript POST request with Xml HTTP Request](https://stackoverflow.com/questions/9713058/send-post-data-using-xmlhttprequest)
- [Javascript Xml HTTP Request confirmation](https://stackoverflow.com/questions/10876123/how-to-find-out-if-xmlhttprequest-send-worked)

#### Miscellaneous Django/Python
- [Django login signal](https://stackoverflow.com/questions/1990502/django-signal-when-user-logs-in)
- [Django search bar](https://stackoverflow.com/questions/66386490/making-search-bar-in-django)
- [Django search functions](https://www.makeuseof.com/add-search-functionality-to-django-apps/)
- [Django custom context processor](https://djangocentral.com/how-to-create-custom-context-processors-in-django/)
- [Country name to country ISO code](https://stackoverflow.com/questions/10997128/language-name-from-iso-639-1-code-in-javascript/75467239#75467239)
- [Handler500 exceptions](https://stackoverflow.com/questions/65926108/how-to-get-exception-in-custom-handler500)

#### Miscellaneous JavaScript
- [Removing duplicate select options](https://stackoverflow.com/questions/22905769/remove-duplicate-options-from-html-select)
- [Javascript args](https://stackoverflow.com/questions/2141520/javascript-variable-number-of-arguments-to-function)
- [Scroll to top feature](https://www.w3schools.com/howto/howto_js_scroll_to_top.asp)
- [Javascript load events](https://stackoverflow.com/questions/39993676/code-inside-domcontentloaded-event-not-working)
- [Javascript text width calculations](https://www.tutorialspoint.com/Calculate-text-width-with-JavaScript)
- [Simultaneous scrolling in DIVs (replaced in final code)](https://stackoverflow.com/questions/11723886/synchronizing-scrolling-between-2-divs)

#### Miscellaneous CSS
- [Centered text in horizontal line](https://stackoverflow.com/questions/2812770/add-centered-text-to-the-middle-of-a-horizontal-rule)
- [HTML Number Input fields](https://stackoverflow.com/questions/31706611/why-does-the-html-input-with-type-number-allow-the-letter-e-to-be-entered-in)
- [Left-align last flexbox row](https://stackoverflow.com/questions/18744164/flex-box-align-last-row-to-grid)