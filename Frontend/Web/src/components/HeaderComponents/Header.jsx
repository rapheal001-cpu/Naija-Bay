import LeftComponent from "./LeftComponent.jsx";
import RightComponent from "./RightComponent.jsx";


const Header = () => {
  return (
      <header className="flex justify-between items-center z-50 fixed top-0 w-full h-20 bg-brand border-b shadow-sm shadow-gray-300 border-b-gray-300 py-3 px-4 lg:px-24">
          <LeftComponent />
          <RightComponent />
      </header>
  )
}

export default Header