import { useNavigate, useParams } from 'react-router-dom';
import ProfileData from "../components/UserComponents/ProfileData.jsx";
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useFetchOtherUserData, useFetchUserData } from '../hooks/UseQuery.js';
import { removeOtherUser, setOtherUser, setUser } from '../slice/UserSlice.js';
import ProfileNotFound from '../components/UserComponents/ProfileNotFound.jsx';
import SkeletonProfile from '../skeletons/skeletonProfile.jsx';


const Profile = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const otherUser = useSelector((state) => state.user.otherUser);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate("/sign-in");
        }
    }, [isAuthenticated, navigate]);

    // Fetch current user
    const currentUser = useFetchUserData(isAuthenticated);

    // Fetch other user — enable as soon as we have an id that might be different
    // Convert to string for safe comparison
    const targetId = id?.toString();
    const currentUserId = user?.id?.toString();
    const isOtherUser = !!targetId && targetId !== currentUserId;
    
    const otherUserQuery = useFetchOtherUserData(targetId, isOtherUser);

    // Sync current user to Redux
    useEffect(() => {
        if (currentUser.isSuccess && currentUser.data) {
            dispatch(setUser(currentUser.data));
        }
    }, [currentUser.isSuccess, currentUser.data, dispatch]);

    // Sync other user to Redux
    useEffect(() => {
        if (otherUserQuery.isSuccess && otherUserQuery.data) {
            dispatch(setOtherUser(otherUserQuery.data));
        }
    }, [otherUserQuery.isSuccess, otherUserQuery.data, dispatch]);

    // Clear otherUser when viewing own profile (prevents stale data)
    useEffect(() => {
        if (!isOtherUser && otherUser) {
            dispatch(removeOtherUser());
        }
    }, [isOtherUser, otherUser, dispatch]);

    // Determine which profile to show
    const isOwnProfile = !targetId || targetId === currentUserId;
    const profile = isOwnProfile ? user : otherUser;

    // Show loading while we're still figuring out who to show
    const isLoading = currentUser.isLoading || (isOtherUser && otherUserQuery.isLoading);

    if (isLoading) {
        return <SkeletonProfile/>;
    }

    return profile ? (
        <ProfileData profile={profile} isOwnProfile={isOwnProfile} />
    ) : (
        <ProfileNotFound />
    );
};

export default Profile;