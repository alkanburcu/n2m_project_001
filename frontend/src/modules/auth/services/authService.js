import api from '@/services/api'
const login = (credentials) => {return api.post ('/auth/login/', credentials)}
const refreshToken = (refresh) => {return api.post('/auth/refresh/', {refresh})}
const logout = (refresh) => {return api.post('/auth/logout/', {refresh})}
export default { login, refreshToken, logout, }
