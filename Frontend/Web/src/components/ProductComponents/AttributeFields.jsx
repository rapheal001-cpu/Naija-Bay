import { HiOutlineCollection } from 'react-icons/hi';

/**
 * Dynamic category-specific specification fields, driven by
 * GET /api/v1/core/attributes/ definitions. Shared by SellForm and EditProductForm.
 *
 * Values register under `attributes.<slug>` (react-hook-form), so the submit
 * payload carries `attributes: { slug: value }` for the product serializer.
 *
 * @param {{ definitions: Array, register: Function, errors: Object }} props
 */
const AttributeFields = ({ definitions, register, errors }) => {
    if (!definitions?.length) return null;

    const inputBase = "w-full border rounded-xl px-4 py-3 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-4 transition-all border-gray-200 focus:border-brand focus:ring-brand/10";

    return (
        <div className="space-y-5">
            <div className="flex items-center gap-2">
                <HiOutlineCollection size={18} className="text-brand" />
                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Specifications</h3>
                <span className="text-xs font-medium text-gray-400">
                    ({definitions.filter((d) => d.required).length} required)
                </span>
            </div>

            <p className="-mt-3 text-xs leading-relaxed text-gray-500">
                Add details that help buyers find your ad in search filters.
                Fields marked <span className="font-bold text-gray-700">*</span> are required for this category.
            </p>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {definitions.map((definition) => {
                    const slug = definition.slug;
                    const fieldName = `attributes.${slug}`;
                    const error = errors?.attributes?.[slug];
                    const label = (
                        <label htmlFor={`attr_${slug}`} className="text-[13px] font-bold text-gray-700 ml-1">
                            {definition.label}
                            {definition.required && <span className="text-red-500"> *</span>}
                            {definition.unit && <span className="font-semibold text-gray-400"> ({definition.unit})</span>}
                        </label>
                    );

                    return (
                        <div key={slug} className="space-y-1.5">
                            {label}

                            {definition.data_type === 'select' && (
                                <select
                                    id={`attr_${slug}`}
                                    {...register(fieldName, {
                                        required: definition.required ? `${definition.label} is required.` : false,
                                    })}
                                    className={`${inputBase} appearance-none ${error ? 'border-red-300 focus:border-red-400 bg-red-50/30' : ''}`}
                                >
                                    <option value="">Select {definition.label.toLowerCase()}</option>
                                    {(definition.options || []).map((option) => (
                                        <option key={option.value} value={option.value}>{option.label}</option>
                                    ))}
                                </select>
                            )}

                            {definition.data_type === 'multiselect' && (
                                <div className="flex flex-wrap gap-2 pt-1">
                                    {(definition.options || []).map((option) => (
                                        <label
                                            key={option.value}
                                            className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-gray-200 px-3 py-2 text-sm font-semibold text-gray-600 has-checked:border-brand has-checked:bg-brand/5 has-checked:text-brand"
                                        >
                                            <input type="checkbox" value={option.value} className="h-4 w-4 accent-brand" {...register(fieldName)} />
                                            {option.label}
                                        </label>
                                    ))}
                                </div>
                            )}

                            {(definition.data_type === 'number' || definition.data_type === 'decimal') && (
                                <input
                                    id={`attr_${slug}`}
                                    type="number"
                                    step="any"
                                    placeholder={definition.min_value != null ? `Min ${definition.min_value}` : ''}
                                    {...register(fieldName, {
                                        valueAsNumber: true,
                                        required: definition.required ? `${definition.label} is required.` : false,
                                        min: definition.min_value != null ? { value: Number(definition.min_value), message: `Minimum is ${definition.min_value}.` } : undefined,
                                        max: definition.max_value != null ? { value: Number(definition.max_value), message: `Maximum is ${definition.max_value}.` } : undefined,
                                    })}
                                    className={`${inputBase} ${error ? 'border-red-300 focus:border-red-400 bg-red-50/30' : ''}`}
                                />
                            )}

                            {definition.data_type === 'boolean' && (
                                <label className="flex items-center gap-3 rounded-xl bg-gray-50 border border-gray-100 px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors select-none">
                                    <input type="checkbox" className="w-5 h-5 accent-brand rounded cursor-pointer" {...register(fieldName)} />
                                    <span className="text-sm font-semibold text-gray-700">Yes</span>
                                </label>
                            )}

                            {definition.data_type === 'date' && (
                                <input
                                    id={`attr_${slug}`}
                                    type="date"
                                    {...register(fieldName, {
                                        required: definition.required ? `${definition.label} is required.` : false,
                                    })}
                                    className={`${inputBase} ${error ? 'border-red-300 focus:border-red-400 bg-red-50/30' : ''}`}
                                />
                            )}

                            {definition.data_type === 'text' && (
                                <input
                                    id={`attr_${slug}`}
                                    type="text"
                                    placeholder={definition.label}
                                    {...register(fieldName, {
                                        required: definition.required ? `${definition.label} is required.` : false,
                                    })}
                                    className={`${inputBase} ${error ? 'border-red-300 focus:border-red-400 bg-red-50/30' : ''}`}
                                />
                            )}

                            {error && <p className="text-red-500 text-xs font-semibold ml-1">{error.message || String(error.message || 'Invalid value')}</p>}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AttributeFields;
