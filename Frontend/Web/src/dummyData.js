import { FaBell, FaHeart, FaInfoCircle } from "react-icons/fa";
import { GiWheat, GiBirdTwitter } from "react-icons/gi";
import { IoMdTrendingUp } from "react-icons/io";
import { LuPackagePlus } from "react-icons/lu";
import { RiHandCoinLine } from "react-icons/ri";
import { BiSolidCategory, BiChip } from "react-icons/bi";
import { MdOutlineStroller, MdWatch } from "react-icons/md";
import {
    TbBolt, TbBackpack, TbShoppingBag, TbBallFootball, TbBabyCarriage, TbBarbell, TbBed, TbBike,
    TbBone, TbBook, TbBook2, TbBox, TbBriefcase, TbBucket, TbBuilding, TbBuildingStore,
    TbCalculator, TbCalendarEvent, TbCamera, TbCar, TbCarrot, TbCat, TbChefHat, TbCode,
    TbCpu, TbDeviceDesktop, TbDeviceGamepad, TbDeviceGamepad2, TbDeviceLaptop,
    TbDeviceMobile, TbDeviceTablet, TbDeviceTv, TbDeviceWatch, TbDog, TbDroplet, TbFish,
    TbHeadphones, TbHeart, TbHeartPlus, TbHome, TbHomeMove, TbHomePlus, TbHorse, TbLamp,
    TbMapPin, TbMoodKid, TbMotorbike, TbMovie, TbMusic, TbPaw, TbPill, TbPlant2, TbPrinter,
    TbSailboat, TbSchool, TbSeedling, TbShirt, TbShoe, TbSnowflake,
    TbSteeringWheel, TbStethoscope, TbTent, TbTool, TbTools, TbToolsKitchen2, TbTractor,
    TbTrendingUp, TbTruck, TbTruckDelivery, TbUsb, TbArmchair
} from "react-icons/tb";


export const timeAgo = (isoString) => {
    const seconds = Math.floor((new Date() - new Date(isoString)) / 1000);
    const intervals = [
        { label: 'y', secs: 31536000 },
        { label: 'mo', secs: 2592000 },
        { label: 'd', secs: 86400 },
        { label: 'h', secs: 3600 },
        { label: 'm', secs: 60 },
    ];
    for (const { label, secs } of intervals) {
        const count = Math.floor(seconds / secs);
        if (count >= 1) return `${count}${label} ago`;
    }
    return 'just now';
};


export const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString('en-NG', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    });
};


export const typeLabels = {
    system_notification: 'System notification',
    product_created: 'Product created',
    product_sold: 'Product sold',
    product_favorite: 'Product favorite',
    product_milestone_views: 'Milestone views',
    other: 'Other',
};


export const typeConfig = {
    system_notification: { icon: FaBell, color: 'text-blue-600', bg: 'bg-blue-50' },
    product_created: { icon: LuPackagePlus, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    product_sold: { icon: RiHandCoinLine, color: 'text-brand', bg: 'bg-brand/10' },
    product_favorite: { icon: FaHeart, color: 'text-red-500', bg: 'bg-red-50' },
    product_milestone_views: { icon: IoMdTrendingUp, color: 'text-purple-600', bg: 'bg-purple-50' },
    other: { icon: FaInfoCircle, color: 'text-gray-500', bg: 'bg-gray-100' },
};


export const CONDITION_CHOICES = [
    { value: 'new', label: 'New' },
    { value: 'used', label: 'Used' },
    { value: 'refurbished', label: 'Refurbished' },
]


export const CONTACT_METHOD_CHOICES = [
    { value: 'phone_call', label: 'Phone' },
    { value: 'whatsapp', label: 'WhatsApp' },
];


export const MAX_IMAGES = 10;


export const categoryIconsMap = {
    'default-icon': BiSolidCategory,
    'phones-tablets': TbDeviceMobile,
    'electronics': TbCpu,
    'vehicles': TbCar,
    'real-estate': TbHome,
    'fashion': TbShirt,
    'home-garden': TbPlant2,
    'jobs': TbBriefcase,
    'services': TbTool,
    'animals-pets': TbPaw,
    'food-agriculture': GiWheat,
    'health-beauty': TbStethoscope,
    'kids-baby': TbBabyCarriage,
    'sports-outdoor': TbBarbell,
    'books-music-movies': TbBook2,
};


export const subcategoryIconsMap = {
  // Phones & Tablets
  'mobile-phones': TbDeviceMobile,
  'tablets': TbDeviceTablet,
  'phone-accessories': TbHeadphones,
  'smartwatches': TbDeviceWatch,
  'phone-parts': BiChip,

  // Electronics
  'laptops-computers': TbDeviceLaptop,
  'tvs': TbDeviceTv,
  'audio-music': TbMusic,
  'cameras': TbCamera,
  'gaming': TbDeviceGamepad,
  'printers': TbPrinter,
  'computer-accessories': TbUsb,

  // Vehicles
  'cars': TbCar,
  'motorcycles': TbMotorbike,
  'trucks-buses': TbTruck,
  'vehicle-parts': TbTools,
  'boats': TbSailboat,
  'bicycles': TbBike,

  // Real Estate
  'houses-rent': TbHome,
  'houses-sale': TbHomePlus,
  'flats-apartments': TbBuilding,
  'land-plots': TbMapPin,
  'commercial-property': TbBuildingStore,
  'short-let': TbHomeMove,

  // Fashion
  'mens-clothing': TbShirt,
  'womens-clothing': TbHeart,
  'kids-clothing': TbMoodKid,
  'shoes': TbShoe,
  'bags': TbShoppingBag,
  'watches-jewelry': MdWatch,
  'traditional-wear': TbShirt,

  // Home & Garden
  'furniture': TbArmchair,
  'kitchen-appliances': TbToolsKitchen2,
  'bedding-linen': TbBed,
  'garden-outdoor': TbPlant2,
  'home-decor': TbLamp,
  'generators': TbBolt,
  'air-conditioners': TbSnowflake,

  // Jobs
  'accounting-finance': TbCalculator,
  'admin-office': TbBuilding,
  'engineering': TbTool,
  'healthcare': TbHeartPlus,
  'it-telecoms': TbDeviceDesktop,
  'sales-marketing': TbTrendingUp,
  'teaching': TbSchool,
  'driving-logistics': TbSteeringWheel,

  // Services
  'repair-maintenance': TbTool,
  'cleaning-services': TbBucket,
  'catering': TbChefHat,
  'event-planning': TbCalendarEvent,
  'photography': TbCamera,
  'web-dev': TbCode,
  'tutoring': TbBook,
  'moving-delivery': TbTruckDelivery,

  // Animals & Pets
  'dogs': TbDog,
  'cats': TbCat,
  'birds': GiBirdTwitter,
  'fish-aquarium': TbFish,
  'pet-accessories': TbBone,
  'livestock': TbHorse,

  // Food & Agriculture
  'farm-produce': TbCarrot,
  'processed-food': TbBox,
  'farming-equipment': TbTractor,
  'seeds-fertilizers': TbSeedling,

  // Health & Beauty
  'skincare': TbDroplet,
  'hair-products': TbTool,
  'vitamins': TbPill,
  'medical-equipment': TbHeartPlus,
  'gym-fitness': TbBarbell,
  'perfumes': TbDroplet,

  // Kids & Baby
  'baby-clothing': TbMoodKid,
  'toys-games': TbDeviceGamepad2,
  'baby-gear': MdOutlineStroller,
  'school-supplies': TbBackpack,

  // Sports & Outdoor
  'football': TbBallFootball,
  'gym-equipment': TbBarbell,
  'outdoor-camping': TbTent,
  'cycling': TbBike,

  // Books, Music & Movies
  'books-textbooks': TbBook,
  'music-instruments': TbMusic,
  'movies-dvds': TbMovie,
  'video-games': TbDeviceGamepad,
};


export const categories = [
    { slug: 'phones-tablets', label: 'Phones & Tablets', icon: TbDeviceMobile },
    { slug: 'electronics', label: 'Electronics', icon: TbCpu },
    { slug: 'vehicles', label: 'Vehicles', icon: TbCar },
    { slug: 'real-estate', label: 'Real Estate', icon: TbHome },
    { slug: 'fashion', label: 'Fashion', icon: TbShirt },
    { slug: 'home-garden', label: 'Home & Garden', icon: TbPlant2 },
    { slug: 'jobs', label: 'Jobs', icon: TbBriefcase },
    { slug: 'services', label: 'Services', icon: TbTool },
    { slug: 'animals-pets', label: 'Animals & Pets', icon: TbPaw },
    { slug: 'food-agriculture', label: 'Food & Agriculture', icon: GiWheat },
    { slug: 'health-beauty', label: 'Health & Beauty', icon: TbStethoscope },
    { slug: 'kids-baby', label: 'Kids & Baby', icon: TbBabyCarriage },
    { slug: 'sports-outdoor', label: 'Sports & Outdoor', icon: TbBarbell },
    { slug: 'books-music-movies', label: 'Books, Music & Movies', icon: TbBook2 },
];


export const CATEGORY_SUBCATEGORY_MAP = {
    "phones-tablets": ['mobile-phones', 'tablets', 'phone-accessories', 'smartwatches', 'phone-parts'],
    "electronics": ['laptops-computers', 'tvs', 'audio-music', 'cameras', 'gaming', 'printers', 'computer-accessories'],
    "vehicles": ['cars', 'motorcycles', 'trucks-buses', 'vehicle-parts', 'boats', 'bicycles'],
    "real-estate": ['houses-rent', 'houses-sale', 'flats-apartments', 'land-plots', 'commercial-property', 'short-let'],
    "fashion": ['mens-clothing', 'womens-clothing', 'kids-clothing', 'shoes', 'bags', 'watches-jewelry', 'traditional-wear'],
    "home-garden": ['furniture', 'kitchen-appliances', 'bedding-linen', 'garden-outdoor', 'home-decor', 'generators', 'air-conditioners'],
    "jobs": ['accounting-finance', 'admin-office', 'engineering', 'healthcare', 'it-telecoms', 'sales-marketing', 'teaching', 'driving-logistics'],
    "services": ['repair-maintenance', 'cleaning-services', 'catering', 'event-planning', 'photography', 'web-dev', 'tutoring', 'moving-delivery'],
    "animals-pets": ['dogs', 'cats', 'birds', 'fish-aquarium', 'pet-accessories', 'livestock'],
    "food-agriculture": ['farm-produce', 'processed-food', 'farming-equipment', 'seeds-fertilizers'],
    "health-beauty": ['skincare', 'hair-products', 'vitamins', 'medical-equipment', 'gym-fitness', 'perfumes'],
    "kids-baby": ['baby-clothing', 'toys-games', 'baby-gear', 'school-supplies'],
    "sports-outdoor": ['football', 'gym-equipment', 'outdoor-camping', 'cycling'],
    "books-music-movies": ['books-textbooks', 'music-instruments', 'movies-dvds', 'video-games'],
};


export const STATE_CITY_MAP = {
    "abia": ['Aba', 'Umuahia', 'Ohafia', 'Arochukwu', 'Isuikwuato', 'Osisioma', 'Ukwa'],
    "adamawa": ['Yola', 'Mubi', 'Numan', 'Jimeta', 'Ganye', 'Hong', 'Michika', 'Song'],
    "akwa-ibom": ['Uyo', 'Ikot Ekpene', 'Eket', 'Oron', 'Abak', 'Itu', 'Ikot Abasi', 'Etinan'],
    "anambra": ['Awka', 'Onitsha', 'Nnewi', 'Ekwulobia', 'Ihiala', 'Ogbaru', 'Aguata', 'Njikoka'],
    "bauchi": ['Bauchi', 'Azare', 'Misau', "Jama'are", 'Ningi', 'Katagum', 'Tafawa Balewa', 'Dass'],
    "bayelsa": ['Yenagoa', 'Brass', 'Nembe', 'Ogbia', 'Sagbama', 'Ekeremor', 'Kolokuma/Opokuma'],
    "benue": ['Makurdi', 'Gboko', 'Otukpo', 'Katsina-Ala', 'Vandeikya', 'Oju', 'Adikpo', 'Aliade'],
    "borno": ['Maiduguri', 'Biu', 'Bama', 'Dikwa', 'Gwoza', 'Monguno', 'Konduga', 'Kukawa'],
    "cross-river": ['Calabar', 'Ikom', 'Obudu', 'Ugep', 'Ogoja', 'Akpabuyo', 'Boki', 'Yala'],
    "delta": ['Asaba', 'Warri', 'Sapele', 'Agbor', 'Ughelli', 'Ozoro', 'Effurun', 'Kwale', 'Burutu'],
    "ebonyi": ['Abakaliki', 'Afikpo', 'Onueke', 'Izzi', 'Ezza', 'Ikwo', 'Ohaukwu', 'Ishielu'],
    "edo": ['Benin City', 'Ekpoma', 'Auchi', 'Iguobazuwa', 'Uromi', 'Sabongida-Ora', 'Igarra', 'Agenebode'],
    "ekiti": ['Ado-Ekiti', 'Ikere-Ekiti', 'Oye-Ekiti', 'Ijero-Ekiti', 'Emure-Ekiti', 'Ise-Ekiti', 'Ilawe-Ekiti', 'Aramoko'],
    "enugu": ['Enugu', 'Nsukka', 'Awgu', 'Udi', 'Oji River', 'Agbani', 'Nkanu', 'Enugu-Ezike'],
    "fct": ['Wuse', 'Garki', 'Maitama', 'Asokoro', 'Jabi', 'Kubwa', 'Gwagwalada', 'Kuje', 'Bwari', 'Abaji', 'Lugbe', 'Nyanya'],
    "gombe": ['Gombe', 'Kaltungo', 'Billiri', 'Dukku', 'Deba', 'Nafada', 'Bajoga', 'Funakaye'],
    "imo": ['Owerri', 'Orlu', 'Okigwe', 'Mgbidi', 'Oguta', 'Mbaise', 'Ehime Mbano', 'Ideato'],
    "jigawa": ['Dutse', 'Hadejia', 'Gumel', 'Ringim', 'Birnin Kudu', 'Kazaure', 'Babura', 'Gwaram'],
    "kaduna": ['Kaduna', 'Zaria', 'Kafanchan', 'Ikara', 'Saminaka', 'Kachia', 'Giwa', 'Birnin Gwari'],
    "kano": ['Kano', 'Wudil', 'Bichi', 'Gaya', 'Rano', 'Kibiya', 'Takai', 'Dawakin Tofa', 'Ungogo', 'Fagge'],
    "katsina": ['Katsina', 'Daura', 'Funtua', 'Malumfashi', 'Kankia', 'Dutsin-Ma', 'Bakori', 'Mani'],
    "kebbi": ['Birnin Kebbi', 'Argungu', 'Yelwa', 'Zuru', 'Jega', 'Kamba', 'Bunza', 'Bagudo'],
    "kogi": ['Lokoja', 'Okene', 'Idah', 'Kabba', 'Anyigba', 'Ankpa', 'Dekina', 'Ajaokuta'],
    "kwara": ['Ilorin', 'Offa', 'Omu-Aran', 'Patigi', 'Lafiagi', 'Jebba', 'Share', 'Erin-Ile'],
    "lagos": ['Ikeja', 'Lagos Island', 'Lagos Mainland', 'Yaba', 'Surulere', 'Ikorodu', 'Epe', 'Badagry', 'Ajah', 'Lekki', 'Victoria Island', 'Ikoyi', 'Apapa', 'Festac', 'Ojo', 'Alimosho', 'Agege', 'Ikotun', 'Egbeda', 'Isolo', 'Mushin', 'Oshodi', 'Maryland', 'Gbagada', 'Ogba', 'Magodo', 'Iju', 'Shomolu', 'Bariga'],
    "nasarawa": ['Lafia', 'Keffi', 'Akwanga', 'Nasarawa Eggon', 'Wamba', 'Doma', 'Karu', 'Toto'],
    "niger": ['Minna', 'Suleja', 'Kontagora', 'Bida', 'New Bussa', 'Lapai', 'Agaie', 'Wushishi'],
    "ogun": ['Abeokuta', 'Ijebu-Ode', 'Sagamu', 'Ilaro', 'Ota', 'Ifo', 'Sango-Ota', 'Ijebu-Igbo', 'Ayetoro', 'Owode'],
    "ondo": ['Akure', 'Ondo', 'Ore', 'Okitipupa', 'Ikare', 'Owo', 'Idanre', 'Ile-Oluji', 'Oka'],
    "osun": ['Osogbo', 'Ile-Ife', 'Ilesha', 'Ede', 'Ikirun', 'Iwo', 'Ejigbo', 'Ikire', 'Ila', 'Gbongan'],
    "oyo": ['Ibadan', 'Oyo', 'Ogbomosho', 'Saki', 'Iseyin', 'Eruwa', 'Kisi', 'Igbo-Ora', 'Lanlate', 'Moniya'],
    "plateau": ['Jos', 'Bukuru', 'Pankshin', 'Langtang', 'Shendam', 'Mangu', 'Bokkos', 'Bassa'],
    "rivers": ['Port Harcourt', 'Obio/Akpor', 'Bonny', 'Degema', 'Ikwerre', 'Oyigbo', 'Ahoada', 'Okrika', 'Eleme', 'Emuoha', 'Tai', 'Gokana', 'Khana'],
    "sokoto": ['Sokoto', 'Tambuwal', 'Gwadabawa', 'Wurno', 'Shagari', 'Binji', 'Bodinga', 'Goronyo'],
    "taraba": ['Jalingo', 'Wukari', 'Bali', 'Gembu', 'Zing', 'Sardauna', 'Takum', 'Ibi'],
    "yobe": ['Damaturu', 'Potiskum', 'Gashua', 'Nguru', 'Gujba', 'Buni Yadi', 'Geidam', 'Yunusari'],
    "zamfara": ['Gusau', 'Kaura-Namoda', 'Anka', 'Talata Mafara', 'Shinkafi', 'Maradun', 'Bakura', 'Bungudu'],
};

export const STORE_TYPE_CHOICES = [
    { value: 'individual', label: 'Individual seller' },
    { value: 'registered', label: 'Registered business' },
];


export const STATE_CHOICES = [
    { value: 'abia', label: 'Abia' },
    { value: 'adamawa', label: 'Adamawa' },
    { value: 'akwa-ibom', label: 'Akwa Ibom' },
    { value: 'anambra', label: 'Anambra' },
    { value: 'bauchi', label: 'Bauchi' },
    { value: 'bayelsa', label: 'Bayelsa' },
    { value: 'benue', label: 'Benue' },
    { value: 'borno', label: 'Borno' },
    { value: 'cross-river', label: 'Cross River' },
    { value: 'delta', label: 'Delta' },
    { value: 'ebonyi', label: 'Ebonyi' },
    { value: 'edo', label: 'Edo' },
    { value: 'ekiti', label: 'Ekiti' },
    { value: 'enugu', label: 'Enugu' },
    { value: 'fct', label: 'Federal Capital Territory (Abuja)' },
    { value: 'gombe', label: 'Gombe' },
    { value: 'imo', label: 'Imo' },
    { value: 'jigawa', label: 'Jigawa' },
    { value: 'kaduna', label: 'Kaduna' },
    { value: 'kano', label: 'Kano' },
    { value: 'katsina', label: 'Katsina' },
    { value: 'kebbi', label: 'Kebbi' },
    { value: 'kogi', label: 'Kogi' },
    { value: 'kwara', label: 'Kwara' },
    { value: 'lagos', label: 'Lagos' },
    { value: 'nasarawa', label: 'Nasarawa' },
    { value: 'niger', label: 'Niger' },
    { value: 'ogun', label: 'Ogun' },
    { value: 'ondo', label: 'Ondo' },
    { value: 'osun', label: 'Osun' },
    { value: 'oyo', label: 'Oyo' },
    { value: 'plateau', label: 'Plateau' },
    { value: 'rivers', label: 'Rivers' },
    { value: 'sokoto', label: 'Sokoto' },
    { value: 'taraba', label: 'Taraba' },
    { value: 'yobe', label: 'Yobe' },
    { value: 'zamfara', label: 'Zamfara' },
];

export const formatJoinDate = (isoString) => {
    return new Date(isoString).toLocaleDateString('en-NG', {
        month: 'long',
        year: 'numeric',
    });
};


export const formatLastLogin = (isoString) => {
    return new Date(isoString).toLocaleDateString('en-NG', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};