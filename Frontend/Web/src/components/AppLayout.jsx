import Header from './HeaderComponents/Header.jsx';
import AppSidebar from './HeaderComponents/AppSidebar.jsx';
import Footer from './FooterComponents/Footer.jsx';

/**
 * Shared page chrome: header on top, optional full-width hero slot,
 * then a sticky sidebar beside the page content, footer below.
 */
const AppLayout = ({ children, hero = null, withSidebar = true }) => (
    <>
        <Header />
        {hero}
        <div className="mx-auto flex max-w-7xl items-start gap-6 px-4 pb-10 lg:px-8">
            {withSidebar && <AppSidebar />}
            <main className="min-w-0 flex-1">{children}</main>
        </div>
        <Footer />
    </>
);

export default AppLayout;
