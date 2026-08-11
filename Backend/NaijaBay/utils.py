import os
import uuid
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# ==============================
# Api Version
# ==============================
API_VERSION = 'api/v1/'


# ==============================
# Condition Choices
# ==============================
CONDITION_CHOICES = [
    ('', 'No Condition'),
    ('new', 'New'),
    ('used', 'Used'),
    ('refurbished', 'Refurbished'),
]


# ==============================
# Contact Method Choices
# ==============================
CONTACT_METHOD_CHOICES = [
    ('', 'Select Contact Method'),
    ('phone_call', 'Phone Call'),
    ('message', 'Message'),          # FIXED: was 'messsage'
    ('whatsapp', 'WhatsApp'),
]


# ===========================
# Sub Category Map
# ===========================
SUBCATEGORY_MAP = {
    '': [''],
    'phones_tablets': ['mobile_phones', 'tablets', 'phone_accessories', 'smartwatches', 'phone_parts'],
    'electronics': ['laptops_computers', 'tvs', 'audio_music', 'cameras', 'gaming', 'printers', 'computer_accessories'],
    'vehicles': ['cars', 'motorcycles', 'trucks_buses', 'vehicle_parts', 'boats', 'bicycles'],
    'real_estate': ['houses_rent', 'houses_sale', 'flats_apartments', 'land_plots', 'commercial_property', 'short_let'],
    'fashion': ['mens_clothing', 'womens_clothing', 'kids_clothing', 'shoes', 'bags', 'watches_jewelry', 'traditional_wear'],
    'home_garden': ['furniture', 'kitchen_appliances', 'bedding_linen', 'garden_outdoor', 'home_decor', 'generators', 'air_conditioners'],
    'jobs': ['accounting_finance', 'admin_office', 'engineering', 'healthcare', 'it_telecoms', 'sales_marketing', 'teaching', 'driving_logistics'],
    'services': ['repair_maintenance', 'cleaning_services', 'catering', 'event_planning', 'photography', 'web_dev', 'tutoring', 'moving_delivery'],
    'animals_pets': ['dogs', 'cats', 'birds', 'fish_aquarium', 'pet_accessories', 'livestock'],
    'food_agriculture': ['farm_produce', 'processed_food', 'farming_equipment', 'seeds_fertilizers'],
    'health_beauty': ['skincare', 'hair_products', 'vitamins', 'medical_equipment', 'gym_fitness', 'perfumes'],
    'kids_baby': ['baby_clothing', 'toys_games', 'baby_gear', 'school_supplies'],
    'sports_outdoor': ['football', 'gym_equipment', 'outdoor_camping', 'cycling'],
    'books_music_movies': ['books_textbooks', 'music_instruments', 'movies_dvds', 'video_games'],
}


# ===========================
# Categories Choices
# ===========================
CATEGORY_LABELS = {
    '': 'Select Category',
    'phones_tablets': 'Phones & Tablets',
    'electronics': 'Electronics',
    'vehicles': 'Vehicles',
    'real_estate': 'Real Estate',
    'fashion': 'Fashion',
    'home_garden': 'Home & Garden',
    'jobs': 'Jobs',
    'services': 'Services',
    'animals_pets': 'Animals & Pets',
    'food_agriculture': 'Food & Agriculture',
    'health_beauty': 'Health & Beauty',
    'kids_baby': 'Kids & Baby',
    'sports_outdoor': 'Sports & Outdoor',
    'books_music_movies': 'Books, Music & Movies',
}

CATEGORY_CHOICES = [
    (slug, CATEGORY_LABELS[slug]) for slug in SUBCATEGORY_MAP.keys()
]


# ===========================
# Sub Categories Choices
# ===========================
SUBCATEGORY_LABEL_OVERRIDES = {
    '': 'Select Sub Category',
    'it_telecoms': 'IT & Telecoms',
    'tvs': 'TVs',
    'suvs': 'SUVs',
}

def _subcategory_label(sub):
    if sub in SUBCATEGORY_LABEL_OVERRIDES:
        return SUBCATEGORY_LABEL_OVERRIDES[sub]
    return sub.title().replace('_', ' ')

SUBCATEGORY_CHOICES = [
    (sub.strip(), _subcategory_label(sub))
    for subs in SUBCATEGORY_MAP.values()
    for sub in subs
]


# ===========================
# State City Map
# ===========================
STATE_CITY_MAP = {
    '': [''],
    'abia': ['Aba', 'Umuahia', 'Ohafia', 'Arochukwu', 'Isuikwuato', 'Osisioma', 'Ukwa'],
    'adamawa': ['Yola', 'Mubi', 'Numan', 'Jimeta', 'Ganye', 'Hong', 'Michika', 'Song'],
    'akwa_ibom': ['Uyo', 'Ikot Ekpene', 'Eket', 'Oron', 'Abak', 'Itu', 'Ikot Abasi', 'Etinan'],
    'anambra': ['Awka', 'Onitsha', 'Nnewi', 'Ekwulobia', 'Ihiala', 'Ogbaru', 'Aguata', 'Njikoka'],
    'bauchi': ['Bauchi', 'Azare', 'Misau', "Jama'are", 'Ningi', 'Katagum', 'Tafawa Balewa', 'Dass'],
    'bayelsa': ['Yenagoa', 'Brass', 'Nembe', 'Ogbia', 'Sagbama', 'Ekeremor', 'Kolokuma/Opokuma'],
    'benue': ['Makurdi', 'Gboko', 'Otukpo', 'Katsina-Ala', 'Vandeikya', 'Oju', 'Adikpo', 'Aliade'],
    'borno': ['Maiduguri', 'Biu', 'Bama', 'Dikwa', 'Gwoza', 'Monguno', 'Konduga', 'Kukawa'],
    'cross_river': ['Calabar', 'Ikom', 'Obudu', 'Ugep', 'Ogoja', 'Akpabuyo', 'Boki', 'Yala'],
    'delta': ['Asaba', 'Warri', 'Sapele', 'Agbor', 'Ughelli', 'Ozoro', 'Effurun', 'Kwale', 'Burutu'],
    'ebonyi': ['Abakaliki', 'Afikpo', 'Onueke', 'Izzi', 'Ezza', 'Ikwo', 'Ohaukwu', 'Ishielu'],
    'edo': ['Benin City', 'Ekpoma', 'Auchi', 'Iguobazuwa', 'Uromi', 'Sabongida-Ora', 'Igarra', 'Agenebode'],
    'ekiti': ['Ado-Ekiti', 'Ikere-Ekiti', 'Oye-Ekiti', 'Ijero-Ekiti', 'Emure-Ekiti', 'Ise-Ekiti', 'Ilawe-Ekiti', 'Aramoko'],
    'enugu': ['Enugu', 'Nsukka', 'Awgu', 'Udi', 'Oji River', 'Agbani', 'Nkanu', 'Enugu-Ezike'],
    'fct': ['Wuse', 'Garki', 'Maitama', 'Asokoro', 'Jabi', 'Kubwa', 'Gwagwalada', 'Kuje', 'Bwari', 'Abaji', 'Lugbe', 'Nyanya'],
    'gombe': ['Gombe', 'Kaltungo', 'Billiri', 'Dukku', 'Deba', 'Nafada', 'Bajoga', 'Funakaye'],
    'imo': ['Owerri', 'Orlu', 'Okigwe', 'Mgbidi', 'Oguta', 'Mbaise', 'Ehime Mbano', 'Ideato'],
    'jigawa': ['Dutse', 'Hadejia', 'Gumel', 'Ringim', 'Birnin Kudu', 'Kazaure', 'Babura', 'Gwaram'],
    'kaduna': ['Kaduna', 'Zaria', 'Kafanchan', 'Ikara', 'Saminaka', 'Kachia', 'Giwa', 'Birnin Gwari'],
    'kano': ['Kano', 'Wudil', 'Bichi', 'Gaya', 'Rano', 'Kibiya', 'Takai', 'Dawakin Tofa', 'Ungogo', 'Fagge'],
    'katsina': ['Katsina', 'Daura', 'Funtua', 'Malumfashi', 'Kankia', 'Dutsin-Ma', 'Bakori', 'Mani'],
    'kebbi': ['Birnin Kebbi', 'Argungu', 'Yelwa', 'Zuru', 'Jega', 'Kamba', 'Bunza', 'Bagudo'],
    'kogi': ['Lokoja', 'Okene', 'Idah', 'Kabba', 'Anyigba', 'Ankpa', 'Dekina', 'Ajaokuta'],
    'kwara': ['Ilorin', 'Offa', 'Omu-Aran', 'Patigi', 'Lafiagi', 'Jebba', 'Share', 'Erin-Ile'],
    'lagos': ['Ikeja', 'Lagos Island', 'Lagos Mainland', 'Yaba', 'Surulere', 'Ikorodu', 'Epe', 'Badagry', 'Ajah', 'Lekki', 'Victoria Island', 'Ikoyi', 'Apapa', 'Festac', 'Ojo', 'Alimosho', 'Agege', 'Ikotun', 'Egbeda', 'Isolo', 'Mushin', 'Oshodi', 'Maryland', 'Gbagada', 'Ogba', 'Magodo', 'Iju', 'Shomolu', 'Bariga'],
    'nasarawa': ['Lafia', 'Keffi', 'Akwanga', 'Nasarawa Eggon', 'Wamba', 'Doma', 'Karu', 'Toto'],
    'niger': ['Minna', 'Suleja', 'Kontagora', 'Bida', 'New Bussa', 'Lapai', 'Agaie', 'Wushishi'],
    'ogun': ['Abeokuta', 'Ijebu-Ode', 'Sagamu', 'Ilaro', 'Ota', 'Ifo', 'Sango-Ota', 'Ijebu-Igbo', 'Ayetoro', 'Owode'],
    'ondo': ['Akure', 'Ondo', 'Ore', 'Okitipupa', 'Ikare', 'Owo', 'Idanre', 'Ile-Oluji', 'Oka'],
    'osun': ['Osogbo', 'Ile-Ife', 'Ilesha', 'Ede', 'Ikirun', 'Iwo', 'Ejigbo', 'Ikire', 'Ila', 'Gbongan'],
    'oyo': ['Ibadan', 'Oyo', 'Ogbomosho', 'Saki', 'Iseyin', 'Eruwa', 'Kisi', 'Igbo-Ora', 'Lanlate', 'Moniya'],
    'plateau': ['Jos', 'Bukuru', 'Pankshin', 'Langtang', 'Shendam', 'Mangu', 'Bokkos', 'Bassa'],
    'rivers': ['Port Harcourt', 'Obio/Akpor', 'Bonny', 'Degema', 'Ikwerre', 'Oyigbo', 'Ahoada', 'Okrika', 'Eleme', 'Emuoha', 'Tai', 'Gokana', 'Khana'],
    'sokoto': ['Sokoto', 'Tambuwal', 'Gwadabawa', 'Wurno', 'Shagari', 'Binji', 'Bodinga', 'Goronyo'],
    'taraba': ['Jalingo', 'Wukari', 'Bali', 'Gembu', 'Zing', 'Sardauna', 'Takum', 'Ibi'],
    'yobe': ['Damaturu', 'Potiskum', 'Gashua', 'Nguru', 'Gujba', 'Buni Yadi', 'Geidam', 'Yunusari'],
    'zamfara': ['Gusau', 'Kaura-Namoda', 'Anka', 'Talata Mafara', 'Shinkafi', 'Maradun', 'Bakura', 'Bungudu'],
}


# ===========================
# State Choices
# ===========================
STATE_LABEL_OVERRIDES = {
    '': 'Select State',
    'fct': 'Federal Capital Territory (Abuja)',
}

def _state_label(state):
    if state in STATE_LABEL_OVERRIDES:
        return STATE_LABEL_OVERRIDES[state]
    return state.title().replace('_', ' ')

STATE_CHOICES = [
    (state.strip(), _state_label(state)) for state in STATE_CITY_MAP.keys()
]


# ===========================
# City Choices
# ===========================
CITY_LABEL_OVERRIDES = {
    '': 'Select City',
}

def _city_slug(city):
    return city.lower().strip().replace(' ', '_').replace('-', '_').replace('/', '_')

def _city_label(city):
    if city in CITY_LABEL_OVERRIDES:
        return CITY_LABEL_OVERRIDES[city]
    return city.title().replace('_', ' ')


CITY_CHOICES = [
    (_city_slug(city), _city_label(city))
    for cities in STATE_CITY_MAP.values()
    for city in cities
]


# ===========================
# Not Allowed Usernames and Email Domains
# ===========================
NOT_ALLOWED_USERNAMES = ['admin', 'administrator', 'root', 'superuser', 'staff', 'support', 'contact', 'help', 'info', 'sales', 'marketing']

NOT_ALLOWED_EMAIL_DOMAINS = ['yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com']


# ===========================
# Notifications Types
# ===========================
NOTIFICATION_TYPES = [
    ('system_notification', 'System Notifications'),
    ('product_created', 'Product Created'),
    ('product_sold', 'Product Sold'),
    ('product_favorite', 'Product Favorite'),
    ('product_milestone_views', 'Product Milestone Views'),
    ('store_members', 'Store Members'),
    ('store_created', 'Store Created'),
    ('store_milestone_members', 'Store Milestone Members'),
    ('other', 'Other'),
]


# ==============================
# Notifications message templates
# ==============================
NOTIFICATION_TEMPLATES = {
    "store_created": ['Your store "{store_name}" is now live and visible to buyers.'],
    "store_milestone_members": [
        "🎉 Congratulations! Your store '{store_name}' has reached {milestone} members."
    ],
    "product_created": [
        'Your listing "{product_name}" was successfully published.',
        'Your product "{product_name}" is now live and visible to buyers.',
    ],
    "product_sold": [
        'Congratulations! "{product_name}" was successfully sold.',
        'Your product "{product_name}" has been marked as sold.',
    ],
    "product_favorite": [
        'Someone added your "{product_name}" to their favorites.',
        'Your product "{product_name}" just got a new favorite.',
    ],
    "product_milestone_views": [
        "{product_name} listing just hit {view_count} views!",
        '"{product_name}" is trending with {view_count} views so far.',
    ],
    "system_notification": [
        "Thank you for joining Nigeria's trusted online marketplace. Verify your account to unlock full access and start buying or selling with confidence, your username is {username}.",
        "New features are now available on the app.",
        "Your account security settings were updated.",
        "Scheduled maintenance will occur tonight from 12am to 2am.",
        "We've updated our terms of service. Please review the changes.",
    ],
    "other": [
        "Reminder: complete your profile to boost visibility.",
        'You have a new message regarding "{product_name}".',
    ],
}

# ==============================
# File Upload Settings
# ==============================
FILE_UPLOAD_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

MAX_IMAGES = 10


# ==============================
# NULL OR EMPTY VALUES
# ==============================
NULL_VALUES = [
    '',
    None,
]


# ==============================
# Boost Product Pricing
# ==============================
BOOSTED_PRODUCT_PRICE = {
    1: 600,
    3: 1500,
    7: 3000,
    15: 5000,
    30: 8000,
}

STORE_TYPE_CHOICES = [
    ("individual", "Individual Seller"),
    ("registered", "Registered Business"),
]


def user_avatar_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("accounts", "avatars", filename)


def store_logo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("accounts", "store", "logos", filename)


def store_banner_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("accounts", "store", "banners", filename)


def product_images_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("products", "images", filename)


def _normalize(value):
    """
    Normalize a string to match database slugs.
    Converts to lowercase and replaces spaces, hyphens, and slashes with underscores.
    This keeps everything consistent with _city_slug and the raw choice keys.
    """
    if not value:
        return ''
    return value.lower().strip().replace(' ', '-').replace('_', '-').replace('/', '-')


def validate_contact_methods(value):
    if not isinstance(value, list):
        raise ValidationError(_("Contact methods must be a list of strings."))

    valid_choices = [choice[0] for choice in CONTACT_METHOD_CHOICES]
    for method in value:
        if method not in valid_choices:
            raise ValidationError(_(f'"{method}" is not a valid contact method.'))

    if not value:
        raise ValidationError(_("At least one contact method is required."))
