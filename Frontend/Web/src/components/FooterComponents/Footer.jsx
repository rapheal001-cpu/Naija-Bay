import { Link } from 'react-router-dom';
import { FaFacebookF, FaTwitter, FaInstagram, FaYoutube, FaEnvelope, FaPhoneAlt, FaMapMarkerAlt } from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    about: [
      { label: 'About NaijaBay', href: '/about' },
      { label: 'Terms & Conditions', href: '/terms' },
      { label: 'Privacy Policy', href: '/privacy' },
    ],
    support: [
      { label: 'Help Center', href: '/' },
      { label: 'Report a Product', href: '/' },
    ],
    sell: [
      { label: 'Sell on NaijaBay', href: '/sell' },
      { label: 'Seller Guidelines', href: '/seller/guidelines' },
    ],
    categories: [
      { label: 'Electronics', href: '/products?category=electronics' },
      { label: 'Fashion', href: '/products?category=fashion' },
      { label: 'Home & Garden', href: '/products?category=real-estate' },
      { label: 'Vehicles', href: '/products?category=vehicles' },
      { label: 'Phones & Tablets', href: '/products?category=phones-tablets' },
    ],
  };

  return (
    <footer className="bg-brand text-gray-300">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8">
          
          {/* Brand Column */}
          <div className="lg:col-span-1">
            <Link to="/" className="text-2xl font-bold text-white">
              Naija<span className="text-white">Bay</span>
            </Link>
            <p className="mt-4 text-sm text-white leading-relaxed">
              Nigeria's trusted marketplace. Buy and sell anything from electronics to cars, fashion to real estate and more.
            </p>
            
            {/* Social Icons */}
            <div className="flex space-x-4 mt-6">
              <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" 
                 className="w-9 h-9 rounded-full bg-white text-blue-600 flex items-center justify-center hover:translate-y-3 transition-transform">
                <FaFacebookF size={16} />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer"
                 className="w-9 h-9 rounded-full bg-white text-blue-400 flex items-center justify-center hover:translate-y-3 transition-transform">
                <FaTwitter size={16} />
              </a>
              <a href="https://instagram.com" target="_blank" rel="noopener noreferrer"
                 className="w-9 h-9 rounded-full bg-white text-red-500 flex items-center justify-center hover:translate-y-3 transition-transform">
                <FaInstagram size={16} />
              </a>
              <a href="https://youtube.com" target="_blank" rel="noopener noreferrer"
                 className="w-9 h-9 rounded-full bg-white text-red-600 flex items-center justify-center hover:translate-y-3 transition-transform">
                <FaYoutube size={16} />
              </a>
            </div>
          </div>

          {/* About Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase text-sm tracking-wider">About</h3>
            <ul className="space-y-3">
              {footerLinks.about.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="text-sm hover:text-white hover:font-semibold transition-transform">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase text-sm tracking-wider">Support</h3>
            <ul className="space-y-3">
              {footerLinks.support.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="text-sm hover:text-white hover:font-semibold transition-transform">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Sell Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase text-sm tracking-wider">Sell</h3>
            <ul className="space-y-3">
              {footerLinks.sell.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="text-sm hover:text-white hover:font-semibold transition-transform">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Categories Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase text-sm tracking-wider">Categories</h3>
            <ul className="space-y-3">
              {footerLinks.categories.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="text-sm hover:text-white hover:font-semibold transition-transform">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Contact Bar */}
        <div className="mt-12 pt-8 border-t border-white grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <FaPhoneAlt size={18} className="text-white" />
            <div>
              <p className="text-sm text-white">Call Us</p>
              <p className="text-white font-medium">+234 800 123 4567</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <FaEnvelope size={18} className="text-white" />
            <div>
              <p className="text-sm text-white">Email Us</p>
              <p className="text-white font-medium">support@naijabay.com</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <FaMapMarkerAlt size={18} className="text-white" />
            <div>
              <p className="text-sm text-white">Location</p>
              <p className="text-white font-medium">Lagos, Nigeria</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="bg-brand/90 border-t border-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-white">
              © {currentYear} NaijaBay. All rights reserved.
            </p>
            <div className="flex space-x-6 text-sm text-white">
              <Link to="/terms" className="hover:font-semibold transition-transform">Terms</Link>
              <Link to="/privacy" className="hover:font-semibold transition-transform">Privacy</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;