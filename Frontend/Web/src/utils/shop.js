// Small helpers shared by the cart / checkout / orders / boost screens.

export const formatNaira = (value) =>
    `₦${Number(value || 0).toLocaleString('en-NG', { maximumFractionDigits: 2 })}`;

export const formatDateTime = (iso) =>
    iso
        ? new Date(iso).toLocaleString('en-NG', { dateStyle: 'medium', timeStyle: 'short' })
        : '-';

/** Turn a DRF / axios error into one readable sentence. */
export const getErrorMessage = (error, fallback = 'Something went wrong. Please try again.') => {
    const data = error?.response?.data;

    if (!data) {
        return error?.message === 'Network Error'
            ? 'Cannot reach the server. Check your connection and try again.'
            : fallback;
    }
    if (typeof data === 'string') return data;
    if (data.detail) return String(data.detail);

    const first = Object.values(data)[0];
    if (Array.isArray(first)) return String(first[0]);
    if (typeof first === 'string') return first;
    return fallback;
};

export const NIGERIA_STATES = [
    ['abia', 'Abia'], ['adamawa', 'Adamawa'], ['akwa_ibom', 'Akwa Ibom'], ['anambra', 'Anambra'],
    ['bauchi', 'Bauchi'], ['bayelsa', 'Bayelsa'], ['benue', 'Benue'], ['borno', 'Borno'],
    ['cross_river', 'Cross River'], ['delta', 'Delta'], ['ebonyi', 'Ebonyi'], ['edo', 'Edo'],
    ['ekiti', 'Ekiti'], ['enugu', 'Enugu'], ['fct', 'Federal Capital Territory (Abuja)'],
    ['gombe', 'Gombe'], ['imo', 'Imo'], ['jigawa', 'Jigawa'], ['kaduna', 'Kaduna'],
    ['kano', 'Kano'], ['katsina', 'Katsina'], ['kebbi', 'Kebbi'], ['kogi', 'Kogi'],
    ['kwara', 'Kwara'], ['lagos', 'Lagos'], ['nasarawa', 'Nasarawa'], ['niger', 'Niger'],
    ['ogun', 'Ogun'], ['ondo', 'Ondo'], ['osun', 'Osun'], ['oyo', 'Oyo'],
    ['plateau', 'Plateau'], ['rivers', 'Rivers'], ['sokoto', 'Sokoto'], ['taraba', 'Taraba'],
    ['yobe', 'Yobe'], ['zamfara', 'Zamfara'],
];
