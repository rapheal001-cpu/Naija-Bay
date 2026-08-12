import io
import random
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from accounts.models import User
from products.models import Product, ProductImage
from NaijaBay.utils import (
    CATEGORY_CHOICES,
    SUBCATEGORY_MAP,
    CONDITION_CHOICES,
    CONTACT_METHOD_CHOICES,
    STATE_CHOICES,
    STATE_CITY_MAP,
)

# =============================================================================
# REALISTIC PRODUCT CATALOG
# =============================================================================

PRODUCT_CATALOG = {
    "phones_tablets": {
        "mobile_phones": [
            "iPhone 14 Pro Max 256GB",
            "Samsung Galaxy S23 Ultra",
            "Google Pixel 7 Pro",
            "Xiaomi Redmi Note 12 Pro",
            "Infinix Hot 30 Play",
            "Tecno Camon 20 Premier",
            "iPhone 11 64GB",
            "Samsung Galaxy A54 5G",
            "Oppo Reno 8T",
            "Nokia G60 5G",
            "iPhone 13 Pro 128GB",
            "Samsung Galaxy Z Fold 5",
            "Nothing Phone 2",
        ],
        "tablets": [
            "iPad Pro 12.9 inch M2",
            "Samsung Galaxy Tab S9",
            "Xiaomi Pad 6",
            "Lenovo Tab P11 Plus",
            "Amazon Fire HD 10",
            "iPad Air 5th Gen",
        ],
        "phone_accessories": [
            "Apple AirPods Pro 2nd Gen",
            "Samsung Galaxy Buds2 Pro",
            "Anker 20W Fast Charger",
            "USB-C to Lightning Cable 2M",
            "Wireless Charging Pad 15W",
            "iPhone 14 Pro Leather Case",
            "Tempered Glass Screen Protector",
            "MagSafe Wallet",
        ],
        "smartwatches": [
            "Apple Watch Series 8",
            "Samsung Galaxy Watch 6 Classic",
            "Garmin Forerunner 265",
            "Fitbit Charge 5",
            "Amazfit GTR 4",
            "Huawei Watch GT 4",
        ],
        "phone_parts": [
            "iPhone 13 OLED Display Screen Original",
            "Samsung S21 Battery Replacement",
            "iPhone 12 Charging Port Flex Cable",
            "Samsung S22 Rear Camera Module",
            "iPhone 14 Back Glass Panel Replacement",
            "Xiaomi Redmi Power Button Flex",
        ],
    },
    "electronics": {
        "laptops_computers": [
            "MacBook Air M2 13-inch",
            "HP Pavilion 15 Core i5",
            "Dell XPS 13 9315",
            "Lenovo ThinkPad X1 Carbon",
            "Asus ZenBook 14",
            "Acer Nitro 5 Gaming Laptop",
        ],
        "tvs": [
            "LG 55 inch OLED Smart TV",
            "Samsung 65 inch Neo QLED 4K",
            "Sony Bravia 50 inch 4K",
            "Hisense 43 inch Smart Android TV",
            "TCL 32 inch HD TV",
            "Samsung 55 inch Smart TV",
        ],
        "audio_music": [
            "Sony WH-1000XM5 Wireless Headphones",
            "JBL Charge 5 Bluetooth Speaker",
            "Bose SoundLink Flex",
            "Samsung Soundbar HW-B450",
            "AirPods Max",
            "Beats Studio3 Wireless",
        ],
        "cameras": [
            "Canon EOS 250D DSLR",
            "Sony Alpha a6400 Mirrorless",
            "Nikon D3500 with 18-55mm Lens",
            "GoPro Hero 11 Black",
            "DJI Osmo Action 4",
            "Canon PowerShot G7X Mark III",
        ],
        "gaming": [
            "Sony PlayStation 5 Console",
            "Xbox Series X 1TB",
            "Nintendo Switch OLED",
            "PS5 DualSense Controller",
            "Gaming Keyboard RGB Mechanical",
            "Logitech G502 Mouse",
        ],
        "printers": [
            "HP LaserJet Pro M404n",
            "Canon PIXMA G3420 Ink Tank",
            "Epson EcoTank L3250",
            "Brother DCP-T720DW",
            "HP DeskJet 2710 All-in-One",
        ],
        "computer_accessories": [
            "Logitech MX Master 3S Mouse",
            "Dell USB-C Hub Adapter",
            "Samsung T7 Portable SSD 1TB",
            "HP Wireless Keyboard and Mouse Combo",
            "Laptop Stand Aluminum Adjustable",
        ],
    },
    "vehicles": {
        "cars": [
            "Toyota Camry 2015 LE",
            "Honda Accord 2013 EX-L",
            "Lexus RX350 2018",
            "Mercedes Benz C300 2017",
            "Kia Rio 2016 LX",
            "Toyota Corolla 2014",
            "Hyundai Elantra 2015",
            "BMW 3 Series 2016",
        ],
        "motorcycles": [
            "Honda ACE 750 Cruiser",
            "Yamaha MT-07 2020",
            "Suzuki GSX-R600",
            "Kawasaki Ninja 400",
            "Boxer Motorcycle 150cc",
            "Haojue Lucky 125cc",
        ],
        "trucks_buses": [
            "Toyota Hilux 2018 Double Cabin",
            "Ford F-150 Raptor 2019",
            "Mitsubishi Canter Truck",
            "Isuzu D-Max 2020",
            "Toyota Coaster Bus 2012",
        ],
        "vehicle_parts": [
            "Toyota Corolla 2014 Front Bumper",
            "Complete Engine for Honda Accord",
            "Car Alloy Rims 17 inch Set of 4",
            "Brand New Shock Absorbers Pair",
            "Car Battery 75AH Maintenance Free",
        ],
        "boats": [
            "Fishing Boat 15HP Outboard",
            "Speed Boat with Yamaha Engine",
            "Fiberglass Canoe",
        ],
        "bicycles": [
            "Mountain Bike 26 inch 21-Speed",
            "Road Bicycle Carbon Frame",
            "Kids Bicycle 16 inch",
            "Electric Bicycle 350W",
            "BMX Freestyle Bike",
        ],
    },
    "real_estate": {
        "houses_rent": [
            "3 Bedroom Flat for Rent",
            "Self-Contained Apartment",
            "2 Bedroom Bungalow",
            "Luxury 4 Bedroom Duplex",
            "Mini Flat with POP Ceiling",
        ],
        "houses_sale": [
            "5 Bedroom Fully Detached Duplex",
            "3 Bedroom Bungalow with BQ",
            "Semi-Detached 4 Bedroom House",
            "Newly Built 2 Bedroom Flat",
        ],
        "flats_apartments": [
            "2 Bedroom Flat in Gated Estate",
            "3 Bedroom Apartment with Gym Access",
            "Luxury Studio Apartment",
            "Serviced 1 Bedroom Flat",
        ],
        "land_plots": [
            "Plot of Land 600sqm with C of O",
            "Half Plot 300sqm Dry Land",
            "1 Acre Farmland for Sale",
            "Corner Piece Land 1000sqm",
        ],
        "commercial_property": [
            "Shop Space in Busy Plaza",
            "Warehouse 5000sqft for Rent",
            "Office Space 200sqm in CBD",
            "Open Space for Event Center",
        ],
        "short_let": [
            "Fully Furnished 2 Bedroom Short Let",
            "Luxury Studio Apartment Daily",
            "3 Bedroom Airbnb-Style Apartment",
            "Self-Contain Short Stay 1 Week",
        ],
    },
    "fashion": {
        "mens_clothing": [
            "Men Native Agbada Set Complete",
            "Corporate Shirt and Trouser Set",
            "Polo Ralph Lauren T-Shirt",
            "Men's Denim Jacket",
            "Traditional Isiagu Wear",
        ],
        "womens_clothing": [
            "Female Ankara Gown with Headtie",
            "Office Wear Skirt and Blouse",
            "Chiffon Dinner Dress",
            "Casual Jumpsuit",
            "Lace Iro and Buba Set",
        ],
        "kids_clothing": [
            "Children School Uniform Set",
            "Baby Onesie Pack of 5",
            "Kids Party Wear Dress",
            "Boys Cargo Shorts Set",
            "Traditional Kids Wear",
        ],
        "shoes": [
            "Nike Air Max 270 Sneakers",
            "Adidas Ultraboost Running Shoes",
            "Men's Leather Official Shoe",
            "Female Block Heels Sandals",
            "Chelsea Boots Genuine Leather",
        ],
        "bags": [
            "Louis Vuitton Inspired Handbag",
            "Leather Laptop Briefcase",
            "School Backpack",
            "Designer Crossbody Bag",
            "Travel Luggage Bag 28 inch",
        ],
        "watches_jewelry": [
            "Female Handmade Jewelry Set",
            "Casio G-Shock Watch",
            "Gold Plated Necklace",
            "Men's Classic Wristwatch",
            "Engagement Ring 18K Gold",
        ],
        "traditional_wear": [
            "Complete Agbada with Fila Cap",
            "Aso Oke Gele and Ipele Set",
            "Isiagu Traditional Top",
            "Coral Beads Necklace Set",
        ],
    },
    "home_garden": {
        "furniture": [
            "5-Seater Fabric Sofa Set",
            "King Size Bed Frame with Mattress",
            "Dining Table 6-Seater Wooden",
            "Wardrobe 4-Door Sliding",
            "Center Glass Table",
        ],
        "kitchen_appliances": [
            "Kitchen Cabinet Complete Set",
            "Microwave Oven 20L",
            "Blender 1.5L 350W",
            "Rice Cooker 2.8L",
            "Electric Kettle Stainless Steel",
        ],
        "bedding_linen": [
            "Bedsheet with 4 Pillowcases Cotton",
            "Duvet and Duvet Cover Set",
            "Memory Foam Pillow",
            "Mosquito Net Canopy",
            "Weighted Blanket 7kg",
        ],
        "garden_outdoor": [
            "Outdoor Patio Chair Set",
            "Garden Umbrella with Stand",
            "Flower Pots Ceramic Set",
            "Lawn Mower Electric",
            "Garden Hose 30M with Spray Gun",
        ],
        "home_decor": [
            "Wall Art Canvas Painting Set",
            "Decorative Mirror 3ft",
            "LED Wall Sconce Light",
            "Artificial Flowers Vase Arrangement",
            "Curtains Blackout 2 Panels",
        ],
        "generators": [
            "Sumec Firman 5KVA Generator",
            "Thermocool 3.5KVA Generator",
            "Elepaq 2.8KVA Generator",
            "Lutian 10KVA Diesel Generator",
            "Tiger 1.8KVA Petrol Generator",
        ],
        "air_conditioners": [
            "LG 1.5HP Split Unit Inverter",
            "Panasonic 2HP Standing AC",
            "Samsung 1HP Window Unit",
            "Midea 1.5HP Split Air Conditioner",
            "Haier Thermocool 2.5HP Split",
        ],
    },
    "jobs": {
        "accounting_finance": [
            "Accountant Needed Urgently",
            "Financial Analyst Position",
            "Auditor with ICAN Certificate",
            "Tax Consultant Remote",
        ],
        "admin_office": [
            "Office Admin Assistant",
            "Front Desk Officer Needed",
            "Personal Assistant to CEO",
            "Data Entry Clerk Remote",
        ],
        "engineering": [
            "Civil Engineer Site Supervisor",
            "Electrical Engineer Needed",
            "Mechanical Engineer",
            "AutoCAD Draftsman",
        ],
        "healthcare": [
            "Registered Nurse Needed",
            "Pharmacy Technician",
            "Medical Laboratory Scientist",
            "Community Health Worker",
        ],
        "it_telecoms": [
            "Full Stack Web Developer",
            "Network Engineer CCNA",
            "UI/UX Designer Remote",
            "Mobile App Developer Flutter",
            "Cybersecurity Analyst",
        ],
        "sales_marketing": [
            "Sales Representative Needed",
            "Digital Marketing Manager",
            "Social Media Manager",
            "Brand Ambassador",
        ],
        "teaching": [
            "Secondary School Mathematics Teacher",
            "Early Years Educator",
            "Private Home Tutor",
            "ICT Teacher Needed Urgently",
        ],
        "driving_logistics": [
            "Driver Wanted Urgently",
            "Truck Driver with License",
            "Dispatch Rider Needed",
            "Logistics Coordinator",
        ],
    },
    "services": {
        "repair_maintenance": [
            "Generator Repair Service",
            "Phone Screen Repair Home Service",
            "AC Installation and Repair",
            "Plumber Available 24/7",
            "Car Mechanic Mobile Service",
        ],
        "cleaning_services": [
            "Professional Home Cleaning Service",
            "Post-Construction Cleaning",
            "Office Cleaning Weekly",
            "Laundry and Dry Cleaning Pickup",
        ],
        "catering": [
            "Small Chops Catering Service",
            "Wedding Catering 500 Guests",
            "Birthday Party Catering",
            "Corporate Lunch Delivery",
        ],
        "event_planning": [
            "Wedding Planner Full Package",
            "Event Decoration and Planning",
            "Birthday Party Organizer",
            "Corporate Event Management",
        ],
        "photography": [
            "Wedding Photography Package",
            "Portrait Studio Session",
            "Event Coverage Photographer",
            "Product Photography for Business",
        ],
        "web_dev": [
            "Business Website Design",
            "E-Commerce Website Development",
            "Portfolio Website",
            "WordPress Blog Setup",
        ],
        "tutoring": [
            "WAEC/NECO Mathematics Tutor",
            "JAMB Preparation Classes",
            "Python Programming Tutor",
            "Private French Lessons",
        ],
        "moving_delivery": [
            "House Moving Service 1 Bedroom",
            "Interstate Delivery Service",
            "Furniture Movers",
            "Packaging and Relocation Service",
        ],
    },
    "animals_pets": {
        "dogs": [
            "Male German Shepherd Puppy 3 Months",
            "Boerboel Guard Dog Adult",
            "Rottweiler Puppy",
            "Lhasa Apso Female",
            "Caucasian Shepherd Puppy",
        ],
        "cats": [
            "Persian Cat Kitten White",
            "Siamese Cat Adult",
            "British Shorthair Kitten",
            "Ragdoll Cat with Papers",
        ],
        "birds": [
            "African Grey Parrot Talking",
            "Fancy Pigeons Pair",
            "Love Birds Pair with Cage",
            "Ostrich Chick",
        ],
        "fish_aquarium": [
            "Koi Carp Fish 6 inches",
            "Aquarium Tank 50 Litres Complete",
            "Arowana Fish Juvenile",
            "Goldfish Pack of 10",
        ],
        "pet_accessories": [
            "Large Dog Cage Metal",
            "Automatic Pet Feeder",
            "Cat Litter Box Self Cleaning",
            "Dog Leash and Collar Set",
            "Aquarium Filter Pump",
        ],
        "livestock": [
            "Goat Male Adult (Ram)",
            "Sheep Ewe Pregnant",
            "Piglets 2 Months Old",
            "Turkey Matured Male",
            "Rabbit Breeding Pair",
        ],
    },
    "food_agriculture": {
        "farm_produce": [
            "Fresh Tomatoes Basket Paint",
            "Bag of Rice 50kg Foreign",
            "Yam Tubers Bulk 100 Pieces",
            "Fresh Pepper Basket",
            "Sweet Potatoes Sack",
        ],
        "processed_food": [
            "Garri Ijebu 5kg Bag",
            "Palm Oil 25 Litres",
            "Honey Pure Organic 1Litre",
            "Groundnut Oil 5 Litres",
            "Smoked Catfish 1kg",
        ],
        "farming_equipment": [
            "Manual Knapsack Sprayer",
            "Water Pumping Machine 2 inch",
            "Wheelbarrow Heavy Duty",
            "Garden Fork and Hoe Set",
            "Maize Thresher Machine",
        ],
        "seeds_fertilizers": [
            "Hybrid Maize Seeds 2kg",
            "NPK Fertilizer 50kg",
            "Organic Compost Manure",
            "Tomato Seeds Imported",
            "Urea Fertilizer 50kg",
        ],
    },
    "health_beauty": {
        "skincare": [
            "Organic Black Soap 500g",
            "Vitamin C Serum for Face",
            "Shea Butter Raw Unrefined",
            "Sunscreen SPF 50",
            "Exfoliating Body Scrub",
        ],
        "hair_products": [
            "Human Hair Wig 24 inches",
            "Virgin Hair Bundle with Closure",
            "Hair Growth Oil Organic",
            "Dreadlock Maintenance Kit",
            "Hair Straightener Brush",
        ],
        "vitamins": [
            "Vitamin D3 1000IU 60 Caps",
            "Zinc and Vitamin C Complex",
            "Omega-3 Fish Oil 1000mg",
            "Multivitamin Tablets Pack",
        ],
        "medical_equipment": [
            "Blood Pressure Monitor Digital",
            "Infrared Thermometer",
            "Glucometer with Strips",
            "Nebulizer Machine",
            "First Aid Kit Complete",
        ],
        "gym_fitness": [
            "Dumbbell Set 20kg Adjustable",
            "Treadmill Electric Foldable",
            "Yoga Mat Non-Slip",
            "Kettlebell 12kg",
            "Resistance Bands Set",
        ],
        "perfumes": [
            "Designer Perfume Oil 100ml",
            "Versace Pour Homme Inspired",
            "Chanel No 5 Type",
            "Unisex Oud Fragrance",
            "Body Spray Set of 3",
        ],
    },
    "kids_baby": {
        "baby_clothing": [
            "Newborn Baby Clothes Set",
            "Baby Rompers Pack of 6",
            "Toddler Party Dress",
            "Baby Sweater Knitted",
        ],
        "toys_games": [
            "Kids Educational Toys Set",
            "Building Blocks LEGO Compatible",
            "Remote Control Car",
            "Baby Walker with Music",
            "Kitchen Play Set for Kids",
        ],
        "baby_gear": [
            "Baby Stroller with Car Seat Combo",
            "Baby Crib Wooden with Mattress",
            "High Chair Feeding",
            "Baby Carrier Ergonomic",
            "Infant Car Seat",
        ],
        "school_supplies": [
            "School Backpack with Lunch Box",
            "Mathematical Set Complete",
            "Exercise Books 40 Leaves Pack",
            "Crayons 48 Colors",
            "School Uniform Set",
        ],
    },
    "sports_outdoor": {
        "football": [
            "Nike Pitch Football Size 5",
            "Football Complete Kit Jersey",
            "Football Boots Studs",
            "Goalkeeper Gloves Professional",
            "Training Cones Set",
        ],
        "gym_equipment": [
            "Adjustable Bench Press",
            "Barbell Rod 5ft with Plates",
            "Pull-Up Bar Doorway",
            "Skipping Rope Digital Counter",
            "Ab Roller Wheel",
        ],
        "outdoor_camping": [
            "Camping Tent 4-Person",
            "Sleeping Bag Waterproof",
            "Portable Camping Stove",
            "Solar Camping Lantern",
            "Outdoor Foldable Chair",
        ],
        "cycling": [
            "Mountain Bike 26 inch",
            "Helmet with LED Light",
            "Bicycle Lock Heavy Duty",
            "Cycling Jersey and Shorts",
            "Bike Pump with Pressure Gauge",
        ],
    },
    "books_music_movies": {
        "books_textbooks": [
            "JAMB Past Questions and Answers",
            "WAEC Mathematics Textbook",
            "Rich Dad Poor Dad",
            "Atomic Habits Hardcover",
            "Nursing School Textbooks Set",
        ],
        "music_instruments": [
            "Keyboard Piano 61 Keys",
            "Acoustic Guitar 40 inch",
            "Yamaha Digital Piano P-45",
            "Violin Starter Pack",
            "Drum Practice Pad",
        ],
        "movies_dvds": [
            "Classic Nollywood Movies Collection",
            "Marvel Cinematic Universe Box Set",
            "African Documentary Collection",
            "Cartoon Network Classics DVD",
        ],
        "video_games": [
            "FIFA 24 PS5 Game",
            "Call of Duty Modern Warfare III",
            "GTA V Premium Edition",
            "God of War Ragnarok",
            "NBA 2K24",
        ],
    },
}

# =============================================================================
# DESCRIPTIONS
# =============================================================================


def generate_description(name, category, sub_category, condition):
    cond = condition or "used"

    if category == "real_estate":
        if "rent" in sub_category or "short_let" in sub_category:
            return f"Spacious {name} available for rent. Well maintained property in a secure neighborhood. Water and light available. Schedule a viewing today."
        elif (
            "sale" in sub_category
            or "land" in sub_category
            or "commercial" in sub_category
        ):
            return f"Premium {name} available for sale. Genuine documentation, good location with access road. Serious buyers only."
        return f"Quality {name} in a desirable location. Good access road and secure environment. Contact for inspection."

    if category == "jobs":
        return f"{name}. Competitive salary and benefits. Qualified candidates should apply with CV. Immediate start available."

    if category == "services":
        return f"Professional {name}. Reliable and experienced team. Affordable rates with quality guaranteed. Book an appointment today."

    if category == "animals_pets":
        if "livestock" in sub_category:
            return f"Healthy {name}. Well fed and vaccinated. Available for immediate pickup. Bulk purchase discount available."
        return f"Healthy and active {name}. Vaccinated and dewormed. Friendly temperament. Genuine buyers only."

    if category == "food_agriculture":
        if "equipment" in sub_category or "seeds" in sub_category:
            return f"Quality {name}. Durable and reliable for farming needs. Available at wholesale price. Nationwide delivery possible."
        return f"Fresh and quality {name}. Farm direct, no preservatives. Bulk orders available at discounted price. Fast delivery."

    if cond == "new":
        return f"Brand new {name}, still sealed in original packaging with full warranty. Fast delivery available. Order now while stock lasts."
    elif cond == "refurbished":
        return f"Certified refurbished {name}. Tested and confirmed working perfectly. Comes with 3 months warranty. Great value for money."
    else:
        return f"{name} in excellent working condition. Well maintained with no faults. Come and inspect before payment. Price is negotiable for serious buyers."


# =============================================================================
# REALISTIC PRICE RANGES PER SUBCATEGORY
# =============================================================================

PRICE_RANGES = {
    "phones_tablets": (45000, 950000),
    "electronics": (18000, 1200000),
    "vehicles": (1200000, 18000000),
    "real_estate": {
        "houses_rent": (250000, 2500000),
        "houses_sale": (15000000, 85000000),
        "flats_apartments": (350000, 4500000),
        "land_plots": (5000000, 55000000),
        "commercial_property": (800000, 15000000),
        "short_let": (15000, 85000),
    },
    "fashion": (3500, 85000),
    "home_garden": (12000, 650000),
    "jobs": (45000, 550000),
    "services": (5000, 250000),
    "animals_pets": (8000, 350000),
    "food_agriculture": (2500, 150000),
    "health_beauty": (2000, 120000),
    "kids_baby": (3500, 120000),
    "sports_outdoor": (4500, 280000),
    "books_music_movies": (2500, 550000),
}


def get_price(category, sub_category):
    if category == "real_estate" and isinstance(PRICE_RANGES.get(category), dict):
        min_p, max_p = PRICE_RANGES[category].get(sub_category, (500000, 5000000))
    else:
        min_p, max_p = PRICE_RANGES.get(category, (5000, 50000))

    price = random.randint(min_p, max_p)
    if price > 50000:
        return round(price / 1000) * 1000
    return round(price / 500) * 500


# =============================================================================
# COLORS
# =============================================================================

COLORS = [
    "black",
    "white",
    "blue",
    "red",
    "silver",
    "gold",
    "green",
    "yellow",
    "pink",
    "purple",
    "gray",
    "orange",
    "brown",
    "beige",
    "navy",
    "cream",
]

# =============================================================================
# PRODUCT IMAGE GENERATOR
# =============================================================================

IMAGE_FORMATS = [
    "JPEG",
    "JPEG",
    "JPEG",
    "PNG",
]  # weighted more toward jpg, like real uploads

PLACEHOLDER_BG_COLORS = [
    (241, 196, 15),
    (231, 76, 60),
    (52, 152, 219),
    (46, 204, 113),
    (155, 89, 182),
    (52, 73, 94),
    (230, 126, 34),
    (26, 188, 156),
    (149, 165, 166),
    (44, 62, 80),
]


def generate_placeholder_image(product_name, image_format, width=800, height=800):
    """Generates a simple colored image with the product name printed on it."""
    bg_color = random.choice(PLACEHOLDER_BG_COLORS)
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    words = product_name.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > width - 80:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    total_text_height = len(lines) * 55
    y = (height - total_text_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill="white", font=font)
        y += 55

    buffer = io.BytesIO()
    img.save(
        buffer, format=image_format, quality=85 if image_format == "JPEG" else None
    )
    buffer.seek(0)
    return buffer


def attach_images_to_product(product):
    """Creates between 6 and 10 ProductImage objects for a product."""
    count = random.randint(6, 10)
    for i in range(count):
        image_format = random.choice(IMAGE_FORMATS)
        extension = "jpg" if image_format == "JPEG" else "png"

        buffer = generate_placeholder_image(product.product_name, image_format)
        filename = f"{product.product_slug}-{i + 1}.{extension}"

        product_image = ProductImage(product=product)
        product_image.image.save(filename, ContentFile(buffer.read()), save=True)


# =============================================================================
# COMMAND
# =============================================================================


class Command(BaseCommand):
    help = "Seed the database with realistic sample products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Username of the user to create products for",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of products to create (default: 20)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        count = options["count"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        categories = [c[0] for c in CATEGORY_CHOICES if c[0]]
        states = [s[0] for s in STATE_CHOICES if s[0]]
        conditions = [c[0] for c in CONDITION_CHOICES if c[0]]
        contact_methods_all = [m[0] for m in CONTACT_METHOD_CHOICES if m[0]]

        created = 0
        used_combinations = set()

        for i in range(count):
            category = random.choice(categories)
            while category not in PRODUCT_CATALOG:
                category = random.choice(categories)

            subcats = list(PRODUCT_CATALOG[category].keys())
            sub_category = random.choice(subcats)

            names = PRODUCT_CATALOG[category][sub_category]
            name = random.choice(names)

            combo_key = (category, sub_category, name)
            if combo_key in used_combinations and len(used_combinations) < count * 2:
                name = f"{name} - {random.choice(['Premium', 'Original', '2024 Model', 'Grade A', 'Direct UK'])}"
            used_combinations.add(combo_key)

            state = random.choice(states)
            city = random.choice(STATE_CITY_MAP.get(state, [""]))

            condition = random.choice(conditions)

            contact_methods = [random.choice(contact_methods_all)]
            if random.random() < 0.4:
                second = random.choice(contact_methods_all)
                if second not in contact_methods:
                    contact_methods.append(second)

            needs_phone = any(m in contact_methods for m in ("phone_call", "whatsapp"))
            contact_number = (
                f"090{random.randint(10000000, 99999999)}" if needs_phone else ""
            )

            description = generate_description(name, category, sub_category, condition)

            price = get_price(category, sub_category)

            product = Product.objects.create(
                product_user=user,
                product_name=name,
                description=description,
                price=Decimal(str(price)),
                category=category,
                sub_category=sub_category,
                condition=condition,
                color=random.choice(COLORS),
                quantity=(
                    random.randint(1, 5)
                    if category not in ["real_estate", "jobs", "services"]
                    else 1
                ),
                negotiable=(
                    random.choice([True, False])
                    if category not in ["real_estate", "jobs"]
                    else True
                ),
                state=state,
                city=city,
                contact_methods=contact_methods,
                contact_number=contact_number,
                active=True,
                sold=False,
            )

            # Generate 6-10 placeholder images for this product
            attach_images_to_product(product)

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created} realistic products for user '{username}'."
            )
        )
