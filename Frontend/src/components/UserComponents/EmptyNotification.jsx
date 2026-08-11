import { FaBell } from "react-icons/fa";


const EmptyNotification = () => {
  return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
          <FaBell size={50} className="text-gray-300 mb-3" strokeWidth={1.5} />
          <p className="text-sm font-semibold text-gray-700">No notifications yet</p>
          <p className="text-xs text-gray-400 mt-1">
              We'll let you know when something happens.
          </p>
      </div>
  )
}

export default EmptyNotification;
