import { Link } from 'react-router-dom';
import { FaFacebookF, FaTwitter, FaInstagram, FaYoutube } from 'react-icons/fa';

/**
 * Slim 2-row footer (brand + essential links). Content sections live in the
 * full sitemap on larger layouts; this stays compact everywhere.
 */
const Footer = () => {
    const year = new Date().getFullYear();
    const social = [
        { href: 'https://facebook.com', icon: FaFacebookF, label: 'Facebook' },
        { href: 'https://twitter.com', icon: FaTwitter, label: 'Twitter / X' },
        { href: 'https://instagram.com', icon: FaInstagram, label: 'Instagram' },
        { href: 'https://youtube.com', icon: FaYoutube, label: 'YouTube' },
    ];
    const links = [
        { label: 'Browse ads', href: '/products' },
        { label: 'Post a free ad', href: '/sell' },
        { label: 'My Ads', href: '/my-ads' },
        { label: 'Messages', href: '/messages' },
        { label: 'About', href: '/about' },
        { label: 'Contact', href: '/contact' },
    ];

    return (
        <footer className="bg-white border-t border-gray-100 pb-24 lg:pb-0">
            <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between">
                <div className="flex items-center gap-3">
                    <Link to="/" className="text-lg font-black tracking-tight text-gray-900">
                        Naija<span className="text-brand">Bay</span>
                    </Link>
                    <p className="hidden text-xs text-gray-400 sm:block">Nigeria's online marketplace.</p>
                </div>

                <nav aria-label="Footer" className="flex flex-wrap items-center gap-x-5 gap-y-2">
                    {links.map((link) => (
                        <Link key={link.label} to={link.href} className="text-xs font-semibold text-gray-500 hover:text-brand">
                            {link.label}
                        </Link>
                    ))}
                </nav>

                <div className="flex items-center gap-2">
                    {social.map(({ href, icon: Icon, label }) => (
                        <a
                            key={label}
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label={label}
                            className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-500 transition-colors hover:bg-brand hover:text-white"
                        >
                            <Icon size={13} />
                        </a>
                    ))}
                </div>
            </div>
            <div className="border-t border-gray-50">
                <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-1 px-4 py-3 text-[11px] text-gray-400 sm:px-6 sm:flex-row lg:px-8">
                    <p>© {year} NaijaBay. All rights reserved.</p>
                    <p>Buy · Sell · Chat — across Nigeria</p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
