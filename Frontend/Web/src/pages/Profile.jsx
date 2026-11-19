import { useNavigate, useParams } from 'react-router-dom';
import ProfileData from "../components/UserComponents/ProfileData.jsx";
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useFetchOtherUserData, useFetchUserData } from '../hooks/UseQuery.js';
import { removeOtherUser, setOtherUser, setUser } from '../slice/UserSlice.js';
import ProfileNotFound from '../components/UserComponents/ProfileNotFound.jsx';
import SkeletonProfile from '../skeletons/skeletonProfile.jsx';
import FeedbackSection from '../components/JijiComponents/FeedbackSection.jsx';
import VerifiedIdCard from '../components/JijiComponents/VerifiedIdCard.jsx';
import SellerTools from '../components/JijiComponents/SellerTools.jsx';
import SafeDealPanel from '../components/JijiComponents/SafeDealPanel.jsx';


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

    const currentUser = useFetchUserData(isAuthenticated);

    const targetId = id?.toString();
    const currentUserId = user?.id?.toString();
    const isOtherUser = !!targetId && targetId !== currentUserId;
    
    const otherUserQuery = useFetchOtherUserData(targetId, isOtherUser);

    useEffect(() => {
        if (currentUser.isSuccess && currentUser.data) {
            dispatch(setUser(currentUser.data));
        }
    }, [currentUser.isSuccess, currentUser.data, dispatch]);

    useEffect(() => {
        if (otherUserQuery.isSuccess && otherUserQuery.data) {
            dispatch(setOtherUser(otherUserQuery.data));
        }
    }, [otherUserQuery.isSuccess, otherUserQuery.data, dispatch]);

    useEffect(() => {
        if (!isOtherUser && otherUser) {
            dispatch(removeOtherUser());
        }
    }, [isOtherUser, otherUser, dispatch]);

    const isOwnProfile = !targetId || targetId === currentUserId;
    const profile = isOwnProfile ? user : otherUser;

    const isLoading = currentUser.isLoading || (isOtherUser && otherUserQuery.isLoading);

    if (isLoading) {
        return <SkeletonProfile/>;
    }

    return profile ? (
        <>
            <ProfileData profile={profile} isOwnProfile={isOwnProfile} />
            <div className="mx-auto max-w-5xl space-y-5 px-4 pb-12">
                <FeedbackSection
                    sellerId={profile.id}
                    currentUserId={user?.id}
                    canReview={!isOwnProfile}
                />
                {isOwnProfile && (
                    <>
                        <VerifiedIdCard isAuthenticated={isAuthenticated} />
                        <SellerTools isAuthenticated={isAuthenticated} />
                        <SafeDealPanel />
                    </>
                )}
            </div>
        </>
    ) : (
        <ProfileNotFound />
    );
};

export default Profile;