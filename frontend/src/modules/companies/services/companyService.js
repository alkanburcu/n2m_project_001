import api from '@/services/api'
const COMPANIES = '/companies/'

const getCompanies = ({
    search = '',
    page = 1,
    pageSize = 20,
}= {}) => {
    return api.get(
        COMPANIES,
    {
        params: {
            search,
            page,
            page_size: pageSize,
        },
    },
)
}

const createCompany = (payload) => {
    return api.post(
        COMPANIES,
        payload,
    )
}

export default{
    getCompanies,
    createCompany,
}